from __future__ import annotations

import json
import subprocess
from dataclasses import replace

import pytest

from conftest import FakeRemote
from harness.agents.base import AgentResult
from harness.config import AgentConfig, ExperimentConfig, RuntimeConfig
from harness.paths import ROOT
from harness.remote import RemoteError
from harness.results import append_record, read_records
from harness.run import HostDirtyError, InfraError, preflight, run_attempt, run_experiment
from harness.tiers import TASK_SETS

SCREENING = TASK_SETS["v1"]["screening"]
PASS_XML = '<testsuites><testsuite><testcase name="a"/><testcase name="b"/></testsuite></testsuites>'
FAIL_XML = '<testsuites><testsuite><testcase name="a"/><testcase name="b"><failure/></testcase></testsuite></testsuites>'
OK = AgentResult(exit_code=0, timed_out=False, wall_s=600.0, steps=4)

CFG = ExperimentConfig(
    id="e0", task_set="v1", tier="screening",
    runtime=RuntimeConfig(kind="ollama", model="m:latest", context=8192),
    agent=AgentConfig(kind="command", name="aider", command="x", version="0.9"),
    timeout_s=100, cooldown_s=7, sampling={"temperature": 0.2})


class BenchRemote(FakeRemote):
    """FakeRemote that serves score.sh output for any attempt."""

    def __init__(self, hidden=PASS_XML, usage=""):
        super().__init__()
        self.hidden = hidden
        self.usage = usage
        self.reply("usage_proxy.py", stdout="111\n")
        self.reply("sample.sh", stdout="222\n")

    def read_text(self, path):
        d = path.rsplit("/", 1)[0]
        if path.endswith("/score/score.json"):
            return json.dumps({"import_log": f"{d}/import.log", "import_timed_out": False,
                               "regression_xml": f"{d}/regression.xml", "regression_timed_out": False,
                               "hidden_xml": f"{d}/hidden.xml", "hidden_timed_out": False,
                               "extra_exit": None, "extra_timed_out": False})
        if path.endswith("/hidden.xml"):
            return self.hidden
        if path.endswith("/regression.xml"):
            return PASS_XML
        if path.endswith("/usage.jsonl"):
            return self.usage
        if path.endswith("/samples.csv"):
            return "ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c\n1,1000,200,300,80.0\n"
        return ""


class FakeRuntime:
    upstream = "http://127.0.0.1:11434"
    model = "m:latest"

    def __init__(self):
        self.loaded = ["m:latest"]
        self.starts = self.stops = 0
        self.start_error: Exception | None = None

    def start(self, remote):
        self.starts += 1
        if self.start_error and self.starts > 1:
            raise self.start_error

    def stop(self, remote):
        self.stops += 1

    def versions(self, remote):
        return {"runtime": "ollama 0.34.4", "model_digest": "sha256:d"}

    def loaded_models(self, remote):
        return list(self.loaded)


class FakeAgent:
    def __init__(self, *script):
        self.script = list(script)  # AgentResult or Exception per call; then OK
        self.calls: list[str] = []

    def run(self, remote, paths, endpoint, model, timeout_s):
        self.calls.append(paths.root)
        assert endpoint == "http://127.0.0.1:11500" and model == "m:latest" and timeout_s == 100
        step = self.script.pop(0) if self.script else OK
        if isinstance(step, Exception):
            raise step
        return step


class FakeBench:
    mirror = "/m.git"

    def __init__(self, push_ok=True):
        self.push_ok = push_ok
        self.updates = 0
        self.prepared: list[tuple[str, str]] = []
        self.prepare_error: Exception | None = None

    def update(self):
        self.updates += 1

    def base_sha(self, task_set):
        return "abc123"

    def prepare_workdir(self, paths, task_set, task, branch):
        if self.prepare_error:
            err, self.prepare_error = self.prepare_error, None
            raise err
        self.prepared.append((task, branch))

    def export_task_files(self, task_set, task, dest):
        pass

    def commit_and_push(self, paths, branch, message):
        return self.push_ok


class FakeClock:
    def __init__(self):
        self.t = 1_800_000_000.0
        self.sleeps: list[float] = []

    def time(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def attempt(remote, runtime=None, agent=None, bench=None, cfg=CFG):
    return run_attempt(cfg, "e0-202610311200", "001-health-clamp", 1, remote=remote,
                       runtime=runtime or FakeRuntime(), agent=agent or FakeAgent(),
                       bench=bench or FakeBench(), scripts_dir=f"{ROOT}/bin",
                       harness_sha="deadbee", clock=FakeClock())


def experiment(tmp_path, remote, agent, runtime=None, bench=None, cfg=CFG, clock=None):
    runtime = runtime or FakeRuntime()
    clock = clock or FakeClock()
    run_experiment(cfg, tmp_path, remote=remote, bench=bench or FakeBench(), clock=clock,
                   runtime=runtime, agent=agent, harness_sha="deadbee")
    return read_records(tmp_path / "results.jsonl"), runtime, clock


def test_pass_record_fields():
    remote = BenchRemote()
    rec = attempt(remote)
    assert rec.status == "pass" and rec.error == ""
    assert (rec.hidden_passed, rec.hidden_total) == (2, 2)
    assert rec.regressions_ok and rec.parse_ok and rec.pushed
    assert rec.branch == "exp/e0-202610311200/001-health-clamp-r1"
    assert rec.wall_s == 600.0 and rec.steps == 4
    assert rec.peak_mem_mib == 1000 and rec.peak_gpu_mem_mib == 500 and not rec.throttled
    assert rec.versions == {"runtime": "ollama 0.34.4", "model_digest": "sha256:d",
                            "agent": "aider 0.9", "harness": "deadbee", "task_set": "v1",
                            "sampling": '{"temperature": 0.2}'}
    assert rec.started_at == "2027-01-15T08:00:00Z"
    # helpers started detached, stopped by process group, score.sh run with the godot binary
    proxy = next(c for c in remote.calls if "usage_proxy.py" in c)
    assert proxy.startswith("setsid nohup ") and "--listen 127.0.0.1:11500" in proxy
    assert "--upstream http://127.0.0.1:11434" in proxy and proxy.endswith("& echo $!")
    assert any("sample.sh" in c and "samples.csv 5" in c for c in remote.calls)
    assert "kill -TERM -- -111" in remote.calls and "kill -TERM -- -222" in remote.calls
    score = next(c for c in remote.calls if "score.sh" in c)
    assert f"{ROOT}/opt/godot/godot" in score and "abc123" in score and "/m.git" in score


def test_upstream_error_becomes_infra_error():
    usage = json.dumps({"path": "/v1/chat", "upstream_error": True}) + "\n"
    rec = attempt(BenchRemote(hidden=FAIL_XML, usage=usage))
    assert rec.status == "infra_error" and rec.upstream_errors == 1 and "upstream" in rec.error


def test_upstream_error_on_pass_stays_pass():
    usage = json.dumps({"path": "/v1/chat", "upstream_error": True}) + "\n"
    assert attempt(BenchRemote(usage=usage)).status == "pass"


def test_preflight_dirty_host_is_infra_error():
    remote = BenchRemote()
    remote.replies.insert(0, ("pgrep", subprocess.CompletedProcess([], 0, "4242\n", "")))
    agent = FakeAgent()
    rec = attempt(remote, agent=agent)
    assert rec.status == "infra_error" and agent.calls == []
    pgrep = next(c for c in remote.calls if "pgrep" in c)
    assert pgrep == "pgrep -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'"


def test_preflight_wrong_loaded_models():
    rt = FakeRuntime()
    rt.loaded = ["m:latest", "other:7b"]
    with pytest.raises(InfraError):
        preflight(FakeRemote(), rt)


def test_score_failure_is_infra_error():
    remote = BenchRemote()
    remote.replies.insert(0, ("score.sh", subprocess.CompletedProcess([], 3, "", "no godot")))

    def run(cmd, timeout=None, check=True):  # emulate Remote's check=True
        r = FakeRemote.run(remote, cmd, timeout, check)
        if check and r.returncode:
            raise subprocess.CalledProcessError(r.returncode, cmd)
        return r
    remote.run = run
    rec = attempt(remote)
    assert rec.status == "infra_error" and "CalledProcessError" in rec.error


def test_agent_error_still_stops_helpers():
    remote = BenchRemote()
    rec = attempt(remote, agent=FakeAgent(RemoteError("ssh dropped")))
    assert rec.status == "infra_error" and "ssh dropped" in rec.error
    assert "kill -TERM -- -111" in remote.calls and "kill -TERM -- -222" in remote.calls


def test_timeout_status():
    rec = attempt(BenchRemote(), agent=FakeAgent(AgentResult(124, True, 100.0)))
    assert rec.status == "timeout"


def test_infra_error_retried_once_then_moves_on(tmp_path):
    agent = FakeAgent(RemoteError("drop 1"), RemoteError("drop 2"))
    recs, rt, _ = experiment(tmp_path, BenchRemote(), agent)
    first = [r for r in recs if r.task == SCREENING[0]]
    assert [r.status for r in first] == ["infra_error", "infra_error"]
    assert [r.task for r in recs[2:]] == SCREENING[1:]
    assert all(r.status == "pass" for r in recs[2:])
    assert rt.starts == 3 and rt.stops == 1  # initial + one restart per infra_error


def test_retry_after_infra_can_pass(tmp_path):
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(RemoteError("drop")))
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]
    assert len(recs) == len(SCREENING) + 1


def test_failed_restart_recorded_and_loop_continues(tmp_path):
    rt = FakeRuntime()
    rt.start_error = RemoteError("ollama dead")
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(RemoteError("drop")), runtime=rt)
    assert [r.status for r in recs[:2]] == ["infra_error", "infra_error"]
    assert "ollama dead" in recs[1].error
    assert len(recs) == len(SCREENING) + 1


def test_bench_error_is_infra_not_fatal(tmp_path):
    bench = FakeBench()
    bench.prepare_error = subprocess.CalledProcessError(128, "git clone")
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), bench=bench)
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]


def test_system_ollama_stopped_before_runtime_and_started_after(tmp_path):
    remote = BenchRemote()
    experiment(tmp_path, remote, FakeAgent())
    assert remote.calls[0] == "sudo -n systemctl stop ollama"
    assert remote.calls[-1] == "sudo -n systemctl start ollama"
    assert remote.calls.count("sudo -n systemctl start ollama") == 1


def test_system_ollama_restored_on_error(tmp_path):
    remote = BenchRemote()
    with pytest.raises(ValueError):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")))
    assert remote.calls[-1] == "sudo -n systemctl start ollama"


def test_system_ollama_restored_on_host_dirty(tmp_path):
    remote = StrayRemote(persistent=True)
    with pytest.raises(HostDirtyError):
        experiment(tmp_path, remote, FakeAgent())
    assert remote.calls[-1] == "sudo -n systemctl start ollama"


def test_system_ollama_restored_when_runtime_start_fails(tmp_path):
    class Boom(FakeRuntime):
        def start(self, remote):
            raise RemoteError("no")
    remote = BenchRemote()
    with pytest.raises(RemoteError):
        experiment(tmp_path, remote, FakeAgent(), runtime=Boom())
    assert remote.calls[-1] == "sudo -n systemctl start ollama"


class StartFlaky(BenchRemote):
    def __init__(self, fail_times, error=None):
        super().__init__()
        self.fail_times, self.error, self.start_calls = fail_times, error, 0

    def run(self, cmd, timeout=None, check=True):
        if cmd == "sudo -n systemctl start ollama":
            self.start_calls += 1
            if self.start_calls <= self.fail_times:
                if self.error:
                    raise self.error
                return subprocess.CompletedProcess([], 1, "", "")
        return super().run(cmd, timeout, check)


def test_system_ollama_start_retried_until_ok(tmp_path, capsys):
    remote = StartFlaky(2, RemoteError("ssh 255"))
    experiment(tmp_path, remote, FakeAgent())
    assert remote.start_calls == 3 and "NOT restarted" not in capsys.readouterr().err


def test_system_ollama_start_nonzero_exit_retried(tmp_path, capsys):
    remote = StartFlaky(1)
    experiment(tmp_path, remote, FakeAgent())
    assert remote.start_calls == 2 and "NOT restarted" not in capsys.readouterr().err


def test_system_ollama_start_always_fails_warns_without_raising(tmp_path, capsys):
    remote = StartFlaky(99, RemoteError("ssh 255"))
    recs, _, _ = experiment(tmp_path, remote, FakeAgent())  # normal run completes
    assert len(recs) == len(SCREENING) and remote.start_calls == 3
    assert "system Ollama NOT restarted" in capsys.readouterr().err


def test_start_failure_does_not_mask_original_error(tmp_path, capsys):
    remote = StartFlaky(99, RemoteError("ssh 255"))
    with pytest.raises(ValueError, match="agent bug"):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")))
    assert "system Ollama NOT restarted" in capsys.readouterr().err


def test_runtime_stop_failure_does_not_mask_original_error(tmp_path, capsys):
    class BadStop(FakeRuntime):
        def stop(self, remote):
            raise RemoteError("stop failed")
    remote = BenchRemote()
    with pytest.raises(ValueError, match="agent bug"):
        experiment(tmp_path, remote, FakeAgent(ValueError("agent bug")), runtime=BadStop())
    assert "runtime stop failed" in capsys.readouterr().err
    assert remote.calls[-1] == "sudo -n systemctl start ollama"


def test_resume_skips_done(tmp_path):
    (tmp_path / "run_id").write_text("e0-202601010000\n")
    seed = attempt(BenchRemote())
    append_record(tmp_path / "results.jsonl", replace(seed, task=SCREENING[0], run_id="e0-202601010000"))
    agent = FakeAgent()
    bench = FakeBench()
    recs, _, _ = experiment(tmp_path, BenchRemote(), agent, bench=bench)
    assert len(agent.calls) == len(SCREENING) - 1
    assert [t for t, _ in bench.prepared] == SCREENING[1:]
    assert all(r.run_id == "e0-202601010000" for r in recs)
    assert bench.prepared[0][1] == f"exp/e0-202601010000/{SCREENING[1]}-r1"


def test_run_id_created_and_persisted(tmp_path):
    clock = FakeClock()
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), clock=clock)
    run_id = (tmp_path / "run_id").read_text().strip()
    assert run_id.startswith("e0-") and len(run_id) == len("e0-YYYYmmddHHMM")
    assert all(r.run_id == run_id and r.experiment == "e0" for r in recs)


def test_cooldown_between_attempts(tmp_path):
    _, _, clock = experiment(tmp_path, BenchRemote(), FakeAgent())
    # 2 s proxy flush wait in every attempt, cooldown only between attempts
    assert clock.sleeps == [2, 7] * (len(SCREENING) - 1) + [2]


def test_push_failure_recorded_not_fatal(tmp_path):
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent(), bench=FakeBench(push_ok=False))
    assert len(recs) == len(SCREENING)
    assert all(not r.pushed and r.status == "pass" for r in recs)


class StrayRemote(BenchRemote):
    """pgrep reports a stray until pkill runs (or always, if persistent)."""

    def __init__(self, persistent=False):
        super().__init__()
        self.persistent = persistent
        self.killed = False

    def run(self, cmd, timeout=None, check=True):
        if cmd.startswith("pkill -KILL"):
            self.killed = True
        if cmd.startswith("pgrep") and (self.persistent or not self.killed):
            self.calls.append(cmd)
            return subprocess.CompletedProcess([], 0, "4242\n", "")
        return super().run(cmd, timeout, check)


def test_strays_cleared_by_pkill_then_retry_runs(tmp_path):
    remote = StrayRemote()
    agent = FakeAgent()
    recs, rt, _ = experiment(tmp_path, remote, agent)
    assert [r.status for r in recs[:2]] == ["infra_error", "pass"]
    assert len(recs) == len(SCREENING) + 1 and len(agent.calls) == len(SCREENING)
    assert "pkill -KILL -u markn -f '[g]odot|agentbench/[r]uns/|agentbench/[b]in/'" in remote.calls
    assert rt.starts == 2


def test_persistent_strays_stop_the_experiment(tmp_path):
    agent = FakeAgent()
    rt = FakeRuntime()
    with pytest.raises(HostDirtyError, match="4242"):
        experiment(tmp_path, StrayRemote(persistent=True), agent, runtime=rt)
    recs = read_records(tmp_path / "results.jsonl")
    assert [(r.task, r.status) for r in recs] == [(SCREENING[0], "infra_error")]
    assert agent.calls == [] and rt.stops == 1
    # resume reruns the interrupted attempt
    recs, _, _ = experiment(tmp_path, BenchRemote(), FakeAgent())
    assert [r.status for r in recs if r.task == SCREENING[0]] == ["infra_error", "pass"]


def test_preflight_infra_record_still_pins_versions():
    remote = BenchRemote()
    remote.replies.insert(0, ("pgrep", subprocess.CompletedProcess([], 0, "4242\n", "")))
    rec = attempt(remote)
    assert rec.versions == {"agent": "aider 0.9", "harness": "deadbee", "task_set": "v1",
                            "sampling": '{"temperature": 0.2}'}


def test_proxy_probe_is_tcp_only():
    remote = BenchRemote()
    attempt(remote)
    assert any("/dev/tcp/127.0.0.1/11500" in c for c in remote.calls)
    assert not any("curl" in c for c in remote.calls)


def test_short_regression_run_fails_and_logs_are_fetched():
    class Short(BenchRemote):
        def read_text(self, path):
            if path.endswith("/score/score.json"):
                d = json.loads(super().read_text(path))
                return json.dumps({**d, "regression_expected": 3,
                                   "regression_log": path.replace("score.json", "regression.log"),
                                   "hidden_log": path.replace("score.json", "hidden.log")})
            return super().read_text(path)
    remote = Short()
    reads = []
    orig = remote.read_text
    remote.read_text = lambda p: (reads.append(p), orig(p))[1]
    rec = attempt(remote)  # regression.xml holds 2 testcases, the files define 3
    assert rec.status == "fail" and not rec.regressions_ok
    assert any(p.endswith("/score/regression.log") for p in reads)
    assert any(p.endswith("/score/hidden.log") for p in reads)
