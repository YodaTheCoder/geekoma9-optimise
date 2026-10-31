from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=15"]


class RemoteError(Exception):
    """ssh exit 255: connection lost or refused (caller maps to infra_error)."""


class Remote:
    def __init__(self, host: str = "markn@geekoma9.local"):
        self.host = host

    def _exec(self, args: list[str], timeout: float | None, check: bool,
              input: str | None = None) -> subprocess.CompletedProcess[str]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, input=input)
        if r.returncode == 255:
            raise RemoteError(f"{args[0]} to {self.host} failed: {(r.stderr or '').strip()}")
        if check and r.returncode != 0:
            raise subprocess.CalledProcessError(r.returncode, args, r.stdout, r.stderr)
        return r

    def run(self, cmd: str, timeout: float | None = None,
            check: bool = True) -> subprocess.CompletedProcess[str]:
        return self._exec(["ssh", *SSH_OPTS, self.host, cmd], timeout, check)

    def read_text(self, path: str) -> str:
        return self.run(f"cat {shlex.quote(path)}").stdout

    def write_text(self, path: str, text: str) -> None:
        self._exec(["ssh", *SSH_OPTS, self.host, f"cat > {shlex.quote(path)}"],
                   None, True, input=text)

    def sync_dir(self, local: Path, remote_path: str) -> None:
        ssh = "ssh " + " ".join(SSH_OPTS)
        self._exec(["rsync", "-a", "--delete", "-e", ssh,
                    f"{str(local).rstrip('/')}/", f"{self.host}:{remote_path.rstrip('/')}/"],
                   None, True)
