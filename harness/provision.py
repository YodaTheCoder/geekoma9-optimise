from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from harness.paths import AGENT_USER, MIRROR, ROOT
from harness.remote import Remote, RemoteError

SCRIPTS_SRC = Path(__file__).resolve().parent / "remote_scripts"
# HTTPS so the clone works before the deploy key is added; BenchRepo.update fetches over ssh later.
MIRROR_CLONE_URL = "https://github.com/YodaTheCoder/godot-agent-bench.git"
GODOT_BIN = f"{ROOT}/opt/godot/godot"
OLLAMA_BIN = "/usr/local/bin/ollama"
MODEL_STORE = "/usr/share/ollama/.ollama/models"
MIN_PYTHON = (3, 10)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def _sh(remote: Remote, cmd: str, timeout: float = 60) -> tuple[bool, str]:
    """Run `cmd` on the host; (success, combined output). Connection loss counts as failure."""
    try:
        r = remote.run("{ " + cmd + "; } 2>&1 </dev/null", timeout=timeout, check=False)
    except RemoteError as e:
        return False, str(e)
    return r.returncode == 0, (r.stdout or "").strip()


def normalise_godot_version(pinned: str) -> str:
    """`.godot-version` holds `4.7.2-stable`; `godot --version` prints `4.7.2.stable.official.<hash>`."""
    return pinned.strip().replace("-", ".")


def check_python(remote: Remote) -> Check:
    ok, out = _sh(remote, "python3 --version")
    m = re.search(r"Python (\d+)\.(\d+)", out)
    if not ok or not m:
        return Check("python3", False, out or "python3 not found")
    version = (int(m[1]), int(m[2]))
    return Check("python3", version >= MIN_PYTHON, f"{out} (need >= {'.'.join(map(str, MIN_PYTHON))})")


def check_godot(remote: Remote) -> Check:
    ok, pinned = _sh(remote, f"git -C {shlex.quote(MIRROR)} show base-v1:.godot-version")
    if not ok or not pinned:
        return Check("godot", False, f"cannot read .godot-version at base-v1: {pinned}")
    want = normalise_godot_version(pinned)
    ok, got = _sh(remote, f"{shlex.quote(GODOT_BIN)} --version")
    if not ok:
        return Check("godot", False, got or "godot --version failed")
    # Match on the version prefix: the build hash after `.official.` is not pinned.
    return Check("godot", got == want or got.startswith(want + "."),
                 f"{got} (pinned {pinned.strip()} -> {want})")


def check_ollama(remote: Remote) -> Check:
    ok, out = _sh(remote, f"{OLLAMA_BIN} --version")
    return Check("ollama", ok, out)


def check_deploy_key(remote: Remote) -> Check:
    # ssh -T exits 1 even when authentication works, so judge by the greeting.
    ok, out = _sh(remote, "ssh -o BatchMode=yes -o ConnectTimeout=10 -T git@github-agentbench; true")
    return Check("deploy-key", "successfully authenticated" in out, out.splitlines()[-1] if out else "")


def check_sudo(remote: Remote) -> Check:
    # Harmless probe: proves passwordless sudo for systemctl without touching the live Ollama.
    ok, out = _sh(remote, "sudo -n systemctl --version")
    return Check("sudo", ok, out.splitlines()[0] if out else "")


def check_linger(remote: Remote) -> Check:
    ok, out = _sh(remote, "loginctl show-user markn -p Linger")
    return Check("linger", ok and out == "Linger=yes", out)


def check_model_store(remote: Remote) -> Check:
    ok, out = _sh(remote, f"ls {MODEL_STORE}/manifests")
    return Check("model-store", ok, out if not ok else f"readable ({out})")


def check_agent_user(remote: Remote) -> Check:
    """The agent user exists, has no sudo, can run Godot, and cannot read the mirror or an
    earlier attempt (setup in docs/provisioning.md)."""
    name = "agent-user"
    u = shlex.quote(AGENT_USER)
    ok, out = _sh(remote, f"id -u {u}")
    if not ok:
        return Check(name, False, out or f"no user {AGENT_USER}")
    _, out = _sh(remote, f"sudo -n -l -U {u}")
    if "is not allowed to run sudo" not in out:
        return Check(name, False, f"{AGENT_USER} may have sudo rights: {out.splitlines()[0] if out else '?'}")
    ok, out = _sh(remote, f"sudo -n -u {u} true")
    if not ok:
        return Check(name, False, f"cannot run commands as {AGENT_USER}: {out}")
    ok, _ = _sh(remote, f"sudo -n -u {u} test -x {shlex.quote(GODOT_BIN)}")
    if not ok:
        return Check(name, False, f"{AGENT_USER} cannot run {GODOT_BIN}")
    _, attempt = _sh(remote, f"ls -d {ROOT}/runs/*/*/work 2>/dev/null | head -n 1")
    closed = [MIRROR] + ([attempt.splitlines()[0]] if attempt else [])
    for path in closed:
        readable, _ = _sh(remote, f"sudo -n -u {u} test -r {shlex.quote(path)}")
        if readable:
            return Check(name, False, f"{AGENT_USER} can read {path}")
    return Check(name, True, f"{AGENT_USER}: no sudo, runs godot, cannot read {', '.join(closed)}")


CHECKS = (check_python, check_godot, check_ollama, check_deploy_key, check_sudo, check_linger,
          check_model_store, check_agent_user)


def provision(remote: Remote, scripts_src: Path = SCRIPTS_SRC) -> int:
    """Sync scripts, ensure the mirror, run every check. Non-zero names the first failure."""
    try:
        remote.run(f"mkdir -p {ROOT}/bin")
        remote.sync_dir(scripts_src, f"{ROOT}/bin")
        remote.run(f"chmod +x {ROOT}/bin/*")
        print(f"synced remote scripts to {ROOT}/bin")
        remote.run(f"test -d {shlex.quote(MIRROR)} || git clone --mirror "
                   f"{MIRROR_CLONE_URL} {shlex.quote(MIRROR)}", timeout=300)
    except (RemoteError, subprocess.CalledProcessError) as e:
        detail = (getattr(e, "stderr", None) or str(e)).strip()
        print(f"FAIL setup: {detail}")
        print("provision: FAILED (setup)")
        return 1
    print(f"mirror present at {MIRROR}")
    results = [check(remote) for check in CHECKS]
    for c in results:
        print(f"{'OK  ' if c.ok else 'FAIL'} {c.name}: {c.detail}")
    failed = [c for c in results if not c.ok]
    if failed:
        print(f"provision: FAILED ({failed[0].name})")
        return 1
    print("provision: ok")
    return 0
