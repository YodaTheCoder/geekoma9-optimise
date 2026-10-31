from __future__ import annotations

import subprocess

from conftest import FakeRemote
from harness import provision as pv
from harness.remote import RemoteError


class ProvRemote(FakeRemote):
    def __init__(self):
        super().__init__()
        self.synced: list[tuple[str, str]] = []
        self.reply("python3 --version", stdout="Python 3.12.3\n")
        self.reply(".godot-version", stdout="4.7.2-stable\n")
        self.reply("godot --version", stdout="4.7.2.stable.official.ed1daf0bf\n")
        self.reply("ollama --version", stdout="ollama version is 0.34.4\n")
        self.reply("github-agentbench", stdout="Hi X! You've successfully authenticated, but GitHub...\n")
        self.reply("systemctl --version", stdout="systemd 255 (255.4)\n")
        self.reply("Linger", stdout="Linger=yes\n")
        self.reply("manifests", stdout="registry.ollama.ai\n")

    def sync_dir(self, local, remote_path):
        self.synced.append((str(local), remote_path))


def failing(remote, substr, rc=1, stdout="nope"):
    remote.replies.insert(0, (substr, subprocess.CompletedProcess([], rc, stdout, "")))


def test_all_ok(capsys):
    remote = ProvRemote()
    assert pv.provision(remote) == 0
    out = capsys.readouterr().out
    assert out.count("OK  ") == len(pv.CHECKS) and "FAIL" not in out
    assert remote.synced == [(str(pv.SCRIPTS_SRC), "/home/markn/agentbench/bin")]
    assert any("chmod +x" in c for c in remote.calls)
    assert any("git clone --mirror https://github.com/YodaTheCoder/godot-agent-bench.git" in c
               for c in remote.calls)
    # nothing may stop the live Ollama
    assert not any("stop ollama" in c for c in remote.calls)


def test_names_first_failure_but_runs_all(capsys):
    remote = ProvRemote()
    failing(remote, "github-agentbench", stdout="Permission denied (publickey).")
    failing(remote, "Linger", stdout="Linger=no")
    assert pv.provision(remote) == 1
    out = capsys.readouterr().out
    assert "FAIL deploy-key" in out and "FAIL linger" in out and "OK   model-store" in out
    assert "provision: FAILED (deploy-key)" in out


def test_godot_version_prefix_match():
    remote = ProvRemote()
    assert pv.check_godot(remote).ok
    failing(remote, "godot --version", rc=0, stdout="4.7.20.stable.official.x")
    assert not pv.check_godot(remote).ok
    failing(remote, "godot --version", rc=0, stdout="4.6.1.stable.official.x")
    assert not pv.check_godot(remote).ok


def test_old_python_fails():
    remote = ProvRemote()
    failing(remote, "python3 --version", rc=0, stdout="Python 3.9.18")
    assert not pv.check_python(remote).ok


def test_unreachable_host_is_a_failed_check():
    class Dead(ProvRemote):
        def run(self, cmd, timeout=None, check=True):
            raise RemoteError("down")
    assert not pv.check_ollama(Dead()).ok


def test_setup_failure_reported_not_traceback(capsys):
    class NoSync(ProvRemote):
        def sync_dir(self, local, remote_path):
            raise RemoteError("rsync: connection refused")
    assert pv.provision(NoSync()) == 1
    out = capsys.readouterr().out
    assert "FAIL setup: rsync: connection refused" in out and "FAILED (setup)" in out


def test_clone_failure_reported(capsys):
    remote = ProvRemote()
    orig = remote.run

    def run(cmd, timeout=None, check=True):
        if "git clone --mirror" in cmd:
            raise subprocess.CalledProcessError(128, cmd, "", "fatal: no network")
        return orig(cmd, timeout, check)
    remote.run = run
    assert pv.provision(remote) == 1
    assert "FAIL setup: fatal: no network" in capsys.readouterr().out
