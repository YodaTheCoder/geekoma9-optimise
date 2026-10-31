from __future__ import annotations

import shlex

from harness.paths import ROOT, AttemptPaths
from harness.remote import Remote

GIT_IDENT = ["-c", "user.name=agentbench", "-c", "user.email=agentbench@localhost"]


class BenchRepo:
    """Access to the benchmark repo through a bare mirror on the remote host."""

    def __init__(self, remote: Remote, mirror: str = f"{ROOT}/bench.git",
                 remote_url: str = "git@github-agentbench:YodaTheCoder/godot-agent-bench.git"):
        self.remote = remote
        self.mirror = mirror
        self.remote_url = remote_url

    def _git(self, *args: str, check: bool = True):
        cmd = "git -C " + shlex.quote(self.mirror) + " " + " ".join(shlex.quote(a) for a in args)
        return self.remote.run(cmd, check=check)

    def update(self) -> None:
        m, u = shlex.quote(self.mirror), shlex.quote(self.remote_url)
        self.remote.run(f"test -d {m} || git clone --mirror {u} {m}")
        self._git("fetch", "--force", self.remote_url, "+refs/*:refs/*")

    def base_sha(self, task_set: str) -> str:
        return self._git("rev-parse", f"base-{task_set}^{{commit}}").stdout.strip()

    def issue_text(self, task_set: str, task: str) -> str:
        return self._git("show", f"taskset-{task_set}:tasks/{task}/issue.md").stdout

    def export_task_files(self, task_set: str, task: str, dest: str) -> None:
        d = shlex.quote(dest)
        self.remote.run(
            f"mkdir -p {d} && git -C {shlex.quote(self.mirror)} archive "
            f"{shlex.quote(f'taskset-{task_set}')} {shlex.quote(f'tasks/{task}')}"
            f" | tar -x -C {d} --strip-components=2")

    def prepare_workdir(self, paths: AttemptPaths, task_set: str, task: str, branch: str) -> None:
        sha = self.base_sha(task_set)
        issue = self.issue_text(task_set, task)
        wd = shlex.quote(paths.workdir)
        # --no-local: a plain local clone copies all of objects/, leaking the tests branch.
        # rm -rf first: an interrupted attempt leaves its folder behind, and resuming must start clean.
        self.remote.run(
            f"rm -rf {shlex.quote(paths.root)} && mkdir -p {shlex.quote(paths.root)} && "
            f"git clone --no-local --single-branch --branch main --no-tags "
            f"{shlex.quote(self.mirror)} {wd}")
        self.remote.run(f"git -C {wd} checkout -b {shlex.quote(branch)} {shlex.quote(sha)}")
        # Drop origin so the agent cannot reach the tests branch / hidden tests.
        self.remote.run(f"git -C {wd} remote remove origin")
        self.remote.write_text(paths.issue_file, issue)

    def commit_and_push(self, paths: AttemptPaths, branch: str, message: str) -> bool:
        wd = shlex.quote(paths.workdir)
        # The workdir is agent-controlled: never run its hooks.
        nohooks = "-c core.hooksPath=/dev/null"
        self.remote.run(f"git -C {wd} {nohooks} add -A")
        self.remote.run(f"git -C {wd} {nohooks} {' '.join(GIT_IDENT)} commit --no-verify --allow-empty -m "
                        f"{shlex.quote(message)}")
        self._git("fetch", paths.workdir, f"+{branch}:{branch}")
        r = self._git("push", self.remote_url, branch, check=False)
        return r.returncode == 0

