from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

from harness.results import AttemptRecord

START = "<!-- results:start -->"
END = "<!-- results:end -->"


@dataclass(frozen=True)
class Summary:
    attempts: int  # all records, infra_error included
    passes: int
    infra_errors: int
    pass_rate: float  # passes / scored (non-infra) attempts
    wall_hours: float  # scored attempts only
    solved_per_8h: float
    median_tg_tps: float | None
    median_pp_tps: float | None
    throttled: int


def _median(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return statistics.median(present) if present else None


def summarize(records: list[AttemptRecord]) -> Summary:
    """Headline metrics; infra_error records never count for or against the config."""
    scored = [r for r in records if r.status != "infra_error"]
    passes = sum(1 for r in scored if r.status == "pass")
    wall_hours = sum(r.wall_s for r in scored) / 3600
    return Summary(
        attempts=len(records),
        passes=passes,
        infra_errors=len(records) - len(scored),
        pass_rate=passes / len(scored) if scored else 0.0,
        wall_hours=wall_hours,
        solved_per_8h=passes / wall_hours * 8 if wall_hours > 0 else 0.0,
        median_tg_tps=_median([r.tg_tps for r in scored]),
        median_pp_tps=_median([r.pp_tps for r in scored]),
        throttled=sum(1 for r in scored if r.throttled),
    )


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_markdown(summary: Summary, records: list[AttemptRecord]) -> str:
    lines = ["| metric | value |", "|---|---|"]
    lines += [f"| {k} | {_fmt(v)} |" for k, v in asdict(summary).items()]
    lines += ["", "| task | repeat | status | hidden | wall min | tg tok/s | throttled | branch |",
              "|---|---|---|---|---|---|---|---|"]
    for r in records:
        tg = "-" if r.tg_tps is None else f"{r.tg_tps:.1f}"
        lines.append(f"| {r.task} | {r.repeat} | {r.status} | {r.hidden_passed}/{r.hidden_total} "
                     f"| {r.wall_s / 60:.1f} | {tg} | {'yes' if r.throttled else 'no'} "
                     f"| {r.branch} |")
    return "\n".join(lines)


def write_readme(readme: Path, block: str) -> None:
    """Replace the text between the results markers, adding the markers if missing."""
    section = f"{START}\n{block}\n{END}"
    text = readme.read_text() if readme.exists() else ""
    start, end = text.find(START), text.find(END)
    if start != -1 and end > start:
        text = text[:start] + section + text[end + len(END):]
    else:
        text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + section + "\n"
    readme.write_text(text)
