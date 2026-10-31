from __future__ import annotations

from dataclasses import replace

from harness import cli
from harness.results import append_record, read_records
from harness.tiers import TASK_SETS
from test_report import r

ALL = TASK_SETS["v1"]["all"]


def test_report_writes_readme(tmp_path):
    append_record(tmp_path / "results.jsonl", r("pass", 1800))
    assert cli.main(["report", str(tmp_path)]) == 0
    text = (tmp_path / "README.md").read_text()
    assert "<!-- results:start -->" in text and "| t1 | 1 | pass |" in text


def test_stub_subcommands_return_2(tmp_path, capsys):
    assert cli.main(["review", str(tmp_path)]) == 2
    assert cli.main(["provision"]) == 2
    assert "not implemented yet" in capsys.readouterr().err


def _fake_run(outcomes):
    """Replace run_experiment: write one record per task with outcomes[kind](task)."""
    seen = []

    def run_experiment(cfg, exp_dir, *, remote, bench, **kw):
        seen.append(cfg)
        for task in ALL:
            append_record(exp_dir / "results.jsonl",
                          replace(r(outcomes[cfg.agent.kind](task), 60), task=task))
    return run_experiment, seen


def test_validate_ok(tmp_path, monkeypatch, capsys):
    fake, seen = _fake_run({"null": lambda t: "fail", "oracle": lambda t: "pass"})
    monkeypatch.setattr(cli, "run_experiment", fake)
    assert cli.main(["validate", "--task-set", "v1", "--experiments-dir", str(tmp_path)]) == 0
    assert [c.id for c in seen] == ["validate-v1-null", "validate-v1-oracle"]
    assert all(c.tier == "all" and c.cooldown_s == 0 for c in seen)
    assert (tmp_path / "validate-v1-oracle" / "config.yaml").exists()
    assert len(read_records(tmp_path / "validate-v1-null" / "results.jsonl")) == len(ALL)


def test_validate_reports_offenders(tmp_path, monkeypatch, capsys):
    fake, _ = _fake_run({"null": lambda t: "pass" if t == ALL[2] else "fail",
                         "oracle": lambda t: "infra_error" if t == ALL[0] else "pass"})
    monkeypatch.setattr(cli, "run_experiment", fake)
    assert cli.main(["validate", "--task-set", "v1", "--experiments-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert f"null: {ALL[2]} r1: pass" in out and f"oracle: {ALL[0]} r1: no result" in out
