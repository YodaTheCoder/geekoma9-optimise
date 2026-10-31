from __future__ import annotations

import shlex
from pathlib import Path

import pytest
import yaml

from harness.agents import make_agent
from harness.agents.command import CommandAgent, render_command
from harness.agents.null import NullAgent
from harness.agents.oracle import OracleAgent
from harness.config import AgentConfig, ConfigError
from harness.remote import RemoteError
from harness.paths import attempt_paths

EMPTY = dict(workdir="", issue_file="", endpoint="", model="", log="")
PATHS = attempt_paths("r1", "t1", 1)


def cfg(**kw):
    return AgentConfig(kind="command", name="x", command="agent {workdir} --m {model}", **kw)


def test_render_quotes_values():
    assert render_command("x {issue_file}", **{**EMPTY, "issue_file": "/a b/i.md"}) == "x '/a b/i.md'"


def test_render_unknown_placeholder():
    with pytest.raises(ConfigError):
        render_command("{nope}", **EMPTY)


def test_shortlist_templates_render():
    root = Path(__file__).resolve().parent.parent
    for h in yaml.safe_load((root / "research/shortlist.yaml").read_text())["harnesses"]:
        render_command(h["command_template"], **EMPTY)


def test_command_agent_reports_timeout(fake_remote):
    fake_remote.reply("setsid", returncode=124)
    res = CommandAgent(cfg()).run(fake_remote, PATHS, "http://127.0.0.1:11500", "m", 5)
    assert res.timed_out and res.exit_code == 124 and res.steps is None


def test_command_agent_137_after_budget_is_timeout(fake_remote):
    fake_remote.reply("setsid", returncode=137)
    assert CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 0).timed_out


def test_command_agent_137_before_budget_is_not_timeout(fake_remote):
    # SIGKILL well inside the budget is the kernel OOM killer, not `timeout -k`
    fake_remote.reply("setsid", returncode=137)
    res = CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 1000)
    assert not res.timed_out and res.exit_code == 137


def test_command_agent_success_not_timeout(fake_remote):
    res = CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert not res.timed_out and res.exit_code == 0 and res.wall_s >= 0


def test_command_agent_kills_process_group(fake_remote):
    CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert any("sudo -n pkill -KILL -s" in c and "agent.sid" in c for c in fake_remote.calls)
    # sudo runs the command in its own session (use_pty): kill everything the user owns too
    assert any("sudo -n pkill -KILL -u agentrun" in c for c in fake_remote.calls)


def _agent_call(remote):
    return next(c for c in remote.calls if "setsid" in c)


def test_command_agent_runs_as_agentrun(fake_remote):
    CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    calls = fake_remote.calls
    own = f"{PATHS.workdir} {PATHS.issue_file}"
    i_give = calls.index(f"sudo -n chown -R agentrun: {own}")
    i_run = calls.index(_agent_call(fake_remote))
    i_kill = next(i for i, c in enumerate(calls) if "pkill" in c)
    i_back = calls.index(f"sudo -n chown -R markn: {own}")
    assert i_give < i_run < i_kill < i_back
    script = shlex.split(_agent_call(fake_remote))[7]
    assert "exec timeout -k 30 5 sudo -n -u agentrun -H bash -c " in script
    # the log is opened by the wrapper (markn), never by the agent user
    assert _agent_call(fake_remote).endswith("> " + PATHS.agent_log + " 2>&1")


def test_command_agent_gives_files_back_when_run_raises(fake_remote):
    orig = fake_remote.run

    def run(cmd, timeout=None, check=True):
        if "setsid" in cmd:
            orig(cmd, timeout, check)
            raise RemoteError("dropped")
        return orig(cmd, timeout, check)
    fake_remote.run = run
    with pytest.raises(RemoteError, match="dropped"):
        CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert fake_remote.calls[-1] == f"sudo -n chown -R markn: {PATHS.workdir} {PATHS.issue_file}"


def test_command_agent_command_shape_and_timeout(fake_remote):
    CommandAgent(cfg(env={"K": "v w"})).run(fake_remote, PATHS, "e", "mod", 50)
    run = _agent_call(fake_remote)
    assert run.startswith(f"cd {PATHS.workdir} && setsid --wait bash -c ")
    assert "timeout -k 30 50 sudo -n -u agentrun -H bash -c" in run
    assert run.endswith("> " + PATHS.agent_log + " 2>&1")
    script = shlex.split(run)[7]               # cd W && setsid bash -c <script> > L 2>&1
    inner = shlex.split(script.split("bash -c ", 1)[1])[0]
    assert "export K='v w'; " in inner
    assert fake_remote.timeouts[fake_remote.calls.index(run)] == 170


def test_command_agent_counts_steps(fake_remote):
    fake_remote.files[PATHS.agent_log] = "tool tool x tool"
    res = CommandAgent(cfg(steps_regex="tool")).run(fake_remote, PATHS, "e", "m", 5)
    assert res.steps == 3


def test_oracle_and_null(fake_remote):
    assert NullAgent().run(fake_remote, PATHS, "e", "m", 5).exit_code == 0
    assert fake_remote.calls == []
    OracleAgent(mirror="/m.git", task_set="v1").run(fake_remote, PATHS, "e", "m", 5)
    # straight from the mirror: no exported task folder exists while an agent runs
    assert fake_remote.calls[0] == (
        "set -o pipefail; git -C /m.git show taskset-v1:tasks/t1/solution.patch"
        f" | git -C {PATHS.workdir} apply")
    assert "task" not in PATHS.workdir.rsplit("/", 1)[-1]


def test_make_agent():
    assert isinstance(make_agent(AgentConfig(kind="null", name="n")), NullAgent)
    oracle = make_agent(AgentConfig(kind="oracle", name="o"), task_set="v1", mirror="/m.git")
    assert isinstance(oracle, OracleAgent) and (oracle.mirror, oracle.task_set) == ("/m.git", "v1")
    assert isinstance(make_agent(cfg()), CommandAgent)


def test_pkill_runs_when_run_raises(fake_remote):
    orig = fake_remote.run

    def run(cmd, timeout=None, check=True):
        if "setsid" in cmd:
            raise RemoteError("dropped")
        if "pkill" in cmd:
            orig(cmd, timeout, check)
            raise RemoteError("dropped again")
        return orig(cmd, timeout, check)

    fake_remote.run = run
    with pytest.raises(RemoteError, match="dropped$"):
        CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert any("pkill -KILL -s" in c for c in fake_remote.calls)


def test_setsid_wait(fake_remote):
    CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert "setsid --wait bash -c" in _agent_call(fake_remote)


@pytest.mark.parametrize("c", [
    cfg(env={"A B": "x"}), cfg(env={"1A": "x"}), cfg(steps_regex="("),
])
def test_invalid_config_raises(fake_remote, c):
    with pytest.raises(ConfigError):
        CommandAgent(c).run(fake_remote, PATHS, "e", "m", 5)


def test_render_attr_error():
    with pytest.raises(ConfigError):
        render_command("{workdir.x}", **EMPTY)


def test_agent_stdin_is_dev_null(fake_remote):
    # An open ssh stdin hangs agents that read piped input (OpenCode `run` waits on it forever).
    CommandAgent(cfg()).run(fake_remote, PATHS, "e", "m", 5)
    assert _agent_call(fake_remote).endswith("< /dev/null > " + PATHS.agent_log + " 2>&1")
