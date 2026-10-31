from __future__ import annotations

from harness.agents.base import AgentResult
from harness.paths import AttemptPaths
from harness.remote import Remote


class NullAgent:
    """Does nothing; measures the benchmark's floor."""

    def run(self, remote: Remote, paths: AttemptPaths, endpoint: str, model: str,
            timeout_s: int) -> AgentResult:
        return AgentResult(exit_code=0, timed_out=False, wall_s=0.0, steps=None)
