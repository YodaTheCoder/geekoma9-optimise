from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from harness.paths import AttemptPaths
from harness.remote import Remote


@dataclass(frozen=True)
class AgentResult:
    exit_code: int
    timed_out: bool
    wall_s: float
    steps: int | None = None


class Agent(Protocol):
    def run(self, remote: Remote, paths: AttemptPaths, endpoint: str, model: str,
            timeout_s: int) -> AgentResult: ...
