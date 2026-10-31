from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from harness.config import load_config
from harness.results import _drop_partial_tail, read_records

REVIEWER = "claude-opus"
CLAUDE = "/Users/marknorton/.local/bin/claude"
CLAUDE_TIMEOUT_S = 600
DEFAULT_BENCH = "~/_dev/claude/godot-agent-bench"

Runner = Callable[[str], str]
Git = Callable[[list[str]], str]


@dataclass
class Review:
    task: str
    repeat: int
    branch: str
    would_merge: bool
    quality: int
    comments: str
    reviewer: str


def build_review_prompt(issue_text: str, diff: str) -> str:
    return f"""You are a maintainer reviewing a patch written by a coding agent for a Godot (GDScript) project.

## Issue

{issue_text}

## Patch (git diff)

```diff
{diff}
```

## Rubric

- Does it meet every requirement in the issue?
- Is it idiomatic GDScript, with no dead code, debug prints or unrelated changes?
- Would a maintainer merge it as is?

Quality: 1 = wrong or harmful, 3 = works but needs changes, 5 = merge as is.

Reply with ONLY a JSON object, no other text:
{{"would_merge": true or false, "quality": integer 1-5, "comments": "short justification"}}
"""


def parse_review(text: str) -> tuple[bool, int, str]:
    candidates = [m.group(1) for m in re.finditer(r"```(?:json)?\s*(.*?)```", text, re.S)]
    candidates.append(text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for c in candidates:
        try:
            d = json.loads(c.strip())
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue
        merge, quality, comments = d.get("would_merge"), d.get("quality"), d.get("comments")
        if (isinstance(merge, bool) and isinstance(quality, int) and not isinstance(quality, bool)
                and 1 <= quality <= 5 and isinstance(comments, str)):
            return merge, quality, comments
    raise ValueError(f"no valid review JSON in reply: {text[:200]!r}")


def append_review(path: Path, rev: Review) -> None:
    _drop_partial_tail(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(rev)) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_reviews(path: Path) -> list[Review]:
    if not path.exists():
        return []
    out: list[Review] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            out.append(Review(**json.loads(line)))
        except (json.JSONDecodeError, TypeError) as e:
            if i == len(lines):
                break
            raise ValueError(f"{path}: bad review on line {i}: {e}") from e
    return out


def claude_runner(prompt: str) -> str:
    """Run the claude CLI with the prompt on stdin (diffs can be large)."""
    r = subprocess.run([CLAUDE, "-p", "--model", "opus", "--output-format", "text"],
                       input=prompt, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT_S,
                       check=True)
    return r.stdout


def make_git(bench: Path) -> Git:
    def git(args: list[str]) -> str:
        return subprocess.run(["git", "-C", str(bench), *args], capture_output=True, text=True,
                              check=True).stdout
    return git


def _diff(git: Git, task_set: str, branch: str) -> str:
    # Fully qualified refs: a branch named `tests` would collide with the tests/ directory.
    last: Exception | None = None
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        try:
            return git(["diff", f"base-{task_set}..{ref}", "--", ".", ":(exclude)tasks"])
        except subprocess.CalledProcessError as e:
            last = e
    raise last  # type: ignore[misc]


def _ask(runner: Runner, prompt: str) -> tuple[bool, int, str]:
    for attempt in (1, 2):
        try:
            return parse_review(runner(prompt))
        except ValueError:
            if attempt == 2:
                raise
    raise AssertionError("unreachable")


def review_experiment(exp_dir: Path, runner: Runner = claude_runner, git: Git | None = None,
                      bench: Path | None = None) -> int:
    cfg = load_config(exp_dir / "config.yaml")
    if git is None:
        git = make_git(Path(bench or DEFAULT_BENCH).expanduser())
    out = exp_dir / "reviews.jsonl"
    done = {(r.task, r.repeat, r.branch) for r in read_reviews(out)}
    todo = [r for r in read_records(exp_dir / "results.jsonl")
            if r.status == "pass" and (r.task, r.repeat, r.branch) not in done]
    if not todo:
        return 0
    try:
        git(["fetch", "origin"])
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"warning: git fetch failed ({e}); using local refs", file=sys.stderr)
    failed = 0
    for rec in todo:
        label = f"{rec.task} r{rec.repeat} ({rec.branch})"
        try:
            issue = git(["show", f"refs/tags/taskset-{cfg.task_set}:tasks/{rec.task}/issue.md"])
            diff = _diff(git, cfg.task_set, rec.branch)
            merge, quality, comments = _ask(runner, build_review_prompt(issue, diff))
        except (ValueError, subprocess.SubprocessError, OSError) as e:
            print(f"warning: could not review {label}: {e}", file=sys.stderr)
            failed += 1
            continue
        append_review(out, Review(rec.task, rec.repeat, rec.branch, merge, quality, comments,
                                  REVIEWER))
        print(f"reviewed {label}: quality {quality}, would_merge {merge}")
    return 1 if failed else 0
