import json
import subprocess

import pytest

from harness import review
from harness.results import AttemptRecord, append_record
from harness.review import Review, build_review_prompt, parse_review

GOOD = {"would_merge": True, "quality": 4, "comments": "fine"}


def test_parse_fenced():
    assert parse_review("```json\n" + json.dumps(GOOD) + "\n```") == (True, 4, "fine")


def test_parse_bare():
    assert parse_review(json.dumps(GOOD)) == (True, 4, "fine")


def test_parse_surrounded_by_prose():
    assert parse_review("Here you go:\n" + json.dumps(GOOD) + "\nHope that helps") == (True, 4, "fine")


@pytest.mark.parametrize("q", [0, 6])
def test_parse_quality_out_of_range(q):
    with pytest.raises(ValueError):
        parse_review(json.dumps({**GOOD, "quality": q}))


@pytest.mark.parametrize("text", ["no json here", "{not json}", json.dumps({"quality": 3}),
                                  json.dumps({**GOOD, "would_merge": "yes"})])
def test_parse_invalid(text):
    with pytest.raises(ValueError):
        parse_review(text)


def test_prompt_contents():
    p = build_review_prompt("ISSUE-TEXT", "DIFF-TEXT")
    assert "ISSUE-TEXT" in p and "DIFF-TEXT" in p
    assert "5 = merge as is" in p


def _rec(task, repeat, status="pass", branch=None):
    return AttemptRecord(
        experiment="e", run_id="r", task=task, repeat=repeat, status=status, hidden_passed=1,
        hidden_total=1, regressions_ok=True, parse_ok=True, wall_s=1.0, prompt_tokens=None,
        gen_tokens=None, pp_tps=None, tg_tps=None, peak_mem_mib=None, peak_gpu_mem_mib=None,
        steps=None, throttled=False, upstream_errors=0, pushed=True,
        branch=branch or f"b-{task}-{repeat}", versions={}, started_at="t")


def _setup(tmp_path, recs):
    (tmp_path / "config.yaml").write_text(
        "id: e\ntask_set: v1\ntier: all\nruntime: {kind: ollama, model: m, context: 1}\n"
        "agent: {kind: \"null\", name: n}\n")
    for r in recs:
        append_record(tmp_path / "results.jsonl", r)
    return tmp_path


class FakeGit:
    def __init__(self, missing=()):
        self.calls, self.missing = [], set(missing)

    def __call__(self, args):
        self.calls.append(args)
        if args[0] == "fetch":
            return ""
        if args[0] == "show":
            return "issue for " + args[1]
        if args[0] == "diff":
            if any(m in args[1] for m in self.missing):
                raise subprocess.CalledProcessError(128, "git")
            return "diff " + args[1]
        raise AssertionError(args)


def test_review_experiment_skips_done_and_non_pass(tmp_path):
    exp = _setup(tmp_path, [_rec("t1", 1), _rec("t2", 1), _rec("t3", 1, status="fail")])
    review.append_review(exp / "reviews.jsonl", Review("t1", 1, "b-t1-1", True, 5, "x", "claude-opus"))
    prompts = []

    def runner(prompt):
        prompts.append(prompt)
        return json.dumps(GOOD)

    git = FakeGit()
    assert review.review_experiment(exp, runner=runner, git=git) == 0
    assert len(prompts) == 1 and "issue for refs/tags/taskset-v1:tasks/t2/issue.md" in prompts[0]
    assert "base-v1..refs/remotes/origin/b-t2-1" in prompts[0]
    got = review.read_reviews(exp / "reviews.jsonl")
    assert [(r.task, r.reviewer) for r in got] == [("t1", "claude-opus"), ("t2", "claude-opus")]
    # rerun reviews nothing
    assert review.review_experiment(exp, runner=runner, git=git) == 0
    assert len(prompts) == 1


def test_review_retries_then_gives_up(tmp_path):
    exp = _setup(tmp_path, [_rec("t1", 1), _rec("t2", 1)])
    outs = iter(["garbage", json.dumps(GOOD), "bad", "worse"])
    calls = []

    def runner(prompt):
        calls.append(1)
        return next(outs)

    assert review.review_experiment(exp, runner=runner, git=FakeGit()) == 1
    assert len(calls) == 4
    assert [r.task for r in review.read_reviews(exp / "reviews.jsonl")] == ["t1"]


def test_fetched_origin_is_the_evidence(tmp_path):
    # After a good fetch only the pushed branch counts: a stale local ref is never reviewed.
    exp = _setup(tmp_path, [_rec("t1", 1, branch="tests")])

    class G(FakeGit):
        def __call__(self, args):
            if args[0] == "diff" and "origin/" in args[1]:
                self.calls.append(args)
                raise subprocess.CalledProcessError(128, "git")
            return super().__call__(args)

    git = G()
    assert review.review_experiment(exp, runner=lambda p: json.dumps(GOOD), git=git) == 1
    diffs = [a[1] for a in git.calls if a[0] == "diff"]
    assert diffs == ["base-v1..refs/remotes/origin/tests"]


def test_local_ref_used_only_when_fetch_failed(tmp_path):
    exp = _setup(tmp_path, [_rec("t1", 1, branch="tests")])

    class G(FakeGit):
        def __call__(self, args):
            if args[0] == "fetch":
                raise subprocess.CalledProcessError(1, "git")
            if args[0] == "diff" and "origin/" in args[1]:
                self.calls.append(args)
                raise subprocess.CalledProcessError(128, "git")
            return super().__call__(args)

    git = G()
    assert review.review_experiment(exp, runner=lambda p: json.dumps(GOOD), git=git) == 0
    diffs = [a[1] for a in git.calls if a[0] == "diff"]
    assert diffs == ["base-v1..refs/remotes/origin/tests", "base-v1..refs/heads/tests"]


def test_fetch_failure_only_warns(tmp_path, capsys):
    exp = _setup(tmp_path, [_rec("t1", 1)])

    class G(FakeGit):
        def __call__(self, args):
            if args[0] == "fetch":
                raise subprocess.CalledProcessError(1, "git")
            return super().__call__(args)

    assert review.review_experiment(exp, runner=lambda p: json.dumps(GOOD), git=G()) == 0
    assert "warning" in capsys.readouterr().err


def test_prompt_fence_survives_backticks_in_diff():
    diff = "+x = \"\"\"\n```\n+````\n"
    p = build_review_prompt("issue", diff)
    assert "5 = merge as is" in p
    fence = "`````"  # longest run is 4, so the fence must be 5
    assert f"{fence}diff\n{diff}\n{fence}" in p


def test_missing_claude_fails_once_before_loop(tmp_path, monkeypatch, capsys):
    exp = _setup(tmp_path, [_rec("t1", 1), _rec("t2", 1)])
    monkeypatch.delenv("CLAUDE_BIN", raising=False)
    monkeypatch.setattr(review.shutil, "which", lambda name: None)
    git = FakeGit()
    assert review.review_experiment(exp, git=git) == 2
    assert git.calls == []
    assert capsys.readouterr().err.count("claude CLI not found") == 1


def test_claude_bin_env_wins(monkeypatch):
    monkeypatch.setenv("CLAUDE_BIN", "/x/claude")
    assert review.find_claude() == "/x/claude"
