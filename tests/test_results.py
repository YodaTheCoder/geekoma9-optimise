from pathlib import Path

import pytest

from harness.results import AttemptRecord, append_record, pending, read_records


def rec(task: str, repeat: int, status: str = "pass") -> AttemptRecord:
    return AttemptRecord(
        experiment="e0", run_id="r1", task=task, repeat=repeat, status=status,
        hidden_passed=3, hidden_total=4, regressions_ok=True, parse_ok=True,
        wall_s=12.5, prompt_tokens=None, gen_tokens=100, pp_tps=None, tg_tps=7.5,
        peak_mem_mib=1024, peak_gpu_mem_mib=None, steps=5, throttled=False,
        upstream_errors=0, pushed=True, branch="b1",
        versions={"llama": "1.0"}, started_at="2026-10-31T00:00:00Z",
    )


def test_roundtrip(tmp_path: Path):
    p = tmp_path / "results.jsonl"
    a, b = rec("001", 1), rec("002", 2, "fail")
    append_record(p, a)
    append_record(p, b)
    out = read_records(p)
    assert out == [a, b]
    assert out[0].versions == {"llama": "1.0"} and out[0].prompt_tokens is None


def test_truncated_last_line_is_skipped(tmp_path: Path):
    p = tmp_path / "results.jsonl"
    append_record(p, rec("001", 1))
    p.write_text(p.read_text() + '{"experiment": "e0", "ta')
    assert [r.task for r in read_records(p)] == ["001"]


def test_bad_middle_line_raises(tmp_path: Path):
    p = tmp_path / "results.jsonl"
    append_record(p, rec("001", 1))
    p.write_text(p.read_text() + "garbage\n")
    append_record(p, rec("002", 1))
    with pytest.raises(ValueError, match="line 2"):
        read_records(p)


def test_pending_skips_completed_and_double_infra():
    plan = [("001", 1), ("002", 1), ("003", 1), ("004", 1)]
    recs = [rec("001", 1, "pass"), rec("002", 1, "infra_error"),
            rec("003", 1, "infra_error"), rec("003", 1, "infra_error"),
            rec("004", 1, "timeout")]
    assert pending(plan, recs) == [("002", 1)]


def test_missing_file_is_empty(tmp_path: Path):
    assert read_records(tmp_path / "none.jsonl") == []


def test_append_after_truncation_recovers(tmp_path: Path):
    p = tmp_path / "results.jsonl"
    a, b, c = rec("001", 1), rec("002", 1), rec("003", 1)
    append_record(p, a)
    p.write_text(p.read_text() + '{"experiment": "e0", "ta')
    append_record(p, b)
    append_record(p, c)
    assert read_records(p) == [a, b, c]


def test_unknown_keys_ignored_and_logged_once(tmp_path: Path, capsys):
    import json
    from dataclasses import asdict
    p = tmp_path / "results.jsonl"
    rows = [{**asdict(rec("001", 1)), "gpu_offload": 0.9, "peak_swap_mib": 3},
            {**asdict(rec("002", 1)), "gpu_offload": 1.0}]
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert [r.task for r in read_records(p)] == ["001", "002"]
    err = capsys.readouterr().err
    assert err.count("ignoring unknown") == 1 and "gpu_offload" in err and "peak_swap_mib" in err


def test_missing_required_key_still_raises(tmp_path: Path):
    import json
    from dataclasses import asdict
    p = tmp_path / "results.jsonl"
    row = asdict(rec("001", 1))
    del row["status"]
    p.write_text(json.dumps(row) + "\n" + json.dumps(asdict(rec("002", 1))) + "\n")
    with pytest.raises(ValueError, match="line 1"):
        read_records(p)
