from __future__ import annotations

import hashlib
import json
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import asdict
from pathlib import Path

from harness.agents import make_agent
from harness.agents.base import Agent, AgentResult
from harness.bench import BenchRepo
from harness.config import ConfigError, ExperimentConfig, check_safe_id
from harness.paths import AGENT_USER, ROOT, AttemptPaths, attempt_paths
from harness.provision import SCRIPTS_SRC, sync_scripts
from harness.remote import Remote, RemoteError
from harness.results import AttemptRecord, append_record, pending, read_records
from harness.runtimes import make_runtime
from harness.runtimes.base import Runtime
from harness.runtimes.ollama import JOURNALCTL, UNIT_NAME
from harness.sampling import summarize_samples
from harness.scoring import decide_status, load_score
from harness.tiers import tier_plan
from harness.usage import summarize_usage

SCRIPTS_DIR = f"{ROOT}/bin"
GODOT_BIN = f"{ROOT}/opt/godot/godot"
PROXY_LISTEN = "127.0.0.1:11500"
ENDPOINT = f"http://{PROXY_LISTEN}"
SAMPLE_INTERVAL_S = 5
PROXY_FLUSH_S = 2  # let the proxy write its last usage row before it is stopped
SCORE_TIMEOUT_S = 3000  # score.sh: import 300 + two GUT suites 600 each + extra 1300, plus slack
SYSTEM_OLLAMA_STOP = "sudo -n systemctl stop ollama"
SYSTEM_OLLAMA_START = "sudo -n systemctl start ollama"
SYSTEM_OLLAMA_ACTIVE = "systemctl is-active ollama"
RUN_LOCK = f"{ROOT}/run.lock"
# Bracket trick: the pattern does not match the shell running pgrep itself.
PREFLIGHT_CMD = "pgrep -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'"
# Nothing may run as the agent user between attempts (and before task files are exported).
AGENT_PGREP = f"pgrep -u {AGENT_USER}"
# Kernel log and runtime journal lines that mean something was OOM-killed.
OOM_PATTERN = "out of memory|oom-kill|killed process"
# Exceptions that make an attempt infra_error instead of aborting the experiment.
INFRA_EXCEPTIONS = (RemoteError, subprocess.CalledProcessError)


class InfraError(Exception):
    """Host not in the expected state (maps to infra_error)."""


class HostDirtyError(Exception):
    """Stray processes survived the cleanup kill: stop the experiment (not an attempt record)."""


class RuntimeRestartError(Exception):
    """The runtime would not restart after an infra_error: stop the experiment, recording
    nothing for the untried retry, so a resume reruns it."""


class RunLockedError(Exception):
    """Another `harness run` holds the remote run lock."""


def config_hash(cfg: ExperimentConfig) -> str:
    """sha256 of the loaded config's canonical JSON."""
    return hashlib.sha256(json.dumps(asdict(cfg), sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest()


def scripts_hash(src: Path = SCRIPTS_SRC) -> str:
    """sha256 over the remote scripts' relative paths and contents (bytecode caches skipped)."""
    h = hashlib.sha256()
    for f in sorted(p for p in Path(src).rglob("*") if p.is_file()
                    and "__pycache__" not in p.parts and p.suffix != ".pyc"):
        h.update(f.relative_to(src).as_posix().encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def _check_config_unchanged(results: Path, records: list[AttemptRecord], current: str) -> None:
    """A run_id holds one config: refuse to resume under a different one."""
    old = sorted({r.versions["config"] for r in records if "config" in r.versions} - {current})
    if old:
        raise ConfigError(
            f"{results} was written with config {old[0]}, but the config now hashes to {current}; "
            f"restore config.yaml, or start a new run (remove run_id and move results.jsonl away)")


def _acquire_run_lock(remote: Remote) -> int:
    """Take `flock -n` on the remote run lock, held by a detached helper; return its pid."""
    lock = shlex.quote(RUN_LOCK)
    r = remote.run(
        f"out=$(mktemp); setsid nohup flock -n {lock} bash -c 'echo locked; exec sleep infinity' "
        f'> "$out" 2>&1 < /dev/null & pid=$!; '
        f'for i in $(seq 50); do '
        f'if grep -q locked "$out"; then rm -f "$out"; echo $pid; exit 0; fi; '
        f'if ! kill -0 $pid 2>/dev/null; then rm -f "$out"; exit 75; fi; sleep 0.1; done; exit 1',
        check=False)
    if r.returncode == 75:
        raise RunLockedError(f"another harness run holds {RUN_LOCK} on the host; wait for it "
                             f"to finish (only one run at a time)")
    try:
        if r.returncode == 0:
            return int(r.stdout.strip())
    except ValueError:
        pass
    raise InfraError(f"could not take {RUN_LOCK} (exit {r.returncode})")


def _interrupt(signum, frame):
    raise KeyboardInterrupt(f"signal {signum}")


def _install_signal_handlers() -> dict:
    """SIGTERM/SIGHUP raise KeyboardInterrupt so the cleanup `finally`s run."""
    if threading.current_thread() is not threading.main_thread():
        return {}
    return {sig: signal.signal(sig, _interrupt) for sig in (signal.SIGTERM, signal.SIGHUP)}


def _agent_procs(remote: Remote) -> list[str]:
    return remote.run(AGENT_PGREP, check=False).stdout.split()


def _strays(remote: Remote) -> list[str]:
    return remote.run(PREFLIGHT_CMD, check=False).stdout.split() + _agent_procs(remote)


def _kill_strays(remote: Remote) -> None:
    try:
        remote.run("pkill -KILL" + PREFLIGHT_CMD.removeprefix("pgrep"), check=False)
        remote.run(f"sudo -n pkill -KILL -u {AGENT_USER}", check=False)
    except RemoteError:
        pass  # host unreachable; the runtime restart / retry records it


def _oom_victim(remote: Remote, since: int) -> str | None:
    """Name of a process OOM-killed since `since` (epoch s), from the kernel log and the
    runtime unit's journal; None if there was none."""
    r = remote.run(
        f"{{ sudo -n journalctl -k --since @{since} --no-pager; "
        f"{JOURNALCTL} -u {UNIT_NAME} --since @{since} --no-pager; }} 2>/dev/null "
        f"| grep -iE {shlex.quote(OOM_PATTERN)} || true", timeout=60, check=False)
    text = r.stdout.strip()
    if not text:
        return None
    m = (re.search(r"Killed process \d+ \(([^)]+)\)", text)
         or re.search(r"task=([^,\s]+)", text))
    return m.group(1) if m else text.splitlines()[0][:120]


def _check_oom(remote: Remote, since: int, phase: str) -> None:
    victim = _oom_victim(remote, since)
    if victim:
        raise InfraError(f"OOM kill during {phase}: {victim}")


def _quiet(remote: Remote, cmd: str) -> None:
    """Best-effort cleanup step: report, never raise."""
    try:
        r = remote.run(cmd, check=False)
        if r.returncode:
            print(f"warning: `{cmd}` exited {r.returncode}", file=sys.stderr)
    except RemoteError as e:
        print(f"warning: `{cmd}` failed: {_short_error(e)}", file=sys.stderr)


def _restore_system_ollama(remote: Remote, clock, attempts: int = 3) -> None:
    """Start the owner's Ollama again; retry, and warn loudly (never raise) if it won't start."""
    detail = ""
    for i in range(attempts):
        if i:
            clock.sleep(2)
        try:
            r = remote.run(SYSTEM_OLLAMA_START, check=False)
            if r.returncode == 0:
                return
            detail = f"exit {r.returncode}"
        except Exception as e:  # noqa: BLE001
            detail = _short_error(e)
    print(f"system Ollama NOT restarted ({detail}) - run: sudo systemctl start ollama",
          file=sys.stderr)


# Attempt roots left open (0711) by an interrupted run, and run folders from before the
# agent user existed: close them so the agent user cannot read earlier attempts.
CLOSE_OLD_ATTEMPTS = (
    f"find {ROOT}/runs -mindepth 1 -maxdepth 1 -type d -exec chmod 711 {{}} + && "
    f"find {ROOT}/runs -mindepth 2 -maxdepth 2 -type d -perm /077 -exec chmod 700 {{}} +")


def preflight(remote: Remote, runtime: Runtime) -> None:
    """Fail unless nothing else is running and only the model under test is loaded."""
    stray = _strays(remote)
    if stray:
        raise InfraError(f"stray processes on host: {' '.join(stray)}")
    loaded = runtime.loaded_models(remote)
    if loaded != [runtime.model]:
        raise InfraError(f"loaded models {loaded}, expected [{runtime.model!r}]")


def harness_version() -> str:
    """Short HEAD sha, with `-dirty` when the harness code has uncommitted changes (the
    experiments' own results and READMEs change during a run and are not counted)."""
    repo = Path(__file__).resolve().parent.parent
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, cwd=repo, check=True).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain", "--", "harness", "pyproject.toml",
                                 "uv.lock"], capture_output=True, text=True, cwd=repo,
                                check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return f"{sha}-dirty" if status.strip() else sha


def _short_error(e: BaseException) -> str:
    lines = str(e).strip().splitlines()
    return f"{type(e).__name__}: {lines[0][:200] if lines else ''}".rstrip(": ")


def _start_helper(remote: Remote, cmd: str, log: str) -> int:
    r = remote.run(f"setsid nohup {cmd} > {shlex.quote(log)} 2>&1 < /dev/null & echo $!")
    try:
        return int(r.stdout.strip())
    except ValueError:
        raise InfraError(f"could not start helper: {cmd}") from None


def _stop_helper(remote: Remote, pid: int) -> None:
    try:
        remote.run(f"kill -TERM -- -{pid}", check=False)
    except RemoteError:
        pass  # host gone; preflight of the next attempt catches survivors


def _fetch(remote: Remote, path: str | None, local: Path) -> str | None:
    """Copy a remote file to `local`; return the local path, or None if it can't be read."""
    if not path:
        return None
    try:
        local.write_text(remote.read_text(path))
    except subprocess.CalledProcessError:
        return None
    return str(local)


def _read_optional(remote: Remote, path: str) -> str:
    try:
        return remote.read_text(path)
    except subprocess.CalledProcessError:
        return ""


def _fetch_score(remote: Remote, paths: AttemptPaths, local: Path):
    """Fetch score.json and the files it names, rewrite paths to local copies, load it."""
    try:
        data = json.loads(remote.read_text(f"{paths.score_dir}/score.json"))
    except json.JSONDecodeError as e:
        raise InfraError(f"bad score.json: {e}") from e
    for key in ("import_log", "regression_log", "hidden_log", "hidden_xml", "regression_xml"):
        data[key] = _fetch(remote, data.get(key), local / f"{key}.txt")
    score_json = local / "score.json"
    score_json.write_text(json.dumps(data))
    return load_score(str(score_json))


def _record(cfg: ExperimentConfig, run_id: str, task: str, repeat: int, branch: str,
            started_at: str, **fields) -> AttemptRecord:
    base = dict(
        status="infra_error", hidden_passed=0, hidden_total=0, regressions_ok=False,
        parse_ok=False, wall_s=0.0, prompt_tokens=None, gen_tokens=None, pp_tps=None,
        tg_tps=None, peak_mem_mib=None, peak_gpu_mem_mib=None, steps=None, throttled=False,
        upstream_errors=0, pushed=False, versions={}, error="")
    base.update(fields)
    return AttemptRecord(experiment=cfg.id, run_id=run_id, task=task, repeat=repeat,
                         branch=branch, started_at=started_at, **base)


def run_attempt(cfg: ExperimentConfig, run_id: str, task: str, repeat: int, *, remote: Remote,
                runtime: Runtime, agent: Agent, bench: BenchRepo, scripts_dir: str = SCRIPTS_DIR,
                harness_sha: str | None = None, scripts_sha: str | None = None,
                try_n: int = 1, clock=time) -> AttemptRecord:
    """Run one attempt end to end. Infrastructure failures become an infra_error record.

    Each try has its own branch (`-t2` for the retry), so a pushed infra_error try never
    hides the retry's evidence."""
    paths = attempt_paths(run_id, task, repeat)
    branch = f"exp/{run_id}/{task}-r{repeat}" + (f"-t{try_n}" if try_n > 1 else "")
    since = int(clock.time())
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(since))
    # Pinned on every record, infra_error included; runtime fields are added when available.
    versions: dict[str, str] = {
        "agent": f"{cfg.agent.name} {cfg.agent.version}".strip(),
        "harness": harness_sha if harness_sha is not None else harness_version(),
        "task_set": cfg.task_set,
        "sampling": json.dumps(cfg.sampling, sort_keys=True),
        "config": config_hash(cfg),
    }
    if scripts_sha is not None:
        versions["remote_scripts"] = scripts_sha
    result: AgentResult | None = None
    try:
        preflight(remote, runtime)
        versions = {**runtime.versions(remote), **versions}
        bench.prepare_workdir(paths, cfg.task_set, task, branch)
        try:
            scripts = shlex.quote(scripts_dir)
            pids: list[int] = []
            try:
                pids.append(_start_helper(
                    remote, f"python3 {scripts}/usage_proxy.py --listen {PROXY_LISTEN} "
                            f"--upstream {shlex.quote(runtime.upstream)} "
                            f"--log {shlex.quote(paths.usage_log)}",
                    f"{paths.root}/usage_proxy.log"))
                pids.append(_start_helper(
                    remote, f"bash {scripts}/sample.sh {shlex.quote(paths.samples_csv)} "
                            f"{SAMPLE_INTERVAL_S}",
                    f"{paths.root}/sample.log"))
                # TCP connect only: an HTTP probe would add a row to usage.jsonl.
                host, port = PROXY_LISTEN.split(":")
                probe = shlex.quote(f"</dev/tcp/{host}/{port}")
                ready = remote.run(f"for i in $(seq 50); do bash -c {probe} 2>/dev/null "
                                   f"&& exit 0; sleep 0.1; done; exit 1", check=False)
                if ready.returncode != 0:
                    raise InfraError("usage proxy did not start listening")
                result = agent.run(remote, paths, ENDPOINT, runtime.model, cfg.timeout_s)
            finally:
                if pids:
                    clock.sleep(PROXY_FLUSH_S)
                for pid in pids:
                    _stop_helper(remote, pid)

            _check_oom(remote, since, "agent run")
            pushed = bench.commit_and_push(paths, branch, f"{run_id} {task} r{repeat}")
            # Hidden tests, solution and scorer appear only now, in a 0700 folder the agent never
            # saw, and only once nothing runs as the agent user.
            survivors = _agent_procs(remote)
            if survivors:
                raise InfraError(
                    f"{AGENT_USER} processes survived the agent: {' '.join(survivors)}")
            try:
                remote.run(f"mkdir -p -m 700 {shlex.quote(paths.score_dir)}")
                bench.export_task_files(cfg.task_set, task, paths.task_files)
                remote.run(" ".join(shlex.quote(a) for a in (
                    "bash", f"{scripts_dir}/score.sh", paths.workdir, paths.task_files,
                    bench.base_sha(cfg.task_set), bench.mirror, paths.score_dir, GODOT_BIN)),
                    timeout=SCORE_TIMEOUT_S)
                with tempfile.TemporaryDirectory() as tmp:
                    parse_ok, hidden, regression, regression_expected = _fetch_score(
                        remote, paths, Path(tmp))
            finally:
                # Keep logs, XML and score.json; drop the hidden material and the scored copy.
                _quiet(remote, f"rm -rf {shlex.quote(paths.task_files)} "
                               f"{shlex.quote(paths.score_dir + '/project')}")
            _check_oom(remote, since, "scoring")
        finally:
            _quiet(remote, f"chmod 700 {shlex.quote(paths.root)}")  # closed to later agents
        usage = summarize_usage(_read_optional(remote, paths.usage_log))
        samples = summarize_samples(_read_optional(remote, paths.samples_csv))
    except (InfraError, *INFRA_EXCEPTIONS) as e:
        return _record(cfg, run_id, task, repeat, branch, started_at, versions=versions,
                       wall_s=result.wall_s if result else 0.0, error=_short_error(e))

    status = decide_status(parse_ok=parse_ok, hidden=hidden, regression=regression,
                           regression_expected=regression_expected,
                           agent_timed_out=result.timed_out)
    error = ""
    if usage.upstream_errors > 0 and status != "pass":
        status = "infra_error"
        error = f"{usage.upstream_errors} upstream error(s) from the runtime"
    return _record(
        cfg, run_id, task, repeat, branch, started_at,
        status=status,
        hidden_passed=hidden.passed if hidden else 0,
        hidden_total=hidden.total if hidden else 0,
        regressions_ok=regression is not None and regression.failed + regression.errors == 0
        and regression.total > 0
        and (regression_expected is None or regression.total == regression_expected),
        parse_ok=parse_ok, wall_s=result.wall_s,
        prompt_tokens=usage.prompt_tokens, gen_tokens=usage.gen_tokens,
        pp_tps=usage.pp_tps, tg_tps=usage.tg_tps,
        peak_mem_mib=samples.peak_mem_mib, peak_gpu_mem_mib=samples.peak_gpu_mem_mib,
        steps=result.steps, throttled=samples.throttled, upstream_errors=usage.upstream_errors,
        pushed=pushed, versions=versions, error=error)


def _run_id(cfg: ExperimentConfig, exp_dir: Path, clock) -> str:
    f = exp_dir / "run_id"
    if f.exists() and f.read_text().strip():
        return check_safe_id(f.read_text().strip(), f"run_id ({f})")
    run_id = f"{cfg.id}-{time.strftime('%Y%m%d%H%M%S', time.localtime(clock.time()))}"
    f.write_text(run_id + "\n")
    return run_id


def run_experiment(cfg: ExperimentConfig, exp_dir: Path, *, remote: Remote, bench: BenchRepo,
                   clock=time, runtime: Runtime | None = None, agent: Agent | None = None,
                   harness_sha: str | None = None, scripts_dir: str = SCRIPTS_DIR) -> None:
    """Run (or resume) every pending attempt of the config's tier, appending to results.jsonl."""
    exp_dir = Path(exp_dir)
    exp_dir.mkdir(parents=True, exist_ok=True)
    results = exp_dir / "results.jsonl"
    runtime = runtime or make_runtime(cfg.runtime)
    agent = agent or make_agent(cfg.agent, task_set=cfg.task_set, mirror=bench.mirror)
    sha = harness_sha if harness_sha is not None else harness_version()
    run_id = _run_id(cfg, exp_dir, clock)
    records = read_records(results)
    _check_config_unchanged(results, records, config_hash(cfg))
    todo = pending(tier_plan(cfg), records)

    lock_pid = _acquire_run_lock(remote)
    handlers = _install_signal_handlers()
    try:
        # The records name the scripts that score them: sync them now, and pin their hash.
        sync_scripts(remote)
        scripts_sha = scripts_hash()
        bench.update()
        remote.run(f"mkdir -p {ROOT}/runs && {CLOSE_OLD_ATTEMPTS}")
        _run_loop(cfg, results, run_id, todo, remote=remote, runtime=runtime, agent=agent,
                  bench=bench, scripts_dir=scripts_dir, sha=sha, scripts_sha=scripts_sha,
                  clock=clock)
    finally:
        for sig, old in handlers.items():
            signal.signal(sig, old)
        _stop_helper(remote, lock_pid)


def _run_loop(cfg: ExperimentConfig, results: Path, run_id: str, todo: list[tuple[str, int]], *,
              remote: Remote, runtime: Runtime, agent: Agent, bench: BenchRepo, scripts_dir: str,
              sha: str, scripts_sha: str, clock) -> None:
    # The owner's system Ollama owns the GPU and port 11434: stop it for the run, and bring it
    # back afterwards (only if it was running) whatever happens. The stop sits inside the try
    # so a half-failed stop is still followed by a start.
    was_active = False
    try:
        was_active = remote.run(SYSTEM_OLLAMA_ACTIVE, check=False).stdout.strip() == "active"
        remote.run(SYSTEM_OLLAMA_STOP)
        runtime.start(remote)
        for i, (task, repeat) in enumerate(todo):
            if i and cfg.cooldown_s > 0:
                clock.sleep(cfg.cooldown_s)
            infra_count = sum(1 for r in read_records(results)
                              if (r.task, r.repeat) == (task, repeat) and r.status == "infra_error")
            while True:
                rec = run_attempt(cfg, run_id, task, repeat, remote=remote, runtime=runtime,
                                  agent=agent, bench=bench, scripts_dir=scripts_dir,
                                  harness_sha=sha, scripts_sha=scripts_sha,
                                  try_n=infra_count + 1, clock=clock)
                append_record(results, rec)
                if rec.status != "infra_error":
                    break
                infra_count += 1
                # Clear survivors and restart the runtime so the next attempt starts clean.
                _kill_strays(remote)
                try:
                    runtime.start(remote)
                except (InfraError, *INFRA_EXCEPTIONS) as e:
                    # Host or network down: recording the untried retry would mark it done
                    # and burn the rest of the plan. Stop; a resume reruns it.
                    raise RuntimeRestartError(
                        f"runtime restart failed after an infra_error on {task} r{repeat}: "
                        f"{_short_error(e)}") from e
                if infra_count >= 2:
                    break
                # A host the kill could not clean would fail every remaining attempt (and mark
                # them done): stop so a later resume reruns them.
                try:
                    stray = _strays(remote)
                except RemoteError:
                    stray = []  # the retry itself records the unreachable host
                if stray:
                    raise HostDirtyError(
                        f"stray processes survived pkill before retrying {task} r{repeat}: "
                        f"{' '.join(stray)}")
    finally:
        # Neither cleanup step may raise: that would mask the error that got us here.
        try:
            runtime.stop(remote)
        except Exception as e:  # noqa: BLE001
            print(f"warning: runtime stop failed: {_short_error(e)}", file=sys.stderr)
        if was_active:
            _restore_system_ollama(remote, clock)
