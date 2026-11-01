from __future__ import annotations

from dataclasses import dataclass

ROOT = "/home/markn/agentbench"
MIRROR = f"{ROOT}/bench.git"
OWNER = "markn"
OWNER_HOME = f"/home/{OWNER}"
# What the agent user must reach lives outside OWNER_HOME, which stays closed (0750): a
# traversable home would expose every world-readable path in it, ~/.claude among them.
AGENT_ROOT = "/srv/agentbench"
RUNS = f"{AGENT_ROOT}/runs"
GODOT_BIN = f"{AGENT_ROOT}/opt/godot/godot"
# Command agents run as this unprivileged user, so they cannot read the mirror (hidden tests,
# solutions), other attempts, or the scoring files (docs/provisioning.md).
AGENT_USER = "agentrun"


@dataclass(frozen=True)
class AttemptPaths:
    task: str
    root: str
    workdir: str
    task_files: str
    issue_file: str
    agent_log: str
    usage_log: str
    samples_csv: str
    score_dir: str


def attempt_paths(run_id: str, task: str, repeat: int) -> AttemptPaths:
    root = f"{RUNS}/{run_id}/{task}-r{repeat}"
    return AttemptPaths(
        task=task,
        root=root,
        workdir=f"{root}/work",
        # Exported only after the agent has exited, inside the 0700 score dir.
        task_files=f"{root}/score/task",
        issue_file=f"{root}/issue.md",
        agent_log=f"{root}/agent.log",
        usage_log=f"{root}/usage.jsonl",
        samples_csv=f"{root}/samples.csv",
        score_dir=f"{root}/score",
    )
