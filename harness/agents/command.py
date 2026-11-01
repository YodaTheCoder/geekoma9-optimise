from __future__ import annotations

import re
import shlex
import time

from harness.agents.base import AgentResult
from harness.config import AgentConfig, ConfigError
from harness.paths import AGENT_HOME_TEMPLATE, AGENT_USER, OWNER, AttemptPaths
from harness.remote import Remote, RemoteError

_ENV_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Run as the agent user before each attempt: nothing an earlier attempt left (OpenCode sessions
# and snapshots, Claude Code transcripts, caches, temp files) may reach the next one. The home is
# rebuilt from AGENT_HOME_TEMPLATE; only Claude Code's install and login are kept.
AGENT_HOME_RESET = (
    "cd ~ && "
    "find . -mindepth 1 -maxdepth 1 ! -name .claude ! -name .claude.json ! -name .local "
    "-exec rm -rf {} + && "
    "{ [ ! -d .claude ] || find .claude -mindepth 1 -maxdepth 1 ! -name .credentials.json "
    "-exec rm -rf {} +; } && "
    "{ [ ! -d .local ] || find .local -mindepth 1 -maxdepth 1 ! -name bin ! -name share "
    "-exec rm -rf {} +; } && "
    "{ [ ! -d .local/bin ] || find .local/bin -mindepth 1 -maxdepth 1 ! -name claude "
    "-exec rm -rf {} +; } && "
    "{ [ ! -d .local/share ] || find .local/share -mindepth 1 -maxdepth 1 ! -name claude "
    "-exec rm -rf {} +; } && "
    f"cp -r --preserve=mode,timestamps {AGENT_HOME_TEMPLATE}/. ~/ && "
    f"find /tmp /var/tmp /dev/shm -mindepth 1 -maxdepth 1 -user {AGENT_USER} -exec rm -rf {{}} +")


def render_command(template: str, **values: str) -> str:
    """Fill {placeholders} with shell-quoted values; unknown placeholders are an error."""
    quoted = {k: shlex.quote(v) for k, v in values.items()}
    try:
        return template.format_map(quoted)
    except (KeyError, IndexError, ValueError, AttributeError) as e:
        raise ConfigError(f"command template: bad placeholder {e}") from e


class CommandAgent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg

    def run(self, remote: Remote, paths: AttemptPaths, endpoint: str, model: str,
            timeout_s: int) -> AgentResult:
        cfg = self.cfg
        for k in cfg.env:
            if not _ENV_KEY.match(k):
                raise ConfigError(f"agent.env: invalid variable name {k!r}")
        if cfg.steps_regex:
            try:
                re.compile(cfg.steps_regex)
            except re.error as e:
                raise ConfigError(f"agent.steps_regex: {e}") from e
        rendered = render_command(
            cfg.command or "", workdir=paths.workdir, issue_file=paths.issue_file,
            endpoint=endpoint, model=model, log=paths.agent_log)
        exports = "".join(f"export {k}={shlex.quote(v)}; " for k, v in cfg.env.items())
        sid = f"{paths.root}/agent.sid"
        # The agent runs as AGENT_USER (no sudo, no access to the mirror or other attempts);
        # the wrapper, its log redirection and the kills stay with the owner.
        inner = (f"echo $$ > {shlex.quote(sid)}; "
                 f"exec timeout -k 30 {int(timeout_s)} sudo -n -u {AGENT_USER} -H "
                 f"bash -c {shlex.quote(exports + rendered)}")
        # stdin from /dev/null: the ssh session's stdin never closes, and agents that read
        # piped input (OpenCode `run`) would wait on it forever.
        cmd = (f"cd {shlex.quote(paths.workdir)} && "
               f"setsid --wait bash -c {shlex.quote(inner)} "
               f"< /dev/null > {shlex.quote(paths.agent_log)} 2>&1")
        own = f"{shlex.quote(paths.workdir)} {shlex.quote(paths.issue_file)}"
        give_back = f"sudo -n chown -R {OWNER}: {own}"
        remote.run(f"sudo -n -u {AGENT_USER} -H bash -c {shlex.quote(AGENT_HOME_RESET)}")
        remote.run(f"sudo -n chown -R {AGENT_USER}: {own}")
        try:
            r, wall = self._run_and_kill(remote, cmd, sid, timeout_s)
        except BaseException:
            try:  # best effort: the original error matters more
                remote.run(give_back, check=False)
            except RemoteError:
                pass
            raise
        remote.run(give_back)
        steps = None
        if cfg.steps_regex:
            steps = len(re.findall(cfg.steps_regex, remote.read_text(paths.agent_log)))
        # 137 is `timeout -k` only once the budget is spent; earlier it is a SIGKILL from
        # elsewhere (the OOM killer), which the orchestrator's kernel-log check reports.
        timed_out = r.returncode == 124 or (r.returncode == 137 and wall >= timeout_s)
        return AgentResult(exit_code=r.returncode, timed_out=timed_out, wall_s=wall, steps=steps)

    @staticmethod
    def _run_and_kill(remote: Remote, cmd: str, sid: str, timeout_s: int):
        start = time.monotonic()
        # ssh timeout outlasts the agent's own so ssh never cuts it first.
        try:
            r = remote.run(cmd, timeout=timeout_s + 120, check=False)
        finally:
            wall = time.monotonic() - start
            # Kill survivors, even if ssh dropped: the wrapper's session, and every process of
            # the agent user (sudo may run the command in a session of its own).
            try:
                remote.run(f'sudo -n pkill -KILL -s "$(cat {shlex.quote(sid)})"; '
                           f"sudo -n pkill -KILL -u {AGENT_USER}", check=False)
            except RemoteError:
                pass
        return r, wall
