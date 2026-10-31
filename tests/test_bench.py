from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path

from harness.bench import BenchRepo
from harness.paths import attempt_paths

PATHS = attempt_paths("r1", "t1", 2)


def repo(fr):
    return BenchRepo(fr, mirror="/m.git", remote_url="URL")


def test_prepare_workdir_removes_origin(fake_remote):
    fake_remote.reply("rev-parse", stdout="abc123\n")
    fake_remote.reply("show", stdout="ISSUE")
    repo(fake_remote).prepare_workdir(PATHS, "ts", "t1", "attempt-1")
    calls = fake_remote.calls
    clone = next(c for c in calls if "git clone" in c)
    assert "--single-branch" in clone and "--no-tags" in clone and "--no-local" in clone and "--branch main" in clone
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
    assert "core.hooksPath=/dev/null" in c[0] and "add -A" in c[0]
    assert "user.name=agentbench" in c[1] and "--allow-empty" in c[1] and "--no-verify" in c[1] and "core.hooksPath=/dev/null" in c[1] and "'msg x'" in c[1]
    assert f"git -C /m.git fetch {PATHS.workdir} +b:b" == c[2]
    assert "git -C /m.git push URL b" == c[3]


def test_commit_and_push_failure_returns_false(fake_remote):
    fake_remote.reply("push", returncode=1)
    assert repo(fake_remote).commit_and_push(PATHS, "b", "m") is False


def test_update_export(fake_remote):
    r = repo(fake_remote)
    r.update()
    assert any("fetch" in c and "+refs/*:refs/*" in c and "--prune" not in c for c in fake_remote.calls)
    r.export_task_files("ts", "t1", "/d")
    last = fake_remote.calls[-1]
    assert "archive taskset-ts tasks/t1" in last and "--strip-components=2" in last


class LocalRemote:
    """Runs commands locally through bash; for integration tests with real git."""

    def run(self, cmd, timeout=None, check=True):
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        if check and r.returncode:
            raise subprocess.CalledProcessError(r.returncode, cmd, r.stdout, r.stderr)
        return r

    def write_text(self, path, text):
        Path(path).write_text(text)


def _git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout


def _bench_mirror(tmp_path):
    """A mirror with main, base-ts, taskset-ts and a tests branch holding a secret; returns (mirror, base, secret)."""
    src = tmp_path / "src"
    subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True)
    (src / "a.txt").write_text("public")
    _git(src, "add", "-A"); _git(src, "commit", "-qm", "base")
    _git(src, "tag", "base-ts")
    _git(src, "checkout", "-qb", "taskset-ts")
    (src / "tasks" / "t1").mkdir(parents=True)
    (src / "tasks" / "t1" / "issue.md").write_text("the issue")
    _git(src, "add", "-A"); _git(src, "commit", "-qm", "ts")
    _git(src, "checkout", "-qb", "tests", "main")
    (src / "secret.txt").write_text("HIDDEN-TESTS")
    _git(src, "add", "-A"); _git(src, "commit", "-qm", "hidden")
    secret = _git(src, "rev-parse", "tests:secret.txt").strip()
    mirror = tmp_path / "bench.git"
    subprocess.run(["git", "clone", "-q", "--mirror", str(src), str(mirror)], check=True)
    base = _git(src, "rev-parse", "base-ts^{commit}").strip()
    return mirror, base, secret


def _local_paths(tmp_path):
    paths = attempt_paths("r", "t1", 1)
    return dataclasses.replace(paths, root=str(tmp_path / "att"), workdir=str(tmp_path / "att/work"),
                               issue_file=str(tmp_path / "att/issue.md"))


def test_workdir_does_not_contain_hidden_objects(tmp_path):
    mirror, base, secret = _bench_mirror(tmp_path)
    paths = _local_paths(tmp_path)
    BenchRepo(LocalRemote(), mirror=str(mirror), remote_url="unused").prepare_workdir(
        paths, "ts", "t1", "attempt-1")
    wd = paths.workdir
    assert _git(wd, "rev-parse", "HEAD").strip() == base
    assert _git(wd, "remote").strip() == ""
    assert Path(paths.issue_file).read_text() == "the issue"
    objs = _git(wd, "cat-file", "--batch-all-objects", "--batch-check")
    assert secret not in objs
    assert "dangling commit" not in _git(wd, "fsck", "--lost-found", "--no-reflogs")


def test_prepare_workdir_replaces_leftover_attempt(tmp_path):
    # Resuming after an interrupted attempt finds its folder still there; git refuses to clone into it.
    mirror, base, _ = _bench_mirror(tmp_path)
    paths = _local_paths(tmp_path)
    repo = BenchRepo(LocalRemote(), mirror=str(mirror), remote_url="unused")
    for n in (1, 2):
        Path(paths.workdir).mkdir(parents=True, exist_ok=True)
        (Path(paths.workdir) / "stale.txt").write_text("left by the interrupted attempt")
        (Path(paths.root) / "agent.log").write_text(f"old log {n}")
        repo.prepare_workdir(paths, "ts", "t1", "attempt-1")
        assert _git(paths.workdir, "rev-parse", "HEAD").strip() == base
        assert not (Path(paths.workdir) / "stale.txt").exists()
        assert not (Path(paths.root) / "agent.log").exists()
        # the failed try's logs are kept beside it, closed to later agents
        kept = Path(f"{paths.root}.try{n}")
        assert (kept / "agent.log").read_text() == f"old log {n}"
        assert kept.stat().st_mode & 0o777 == 0o700
        (Path(paths.root) / "agent.log").write_text("")  # next round: a fresh leftover
        (Path(paths.workdir) / "stale.txt").write_text("")
    assert not Path(f"{paths.root}.try3").exists()


def test_attempt_root_is_traverse_only(tmp_path):
    # The agent user can reach its workdir and issue by path, but list nothing.
    mirror, _, _ = _bench_mirror(tmp_path)
    paths = _local_paths(tmp_path)
    BenchRepo(LocalRemote(), mirror=str(mirror), remote_url="unused").prepare_workdir(
        paths, "ts", "t1", "attempt-1")
    assert Path(paths.root).stat().st_mode & 0o777 == 0o711
    assert Path(paths.root).parent.stat().st_mode & 0o777 == 0o711
