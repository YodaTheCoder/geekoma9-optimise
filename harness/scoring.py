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
    are excluded entirely.
    """
    root = ET.fromstring(xml)
    passed = failed = errors = 0
    for case in root.iter("testcase"):
        if case.find("skipped") is not None:
            continue
        if case.find("error") is not None:
            errors += 1
        elif case.find("failure") is not None:
            failed += 1
        else:
            passed += 1
    return TestCounts(passed, failed, errors)


_PARSE_ERROR = re.compile(r"SCRIPT ERROR: Parse Error|Failed to load script")


def parse_ok_from_log(log: str) -> bool:
    return _PARSE_ERROR.search(log) is None


def decide_status(
    *,
    parse_ok: bool,
    hidden: TestCounts | None,
    regression: TestCounts | None,
    agent_timed_out: bool,
) -> Literal["pass", "fail", "timeout"]:
    if agent_timed_out:
        return "timeout"
    if not parse_ok or hidden is None or regression is None:
        return "fail"
    if hidden.total == 0 or hidden.failed or hidden.errors:
        return "fail"
    if regression.failed or regression.errors:
        return "fail"
    return "pass"


def _load_counts(path: str | None, timed_out: bool) -> TestCounts | None:
    if timed_out or not path or not Path(path).is_file():
        return None
    try:
        return parse_junit(Path(path).read_text())
    except ET.ParseError:
        return None


def load_score(score_json: str) -> tuple[bool, TestCounts | None, TestCounts | None]:
    """Return (parse_ok, hidden, regression) from a score.json path."""
    data = json.loads(Path(score_json).read_text())
    log_path = data.get("import_log")
    log = Path(log_path).read_text(errors="replace") if log_path and Path(log_path).is_file() else ""
    parse_ok = not data.get("import_timed_out") and parse_ok_from_log(log)
    extra_failed = bool(data.get("extra_timed_out")) or data.get("extra_exit") not in (None, 0)
    hidden = _load_counts(data.get("hidden_xml"), bool(data.get("hidden_timed_out")) or extra_failed)
    regression = _load_counts(data.get("regression_xml"), bool(data.get("regression_timed_out")))
    return parse_ok, hidden, regression
