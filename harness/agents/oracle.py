from __future__ import annotations

import shlex
import time

from harness.agents.base import AgentResult
from harness.paths import AttemptPaths
from harness.remote import Remote


class OracleAgent:
    """Applies the reference solution; measures the benchmark's ceiling."""

    def run(self, remote: Remote, paths: AttemptPaths, endpoint: str, model: str,
            timeout_s: int) -> AgentResult:
        start = time.monotonic()
        r = remote.run(f"git -C {shlex.quote(paths.workdir)} apply "
                       f"{shlex.quote(paths.task_files + '/solution.patch')}", check=False)
        return AgentResult(exit_code=r.returncode, timed_out=False,
                           wall_s=time.monotonic() - start, steps=None)
