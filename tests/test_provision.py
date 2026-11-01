from __future__ import annotations

import subprocess

from conftest import FakeRemote
from harness import provision as pv
from harness.remote import RemoteError


class ProvRemote(FakeRemote):
    def __init__(self):
        super().__init__()
        self.reply("python3 --version", stdout="Python 3.12.3\n")
        self.reply(".godot-version", stdout="4.7.2-stable\n")
        self.reply("godot --version", stdout="4.7.2.stable.official.ed1daf0bf\n")
        self.reply("ollama --version", stdout="ollama version is 0.34.4\n")
        self.reply("github-agentbench", stdout="Hi X! You've successfully authenticated, but GitHub...\n")
        self.reply("systemctl --version", stdout="systemd 255 (255.4)\n")
        self.reply("Linger", stdout="Linger=yes\n")
        self.reply("manifests", stdout="registry.ollama.ai\n")
        self.reply("id -u agentrun", stdout="1001\n")
        self.reply("sudo -n -l -U agentrun", stdout="User agentrun is not allowed to run sudo on geekoma9.\n")
        self.reply("ls -d /srv/agentbench/runs/*/*/work",
                   stdout="/srv/agentbench/runs/e0-1/001-a-r1/work\n")
        self.reply("test -x /home/markn", returncode=1)  # agentrun cannot enter markn's home
        self.reply("test -r", returncode=1)  # agentrun can read neither the mirror nor attempts



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


def test_agent_user_ok():
    remote = ProvRemote()
    c = pv.check_agent_user(remote)
    assert c.name == "agent-user" and c.ok, c.detail
    calls = "\n".join(remote.calls)
    assert "sudo -n -u agentrun test -r /home/markn/agentbench/bench.git" in calls
    assert "sudo -n -u agentrun test -r /srv/agentbench/runs/e0-1/001-a-r1/work" in calls
    assert "sudo -n -u agentrun test -x /srv/agentbench/opt/godot/godot" in calls
    assert "sudo -n -u agentrun test -x /home/markn" in calls


def test_agent_user_missing():
    remote = ProvRemote()
    failing(remote, "id -u agentrun", stdout="id: 'agentrun': no such user")
    c = pv.check_agent_user(remote)
    assert not c.ok and "no such user" in c.detail


def test_agent_user_with_sudo_rights_fails():
    remote = ProvRemote()
    failing(remote, "sudo -n -l -U agentrun", rc=0,
            stdout="User agentrun may run the following commands on geekoma9:\n    (ALL) ALL")
    c = pv.check_agent_user(remote)
    assert not c.ok and "sudo" in c.detail


def test_agent_user_can_read_mirror_fails():
    remote = ProvRemote()
    failing(remote, "test -r /home/markn/agentbench/bench.git", rc=0, stdout="")
    c = pv.check_agent_user(remote)
    assert not c.ok and "bench.git" in c.detail


def test_agent_user_can_read_other_attempt_fails():
    remote = ProvRemote()
    failing(remote, "test -r /srv/agentbench/runs/", rc=0, stdout="")
    c = pv.check_agent_user(remote)
    assert not c.ok and "001-a-r1" in c.detail


def test_agent_user_can_enter_owner_home_fails():
    # A traversable home exposes every o+r path in it (~/.claude/projects holds transcripts).
    remote = ProvRemote()
    failing(remote, "test -x /home/markn", rc=0, stdout="")
    c = pv.check_agent_user(remote)
    assert not c.ok and "/home/markn" in c.detail


def test_agent_user_cannot_run_godot_fails():
    remote = ProvRemote()
    failing(remote, "test -x /srv/agentbench/opt/godot/godot", rc=1, stdout="")
    assert not pv.check_agent_user(remote).ok
