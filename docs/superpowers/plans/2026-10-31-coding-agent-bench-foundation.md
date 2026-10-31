# Coding-agent benchmark foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build everything needed to measure coding-agent configs on geekoma9 — research shortlist, public Godot benchmark, Mac-side harness — and produce the E0 baseline result.

**Architecture:** A Python harness on the Mac drives geekoma9 over SSH. On geekoma9 it runs the runtime under test (as a systemd user unit), the agent under test in a single-branch clone of the benchmark, a stdlib-only usage proxy and a sampler for metrics, and a scoring script that runs Godot headless with hidden GUT tests. Results are appended to JSONL in this repo, and each attempt is pushed as a branch to the public benchmark repo.

**Tech Stack:** Python 3.12, uv, pytest, PyYAML (Mac). Bash, Python 3 stdlib, git, Ollama, Godot 4 headless and GUT (geekoma9).

**Spec:** `docs/superpowers/specs/2026-10-31-coding-agent-optimisation-design.md`

**Scope:** spec sub-projects 1–3 up to and including E0. E1–E5 each get a short follow-up plan written from the research shortlist and the E0 results, because their configs depend on that data.

## Global Constraints

- Orchestrator host: the Mac. Target host: `markn@geekoma9.local`. Nothing heavy runs on geekoma9 except what is under test. Its instrumentation (`usage_proxy.py`, `sample.sh`) must be stdlib-only Python or plain bash.
- Agent time budget: 45 minutes wall clock (`timeout_s = 2700`).
- Tiers: screening = 6 tasks × 1 run; finalists = 12 tasks × 3 runs; all = 12 tasks × 1 run (validation and calibration).
- Pass = parses headless with no script errors AND all hidden GUT tests pass AND regression tests on `main` still pass AND finished within the budget.
- An infrastructure failure (runtime crash, OOM, SSH drop, upstream connection error) is `infra_error`, retried once, and never counted against the model.
- A throttled attempt is flagged: any Tctl sample ≥ 95 °C.
- Branch per attempt: `exp/<run-id>/<task>-r<repeat>` in the benchmark repo, containing the agent's output unmodified.
- Agent workdirs are single-branch clones of `main` with no remote, so the agent cannot reach the hidden tests or solutions.
- Every JSONL record pins: runtime version, model digest, agent version, harness git sha, task-set version, and sampling settings.
- Owner actions are kept explicit: BIOS changes, kernel boot params, sudoers, deploy key, creating the public repo, first push, Claude login on geekoma9. Stop and ask at each one.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **The agent edits test infrastructure** (deletes or weakens `tests/regression`, or patches `addons/gut`) to get a pass. Scoring must restore both from the base commit before running. Pinned in Task 4.
2. **The agent's code hangs Godot** (an infinite loop in `_ready`). Import and test runs each have their own timeout, and a hang counts as `fail`, not `infra_error`. Pinned in Task 4.
3. **Leftover processes** (an agent child, godot, a runtime still generating) skew the next attempt. The agent runs in its own process group, which gets killed, and preflight refuses to start a dirty host. Pinned in Tasks 8 and 9.
4. **The runtime dies mid-attempt** and looks like the model failing. Proxy upstream errors turn the attempt into `infra_error`. Pinned in Tasks 6 and 9.
5. **An interrupted run leaves a truncated last JSONL line.** The reader skips it and resume redoes that attempt. Pinned in Task 3.

---

## File structure

```
pyproject.toml                       # uv project, console script `harness`
README.md                            # what this is, how to reproduce
research/{runtimes,memory,models,harnesses}.md, research/shortlist.yaml
harness/
  __init__.py
  config.py        # ExperimentConfig + load_config
  tiers.py         # task sets, tier_plan
  results.py       # AttemptRecord, JSONL store, resume
  scoring.py       # junit parsing, status decision
  sampling.py      # sampler CSV -> SampleSummary
  usage.py         # usage log -> UsageSummary
  paths.py         # AttemptPaths on geekoma9
  remote.py        # Remote (ssh/rsync)
  bench.py         # BenchRepo (mirror, workdir, push)
  runtimes/{__init__,base,ollama}.py
  agents/{__init__,base,null,oracle,command}.py
  run.py           # run_experiment, run_attempt, preflight
  report.py        # Summary, markdown
  review.py        # frontier review via `claude -p`
  cli.py           # run | validate | report | review | provision
  remote_scripts/{score.sh,sample.sh,usage_proxy.py}
tests/test_*.py
experiments/<id>/{config.yaml,run_id,results.jsonl,reviews.jsonl,README.md}
docs/FINDINGS.md
```

Benchmark repo (`~/_dev/claude/godot-agent-bench`, GitHub `YodaTheCoder/godot-agent-bench`):

```
main:  project.godot, .godot-version, addons/gut/, scripts/, scenes/, tests/regression/
       tag base-v1
tests: tasks/NNN-slug/{issue.md, tests/test_*.gd, solution.patch, score_extra.sh?}
       tag taskset-v1
```

(The spec places `issue.md` under `tasks/`. This plan keeps the whole `tasks/` tree on the `tests` branch so the agent's checkout contains only the game.)

---

### Task 1: Research and shortlist

**Files:**
- Create: `research/runtimes.md`, `research/memory.md`, `research/models.md`, `research/harnesses.md`, `research/shortlist.yaml`

**Interfaces:**
- Produces: `research/shortlist.yaml` with this exact top-level schema, used by Task 8's test and by the E0–E5 configs:

```yaml
runtimes:  [{name, why, gtt_capable: bool, gfx1150_status, sources: [url]}]
memory:    {bios_uma_options: [str], gtt_kernel_params: str, variants_to_test: [str], sources: [url]}
models:    [{name, ollama_ref: str|null, gguf_repo: str|null, quants: [str], total_params_b: float,
             active_params_b: float, est_weights_gb: float, max_context: int,
             tool_calling_evidence: str, gdscript_evidence: str, sources: [url]}]
harnesses: [{name, version, api: openai|anthropic|ollama, install: str,
             command_template: str, steps_regex: str|null, headless: bool, sources: [url]}]
e0_default_harness: <harness name>
```

`command_template` may use only `{workdir} {issue_file} {endpoint} {model} {log}`.

- [ ] **Step 1:** Read-only checks on geekoma9 to ground the research: `cat /sys/class/drm/card0/device/mem_info_{vram,gtt}_total`, `sudo dmidecode -t memory` (ask the owner if sudo prompts), the BIOS version (`cat /sys/class/dmi/id/bios_version`), and `vulkaninfo --summary` (install `vulkan-tools` only after asking). Record the results in `research/memory.md`.
- [ ] **Step 2:** Research each area. Use `anthropic-skills:deep-research` or direct searches; prefer sources from 2026. Cover:
  - **Runtimes:** Ollama vs llama.cpp Vulkan vs ROCm on gfx1150, prompt-processing speed, prefix caching.
  - **Memory:** UMA options on the A9 Max BIOS, and the GTT kernel params (`ttm.pages_limit`, `amdgpu.gttsize`) with which runtimes honour them.
  - **Models:** coding MoE ≤ ~24 GB with context, plus evidence on tool-calling and GDScript.
  - **Harnesses:** headless agents that work with local endpoints, with their tool-calling compatibility.
- [ ] **Step 3:** Write the four `.md` files, each with a sources list, and `shortlist.yaml`. The shortlist should have 2–3 runtimes, 3–4 models, 2–3 harnesses, and the `e0_default_harness` with a one-line justification in `harnesses.md`.
- [ ] **Step 4:** Verify the YAML parses and has the schema keys: `uv run --with pyyaml python -c "import yaml;d=yaml.safe_load(open('research/shortlist.yaml'));assert {'runtimes','memory','models','harnesses','e0_default_harness'}<=d.keys()"`. Expected: no output.
- [ ] **Step 5:** Commit: `git add research && git commit -m "research: runtimes, memory, models, harnesses shortlist"`

### Task 2: Harness scaffold, config and tiers

**Files:**
- Create: `pyproject.toml`, `README.md`, `.gitignore`, `harness/__init__.py`, `harness/config.py`, `harness/tiers.py`
- Test: `tests/test_config.py`, `tests/test_tiers.py`

**Interfaces:**
- Produces (`harness/config.py`):
  - `ConfigError(Exception)`
  - `RuntimeConfig(kind: Literal["ollama"], model: str, context: int, env: dict[str,str] = {})` (frozen dataclass; the llama-server kind arrives with the E2 plan)
  - `AgentConfig(kind: Literal["null","oracle","command"], name: str, command: str | None = None, version: str = "", steps_regex: str | None = None, env: dict[str,str] = {})`
  - `ExperimentConfig(id: str, task_set: str, tier: Literal["screening","finalists","all"], runtime: RuntimeConfig, agent: AgentConfig, timeout_s: int = 2700, cooldown_s: int = 120, sampling: dict[str, float] = {}, notes: str = "")`
  - `load_config(path: Path) -> ExperimentConfig`
- Produces (`harness/tiers.py`): `TASK_SETS: dict[str, dict[str, list[str]]]`, `tier_plan(cfg: ExperimentConfig) -> list[tuple[str, int]]` (task, repeat index from 1)

- [ ] **Step 1:** `uv init --package --name harness --python 3.12`, then restructure to the flat `harness/` package. Add deps `pyyaml` and dev dep `pytest`, set `[project.scripts] harness = "harness.cli:main"`, and add a `.gitignore` for `.venv/ __pycache__/ .pytest_cache/`. The README gets a short purpose statement, a pointer to the spec, and a "Reproduce" heading for Task 16 to fill in.
- [ ] **Step 2: Write failing tests**

```python
# tests/test_config.py
def test_loads_minimal_config(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("""id: e0-baseline
task_set: v1
tier: screening
runtime: {kind: ollama, model: "qwen3-coder:30b", context: 65536}
agent: {kind: command, name: opencode, command: "run {issue_file}"}
""")
    cfg = load_config(p)
    assert cfg.timeout_s == 2700 and cfg.cooldown_s == 120
    assert cfg.runtime.context == 65536 and cfg.agent.name == "opencode"

@pytest.mark.parametrize("bad", [
    "tier: nightly", "runtime: {kind: vllm, model: m, context: 1}",
    "agent: {kind: command, name: x}",            # command agent without command
])
def test_rejects_invalid(tmp_path, bad): ...   # merge `bad` over the minimal config -> raises ConfigError

# tests/test_tiers.py
def test_screening_is_six_by_one(): assert len(tier_plan(cfg(tier="screening"))) == 6
def test_finalists_is_twelve_by_three():
    plan = tier_plan(cfg(tier="finalists"))
    assert len(plan) == 36 and {r for _, r in plan} == {1, 2, 3}
def test_all_is_twelve_by_one(): assert len(tier_plan(cfg(tier="all"))) == 12
def test_unknown_task_set_raises(): with pytest.raises(ConfigError): tier_plan(cfg(task_set="v9"))
```

- [ ] **Step 3:** Run `uv run pytest tests/test_config.py tests/test_tiers.py -v`. Expected: FAIL (import errors).
- [ ] **Step 4:** Implement `load_config` (yaml.safe_load, then manual validation raising `ConfigError` with the offending key) and `tiers.py` with `TASK_SETS = {"v1": {"all": ["001-health-clamp", "002-damage-signal", "003-score-combo", "004-weapon-cooldown", "005-inventory-pickup", "006-save-load", "007-patrol-enemy", "008-hud-health", "009-event-bus", "010-wave-spawner", "011-status-effects", "012-weapon-tests"], "screening": ["001-health-clamp", "004-weapon-cooldown", "005-inventory-pickup", "007-patrol-enemy", "009-event-bus", "011-status-effects"]}}`. Screening runs `repeats = 1`, finalists `3`, all `1`; order the plan task-major, then by repeat.
- [ ] **Step 5:** Run `uv run pytest -v`. Expected: PASS.
- [ ] **Step 6:** Commit: `git commit -am "harness: scaffold, config, tiers"` (add new files first).

### Task 3: Results store with resume

**Files:**
- Create: `harness/results.py`
- Test: `tests/test_results.py`

**Interfaces:**
- Produces:
  - `Status = Literal["pass","fail","timeout","infra_error"]`
  - `AttemptRecord` (dataclass) with these fields:
    - `experiment, run_id, task: str; repeat: int; status: Status`
    - `hidden_passed, hidden_total: int; regressions_ok, parse_ok: bool`
    - `wall_s: float; prompt_tokens, gen_tokens: int|None; pp_tps, tg_tps: float|None`
    - `peak_mem_mib, peak_gpu_mem_mib: int|None; steps: int|None`
    - `throttled: bool; upstream_errors: int; pushed: bool; branch: str`
    - `versions: dict[str,str]; started_at: str; error: str = ""`
  - `append_record(path: Path, rec: AttemptRecord) -> None` writes one JSON line and flushes plus fsyncs.
  - `read_records(path: Path) -> list[AttemptRecord]`
  - `pending(plan: list[tuple[str,int]], records: list[AttemptRecord]) -> list[tuple[str,int]]`

- [ ] **Step 1: Write failing tests**

```python
def test_roundtrip(tmp_path): append twice -> read_records returns equal records in order
def test_truncated_last_line_is_skipped(tmp_path):
    append_record(p, rec("001", 1)); p.write_text(p.read_text() + '{"experiment": "e0", "ta')
    assert [r.task for r in read_records(p)] == ["001"]
def test_pending_skips_completed_and_double_infra():
    plan = [("001",1), ("002",1), ("003",1), ("004",1)]
    recs = [rec("001",1,"pass"), rec("002",1,"infra_error"),
            rec("003",1,"infra_error"), rec("003",1,"infra_error"), rec("004",1,"timeout")]
    assert pending(plan, recs) == [("002",1)]
def test_missing_file_is_empty(tmp_path): assert read_records(tmp_path / "none.jsonl") == []
```

- [ ] **Step 2:** Run `uv run pytest tests/test_results.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement. `read_records` ignores a final line that fails `json.loads`. A bad line anywhere else raises `ValueError` naming the line number. `pending` treats an attempt as done if it has a non-infra record or two infra records.
- [ ] **Step 4:** Run `uv run pytest tests/test_results.py -v`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: JSONL results store with resume"`

### Task 4: Scoring

**Files:**
- Create: `harness/scoring.py`, `harness/remote_scripts/score.sh`
- Test: `tests/test_scoring.py`, `tests/fixtures/junit_*.xml`

**Interfaces:**
- Produces (`scoring.py`):
  - `TestCounts(passed: int, failed: int, errors: int)` with property `total`
  - `parse_junit(xml: str) -> TestCounts`
  - `parse_ok_from_log(log: str) -> bool`
  - `decide_status(*, parse_ok: bool, hidden: TestCounts | None, regression: TestCounts | None, agent_timed_out: bool) -> Literal["pass","fail","timeout"]`
  - `load_score(score_json: str) -> tuple[bool, TestCounts|None, TestCounts|None]` returns (parse_ok, hidden, regression)
- Produces (`score.sh`): `score.sh <workdir> <task_files_dir> <base_sha> <bench_mirror> <out_dir> <godot_bin>`. It writes `<out_dir>/{import.log,regression.xml,hidden.xml,score.json}`. `score.json` has the keys `import_exit, import_timed_out, regression_exit, regression_timed_out, hidden_exit, hidden_timed_out` (ints and bools), plus `regression_xml`, `hidden_xml` (file paths or null) and `import_log` (path).

- [ ] **Step 1: Write failing tests**

```python
def test_parse_junit_counts(): assert parse_junit(fixture("junit_mixed.xml")) == TestCounts(3, 1, 1)
def test_parse_junit_empty_suite_is_zero(): assert parse_junit(fixture("junit_empty.xml")).total == 0
@pytest.mark.parametrize("line", ["SCRIPT ERROR: Parse Error: Expected", "Failed to load script \"res://x.gd\""])
def test_parse_errors_detected(line): assert not parse_ok_from_log("ok\n" + line)
def test_pass_requires_everything():
    ok = TestCounts(5, 0, 0)
    assert decide_status(parse_ok=True, hidden=ok, regression=ok, agent_timed_out=False) == "pass"
    assert decide_status(parse_ok=True, hidden=TestCounts(4,1,0), regression=ok, agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=True, hidden=ok, regression=TestCounts(5,0,1), agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=False, hidden=ok, regression=ok, agent_timed_out=False) == "fail"
    assert decide_status(parse_ok=True, hidden=ok, regression=ok, agent_timed_out=True) == "timeout"
def test_hang_or_missing_xml_is_fail():      # Review Focus 2
    assert decide_status(parse_ok=True, hidden=None, regression=TestCounts(5,0,0), agent_timed_out=False) == "fail"
def test_zero_hidden_tests_is_fail():
    assert decide_status(parse_ok=True, hidden=TestCounts(0,0,0), regression=TestCounts(5,0,0), agent_timed_out=False) == "fail"
def test_load_score_marks_timed_out_tests_as_none(): ...  # hidden_timed_out true -> hidden is None
```

- [ ] **Step 2:** Run `uv run pytest tests/test_scoring.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement `scoring.py` (`xml.etree`, summing `tests`/`failures`/`errors` over all `testsuite` elements; passed = tests − failures − errors). Implement `score.sh` (bash, `set -euo pipefail`):
  1. `rsync -a --delete <workdir>/ <out_dir>/project/`, excluding `.git`.
  2. **Review Focus 1:** delete `project/tests/regression` and `project/addons/gut`, then restore both from `git -C <bench_mirror> archive <base_sha> tests/regression addons/gut | tar -x -C project`.
  3. Copy `<task_files_dir>/tests/*.gd` to `project/tests/hidden/`.
  4. `timeout -k 10 300 <godot_bin> --headless --path project --import` > import.log.
  5. GUT for `res://tests/regression` and `res://tests/hidden` separately, each under `timeout -k 10 600`, with `-gexit -gjunit_xml_file=<abs xml>`.
  6. If `<task_files_dir>/score_extra.sh` exists, run it with `project`, `<godot_bin>` and `<out_dir>` as arguments. It overwrites `hidden.xml`.
  7. Write `score.json` (timeout exit 124/137 → `*_timed_out: true`).
- [ ] **Step 4:** Run `uv run pytest tests/test_scoring.py -v`. Expected: PASS. Then run `bash -n harness/remote_scripts/score.sh`. Expected: no output.
- [ ] **Step 5:** Commit: `git commit -m "harness: scoring with pristine test restore and timeouts"`

### Task 5: Sampler

**Files:**
- Create: `harness/sampling.py`, `harness/remote_scripts/sample.sh`
- Test: `tests/test_sampling.py`

**Interfaces:**
- Produces:
  - `sample.sh <out.csv> <interval_s>`: loops until killed and writes the header `ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c,edge_c,sclk_mhz,cpu_mhz_avg`. Sources: `/proc/meminfo` (MemTotal − MemAvailable), `/sys/class/drm/card0/device/mem_info_{vram,gtt}_used`, hwmon `k10temp` temp1 and `amdgpu` temp1, the active `*` line of `pp_dpm_sclk`, and the average of `/proc/cpuinfo` MHz. Missing sources are written as an empty field.
  - `SampleSummary(peak_mem_mib: int|None, peak_gpu_mem_mib: int|None, max_tctl_c: float|None, throttled: bool)`
  - `summarize_samples(csv_text: str) -> SampleSummary`. GPU memory = vram + gtt; throttled = max_tctl_c ≥ 95.0.

- [ ] **Step 1: Write failing tests.** These cover:
  - peaks across 3 rows;
  - an empty field ignored;
  - a header-only CSV → all None and `throttled=False`;
  - a 95.0 °C row → `throttled=True`, while 94.9 °C → False.
- [ ] **Step 2:** Run `uv run pytest tests/test_sampling.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement both. `sample.sh` uses only bash and coreutils/awk.
- [ ] **Step 4:** Run `uv run pytest tests/test_sampling.py -v`. Expected: PASS. Smoke-test it remotely: `scp harness/remote_scripts/sample.sh markn@geekoma9.local:/tmp/ && ssh markn@geekoma9.local 'timeout 3 bash /tmp/sample.sh /tmp/s.csv 1; cat /tmp/s.csv'`. Expected: the header plus 2–3 rows with mem, vram and tctl populated.
- [ ] **Step 5:** Commit: `git commit -m "harness: resource and thermal sampler"`

### Task 6: Usage proxy

**Files:**
- Create: `harness/remote_scripts/usage_proxy.py`, `harness/usage.py`
- Test: `tests/test_usage.py`

**Interfaces:**
- Produces (`usage_proxy.py`, stdlib only, runnable as `python3 usage_proxy.py --listen 127.0.0.1:11500 --upstream http://127.0.0.1:11434 --log <usage.jsonl>`):
  - It forwards every method, path and header and streams the response through chunk by chunk.
  - It appends one JSON line per request with: `path, status, duration_s, ttft_s, prompt_tokens, gen_tokens, upstream_error`.
  - On an upstream connection failure it returns 502 and sets `upstream_error: true`.
  - `extract_usage(body: bytes, content_type: str) -> tuple[int|None, int|None]` reads:
    - OpenAI `usage.prompt_tokens/completion_tokens`, in JSON or as the last SSE chunk carrying `usage`;
    - Anthropic `usage.input_tokens/output_tokens` from `message_start`/`message_delta` SSE events;
    - Ollama NDJSON or JSON `prompt_eval_count/eval_count`.
- Produces (`usage.py`):
  - `UsageSummary(requests: int, prompt_tokens: int|None, gen_tokens: int|None, pp_tps: float|None, tg_tps: float|None, upstream_errors: int)`
  - `summarize_usage(jsonl_text: str) -> UsageSummary`, where pp_tps = Σprompt / Σttft and tg_tps = Σgen / Σ(duration − ttft), counting only requests with known tokens.

- [ ] **Step 1: Write failing tests.** These cover:
  - `extract_usage` for the OpenAI JSON, OpenAI SSE, Anthropic SSE and Ollama NDJSON fixtures;
  - an unknown body → `(None, None)`;
  - `summarize_usage` arithmetic on 2 lines, e.g. prompt 1000 and 3000 over ttft 1 s and 3 s → `pp_tps == 1000.0`;
  - an `upstream_error` line counted;
  - a live test (`@pytest.mark.live`, skipped by default): start the proxy against a stub `http.server` upstream on localhost, POST through it, and assert one log line with status 200. Then stop the upstream, POST again, and assert 502 with `upstream_error` true (Review Focus 4).
- [ ] **Step 2:** Run `uv run pytest tests/test_usage.py -v -m "live or not live"`. Expected: FAIL.
- [ ] **Step 3:** Implement with `http.server.ThreadingHTTPServer` and `http.client`, buffering only a copy of the body for `extract_usage` after streaming it to the client. Configure `-m "not live"` as the default in `pyproject.toml` `[tool.pytest.ini_options]`.
- [ ] **Step 4:** Run `uv run pytest tests/test_usage.py -v -m "live or not live"`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: stdlib usage proxy and summary"`

### Task 7: Remote and Ollama runtime

**Files:**
- Create: `harness/remote.py`, `harness/paths.py`, `harness/runtimes/__init__.py`, `harness/runtimes/base.py`, `harness/runtimes/ollama.py`
- Test: `tests/test_remote.py`, `tests/test_ollama.py`

**Interfaces:**
- Produces (`remote.py`):
  - `RemoteError(Exception)`, raised for ssh exit 255 (connection lost; the caller maps it to infra_error)
  - `Remote(host: str = "markn@geekoma9.local")` with:
    - `run(cmd: str, timeout: float | None = None, check: bool = True) -> subprocess.CompletedProcess[str]`
    - `read_text(path: str) -> str`
    - `write_text(path: str, text: str) -> None` (via stdin)
    - `sync_dir(local: Path, remote_path: str) -> None` (rsync)
  - Every ssh call uses `-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15`.
- Produces (`paths.py`):
  - `ROOT = "/home/markn/agentbench"`
  - `AttemptPaths(root, workdir, task_files, issue_file, agent_log, usage_log, samples_csv, score_dir)`
  - `attempt_paths(run_id: str, task: str, repeat: int) -> AttemptPaths`, rooted at `{ROOT}/runs/{run_id}/{task}-r{repeat}`
- Produces (`runtimes/base.py`): the `Runtime` Protocol with:
  - `start(remote: Remote) -> None`, which also warms up the model;
  - `stop(remote: Remote) -> None`;
  - `upstream: str` (URL on geekoma9);
  - `model: str`;
  - `versions(remote: Remote) -> dict[str, str]`;
  - `loaded_models(remote: Remote) -> list[str]`.
- Produces (`runtimes/ollama.py`): `OllamaRuntime(cfg: RuntimeConfig)` and `render_unit(cfg: RuntimeConfig) -> str`. The unit is the systemd user unit `agentbench-runtime.service` with `ExecStart=/usr/local/bin/ollama serve` and `Environment=` lines: `OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_CONTEXT_LENGTH=<context>`, `OLLAMA_KEEP_ALIVE=-1`, `OLLAMA_MAX_LOADED_MODELS=1`, then `cfg.env` sorted.
- Produces (`runtimes/__init__.py`): `make_runtime(cfg: RuntimeConfig) -> Runtime`

- [ ] **Step 1: Write failing tests.** These cover:
  - `Remote.run` builds `["ssh", <opts...>, host, cmd]`, using a monkeypatched `subprocess.run`;
  - exit 255 raises `RemoteError`;
  - exit 1 with `check=True` raises `subprocess.CalledProcessError`;
  - `attempt_paths("e0-202611010100", "001-health-clamp", 2).workdir == "/home/markn/agentbench/runs/e0-202611010100/001-health-clamp-r2/work"`;
  - `render_unit` contains `Environment=OLLAMA_CONTEXT_LENGTH=65536` and the `cfg.env` entries in sorted order.
- [ ] **Step 2:** Run `uv run pytest tests/test_remote.py tests/test_ollama.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement.
  - `OllamaRuntime.start`:
    1. Write the unit to `~/.config/systemd/user/`, then `systemctl --user daemon-reload` and `systemctl --user restart agentbench-runtime`.
    2. Poll `curl -sf 127.0.0.1:11434/api/version` for up to 60 s.
    3. Warm up: POST `/api/generate` with `{"model", "prompt": "hi", "options": {"num_predict": 1}, "keep_alive": -1}`.
  - `versions` returns `runtime=ollama <ollama --version>` and `model_digest` from `/api/tags`.
  - `loaded_models` reads `/api/ps`.
- [ ] **Step 4:** Run `uv run pytest tests/test_remote.py tests/test_ollama.py -v`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: ssh remote, attempt paths, ollama runtime"`

### Task 8: Benchmark-repo access and agents

**Files:**
- Create: `harness/bench.py`, `harness/agents/__init__.py`, `harness/agents/base.py`, `harness/agents/null.py`, `harness/agents/oracle.py`, `harness/agents/command.py`
- Test: `tests/test_command_agent.py`, `tests/test_bench.py`

**Interfaces:**
- Consumes: `Remote`, `AttemptPaths` (Task 7), `AgentConfig`, `ConfigError` (Task 2)
- Produces (`bench.py`): `BenchRepo(remote: Remote, mirror: str = f"{ROOT}/bench.git", remote_url: str = "git@github-agentbench:YodaTheCoder/godot-agent-bench.git")` with:
  - `update() -> None` fetches all branches and tags into the mirror, `+refs/*:refs/*`.
  - `base_sha(task_set: str) -> str` resolves `base-<task_set>`.
  - `issue_text(task_set: str, task: str) -> str` reads `taskset-<task_set>:tasks/<task>/issue.md`.
  - `export_task_files(task_set: str, task: str, dest: str) -> None` uses `git archive` of `tasks/<task>`, flattened into dest.
  - `prepare_workdir(paths: AttemptPaths, task_set: str, branch: str) -> None`:
    1. `git clone --single-branch --branch main --no-tags <mirror> <workdir>`.
    2. `git checkout -b <branch> <base_sha>`.
    3. `git remote remove origin`.
    4. Write the issue to `paths.issue_file`, outside the workdir.
  - `commit_and_push(paths: AttemptPaths, branch: str, message: str) -> bool`:
    1. In the workdir: `git add -A` and `git commit --allow-empty`, with author `agentbench <agentbench@localhost>`.
    2. In the mirror: `git fetch <workdir> <branch>:<branch>`.
    3. `git push <remote_url> <branch>`.
    4. Returns False on a push failure and never raises for it.
- Produces (`agents/base.py`): `AgentResult(exit_code: int, timed_out: bool, wall_s: float, steps: int|None)` and the `Agent` Protocol `run(remote, paths: AttemptPaths, endpoint: str, model: str, timeout_s: int) -> AgentResult`
- Produces (`agents/command.py`):
  - `render_command(template: str, **values: str) -> str`: values are shell-quoted, and an unknown placeholder raises `ConfigError`.
  - `CommandAgent(cfg: AgentConfig)`: the full call is `cd <workdir> && setsid timeout -k 30 <timeout_s> bash -c <rendered> > <agent_log> 2>&1`, with cfg.env exported.
    - `timed_out` = exit 124 or 137.
    - After the run it kills any surviving process group (`pkill -KILL -s <sid>`) — Review Focus 3.
    - `steps` = count of `steps_regex` matches in the log, or None.
- Produces (`agents/null.py`): `NullAgent` (no-op, returns exit 0) and (`agents/oracle.py`): `OracleAgent` (`git -C <workdir> apply <task_files>/solution.patch`)
- Produces (`agents/__init__.py`): `make_agent(cfg: AgentConfig) -> Agent`

- [ ] **Step 1: Write failing tests**

```python
def test_render_quotes_values():
    assert render_command("x {issue_file}", issue_file="/a b/i.md", workdir="", endpoint="", model="", log="") == "x '/a b/i.md'"
def test_render_unknown_placeholder(): with pytest.raises(ConfigError): render_command("{nope}", **EMPTY)
def test_shortlist_templates_render():     # cross-checks Task 1 output
    for h in yaml.safe_load(open("research/shortlist.yaml"))["harnesses"]:
        render_command(h["command_template"], **EMPTY)
def test_command_agent_reports_timeout(fake_remote):  # fake_remote returns exit 124
    assert CommandAgent(cfg).run(fake_remote, paths, "http://127.0.0.1:11500", "m", 5).timed_out
def test_command_agent_kills_process_group(fake_remote): ...  # asserts a pkill -s call was issued
def test_prepare_workdir_removes_origin(fake_remote): ...     # asserts the issued command sequence includes `git remote remove origin` and the clone uses --single-branch --no-tags
```

- [ ] **Step 2:** Run `uv run pytest tests/test_command_agent.py tests/test_bench.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement. `fake_remote` is a recording stub in `tests/conftest.py` that returns canned `CompletedProcess` objects.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: bench repo access, null/oracle/command agents"`

### Task 9: Orchestrator, report and CLI

**Files:**
- Create: `harness/run.py`, `harness/report.py`, `harness/cli.py`
- Test: `tests/test_run.py`, `tests/test_report.py`

**Interfaces:**
- Consumes: everything from Tasks 2–8.
- Produces (`run.py`):
  - `InfraError(Exception)`
  - `preflight(remote: Remote, runtime: Runtime) -> None` raises `InfraError` if `pgrep -u markn -f 'godot|agentbench-agent'` finds anything, or if `runtime.loaded_models()` ≠ `[runtime.model]`.
  - `run_attempt(cfg, run_id, task, repeat, *, remote, runtime, agent, bench, scripts_dir: str) -> AttemptRecord`
  - `run_experiment(cfg: ExperimentConfig, exp_dir: Path, *, remote: Remote, bench: BenchRepo, clock=time) -> None`
- Produces (`report.py`):
  - `Summary(attempts, passes, infra_errors, pass_rate: float, wall_hours: float, solved_per_8h: float, median_tg_tps: float|None, median_pp_tps: float|None, throttled: int)`
  - `summarize(records: list[AttemptRecord]) -> Summary`
  - `render_markdown(summary: Summary, records: list[AttemptRecord]) -> str`
- Produces (`cli.py`): `main(argv: list[str] | None = None) -> int` with these subcommands:
  - `run CONFIG`
  - `validate --task-set v1`
  - `report EXP_DIR` (rewrites the block between `<!-- results:start -->` and `<!-- results:end -->` in the experiment README)
  - `review EXP_DIR` (Task 14)
  - `provision` (Task 13)

`run_attempt` sequence:
1. `preflight`.
2. `bench.prepare_workdir` and `export_task_files`.
3. Start `usage_proxy.py` and `sample.sh` in the background with `setsid nohup`, recording their pids.
4. `agent.run` with endpoint `http://127.0.0.1:11500`.
5. Stop the proxy and sampler.
6. `commit_and_push`.
7. `score.sh`.
8. Build the record from `load_score`, `summarize_usage`, `summarize_samples`, plus `versions` = runtime versions + `agent=<name> <version>` + `harness=<git sha>` + `task_set` + `sampling=<json of cfg.sampling>`.

Status rules:
- An upstream error (`usage.upstream_errors > 0`) when the agent did not pass → `infra_error` (Review Focus 4).
- `RemoteError` or `InfraError` anywhere → `infra_error` with `error` set.
- Otherwise `decide_status`.

`run_experiment` sequence:
1. Create or reuse `exp_dir/run_id` (`<id>-<YYYYmmddHHMM>`).
2. `bench.update()`, then `runtime.start()`.
3. Loop over `pending(tier_plan(cfg), read_records(...))`. Retry an `infra_error` once immediately: restart the runtime first, then rerun the attempt.
4. Sleep `cooldown_s` between attempts.
5. Stop the runtime at the end.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_report.py
def test_solved_per_8h(): # 2 pass + 1 fail, 1800 s each, + 1 infra_error (excluded)
    s = summarize([r("pass",1800), r("pass",1800), r("fail",1800), r("infra_error",60)])
    assert s.passes == 2 and s.infra_errors == 1
    assert s.wall_hours == pytest.approx(1.5) and s.solved_per_8h == pytest.approx(10.667, rel=1e-3)
def test_empty_summary_is_zero(): assert summarize([]).solved_per_8h == 0.0

# tests/test_run.py  (all with fakes: FakeRemote, FakeRuntime, FakeAgent, FakeBench)
def test_upstream_error_becomes_infra_error(): ...       # usage log has upstream_error -> status infra_error
def test_preflight_dirty_host_is_infra_error(): ...      # pgrep returns a pid -> infra_error, agent never run
def test_infra_error_retried_once_then_moves_on(): ...   # agent raises RemoteError twice -> 2 records, next task runs
def test_resume_skips_done(): ...                        # pre-seeded pass record -> agent called only for remaining
def test_cooldown_between_attempts(): ...                # fake clock records sleep(cfg.cooldown_s) between attempts
def test_push_failure_recorded_not_fatal(): ...          # commit_and_push False -> pushed False, status from scoring
```

- [ ] **Step 2:** Run `uv run pytest tests/test_run.py tests/test_report.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement. `validate` builds two `ExperimentConfig`s (agent `null` and `oracle`, tier `all`, `cooldown_s=0`) under `experiments/validate-<set>-{null,oracle}/`. It exits 1 unless every oracle attempt is `pass` and every null attempt is `fail`, and prints the offending tasks.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: orchestrator, report, cli"`

### Task 10: Benchmark repo — base game and regression tests

**Files (in `~/_dev/claude/godot-agent-bench`):**
- Create: `project.godot`, `.godot-version`, `README.md`, `LICENSE` (MIT), `addons/gut/` (vendored), `scripts/components/health.gd`, `scripts/weapon.gd`, `scripts/player.gd`, `scripts/enemy.gd`, `scripts/hud.gd`, `scripts/score_manager.gd` (autoload `ScoreManager`), `scenes/{player,enemy,hud,main}.tscn`, `tests/regression/test_{health,weapon,score,player,enemy}.gd`, `.gutconfig.json`

**Interfaces (the public API that task issues and hidden tests rely on):**
- `class_name Health extends Node`: `@export var max_health := 100`, `var current: int`, `signal died`, `func damage(amount: int) -> void`, `func heal(amount: int) -> void`. **Seeded bug for 001:** `heal` does not clamp to `max_health`.
- `class_name Weapon extends Node`: `@export var fire_rate := 4.0` (shots/s), `func try_fire(now: float) -> bool`. **Seeded bug for 004:** the cooldown compares against `fire_rate` instead of `1.0 / fire_rate`.
- `ScoreManager` (autoload): `var score: int`, `func add_points(n: int) -> void`, `func reset() -> void`.
- `class_name Player extends CharacterBody2D`: `@export var speed := 200.0`, `static func compute_velocity(input: Vector2, speed: float) -> Vector2` (normalised), with child nodes `Health` and `Weapon`.
- `class_name Enemy extends CharacterBody2D`: `@export var points := 10`, `var target: Node2D`, `func direction_to_target() -> Vector2`. On `Health.died` it calls `ScoreManager.add_points(points)` directly and `queue_free()`. That direct call is what task 009 refactors.
- `HUD` (`hud.gd` on a CanvasLayer): `@onready var score_label: Label`, updated every frame from `ScoreManager.score`.

- [ ] **Step 1:** Owner action: ask the owner to create the public repo `YodaTheCoder/godot-agent-bench` (empty), or to approve `gh repo create YodaTheCoder/godot-agent-bench --public`. Then clone it to `~/_dev/claude/godot-agent-bench`.
- [ ] **Step 2:** Pick the latest stable Godot 4 release from godotengine.org and the GUT release that supports it. Write the Godot version to `.godot-version` (e.g. `4.x.y-stable`) and vendor GUT into `addons/gut`. Install the same Godot on the Mac for authoring (`brew install --cask godot`, or the official zip if brew's version differs) — ask the owner before installing.
- [ ] **Step 3:** Write the regression tests first, covering only correct behaviour (not the seeded bugs):
  - damage reduces `current`, and `died` is emitted at 0;
  - `try_fire` returns true for the first shot;
  - `add_points` accumulates and `reset` zeroes;
  - `compute_velocity(Vector2(1,1), 200)` has length 200;
  - `direction_to_target` is normalised.
- [ ] **Step 4:** Run `godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://tests/regression -gexit`. Expected: FAIL (missing scripts).
- [ ] **Step 5:** Implement the scripts and scenes to the API above. `main.tscn` contains a Player, 2 Enemies targeting it, and the HUD.
- [ ] **Step 6:** Run the same GUT command. Expected: all regression tests pass. Then run `godot --headless --path . --import`. Expected: no `SCRIPT ERROR`.
- [ ] **Step 7:** Commit on `main`, tag `base-v1`, and push (ask the owner before this first push to the public repo): `git push -u origin main --tags`.

### Task 11: Benchmark tasks 001–006

**Files (in the benchmark repo, branch `tests`, created from `base-v1`):**
- Create, for each task: `tasks/<id>/issue.md`, `tasks/<id>/tests/test_<id_short>.gd`, `tasks/<id>/solution.patch`

**Rules for every task:**
- Write `issue.md` like a frontier-written agent issue, with Context, Requirements and Acceptance criteria sections. It must name every class, file path, signal, method and signature the hidden tests touch, and must not include test code.
- `solution.patch` is `git diff base-v1` of a reference implementation made on a scratch branch.
- Hidden tests: 3–8 GUT tests.

| id | tier | issue (summary) | hidden tests assert |
|---|---|---|---|
| 001-health-clamp | S | `heal` must not exceed `max_health`; healing a dead entity does nothing | heal past max → `current == max_health`; heal at 0 → stays 0 |
| 002-damage-signal | S | add `signal damaged(amount: int, remaining: int)` to Health, emitted on each damage | emitted with correct args; not emitted for `damage(0)` |
| 003-score-combo | S | ScoreManager combo: `add_points` multiplies by `combo` (starts 1, +1 per call within 2.0 s via `func add_points(n: int, now: float)`, resets after) | 3 quick calls of 10 → 60; gap > 2 s resets the multiplier |
| 004-weapon-cooldown | S | fix fire-rate cooldown so `fire_rate` is shots per second | at 4.0: fire at t=0 true, t=0.2 false, t=0.25 true |
| 005-inventory-pickup | M | new `class_name Inventory extends Resource` (`add(item_id: StringName, qty := 1)`, `count(item_id) -> int`, `signal changed`), `Player.inventory`, new `scenes/pickup.tscn` (Area2D, `@export item_id`, `@export qty`) that adds to the player's inventory on body entered and frees itself | add and count; `changed` emitted; instancing the pickup and calling its `_on_body_entered(player)` adds the items and queues free |
| 006-save-load | M | `class_name SaveData extends Resource` (`score`, `player_health`, `inventory`) plus autoload `SaveGame` with `save(path := "user://save.tres")` and `load_into(player) -> bool` | round-trip restores score and health; a missing file → false with state unchanged |

- [ ] **Step 1:** For each task, write the hidden test first, on a scratch branch from `base-v1`, and run it with GUT. Expected: FAIL.
- [ ] **Step 2:** Write the reference implementation on the scratch branch and run the hidden tests plus the regression tests. Expected: PASS.
- [ ] **Step 3:** Save `solution.patch`, then copy the tests and the issue to `tests:tasks/<id>/`.
- [ ] **Step 4:** Check the patch applies cleanly: `git checkout base-v1 -- . && git apply --check tasks/<id>/solution.patch`, in a throwaway worktree. Expected: no output.
- [ ] **Step 5:** Commit each task separately on `tests`: `git commit -m "task <id>"`.

### Task 12: Benchmark tasks 007–012

Same files, rules and steps as Task 11.

| id | tier | issue (summary) | hidden tests assert |
|---|---|---|---|
| 007-patrol-enemy | M | new `scenes/patrol_enemy.tscn` + `class_name PatrolEnemy extends Enemy`, `@export var waypoints: PackedVector2Array`, `func next_waypoint_index() -> int`, cycling through waypoints, chasing the target when within `@export var aggro_range := 150.0` | cycling order; `is_chasing()` true inside the range, false outside; the scene instantiates with no errors |
| 008-hud-health | M | HUD shows player health in `health_label` as `"HP: <current>/<max>"`, updated via a Health signal, not per frame (`func bind_health(h: Health)`) | the label text after damage; no `_process` override in `hud.gd` (checked via `has_method`/script source) |
| 009-event-bus | L | add autoload `Events` with `signal enemy_died(points: int)`; Enemy emits it instead of calling ScoreManager; ScoreManager connects in `_ready` | emitting `Events.enemy_died(10)` adds 10; `enemy.gd` source has no `ScoreManager.` reference; killing an enemy still scores |
| 010-wave-spawner | L | `class_name WaveConfig extends Resource` (`enemy_scene`, `count`, `interval`), `class_name WaveSpawner extends Node2D` with `@export var waves: Array[WaveConfig]`, `func start()`, `signal wave_finished(index)`, `signal all_waves_finished`, added to `main.tscn` | stepping `_process` with a fake delta spawns `count` children per wave at the right intervals; the signals fire in order; `main.tscn` contains a WaveSpawner |
| 011-status-effects | L | `class_name StatusEffect extends Resource` (`duration`, `func apply_tick(target, delta)`), subclasses `Poison` (damage per second) and `Slow` (speed multiplier), `class_name StatusEffects extends Node` component with `add(effect)` and `tick(delta)`, Player has one, and the slow affects `compute_velocity` usage | poison 5 dps for 2 s → health −10, then stops; slow 0.5 halves the player's effective speed and expires; stacking two poisons adds |
| 012-weapon-tests | L | write GUT tests for Weapon in `tests/test_weapon_extra.gd` covering the cooldown, plus a new `func reset()` | uses `score_extra.sh`: the agent's tests must pass on the reference solution and fail on each of `tasks/012-weapon-tests/mutants/{1,2,3}.patch`; `hidden.xml` is written with one test case per check |

- [ ] **Steps 1–5:** As in Task 11. For 012, also create the three mutant patches and `score_extra.sh`. It applies the reference solution, runs the agent's test file and requires a pass; then for each mutant it runs on a fresh copy and requires a fail; then it writes a JUnit file to `<out_dir>/hidden.xml`.
- [ ] **Step 6:** Tag `taskset-v1` on `tests` and push: `git push origin tests --tags`.

### Task 13: Provision geekoma9

**Files:**
- Modify: `harness/cli.py` (implement `provision`), `harness/run.py` (system Ollama stop/start)
- Create: `docs/provisioning.md`
- Test: `tests/test_run.py`

**Interfaces:**
- Produces: `harness provision` does the following, and exits non-zero naming the first failing check:
  1. Syncs `harness/remote_scripts/` to `~/agentbench/bin/`.
  2. Clones the benchmark mirror if it's missing.
  3. Verifies: `python3 --version` ≥ 3.10; `~/agentbench/opt/godot/godot --version` matches `.godot-version` at `base-v1`; `ollama --version`; `ssh -T git@github-agentbench` authenticates; `sudo -n systemctl stop ollama` is allowed; `loginctl show-user markn -p Linger` = yes.

- [ ] **Step 1:** Write `docs/provisioning.md` listing the owner actions, then stop and ask the owner to perform them:
  - Add a sudoers rule via `sudo visudo -f /etc/sudoers.d/agentbench`: `markn ALL=(root) NOPASSWD: /usr/bin/systemctl stop ollama, /usr/bin/systemctl start ollama`. The harness stops the system Ollama for a run and starts it again afterwards, so the owner's normal LAN Ollama setup comes back.
  - `sudo loginctl enable-linger markn`.
  - Add the deploy key printed by `ssh-keygen -t ed25519 -f ~/.ssh/agentbench_deploy -N '' -C agentbench@geekoma9` (generated by me on geekoma9) to the benchmark repo with write access, plus a `~/.ssh/config` entry `Host github-agentbench / HostName github.com / IdentityFile ~/.ssh/agentbench_deploy / IdentitiesOnly yes`.
- [ ] **Step 2:** Install the pinned Godot Linux x86_64 editor binary on geekoma9 to `~/agentbench/opt/godot/godot`, from the official GitHub release, with its checksum verified.
- [ ] **Step 3:** Make `run_experiment` call `sudo -n systemctl stop ollama` before `runtime.start` and `sudo -n systemctl start ollama` in a `finally` block. Add a test in `tests/test_run.py`, `test_system_ollama_restored_on_error`: the agent raises → the start command was still issued.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: PASS. Then run `uv run harness provision`. Expected: exit 0, all checks OK.
- [ ] **Step 5:** Commit: `git commit -m "harness: provisioning checks and docs"`

### Task 14: Frontier review

**Files:**
- Create: `harness/review.py`
- Modify: `harness/cli.py` (`review`)
- Test: `tests/test_review.py`

**Interfaces:**
- Produces:
  - `Review(task: str, repeat: int, branch: str, would_merge: bool, quality: int, comments: str, reviewer: str)`
  - `build_review_prompt(issue_text: str, diff: str) -> str`
  - `parse_review(text: str) -> tuple[bool, int, str]`, which reads a fenced or bare JSON object `{"would_merge": bool, "quality": 1-5, "comments": str}` and raises `ValueError` otherwise.
  - `harness review EXP_DIR`: for each `pass` record not yet in `reviews.jsonl`, it gets the issue and `git diff base-v1..<branch>` from a local clone of the benchmark repo. It runs `claude -p --model opus --output-format text <prompt>` on the Mac, retries once on a parse failure, and appends to `reviews.jsonl`.
- The rubric fixed in the prompt:
  - Does it meet every requirement in the issue?
  - Is it idiomatic GDScript, with no dead code, debug prints or unrelated changes?
  - Would a maintainer merge it as is?
  - Quality: 1 = wrong or harmful, 3 = works but needs changes, 5 = merge as is.

- [ ] **Step 1: Write failing tests.** These cover:
  - `parse_review` on fenced JSON, bare JSON, and JSON surrounded by prose;
  - quality 0 or 6 → `ValueError`;
  - non-JSON → `ValueError`;
  - `build_review_prompt` contains the issue text, the diff, and the exact rubric line `5 = merge as is`.
- [ ] **Step 2:** Run `uv run pytest tests/test_review.py -v`. Expected: FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: PASS.
- [ ] **Step 5:** Commit: `git commit -m "harness: frontier review"`

### Task 15: Validate the benchmark and calibrate

**Files:**
- Create: `experiments/validate-v1-null/`, `experiments/validate-v1-oracle/` (generated), `experiments/calibration-frontier/config.yaml`, `experiments/calibration-frontier/README.md`

- [ ] **Step 1:** Run `uv run harness validate --task-set v1`. Expected: exit 0 — all 12 oracle attempts `pass` and all 12 null attempts `fail`. If any fail, fix that task's tests or solution in the benchmark repo, retag `taskset-v1` (the tag isn't used by any real run yet), and rerun.
- [ ] **Step 2:** Owner action: install Claude Code on geekoma9 and log in, or set an API key, for calibration only. Confirm the cost is acceptable first (12 tasks with Claude, roughly 12 sessions).
- [ ] **Step 3:** Write `experiments/calibration-frontier/config.yaml`:
  - tier `all`;
  - agent `command`, name `claude-code`, with command `claude -p --dangerously-skip-permissions "$(cat {issue_file})"` (it runs in a disposable clone);
  - runtime `ollama` with the E0 model kept loaded (it's unused, but it keeps preflight uniform).
- [ ] **Step 4:** Run `uv run harness run experiments/calibration-frontier/config.yaml` in the background, then `uv run harness report experiments/calibration-frontier` and `uv run harness review experiments/calibration-frontier`. Expected: most tasks pass. Look into any task the frontier model fails and, together with the owner, decide whether it's too hard or unfair before freezing v1.
- [ ] **Step 5:** Commit: `git add experiments && git commit -m "bench v1 validated and calibrated"`

### Task 16: E0 baseline

**Files:**
- Create: `experiments/e0-baseline/config.yaml`, `experiments/e0-baseline/README.md`, `docs/FINDINGS.md`
- Modify: `README.md` (the Reproduce section)

- [ ] **Step 1:** Write `config.yaml`:
  - tier `screening`;
  - runtime `{kind: ollama, model: "qwen3-coder:30b", context: 65536}`;
  - agent = the `e0_default_harness` entry from `research/shortlist.yaml`, with name, version, command_template and steps_regex copied from it;
  - notes recording the current BIOS split (24 GiB UMA) and Ollama 0.34.4.
- [ ] **Step 2:** Install that harness on geekoma9 using its shortlist `install` command, after confirming with the owner. Do a dry run on one task: copy the config with `tier: all`, interrupt after the first attempt finishes, check the record and the branch look right, then delete that scratch experiment directory.
- [ ] **Step 3:** Run `uv run harness run experiments/e0-baseline/config.yaml` in the background (up to ~4.5 h). When it finishes: `uv run harness report experiments/e0-baseline`.
- [ ] **Step 4:** Write the README findings for `e0-baseline` (what passed and failed and why, from the agent logs; tok/s; memory headroom; any throttling). Then start `docs/FINDINGS.md` with "Current best: E0 baseline" and its `solved_per_8h`, and fill in the main README's Reproduce section.
- [ ] **Step 5:** Commit and push this repo (ask the owner before the first push): `git commit -m "E0 baseline results" && git push -u origin main`.
- [ ] **Step 6:** Hand off: write the E1 plan (memory split) from `research/memory.md` and the E0 results, using `superpowers:writing-plans`.
