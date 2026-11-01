from __future__ import annotations

import shlex
import time

from harness.agents.base import AgentResult
from harness.paths import MIRROR, AttemptPaths
from harness.remote import Remote


class OracleAgent:
    """Applies the reference solution; measures the benchmark's ceiling."""

    def __init__(self, mirror: str = MIRROR, task_set: str = ""):
        self.mirror = mirror
        self.task_set = task_set

    def run(self, remote: Remote, paths: AttemptPaths, endpoint: str, model: str,
            timeout_s: int) -> AgentResult:
        start = time.monotonic()
        # Straight from the mirror: task files are exported only after the agent has run.
        ref = f"taskset-{self.task_set}:tasks/{paths.task}/solution.patch"
        r = remote.run(f"set -o pipefail; git -C {shlex.quote(self.mirror)} show {shlex.quote(ref)}"
                       f" | git -C {shlex.quote(paths.workdir)} apply", check=False)
        return AgentResult(exit_code=r.returncode, timed_out=False,
                           wall_s=time.monotonic() - start, steps=None)
