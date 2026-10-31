from __future__ import annotations

import pytest

from harness.report import render_markdown, summarize, write_readme
from harness.results import AttemptRecord


def r(status, wall_s, tg=None, pp=None, throttled=False, task="t1", repeat=1):
    return AttemptRecord(
        experiment="e", run_id="e-1", task=task, repeat=repeat, status=status,
        hidden_passed=3 if status == "pass" else 0, hidden_total=3, regressions_ok=True,
        parse_ok=True, wall_s=wall_s, prompt_tokens=None, gen_tokens=None, pp_tps=pp,
        tg_tps=tg, peak_mem_mib=None, peak_gpu_mem_mib=None, steps=None, throttled=throttled,
        upstream_errors=0, pushed=True, branch=f"exp/e-1/{task}-r{repeat}", versions={},
        started_at="2026-10-31T12:00:00Z")


def test_solved_per_8h():  # 2 pass + 1 fail, 1800 s each, + 1 infra_error (excluded)
    s = summarize([r("pass", 1800), r("pass", 1800), r("fail", 1800), r("infra_error", 60)])
    assert s.passes == 2 and s.infra_errors == 1
    assert s.attempts == 4
    assert s.pass_rate == pytest.approx(2 / 3)
    assert s.wall_hours == pytest.approx(1.5) and s.solved_per_8h == pytest.approx(10.667, rel=1e-3)


def test_empty_summary_is_zero():
    s = summarize([])
    assert s.solved_per_8h == 0.0 and s.pass_rate == 0.0 and s.median_tg_tps is None


def test_medians_and_throttled_skip_infra():
    s = summarize([r("pass", 10, tg=10.0, pp=100.0, throttled=True), r("fail", 10, tg=20.0),
                   r("fail", 10, tg=30.0, pp=300.0), r("infra_error", 1, tg=999.0, throttled=True)])
    assert s.median_tg_tps == 20.0 and s.median_pp_tps == 200.0 and s.throttled == 1


def test_render_markdown_has_summary_and_task_rows():
    recs = [r("pass", 1800, tg=12.345, task="001-a"), r("fail", 600, throttled=True, task="002-b")]
    md = render_markdown(summarize(recs), recs)
    assert "solved_per_8h" in md
    assert "| 001-a | 1 | pass | 3/3 | 30.0 | 12.3 | no | exp/e-1/001-a-r1 |" in md
    assert "| 002-b | 1 | fail | 0/3 | 10.0 | - | yes | exp/e-1/002-b-r1 |" in md


def test_write_readme_creates_and_replaces_block(tmp_path):
    readme = tmp_path / "README.md"
    write_readme(readme, "first")
    text = readme.read_text()
    assert "<!-- results:start -->\nfirst\n<!-- results:end -->" in text
    readme.write_text("# Notes\n\nkeep me\n\n<!-- results:start -->\nold\n<!-- results:end -->\n\ntail\n")
    write_readme(readme, "second")
    text = readme.read_text()
    assert text == "# Notes\n\nkeep me\n\n<!-- results:start -->\nsecond\n<!-- results:end -->\n\ntail\n"


def test_write_readme_appends_markers_when_missing(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Findings\n")
    write_readme(readme, "x")
    assert readme.read_text() == "# Findings\n\n<!-- results:start -->\nx\n<!-- results:end -->\n"
