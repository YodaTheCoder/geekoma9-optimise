from __future__ import annotations

import json
import subprocess
from dataclasses import replace

import pytest

from conftest import FakeRemote
from harness.agents.base import AgentResult
from harness.config import AgentConfig, ExperimentConfig, RuntimeConfig
from harness.paths import ROOT
from harness.remote import RemoteError
from harness.results import append_record, read_records
from harness.config import ConfigError
from harness.provision import SCRIPTS_SRC
from harness.run import (HostDirtyError, InfraError, RunLockedError, RuntimeRestartError,
                         config_hash, harness_version, preflight, run_attempt, run_experiment,
                         scripts_hash)
from harness.tiers import TASK_SETS

SCREENING = TASK_SETS["v1"]["screening"]
PASS_XML = '<testsuites><testsuite><testcase name="a"/><testcase name="b"/></testsuite></testsuites>'
FAIL_XML = '<testsuites><testsuite><testcase name="a"/><testcase name="b"><failure/></testcase></testsuite></testsuites>'
OK = AgentResult(exit_code=0, timed_out=False, wall_s=600.0, steps=4)

CFG = ExperimentConfig(
    id="e0", task_set="v1", tier="screening",
    runtime=RuntimeConfig(kind="ollama", model="m:latest", context=8192),
    agent=AgentConfig(kind="command", name="aider", command="x", version="0.9"),
    timeout_s=100, cooldown_s=7)


class BenchRemote(FakeRemote):
    """FakeRemote that serves score.sh output for any attempt."""

    def __init__(self, hidden=PASS_XML, usage=""):
        super().__init__()
        self.hidden = hidden
        self.usage = usage
        self.reply("usage_proxy.py", stdout="111\n")
        self.reply("sample.sh", stdout="222\n")
        self.reply("run.lock", stdout="333\n")
        self.reply("systemctl is-active ollama", stdout="active\n")

    def read_text(self, path):
        d = path.rsplit("/", 1)[0]
        if path.endswith("/score/score.json"):
            return json.dumps({"import_log": f"{d}/import.log", "import_timed_out": False,
                               "regression_xml": f"{d}/regression.xml", "regression_timed_out": False,
                               "hidden_xml": f"{d}/hidden.xml", "hidden_timed_out": False,
                               "extra_exit": None, "extra_timed_out": False})
        if path.endswith("/hidden.xml"):
            return self.hidden
        if path.endswith("/regression.xml"):
            return PASS_XML
        if path.endswith("/usage.jsonl"):
            return self.usage
        if path.endswith("/samples.csv"):
            return "ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c\n1,1000,200,300,80.0\n"
        return ""


class FakeRuntime:
    upstream = "http://127.0.0.1:11434"
    model = "m:latest"

    def __init__(self):
        self.loaded = ["m:latest"]
        self.starts = self.stops = 0
        self.start_error: Exception | None = None

    def start(self, remote):
        self.starts += 1
        if self.start_error and self.starts > 1:
            raise self.start_error

    def stop(self, remote):
        self.stops += 1

    def versions(self, remote):
        return {"runtime": "ollama 0.34.4", "model_digest": "sha256:d"}

    def loaded_models(self, remote):
        return list(self.loaded)


class FakeAgent:
    def __init__(self, *script, events=None):
        self.script = list(script)  # AgentResult or Exception per call; then OK
        self.calls: list[str] = []
        self.events = events if events is not None else []

    def run(self, remote, paths, endpoint, model, timeout_s):
        self.calls.append(paths.root)
        self.events.append("agent")
        assert endpoint == "http://127.0.0.1:11500" and model == "m:latest" and timeout_s == 100
        step = self.script.pop(0) if self.script else OK
        if isinstance(step, BaseException):
            raise step
        return step


class FakeBench:
    mirror = "/m.git"

    def __init__(self, push_ok=True, events=None):
        self.push_ok = push_ok
        self.updates = 0
        self.prepared: list[tuple[str, str]] = []
        self.exported: list[str] = []
        self.prepare_error: Exception | None = None
        self.events = events if events is not None else []

    def update(self):
        self.updates += 1

    def base_sha(self, task_set):
        return "abc123"

    def prepare_workdir(self, paths, task_set, task, branch):
        if self.prepare_error:
            err, self.prepare_error = self.prepare_error, None
            raise err
        self.prepared.append((task, branch))

    def export_task_files(self, task_set, task, dest):
        self.events.append("export")
        self.exported.append(dest)

    def commit_and_push(self, paths, branch, message):
        return self.push_ok


class FakeClock:
    def __init__(self):
        self.t = 1_800_000_000.0
        self.sleeps: list[float] = []

    def time(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def attempt(remote, runtime=None, agent=None, bench=None, cfg=CFG):
    return run_attempt(cfg, "e0-202610311200", "001-health-clamp", 1, remote=remote,
                       runtime=runtime or FakeRuntime(), agent=agent or FakeAgent(),
                       bench=bench or FakeBench(), scripts_dir=f"{ROOT}/bin",
                       harness_sha="deadbee", clock=FakeClock())


def experiment(tmp_path, remote, agent, runtime=None, bench=None, cfg=CFG, clock=None):
    runtime = runtime or FakeRuntime()
    clock = clock or FakeClock()
    run_experiment(cfg, tmp_path, remote=remote, bench=bench or FakeBench(), clock=clock,
                   runtime=runtime, agent=agent, harness_sha="deadbee")
    return read_records(tmp_path / "results.jsonl"), runtime, clock


def test_pass_record_fields():
    remote = BenchRemote()
    rec = attempt(remote)
    assert rec.status == "pass" and rec.error == ""
    assert (rec.hidden_passed, rec.hidden_total) == (2, 2)
    assert rec.regressions_ok and rec.parse_ok and rec.pushed
    assert rec.branch == "exp/e0-202610311200/001-health-clamp-r1"
    assert rec.wall_s == 600.0 and rec.steps == 4
    assert rec.peak_mem_mib == 1000 and rec.peak_gpu_mem_mib == 500 and not rec.throttled
    assert rec.versions == {"runtime": "ollama 0.34.4", "model_digest": "sha256:d",
                            "agent": "aider 0.9", "harness": "deadbee", "task_set": "v1",
                            "sampling": "{}", "config": config_hash(CFG)}
    assert rec.started_at == "2027-01-15T08:00:00Z"
    # helpers started detached, stopped by process group, score.sh run with the godot binary
    proxy = next(c for c in remote.calls if "usage_proxy.py" in c)
    assert proxy.startswith("setsid nohup ") and "--listen 127.0.0.1:11500" in proxy
    assert "--upstream http://127.0.0.1:11434" in proxy and proxy.endswith("& echo $!")
    assert any("sample.sh" in c and "samples.csv 5" in c for c in remote.calls)
    assert "kill -TERM -- -111" in remote.calls and "kill -TERM -- -222" in remote.calls
    score = next(c for c in remote.calls if "score.sh" in c)
    assert "/srv/agentbench/opt/godot/godot" in score and "abc123" in score and "/m.git" in score


def test_upstream_error_becomes_infra_error():
    usage = json.dumps({"path": "/v1/chat", "upstream_error": True}) + "\n"
    rec = attempt(BenchRemote(hidden=FAIL_XML, usage=usage))
    assert rec.status == "infra_error" and rec.upstream_errors == 1 and "upstream" in rec.error


def test_upstream_error_on_pass_stays_pass():
    usage = json.dumps({"path": "/v1/chat", "upstream_error": True}) + "\n"
    assert attempt(BenchRemote(usage=usage)).status == "pass"


def test_preflight_dirty_host_is_infra_error():
    remote = BenchRemote()
    remote.replies.insert(0, ("pgrep", subprocess.CompletedProcess([], 0, "4242\n", "")))
    agent = FakeAgent()
    rec = attempt(remote, agent=agent)
    assert rec.status == "infra_error" and agent.calls == []
    pgrep = next(c for c in remote.calls if "pgrep" in c)
    assert pgrep == "pgrep -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'"


def test_preflight_wrong_loaded_models():
    rt = FakeRuntime()
    rt.loaded = ["m:latest", "other:7b"]
    with pytest.raises(InfraError):
        preflight(FakeRemote(), rt)


def test_score_failure_is_infra_error():
    remote = BenchRemote()
    remote.replies.insert(0, ("score.sh", subprocess.CompletedProcess([], 3, "", "no godot")))

    def run(cmd, timeout=None, check=True):  # emulate Remote's check=True
        r = FakeRemote.run(remote, cmd, timeout, check)
        if check and r.returncode:
            raise subprocess.CalledProcessError(r.returncode, cmd)
        return r
    remote.run = run
    rec = attempt(remote)
    assert rec.status == "infra_error" and "CalledProcessError" in rec.error


def test_agent_error_still_stops_helpers():
    remote = BenchRemote()
    rec = attempt(remote, agent=FakeAgent(RemoteError("ssh dropped")))
    assert rec.status == "infra_error" and "ssh dropped" in rec.error
    assert "kill -TERM -- -111" in remote.calls and "kill -TERM -- -222" in remote.calls


def test_timeout_status():
    rec = attempt(BenchRemote(), agent=FakeAgent(AgentResult(124, True, 100.0)))
    assert rec.status == "timeout"


def test_infra_error_retried_once_then_moves_on(tmp_path):
    agent = FakeAgent(RemoteError("drop 1"), RemoteError("drop 2"))
    recs, rt, _ = experiment(tmp_path, BenchRemote(), agent)
    first = [r for r in recs if r.task == SCREENING[0]]
    assert [r.status for r in first] == ["infra_error", "infra_error"]
    assert [r.task for r in recs[2:]] == SCREENING[1:]
    assert all(r.status == "pass" for r in recs[2:])
    assert rt.starts == 3 and rt.stops == 1  # initial + one restart per infra_error


def test_retry_after_infra_can_pass(tmp_path):
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(RemoteError("drop")))
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]
    assert len(recs) == len(SCREENING) + 1


def test_failed_restart_stops_the_run_without_recording_the_retry(tmp_path):
    # e.g. ssh down for minutes: recording the untried retry would mark the entry done
    rt = FakeRuntime()
    rt.start_error = RemoteError("ollama dead")
    remote = BenchRemote()
    with pytest.raises(RuntimeRestartError, match="ollama dead"):
        experiment(tmp_path, remote, FakeAgent(RemoteError("drop")), runtime=rt)
    recs = read_records(tmp_path / "results.jsonl")
    assert [(r.task, r.status) for r in recs] == [(SCREENING[0], "infra_error")]
    assert remote.calls[-2] == "sudo -n systemctl start ollama"  # restored, then lock released
    # a resume reruns the untried retry, on its own branch
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent())
    assert [r.status for r in recs if r.task == SCREENING[0]] == ["infra_error", "pass"]
    assert len(recs) == len(SCREENING) + 1


def test_bench_error_is_infra_not_fatal(tmp_path):
    bench = FakeBench()
    bench.prepare_error = subprocess.CalledProcessError(128, "git clone")
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), bench=bench)
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]


def test_system_ollama_stopped_before_runtime_and_started_after(tmp_path):
    remote = BenchRemote()
    experiment(tmp_path, remote, FakeAgent())
    i_active = remote.calls.index("systemctl is-active ollama")
    i_stop = remote.calls.index("sudo -n systemctl stop ollama")
    assert i_active < i_stop < next(i for i, c in enumerate(remote.calls) if "usage_proxy" in c)
    assert remote.calls[-2] == "sudo -n systemctl start ollama"
    assert remote.calls.count("sudo -n systemctl start ollama") == 1


def test_system_ollama_restored_on_error(tmp_path):
    remote = BenchRemote()
    with pytest.raises(ValueError):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")))
    assert remote.calls[-2] == "sudo -n systemctl start ollama"


def test_system_ollama_restored_on_host_dirty(tmp_path):
    remote = StrayRemote(persistent=True)
    with pytest.raises(HostDirtyError):
        experiment(tmp_path, remote, FakeAgent())
    assert remote.calls[-2] == "sudo -n systemctl start ollama"


def test_system_ollama_restored_when_runtime_start_fails(tmp_path):
    class Boom(FakeRuntime):
        def start(self, remote):
            raise RemoteError("no")
    remote = BenchRemote()
    with pytest.raises(RemoteError):
        experiment(tmp_path, remote, FakeAgent(), runtime=Boom())
    assert remote.calls[-2] == "sudo -n systemctl start ollama"


class StartFlaky(BenchRemote):
    def __init__(self, fail_times, error=None):
        super().__init__()
        self.fail_times, self.error, self.start_calls = fail_times, error, 0

    def run(self, cmd, timeout=None, check=True):
        if cmd == "sudo -n systemctl start ollama":
            self.start_calls += 1
            if self.start_calls <= self.fail_times:
                if self.error:
                    raise self.error
                return subprocess.CompletedProcess([], 1, "", "")
        return super().run(cmd, timeout, check)


def test_system_ollama_start_retried_until_ok(tmp_path, capsys):
    remote = StartFlaky(2, RemoteError("ssh 255"))
    experiment(tmp_path, remote, FakeAgent())
    assert remote.start_calls == 3 and "NOT restarted" not in capsys.readouterr().err


def test_system_ollama_start_nonzero_exit_retried(tmp_path, capsys):
    remote = StartFlaky(1)
    experiment(tmp_path, remote, FakeAgent())
    assert remote.start_calls == 2 and "NOT restarted" not in capsys.readouterr().err


def test_system_ollama_start_always_fails_warns_without_raising(tmp_path, capsys):
    remote = StartFlaky(99, RemoteError("ssh 255"))
    recs, _, _ = experiment(tmp_path, remote, FakeAgent())  # normal run completes
    assert len(recs) == len(SCREENING) and remote.start_calls == 3
    assert "system Ollama NOT restarted" in capsys.readouterr().err


def test_start_failure_does_not_mask_original_error(tmp_path, capsys):
    remote = StartFlaky(99, RemoteError("ssh 255"))
    with pytest.raises(ValueError, match="agent bug"):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")))
    assert "system Ollama NOT restarted" in capsys.readouterr().err


def test_runtime_stop_failure_does_not_mask_original_error(tmp_path, capsys):
    class BadStop(FakeRuntime):
        def stop(self, remote):
            raise RemoteError("stop failed")
    remote = BenchRemote()
    with pytest.raises(ValueError, match="agent bug"):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")), runtime=BadStop())
    assert "runtime stop failed" in capsys.readouterr().err
    assert remote.calls[-2] == "sudo -n systemctl start ollama"


def test_resume_skips_done(tmp_path):
    (tmp_path / "run_id").write_text("e0-202601010000\n")
    seed = attempt(BenchRemote())
    append_record(tmp_path / "results.jsonl", replace(seed, task=SCREENING[0], run_id="e0-202601010000"))
    agent = FakeAgent()
    bench = FakeBench()
    recs, _, _ = experiment(tmp_path, BenchRemote(), agent, bench=bench)
    assert len(agent.calls) == len(SCREENING) - 1
    assert [t for t, _ in bench.prepared] == SCREENING[1:]
    assert all(r.run_id == "e0-202601010000" for r in recs)
    assert bench.prepared[0][1] == f"exp/e0-202601010000/{SCREENING[1]}-r1"


def test_run_id_created_and_persisted(tmp_path):
    clock = FakeClock()
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), clock=clock)
    run_id = (tmp_path / "run_id").read_text().strip()
    # seconds: a validate rerun within the same minute must not reuse branch names
    assert run_id.startswith("e0-") and len(run_id) == len("e0-YYYYmmddHHMMSS")
    assert all(r.run_id == run_id and r.experiment == "e0" for r in recs)


def test_cooldown_between_attempts(tmp_path):
    _, _, clock = experiment(tmp_path, BenchRemote(), FakeAgent())
    # 2 s proxy flush wait in every attempt, cooldown only between attempts
    assert clock.sleeps == [2, 7] * (len(SCREENING) - 1) + [2]


def test_push_failure_recorded_not_fatal(tmp_path):
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), bench=FakeBench(push_ok=False))
    assert len(recs) == len(SCREENING)
    assert all(not r.pushed and r.status == "pass" for r in recs)


class StrayRemote(BenchRemote):
    """pgrep reports a stray until pkill runs (or always, if persistent)."""

    def __init__(self, persistent=False):
        super().__init__()
        self.persistent = persistent
        self.killed = False

    def run(self, cmd, timeout=None, check=True):
        if cmd.startswith("pkill -KILL"):
            self.killed = True
        if cmd.startswith("pgrep") and (self.persistent or not self.killed):
            self.calls.append(cmd)
            return subprocess.CompletedProcess([], 0, "4242\n", "")
        return super().run(cmd, timeout, check)


def test_strays_cleared_by_pkill_then_retry_runs(tmp_path):
    remote = StrayRemote()
    agent = FakeAgent()
    recs, rt, _ = experiment(tmp_path, remote, agent)
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]
    assert len(recs) == len(SCREENING) + 1 and len(agent.calls) == len(SCREENING)
    assert "pkill -KILL -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'" in remote.calls
    assert rt.starts == 2


def test_persistent_strays_stop_the_experiment(tmp_path):
    agent = FakeAgent()
    rt = FakeRuntime()
    with pytest.raises(HostDirtyError, match="4242"):
        experiment(tmp_path, StrayRemote(persistent=True), agent, runtime=rt)
    recs = read_records(tmp_path / "results.jsonl")
    assert [(r.task, r.status) for r in recs] == [(SCREENING[0], "infra_error")]
    assert agent.calls == [] and rt.stops == 1
    # resume reruns the interrupted attempt
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent())
    assert [r.status for r in recs if r.task == SCREENING[0]] == ["infra_error", "pass"]


def test_preflight_infra_record_still_pins_versions():
    remote = BenchRemote()
    remote.replies.insert(0, ("pgrep", subprocess.CompletedProcess([], 0, "4242\n", "")))
    rec = attempt(remote)
    assert rec.versions == {"agent": "aider 0.9", "harness": "deadbee", "task_set": "v1",
                            "sampling": "{}", "config": config_hash(CFG)}


def test_proxy_probe_is_tcp_only():
    remote = BenchRemote()
    attempt(remote)
    assert any("/dev/tcp/127.0.0.1/11500" in c for c in remote.calls)
    assert not any("curl" in c for c in remote.calls)


def test_short_regression_run_fails_and_logs_are_fetched():
    class Short(BenchRemote):
        def read_text(self, path):
            if path.endswith("/score/score.json"):
                d = json.loads(super().read_text(path))
                return json.dumps({**d, "regression_expected": 3,
                                   "regression_log": path.replace("score.json", "regression.log"),
                                   "hidden_log": path.replace("score.json", "hidden.log")})
            return super().read_text(path)
    remote = Short()
    reads = []
    orig = remote.read_text
    remote.read_text = lambda p: (reads.append(p), orig(p))[1]
    rec = attempt(remote)  # regression.xml holds 2 testcases, the files define 3
    assert rec.status == "fail" and not rec.regressions_ok
    assert any(p.endswith("/score/regression.log") for p in reads)
    assert any(p.endswith("/score/hidden.log") for p in reads)


# ---------------------------------------------------------------- C1: hidden material, agent user

ATT = "/srv/agentbench/runs/e0-202610311200/001-health-clamp-r1"


def test_task_files_exported_only_after_agent_into_score_dir():
    events: list[str] = []
    remote = BenchRemote()
    bench = FakeBench(events=events)
    rec = attempt(remote, agent=FakeAgent(events=events), bench=bench)
    assert rec.status == "pass"
    assert events == ["agent", "export"]
    assert bench.exported == [f"{ATT}/score/task"]
    calls = remote.calls
    i_mkdir = calls.index(f"mkdir -p -m 700 {ATT}/score")
    i_score = next(i for i, c in enumerate(calls) if "score.sh" in c)
    assert i_mkdir < i_score
    assert f" {ATT}/score/task " in calls[i_score]
    i_rm = calls.index(f"rm -rf {ATT}/score/task {ATT}/score/project")
    i_lock = calls.index(f"chmod 700 {ATT}")
    assert i_score < i_rm and i_score < i_lock


def test_cleanup_runs_when_scoring_fails():
    remote = BenchRemote()
    remote.replies.insert(0, ("score.sh", subprocess.CompletedProcess([], 3, "", "")))

    def run(cmd, timeout=None, check=True):
        r = FakeRemote.run(remote, cmd, timeout, check)
        if check and r.returncode:
            raise subprocess.CalledProcessError(r.returncode, cmd)
        return r
    remote.run = run
    assert attempt(remote).status == "infra_error"
    assert f"rm -rf {ATT}/score/task {ATT}/score/project" in remote.calls
    assert f"chmod 700 {ATT}" in remote.calls


def test_attempt_closed_when_agent_fails():
    remote = BenchRemote()
    rec = attempt(remote, agent=FakeAgent(RemoteError("ssh dropped")))
    assert rec.status == "infra_error" and f"chmod 700 {ATT}" in remote.calls


def test_preflight_fails_on_agent_user_process():
    remote = BenchRemote()
    remote.replies.insert(0, ("pgrep -u agentrun", subprocess.CompletedProcess([], 0, "777\n", "")))
    agent = FakeAgent()
    rec = attempt(remote, agent=agent)
    assert rec.status == "infra_error" and "777" in rec.error and agent.calls == []


def test_kill_strays_kills_agent_user(tmp_path):
    remote = StrayRemote()
    experiment(tmp_path, remote, FakeAgent())
    assert "sudo -n pkill -KILL -u agentrun" in remote.calls


class SurvivorRemote(BenchRemote):
    """An agent-user process shows up once the agent has run (it survived the kill)."""

    def __init__(self):
        super().__init__()
        self.agent_ran = False

    def run(self, cmd, timeout=None, check=True):
        if cmd == "pgrep -u agentrun" and self.agent_ran:
            self.calls.append(cmd)
            return subprocess.CompletedProcess([], 0, "888\n", "")
        return super().run(cmd, timeout, check)


def test_agent_user_survivor_blocks_export():
    remote = SurvivorRemote()
    events: list[str] = []

    class A(FakeAgent):
        def run(self, *a):
            remote.agent_ran = True
            return super().run(*a)
    bench = FakeBench(events=events)
    rec = attempt(remote, agent=A(events=events), bench=bench)
    assert rec.status == "infra_error" and "888" in rec.error
    assert bench.exported == [] and not any("score.sh" in c for c in remote.calls)


# ---------------------------------------------------------------- I1: OOM is infra, not the model

OOM_LINE = ("Oct 31 12:00:01 geekoma9 kernel: Out of memory: Killed process 4242 (ollama) "
            "total-vm:1234kB, anon-rss:999kB\n")


def test_kernel_oom_during_agent_is_infra_error():
    remote = BenchRemote()
    remote.replies.insert(0, ("journalctl -k", subprocess.CompletedProcess([], 0, OOM_LINE, "")))
    rec = attempt(remote, agent=FakeAgent(AgentResult(137, False, 50.0)))
    assert rec.status == "infra_error" and "OOM" in rec.error and "ollama" in rec.error
    assert "agent" in rec.error
    assert not any("score.sh" in c for c in remote.calls)
    j = next(c for c in remote.calls if "journalctl -k" in c)
    assert "sudo -n journalctl -k --since @1800000000 --no-pager" in j
    assert "journalctl --user -u agentbench-runtime --since @1800000000 --no-pager" in j
    assert "out of memory|oom-kill|killed process" in j


def test_oom_during_scoring_is_infra_error():
    class LateOom(BenchRemote):
        scored = False

        def run(self, cmd, timeout=None, check=True):
            if "score.sh" in cmd:
                self.scored = True
            if "journalctl -k" in cmd and self.scored:
                self.calls.append(cmd)
                return subprocess.CompletedProcess(
                    [], 0, "kernel: oom-kill:constraint=CONSTRAINT_NONE,task=godot,pid=99\n", "")
            return super().run(cmd, timeout, check)
    rec = attempt(LateOom())
    assert rec.status == "infra_error" and "scoring" in rec.error and "godot" in rec.error


def test_old_attempts_closed_at_run_start(tmp_path):
    remote = BenchRemote()
    experiment(tmp_path, remote, FakeAgent())
    sweep = next(c for c in remote.calls if "find " in c and "/runs" in c)
    assert "find /srv/agentbench/runs " in sweep
    assert "-mindepth 2 -maxdepth 2 -type d -perm /077 -exec chmod 700" in sweep
    assert remote.calls.index(sweep) < next(i for i, c in enumerate(remote.calls) if "usage_proxy" in c)


# ---------------------------------------------------------------- I3: a branch per try

def test_retry_gets_its_own_branch(tmp_path):
    bench = FakeBench()
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(RemoteError("drop")), bench=bench)
    base = (tmp_path / "run_id").read_text().strip()
    first = f"exp/{base}/{SCREENING[0]}-r1"
    assert [(r.status, r.branch) for r in recs[:2]] == [("infra_error", first),
                                                        ("pass", first + "-t2")]
    assert [b for _, b in bench.prepared[:2]] == [first, first + "-t2"]
    assert recs[2].branch == f"exp/{base}/{SCREENING[1]}-r1"


def test_resumed_retry_uses_second_try_branch(tmp_path):
    (tmp_path / "run_id").write_text("e0-20260101000000\n")
    seed = attempt(BenchRemote())
    append_record(tmp_path / "results.jsonl",
                  replace(seed, task=SCREENING[0], run_id="e0-20260101000000", status="infra_error"))
    bench = FakeBench()
    experiment(tmp_path, BenchRemote(), FakeAgent(), bench=bench)
    assert bench.prepared[0] == (SCREENING[0], f"exp/e0-20260101000000/{SCREENING[0]}-r1-t2")


# ---------------------------------------------------------------- I7 / M2: provenance

def test_scripts_synced_and_hashes_recorded(tmp_path):
    remote = BenchRemote()
    recs, _, _ = experiment(tmp_path, remote, FakeAgent())
    assert remote.synced == [(str(SCRIPTS_SRC), f"{ROOT}/bin")]
    sync = remote.calls.index(f"<sync {SCRIPTS_SRC} -> {ROOT}/bin>")
    assert sync < next(i for i, c in enumerate(remote.calls) if "usage_proxy" in c)
    assert all(r.versions["remote_scripts"] == scripts_hash(SCRIPTS_SRC) for r in recs)
    assert all(r.versions["config"] == config_hash(CFG) for r in recs)


def test_scripts_hash_covers_contents(tmp_path):
    (tmp_path / "a.sh").write_text("one")
    h1 = scripts_hash(tmp_path)
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.pyc").write_text("junk")
    assert scripts_hash(tmp_path) == h1
    (tmp_path / "a.sh").write_text("two")
    assert scripts_hash(tmp_path) != h1


def test_config_hash_tracks_every_field():
    assert config_hash(CFG) == config_hash(replace(CFG))
    assert config_hash(CFG) != config_hash(replace(CFG, runtime=replace(CFG.runtime, context=4096)))
    assert config_hash(CFG) != config_hash(replace(CFG, agent=replace(CFG.agent, env={"A": "1"})))


def test_resume_refuses_changed_config(tmp_path):
    (tmp_path / "run_id").write_text("e0-20260101000000\n")
    seed = attempt(BenchRemote())
    append_record(tmp_path / "results.jsonl",
                  replace(seed, versions={**seed.versions, "config": "0" * 64}))
    remote = BenchRemote()
    with pytest.raises(ConfigError) as e:
        experiment(tmp_path, remote, FakeAgent())
    assert "0" * 64 in str(e.value) and config_hash(CFG) in str(e.value)
    assert remote.calls == []  # refused before touching the host


def test_resume_accepts_records_without_config_hash(tmp_path):
    (tmp_path / "run_id").write_text("e0-20260101000000\n")
    seed = attempt(BenchRemote())
    old = {k: v for k, v in seed.versions.items() if k != "config"}
    append_record(tmp_path / "results.jsonl", replace(seed, task=SCREENING[0], versions=old))
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent())
    assert len(recs) == len(SCREENING)


def test_harness_version_marks_dirty_tree(monkeypatch):
    import harness.run as run_mod

    def fake(status):
        def run(args, **kw):
            out = "abc1234\n" if "rev-parse" in args else status
            return subprocess.CompletedProcess(args, 0, out, "")
        return run
    monkeypatch.setattr(run_mod.subprocess, "run", fake(""))
    assert harness_version() == "abc1234"
    monkeypatch.setattr(run_mod.subprocess, "run", fake(" M harness/run.py\n"))
    assert harness_version() == "abc1234-dirty"


# ---------------------------------------------------------------- M4: owner's Ollama, signals

def test_inactive_system_ollama_is_left_stopped(tmp_path):
    remote = BenchRemote()
    remote.replies.insert(0, ("systemctl is-active ollama",
                              subprocess.CompletedProcess([], 3, "inactive\n", "")))
    experiment(tmp_path, remote, FakeAgent())
    assert "sudo -n systemctl start ollama" not in remote.calls


@pytest.mark.parametrize("signum", ["SIGTERM", "SIGHUP"])
def test_signal_runs_cleanup(tmp_path, signum):
    import os
    import signal
    sig = getattr(signal, signum)
    before = signal.getsignal(sig)

    class Killed(FakeAgent):
        def run(self, *a):
            os.kill(os.getpid(), sig)
            return super().run(*a)
    remote = BenchRemote()
    with pytest.raises(KeyboardInterrupt):
        experiment(tmp_path, remote, Killed())
    assert remote.calls[-2] == "sudo -n systemctl start ollama"
    assert "kill -TERM -- -111" in remote.calls  # helpers stopped too
    assert signal.getsignal(sig) == before


def test_keyboard_interrupt_restores_ollama(tmp_path):
    remote = BenchRemote()
    with pytest.raises(KeyboardInterrupt):
        experiment(tmp_path, remote, FakeAgent(KeyboardInterrupt()))
    assert remote.calls[-2] == "sudo -n systemctl start ollama"


# ---------------------------------------------------------------- M5: run_id

@pytest.mark.parametrize("bad", ["../e0", "e0/x", "E0-1", "e0..1"])
def test_bad_run_id_file_rejected(tmp_path, bad):
    (tmp_path / "run_id").write_text(bad + "\n")
    with pytest.raises(ConfigError, match="run_id"):
        experiment(tmp_path, BenchRemote(), FakeAgent())


# ---------------------------------------------------------------- M9: one run at a time

def test_run_lock_held_for_whole_run(tmp_path):
    remote = BenchRemote()
    experiment(tmp_path, remote, FakeAgent())
    lock = next(i for i, c in enumerate(remote.calls) if "run.lock" in c)
    assert f"flock -n {ROOT}/run.lock" in remote.calls[lock]
    assert lock < remote.calls.index("sudo -n systemctl stop ollama")
    assert remote.calls[-1] == "kill -TERM -- -333"


def test_second_run_fails_fast(tmp_path):
    remote = BenchRemote()
    remote.replies.insert(0, ("run.lock", subprocess.CompletedProcess([], 75, "", "")))
    with pytest.raises(RunLockedError, match="another harness run"):
        experiment(tmp_path, remote, FakeAgent())
    assert not any("ollama" in c for c in remote.calls) and remote.synced == []
