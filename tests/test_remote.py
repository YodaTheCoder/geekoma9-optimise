import subprocess
from pathlib import Path

import pytest

from harness.paths import attempt_paths
from harness.remote import Remote, RemoteError

OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=15"]


def fake_run(calls, rc=0, out="", err=""):
    def _run(args, **kw):
        calls.append((args, kw))
        return subprocess.CompletedProcess(args, rc, out, err)
    return _run


def test_run_builds_ssh_command(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", fake_run(calls, out="geekoma9\n"))
    r = Remote().run("uname -n", timeout=5)
    assert calls[0][0] == ["ssh", *OPTS, "markn@geekoma9.local", "uname -n"]
    assert calls[0][1]["timeout"] == 5
    assert r.stdout == "geekoma9\n"


def test_exit_255_raises_remote_error_even_without_check(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_run([], rc=255, err="refused"))
    with pytest.raises(RemoteError):
        Remote().run("x", check=False)


def test_exit_1_check_raises(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_run([], rc=1))
    with pytest.raises(subprocess.CalledProcessError):
        Remote().run("false")


def test_exit_1_no_check_returns(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_run([], rc=1))
    assert Remote().run("false", check=False).returncode == 1


def test_read_text(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", fake_run(calls, out="hello"))
    assert Remote().read_text("/a b/c") == "hello"
    assert calls[0][0][-1] == "cat '/a b/c'"


def test_write_text_via_stdin(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", fake_run(calls))
    Remote().write_text("/a b/c", "data")
    assert calls[0][0][-1] == "cat > '/a b/c'"
    assert calls[0][1]["input"] == "data"


def test_sync_dir(monkeypatch, tmp_path: Path):
    calls = []
    monkeypatch.setattr(subprocess, "run", fake_run(calls))
    Remote().sync_dir(tmp_path, "/r/dst")
    args = calls[0][0]
    assert args[:3] == ["rsync", "-a", "--delete"]
    assert args[3] == "-e"
    assert args[4] == "ssh " + " ".join(OPTS)
    assert args[5:] == [f"{tmp_path}/", "markn@geekoma9.local:/r/dst/"]


def test_sync_dir_255(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(subprocess, "run", fake_run([], rc=255))
    with pytest.raises(RemoteError):
        Remote().sync_dir(tmp_path, "/r/dst")


def test_attempt_paths():
    p = attempt_paths("e0-202611010100", "001-health-clamp", 2)
    root = "/home/markn/agentbench/runs/e0-202611010100/001-health-clamp-r2"
    assert p.root == root
    assert p.workdir == f"{root}/work"
    assert p.task_files == f"{root}/score/task"  # exported after the agent, never beside it
    assert p.task == "001-health-clamp"
    assert p.issue_file == f"{root}/issue.md"
    assert p.agent_log == f"{root}/agent.log"
    assert p.usage_log == f"{root}/usage.jsonl"
    assert p.samples_csv == f"{root}/samples.csv"
    assert p.score_dir == f"{root}/score"


def test_timeout_maps_to_remote_error(monkeypatch):
    def boom(args, **kw):
        raise subprocess.TimeoutExpired(args, 1)
    monkeypatch.setattr(subprocess, "run", boom)
    with pytest.raises(RemoteError):
        Remote().run("sleep 9", timeout=1)
