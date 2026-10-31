from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class TestCounts:
    __test__ = False  # not a pytest class, despite the name

    passed: int
    failed: int
    errors: int

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.errors


def parse_junit(xml: str) -> TestCounts:
    """Count per testcase; suite attributes are ignored (GUT counts failed asserts there).

    A testcase with an <error> child is an error, else with a <failure> child
    it is a failure, else it passes. <skipped> (GUT pending/risky) testcases
    are excluded entirely. A testcase that made no assertions (`assertions="0"`)
    fails: it proves nothing. Without the attribute (score_extra's checks) it is
    judged by its children alone.
    """
    root = ET.fromstring(xml)
    passed = failed = errors = 0
    for case in root.iter("testcase"):
        if case.find("skipped") is not None:
            continue
        if case.find("error") is not None:
            errors += 1
        elif case.find("failure") is not None or case.get("assertions") == "0":
            failed += 1
        else:
            passed += 1
    return TestCounts(passed, failed, errors)


# GUT skips a test script it cannot load ("could not be loaded") without a failure in the
# JUnit file, so these are searched for in the import log and both suite logs.
_PARSE_ERROR = re.compile(r"could not be loaded|Parse Error|Failed to load script")
_LOGS = ("import_log", "regression_log", "hidden_log")


def parse_ok_from_log(log: str) -> bool:
    return _PARSE_ERROR.search(log) is None


def decide_status(
    *,
    parse_ok: bool,
    hidden: TestCounts | None,
    regression: TestCounts | None,
    agent_timed_out: bool,
    regression_expected: int | None = None,
) -> Literal["pass", "fail", "timeout"]:
    """`regression_expected` is the `func test_` count of the pristine regression files
    (None for score.json files written before score.sh counted them)."""
    if agent_timed_out:
        return "timeout"
    if not parse_ok or hidden is None or regression is None:
        return "fail"
    if hidden.total == 0 or hidden.failed or hidden.errors:
        return "fail"
    if regression.total == 0 or regression.failed or regression.errors:
        return "fail"
    if regression_expected is not None and regression.total != regression_expected:
        return "fail"
    return "pass"


def _load_counts(path: str | None, timed_out: bool) -> TestCounts | None:
    if timed_out or not path or not Path(path).is_file():
        return None
    try:
        return parse_junit(Path(path).read_text())
    except ET.ParseError:
        return None


def _read_log(path: str | None) -> str:
    return Path(path).read_text(errors="replace") if path and Path(path).is_file() else ""


def load_score(score_json: str) -> tuple[bool, TestCounts | None, TestCounts | None, int | None]:
    """Return (parse_ok, hidden, regression, regression_expected) from a score.json path."""
    data = json.loads(Path(score_json).read_text())
    parse_ok = not data.get("import_timed_out") and all(
        parse_ok_from_log(_read_log(data.get(key))) for key in _LOGS)
    extra_failed = bool(data.get("extra_timed_out")) or data.get("extra_exit") not in (None, 0)
    hidden = _load_counts(data.get("hidden_xml"), bool(data.get("hidden_timed_out")) or extra_failed)
    regression = _load_counts(data.get("regression_xml"), bool(data.get("regression_timed_out")))
    expected = data.get("regression_expected")
    return parse_ok, hidden, regression, expected if isinstance(expected, int) else None
