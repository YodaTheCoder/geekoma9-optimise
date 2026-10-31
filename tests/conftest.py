from __future__ import annotations

import subprocess

import pytest


class FakeRemote:
    """Recording stub: replies are matched by substring of the command, first match wins."""

    def __init__(self):
        self.calls: list[str] = []
        self.timeouts: list[float | None] = []
        self.written: dict[str, str] = {}
        self.files: dict[str, str] = {}
        self.replies: list[tuple[str, subprocess.CompletedProcess]] = []

    def reply(self, substr: str, returncode: int = 0, stdout: str = "") -> None:
        self.replies.append((substr, subprocess.CompletedProcess([], returncode, stdout, "")))

    def run(self, cmd, timeout=None, check=True):
        self.calls.append(cmd)
        self.timeouts.append(timeout)
        for substr, r in self.replies:
            if substr in cmd:
                return r
        return subprocess.CompletedProcess([], 0, "", "")

    def read_text(self, path):
        return self.files.get(path, "")

    def write_text(self, path, text):
        self.written[path] = text


@pytest.fixture
def fake_remote():
    return FakeRemote()
