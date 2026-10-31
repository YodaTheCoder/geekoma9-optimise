from __future__ import annotations

import re
import shlex
import time

from harness.agents.base import AgentResult
from harness.config import AgentConfig, ConfigError
from harness.paths import AttemptPaths
from harness.remote import Remote, RemoteError

_TIMEOUT_CODES = (124, 137)
_ENV_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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
        inner = (f"echo $$ > {shlex.quote(sid)}; "
                 f"exec timeout -k 30 {int(timeout_s)} bash -c {shlex.quote(exports + rendered)}")
        cmd = (f"cd {shlex.quote(paths.workdir)} && "
               f"setsid --wait bash -c {shlex.quote(inner)} > {shlex.quote(paths.agent_log)} 2>&1")
        start = time.monotonic()
        # ssh timeout outlasts the agent's own so ssh never cuts it first.
        try:
            r = remote.run(cmd, timeout=timeout_s + 120, check=False)
        finally:
            wall = time.monotonic() - start
            # Kill survivors in the agent's session, even if ssh dropped.
            try:
                remote.run(f'pkill -KILL -s "$(cat {shlex.quote(sid)})"', check=False)
            except RemoteError:
                pass
        steps = None
        if cfg.steps_regex:
            steps = len(re.findall(cfg.steps_regex, remote.read_text(paths.agent_log)))
        return AgentResult(exit_code=r.returncode, timed_out=r.returncode in _TIMEOUT_CODES,
                           wall_s=wall, steps=steps)
