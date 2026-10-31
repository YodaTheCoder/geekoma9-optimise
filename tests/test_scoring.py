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


def test_parse_junit_real_gut_counts_per_testcase():
    # GUT 9.7.1: suite failures="3" counts asserts/pending, not testcases; pending is <skipped>.
    assert parse_junit(fixture("junit_gut_real.xml")) == TestCounts(1, 1, 0)


def test_parse_junit_only_skipped_is_zero():
    xml = '<testsuites><testsuite><testcase name="a"><skipped/></testcase></testsuite></testsuites>'
    assert parse_junit(xml).total == 0


def test_parse_junit_no_testcases_ignores_suite_attributes():
    xml = '<testsuites><testsuite tests="5" failures="2"/></testsuites>'
    assert parse_junit(xml) == TestCounts(0, 0, 0)


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
    assert load_score(_score(tmp_path)) == (True, TestCounts(3, 1, 1), TestCounts(3, 1, 1), None)


def test_load_score_marks_timed_out_tests_as_none(tmp_path):
    parse_ok, hidden, regression, _ = load_score(_score(tmp_path, hidden_timed_out=True))
    assert hidden is None and regression == TestCounts(3, 1, 1)
    _, hidden, regression, _ = load_score(_score(tmp_path, regression_timed_out=True, hidden_timed_out=False))
    assert regression is None and hidden is not None


def test_load_score_null_or_missing_xml_is_none(tmp_path):
    _, hidden, _, _ = load_score(_score(tmp_path, hidden_xml=None))
    assert hidden is None
    _, hidden, _, _ = load_score(_score(tmp_path, hidden_xml=str(tmp_path / "gone.xml")))
    assert hidden is None


def test_load_score_import_timeout_or_bad_log_is_not_parse_ok(tmp_path):
    assert load_score(_score(tmp_path, import_timed_out=True))[0] is False
    assert load_score(_score(tmp_path, log="SCRIPT ERROR: Parse Error: x\n"))[0] is False


@pytest.mark.parametrize("over", [{"extra_exit": 1}, {"extra_exit": 124, "extra_timed_out": True}])
def test_load_score_failed_extra_makes_hidden_none(tmp_path, over):
    _, hidden, regression, _ = load_score(_score(tmp_path, **over))
    assert hidden is None and regression == TestCounts(3, 1, 1)


def test_load_score_successful_extra_keeps_hidden(tmp_path):
    _, hidden, _, _ = load_score(_score(tmp_path, extra_exit=0, extra_timed_out=False))
    assert hidden == TestCounts(3, 1, 1)


@pytest.mark.parametrize("line", [
    "ERROR: Script 'res://tests/regression/test_score.gd' could not be loaded",
    "Parse Error: Identifier not declared",
])
def test_unloadable_test_script_is_parse_error(line):
    assert not parse_ok_from_log("ok\n" + line)


def test_zero_regression_tests_is_fail():
    ok = TestCounts(5, 0, 0)
    assert decide_status(parse_ok=True, hidden=ok, regression=TestCounts(0, 0, 0),
                         agent_timed_out=False) == "fail"


def test_regression_count_must_match_expected():
    ok = TestCounts(5, 0, 0)
    kw = dict(parse_ok=True, hidden=ok, agent_timed_out=False)
    assert decide_status(regression=TestCounts(14, 0, 0), regression_expected=14, **kw) == "pass"
    # a regression file that failed to load drops its tests from the JUnit file
    assert decide_status(regression=TestCounts(12, 0, 0), regression_expected=14, **kw) == "fail"
    assert decide_status(regression=TestCounts(12, 0, 0), regression_expected=None, **kw) == "pass"


def test_load_score_reads_suite_logs(tmp_path):
    (tmp_path / "hidden.log").write_text("Script 'res://tests/hidden/t.gd' could not be loaded\n")
    path = _score(tmp_path, hidden_log=str(tmp_path / "hidden.log"))
    assert load_score(path)[0] is False
    (tmp_path / "regression.log").write_text("Failed to load script \"res://x.gd\"\n")
    path = _score(tmp_path, regression_log=str(tmp_path / "regression.log"))
    assert load_score(path)[0] is False


def test_load_score_regression_expected(tmp_path):
    assert load_score(_score(tmp_path, regression_expected=14))[3] == 14
    assert load_score(_score(tmp_path))[3] is None  # score.json from before the key existed


def test_zero_assertion_testcase_is_failed():
    xml = ('<testsuites><testsuite>'
           '<testcase name="a" assertions="0"/>'
           '<testcase name="b" assertions="2"/>'
           '<testcase name="c"/>'
           '<testcase name="d" assertions="0"><skipped/></testcase>'
           '</testsuite></testsuites>')
    assert parse_junit(xml) == TestCounts(2, 1, 0)


# ---------------------------------------------------------------- score.sh

SCORE_SH = Path(__file__).resolve().parent.parent / "harness" / "remote_scripts" / "score.sh"
FAKE_GODOT = """#!/usr/bin/env bash
# Fake godot: --import does nothing; a GUT run writes one passing testcase per `func test_`.
xml="" dir=""
for a in "$@"; do
    case $a in -gjunit_xml_file=*) xml=${a#*=} ;; -gdir=res://*) dir=${a#-gdir=res://} ;; esac
done
[ -z "$xml" ] && exit 0
project=$3
{ echo '<testsuites><testsuite>'
  grep -h '^func test_' "$project/$dir"/*.gd 2>/dev/null | sed 's/.*/<testcase name="x"\\/>/'
  echo '</testsuite></testsuites>'; } > "$xml"
echo "$FAKE_GODOT_LOG"
"""
TIMEOUT_SHIM = "#!/usr/bin/env bash\nshift 3\nexec \"$@\"\n"  # timeout -k N SECS cmd...


def _sh_git(cwd, *a):
    import subprocess
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                   check=True, capture_output=True)


def _run_score_sh(tmp_path, regression_files, godot_log=""):
    import os
    import subprocess
    src = tmp_path / "src"
    (src / "tests" / "regression").mkdir(parents=True)
    (src / "addons" / "gut").mkdir(parents=True)
    (src / "addons" / "gut" / "gut_cmdln.gd").write_text("")
    for name, text in regression_files.items():
        (src / "tests" / "regression" / name).write_text(text)
    subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True)
    _sh_git(src, "add", "-A")
    _sh_git(src, "commit", "-qm", "base")
    task = tmp_path / "task" / "tests"
    task.mkdir(parents=True)
    (task / "test_hidden.gd").write_text("func test_h():\n\tpass\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "godot").write_text(FAKE_GODOT)
    (bin_dir / "timeout").write_text(TIMEOUT_SHIM)
    for f in bin_dir.iterdir():
        f.chmod(0o755)
    out = tmp_path / "score"
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_GODOT_LOG": godot_log}
    subprocess.run(["bash", str(SCORE_SH), str(src), str(tmp_path / "task"), "HEAD", str(src / ".git"),
                    str(out), str(bin_dir / "godot")], check=True, env=env, capture_output=True)
    return json.loads((out / "score.json").read_text()), out


def test_score_sh_writes_regression_expected_and_logs(tmp_path):
    data, out = _run_score_sh(tmp_path, {
        "test_a.gd": "func test_one():\n\tpass\nfunc test_two():\n\tpass\nfunc helper():\n\tpass\n",
        "test_b.gd": "func test_three():\n\tpass\n",
        "test_b.gd.uid": "func test_not_a_script():\n",
    })
    assert data["regression_expected"] == 3
    assert data["regression_log"] == str(out / "regression.log")
    assert data["hidden_log"] == str(out / "hidden.log")
    parse_ok, hidden, regression, expected = load_score(str(out / "score.json"))
    assert parse_ok and hidden == TestCounts(1, 0, 0) and regression == TestCounts(3, 0, 0)
    assert decide_status(parse_ok=parse_ok, hidden=hidden, regression=regression,
                         regression_expected=expected, agent_timed_out=False) == "pass"


def test_score_sh_unloadable_suite_log_fails_parse(tmp_path):
    data, out = _run_score_sh(tmp_path, {"test_a.gd": "func test_one():\n\tpass\n"},
                              godot_log="Script 'res://tests/regression/test_a.gd' could not be loaded")
    assert load_score(str(out / "score.json"))[0] is False


def test_score_sh_extra_timeout_covers_four_inner_runs():
    # score_extra.sh (task 012) runs up to four 300 s GUT suites of its own.
    assert "run_timed 1300 bash \"$task_files/score_extra.sh\"" in SCORE_SH.read_text()
