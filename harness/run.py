from __future__ import annotations

import json
import shlex
import subprocess
import tempfile
import time
from pathlib import Path

from harness.agents import make_agent
from harness.agents.base import Agent, AgentResult
from harness.bench import BenchRepo
from harness.config import ExperimentConfig
from harness.paths import ROOT, AttemptPaths, attempt_paths
from harness.remote import Remote, RemoteError
from harness.results import AttemptRecord, append_record, pending, read_records
from harness.runtimes import make_runtime
from harness.runtimes.base import Runtime
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
SCORE_TIMEOUT_S = 2400  # score.sh: import 300 + two GUT suites 600 each + extra 600, plus slack
# Bracket trick: the pattern does not match the shell running pgrep itself.
PREFLIGHT_CMD = "pgrep -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'"
# Exceptions that make an attempt infra_error instead of aborting the experiment.
INFRA_EXCEPTIONS = (RemoteError, subprocess.CalledProcessError)


class InfraError(Exception):
    """Host not in the expected state (maps to infra_error)."""


def preflight(remote: Remote, runtime: Runtime) -> None:
    """Fail unless nothing else is running and only the model under test is loaded."""
    stray = remote.run(PREFLIGHT_CMD, check=False).stdout.split()
    if stray:
        raise InfraError(f"stray processes on host: {' '.join(stray)}")
    loaded = runtime.loaded_models(remote)
    if loaded != [runtime.model]:
        raise InfraError(f"loaded models {loaded}, expected [{runtime.model!r}]")


def harness_version() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parent.parent, check=True)
        return r.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


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
    for key in ("import_log", "hidden_xml", "regression_xml"):
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
                harness_sha: str | None = None, clock=time) -> AttemptRecord:
    """Run one attempt end to end. Infrastructure failures become an infra_error record."""
    paths = attempt_paths(run_id, task, repeat)
    branch = f"exp/{run_id}/{task}-r{repeat}"
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(clock.time()))
    versions: dict[str, str] = {}
    result: AgentResult | None = None
    try:
        preflight(remote, runtime)
        versions = {
            **runtime.versions(remote),
            "agent": f"{cfg.agent.name} {cfg.agent.version}".strip(),
            "harness": harness_sha if harness_sha is not None else harness_version(),
            "task_set": cfg.task_set,
            "sampling": json.dumps(cfg.sampling, sort_keys=True),
        }
        bench.prepare_workdir(paths, cfg.task_set, task, branch)
        bench.export_task_files(cfg.task_set, task, paths.task_files)

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
            ready = remote.run(f"for i in $(seq 50); do curl -s -o /dev/null {ENDPOINT}/ "
                               f"&& exit 0; sleep 0.1; done; exit 1", check=False)
            if ready.returncode != 0:
                raise InfraError("usage proxy did not start listening")
            result = agent.run(remote, paths, ENDPOINT, runtime.model, cfg.timeout_s)
        finally:
            if pids:
                clock.sleep(PROXY_FLUSH_S)
            for pid in pids:
                _stop_helper(remote, pid)

        pushed = bench.commit_and_push(paths, branch, f"{run_id} {task} r{repeat}")
        remote.run(" ".join(shlex.quote(a) for a in (
            "bash", f"{scripts_dir}/score.sh", paths.workdir, paths.task_files,
            bench.base_sha(cfg.task_set), bench.mirror, paths.score_dir, GODOT_BIN)),
            timeout=SCORE_TIMEOUT_S)
        with tempfile.TemporaryDirectory() as tmp:
            parse_ok, hidden, regression = _fetch_score(remote, paths, Path(tmp))
        usage = summarize_usage(_read_optional(remote, paths.usage_log))
        samples = summarize_samples(_read_optional(remote, paths.samples_csv))
    except (InfraError, *INFRA_EXCEPTIONS) as e:
        return _record(cfg, run_id, task, repeat, branch, started_at, versions=versions,
                       wall_s=result.wall_s if result else 0.0, error=_short_error(e))

    status = decide_status(parse_ok=parse_ok, hidden=hidden, regression=regression,
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
        and regression.total > 0,
        parse_ok=parse_ok, wall_s=result.wall_s,
        prompt_tokens=usage.prompt_tokens, gen_tokens=usage.gen_tokens,
        pp_tps=usage.pp_tps, tg_tps=usage.tg_tps,
        peak_mem_mib=samples.peak_mem_mib, peak_gpu_mem_mib=samples.peak_gpu_mem_mib,
        steps=result.steps, throttled=samples.throttled, upstream_errors=usage.upstream_errors,
        pushed=pushed, versions=versions, error=error)


def _run_id(cfg: ExperimentConfig, exp_dir: Path, clock) -> str:
    f = exp_dir / "run_id"
    if f.exists() and f.read_text().strip():
        return f.read_text().strip()
    run_id = f"{cfg.id}-{time.strftime('%Y%m%d%H%M', time.localtime(clock.time()))}"
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
    agent = agent or make_agent(cfg.agent)
    sha = harness_sha if harness_sha is not None else harness_version()
    run_id = _run_id(cfg, exp_dir, clock)
    todo = pending(tier_plan(cfg), read_records(results))

    bench.update()
    runtime.start(remote)
    try:
        for i, (task, repeat) in enumerate(todo):
            if i and cfg.cooldown_s > 0:
                clock.sleep(cfg.cooldown_s)
            infra_count = sum(1 for r in read_records(results)
                              if (r.task, r.repeat) == (task, repeat) and r.status == "infra_error")
            while True:
                rec = run_attempt(cfg, run_id, task, repeat, remote=remote, runtime=runtime,
                                  agent=agent, bench=bench, scripts_dir=scripts_dir,
                                  harness_sha=sha, clock=clock)
                append_record(results, rec)
                if rec.status != "infra_error":
                    break
                infra_count += 1
                # Restart the runtime after any infra_error so the next attempt starts clean.
                try:
                    runtime.start(remote)
                except (InfraError, *INFRA_EXCEPTIONS) as e:
                    if infra_count < 2:
                        append_record(results, _record(
                            cfg, run_id, task, repeat, f"exp/{run_id}/{task}-r{repeat}",
                            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(clock.time())),
                            versions=rec.versions,
                            error=f"runtime restart failed: {_short_error(e)}"))
                    break
                if infra_count >= 2:
                    break
    finally:
        runtime.stop(remote)
