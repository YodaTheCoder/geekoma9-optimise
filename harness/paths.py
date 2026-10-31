from __future__ import annotations

from dataclasses import dataclass

ROOT = "/home/markn/agentbench"


@dataclass(frozen=True)
class AttemptPaths:
    root: str
    workdir: str
    task_files: str
    issue_file: str
    agent_log: str
    usage_log: str
    samples_csv: str
    score_dir: str


def attempt_paths(run_id: str, task: str, repeat: int) -> AttemptPaths:
    root = f"{ROOT}/runs/{run_id}/{task}-r{repeat}"
    return AttemptPaths(
        root=root,
        workdir=f"{root}/work",
        task_files=f"{root}/task",
        issue_file=f"{root}/issue.md",
        agent_log=f"{root}/agent.log",
        usage_log=f"{root}/usage.jsonl",
        samples_csv=f"{root}/samples.csv",
        score_dir=f"{root}/score",
    )
