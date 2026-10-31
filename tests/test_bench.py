from __future__ import annotations

from harness.bench import BenchRepo
from harness.paths import attempt_paths

PATHS = attempt_paths("r1", "t1", 2)


def repo(fr):
    return BenchRepo(fr, mirror="/m.git", remote_url="URL")


def test_prepare_workdir_removes_origin(fake_remote):
    fake_remote.reply("rev-parse", stdout="abc123\n")
    fake_remote.reply("show", stdout="ISSUE")
    repo(fake_remote).prepare_workdir(PATHS, "ts", "attempt-1")
    calls = fake_remote.calls
    clone = next(c for c in calls if "git clone" in c)
    assert "--single-branch" in clone and "--no-tags" in clone and "--branch main" in clone
    iclone = calls.index(clone)
    icheck = next(i for i, c in enumerate(calls) if "checkout -b attempt-1 abc123" in c)
    irm = next(i for i, c in enumerate(calls) if "git -C " + PATHS.workdir + " remote remove origin" in c)
    assert iclone < icheck < irm
    assert fake_remote.written[PATHS.issue_file] == "ISSUE"
    assert any("show taskset-ts:tasks/t1/issue.md" in c for c in calls)
    assert any("base-ts" in c for c in calls)


def test_commit_and_push_ok(fake_remote):
    assert repo(fake_remote).commit_and_push(PATHS, "b", "msg x") is True
    c = fake_remote.calls
    assert "add -A" in c[0]
    assert "user.name=agentbench" in c[1] and "--allow-empty" in c[1] and "'msg x'" in c[1]
    assert f"git -C /m.git fetch {PATHS.workdir} b:b" == c[2]
    assert "git -C /m.git push URL b" == c[3]


def test_commit_and_push_failure_returns_false(fake_remote):
    fake_remote.reply("push", returncode=1)
    assert repo(fake_remote).commit_and_push(PATHS, "b", "m") is False


def test_update_export(fake_remote):
    r = repo(fake_remote)
    r.update()
    assert any("fetch" in c and "+refs/*:refs/*" in c for c in fake_remote.calls)
    r.export_task_files("ts", "t1", "/d")
    last = fake_remote.calls[-1]
    assert "archive taskset-ts tasks/t1" in last and "--strip-components=2" in last
