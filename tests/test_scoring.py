import json
from pathlib import Path

import pytest

from harness.scoring import (
    TestCounts,
    decide_status,
    load_score,
    parse_junit,
    parse_ok_from_log,
)

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_parse_junit_counts():
    assert parse_junit(fixture("junit_mixed.xml")) == TestCounts(3, 1, 1)


def test_parse_junit_empty_suite_is_zero():
    assert parse_junit(fixture("junit_empty.xml")).total == 0


def test_total_property():
    assert TestCounts(3, 1, 1).total == 5


@pytest.mark.parametrize(
    "line",
    ["SCRIPT ERROR: Parse Error: Expected", 'Failed to load script "res://x.gd"'],
)
def test_parse_errors_detected(line):
    assert not parse_ok_from_log("ok\n" + line)


def test_clean_log_is_parse_ok():
    assert parse_ok_from_log("Godot Engine v4\nall good\n")


def test_pass_requires_everything():
    ok = TestCounts(5, 0, 0)
    assert decide_status(parse_ok=True, hidden=ok, regression=ok, agent_timed_out=False) == "pass"
    assert decide_status(parse_ok=True, hidden=TestCounts(4, 1, 0), regression=ok, agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=True, hidden=ok, regression=TestCounts(5, 0, 1), agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=False, hidden=ok, regression=ok, agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=True, hidden=ok, regression=ok, agent_timed_out=True) == "timeout"


def test_hang_or_missing_xml_is_fail():
    assert decide_status(parse_ok=True, hidden=None, regression=TestCounts(5, 0, 0), agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=True, hidden=TestCounts(5, 0, 0), regression=None, agent_timed_out=False) == "fail"


def test_zero_hidden_tests_is_fail():
    assert decide_status(parse_ok=True, hidden=TestCounts(0, 0, 0), regression=TestCounts(5, 0, 0), agent_timed_out=False) == "fail"


def _score(tmp_path, log="ok\n", **over):
    (tmp_path / "import.log").write_text(log)
    (tmp_path / "hidden.xml").write_text(fixture("junit_mixed.xml"))
    (tmp_path / "regression.xml").write_text(fixture("junit_mixed.xml"))
    d = {
        "import_exit": 0, "import_timed_out": False, "import_log": str(tmp_path / "import.log"),
        "regression_exit": 0, "regression_timed_out": False, "regression_xml": str(tmp_path / "regression.xml"),
        "hidden_exit": 0, "hidden_timed_out": False, "hidden_xml": str(tmp_path / "hidden.xml"),
    }
    d.update(over)
    p = tmp_path / "score.json"
    p.write_text(json.dumps(d))
    return str(p)


def test_load_score_reads_counts(tmp_path):
    assert load_score(_score(tmp_path)) == (True, TestCounts(3, 1, 1), TestCounts(3, 1, 1))


def test_load_score_marks_timed_out_tests_as_none(tmp_path):
    parse_ok, hidden, regression = load_score(_score(tmp_path, hidden_timed_out=True))
    assert hidden is None and regression == TestCounts(3, 1, 1)
    _, hidden, regression = load_score(_score(tmp_path, regression_timed_out=True, hidden_timed_out=False))
    assert regression is None and hidden is not None


def test_load_score_null_or_missing_xml_is_none(tmp_path):
    _, hidden, _ = load_score(_score(tmp_path, hidden_xml=None))
    assert hidden is None
    _, hidden, _ = load_score(_score(tmp_path, hidden_xml=str(tmp_path / "gone.xml")))
    assert hidden is None


def test_load_score_import_timeout_or_bad_log_is_not_parse_ok(tmp_path):
    assert load_score(_score(tmp_path, import_timed_out=True))[0] is False
    assert load_score(_score(tmp_path, log="SCRIPT ERROR: Parse Error: x\n"))[0] is False
