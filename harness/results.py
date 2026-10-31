from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Literal

Status = Literal["pass", "fail", "timeout", "infra_error"]


@dataclass
class AttemptRecord:
    # Backward compatible both ways: every field added from now on has a default (old
    # files stay readable), and read_records ignores keys it does not know (newer files).
    experiment: str
    run_id: str
    task: str
    repeat: int
    status: Status
    hidden_passed: int
    hidden_total: int
    regressions_ok: bool
    parse_ok: bool
    wall_s: float
    prompt_tokens: int | None
    gen_tokens: int | None
    pp_tps: float | None
    tg_tps: float | None
    peak_mem_mib: int | None
    peak_gpu_mem_mib: int | None
    steps: int | None
    throttled: bool
    upstream_errors: int
    pushed: bool
    branch: str
    versions: dict[str, str]
    started_at: str
    error: str = ""


def drop_partial_tail(path: Path) -> None:
    """Truncate an unterminated trailing fragment so the next append starts a clean line."""
    if not path.exists() or path.stat().st_size == 0:
        return
    data = path.read_bytes()
    if data.endswith(b"\n"):
        return
    with path.open("r+b") as f:
        f.truncate(data.rfind(b"\n") + 1)


def append_record(path: Path, rec: AttemptRecord) -> None:
    """Append one JSON line, flushed and fsynced so a crash loses at most this line."""
    drop_partial_tail(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(rec)) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_records(path: Path) -> list[AttemptRecord]:
    """Read all records; a corrupt final line (interrupted write) is ignored."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    known = {f.name for f in fields(AttemptRecord)}
    unknown: set[str] = set()
    out: list[AttemptRecord] = []
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            unknown |= set(data) - known
            out.append(AttemptRecord(**{k: v for k, v in data.items() if k in known}))
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            if i == len(lines):
                break
            raise ValueError(f"{path}: bad record on line {i}: {e}") from e
    if unknown:
        print(f"warning: {path}: ignoring unknown record fields: {', '.join(sorted(unknown))}",
              file=sys.stderr)
    return out


def pending(plan: list[tuple[str, int]], records: list[AttemptRecord]) -> list[tuple[str, int]]:
    """Plan entries still to run: done = any non-infra record, or two infra records."""
    infra: dict[tuple[str, int], int] = {}
    done: set[tuple[str, int]] = set()
    for r in records:
        key = (r.task, r.repeat)
        if r.status == "infra_error":
            infra[key] = infra.get(key, 0) + 1
        else:
            done.add(key)
    return [k for k in plan if k not in done and infra.get(k, 0) < 2]
