# Coding-agent optimisation for geekoma9 — design

Date: 2026-10-31
Status: draft, awaiting review

## Goal

Find the configuration of geekoma9 (GEEKOM A9 Max) that lets a local coding agent turn
well-specified GitHub issues into pull requests that pass review, as many per night as possible,
unattended.

The intended production use (out of scope for this spec, see "Later work"): a frontier model and
the owner write epics, milestones and agent-sized GitHub issues for a Godot game; geekoma9 runs as
a self-hosted GitHub Actions runner and works through those issues overnight; a frontier model
reviews the resulting PRs and leaves comments.

The project and its benchmark are public so others can reproduce and reference the results.

## Constraints

- Hardware is fixed: Ryzen AI 9 HX 470, Radeon 890M (16 CU, RDNA 3.5), 32 GB DDR5 SODIMM
  (dual channel), 2 TB NVMe. A RAM upgrade is ruled out on cost.
- The BIOS memory split between system and GPU is open to change. Current state: 24 GiB reserved
  as VRAM, ~4 GiB GTT, 7.4 GiB visible to Linux (which is already swapping lightly).
- Ubuntu 24.04, kernel 7.0. Ollama 0.34.4 is installed with `OLLAMA_IGPU_ENABLE=1`,
  `OLLAMA_CONTEXT_LENGTH=65536`, listening on `0.0.0.0:11434`.
- No hard requirement on runtime (Ollama, llama.cpp, other) or agent harness (Claude Code, OpenCode,
  Aider, other). "Most bang for the buck" decides.
- Measurement must not be disturbed by the orchestration: Claude and the harness run on the Mac
  (or another LAN machine) and drive geekoma9 over SSH/HTTP. geekoma9 runs only what is under test.
- The owner's real game repo is private and is not used. The benchmark is a separate public repo.

## Success criteria

- A recommended configuration (memory split, runtime and build, model and quant, context/KV
  settings, agent harness and its settings) recorded in `FINDINGS.md`, backed by committed data.
- Primary metric: **tasks solved per 8 hours** on the benchmark (pass rate × throughput); pass rate
  breaks ties.
- For the winning config, a frontier review on its passing attempts confirms that "tests pass"
  broadly corresponds to "would merge".
- Every result reproducible from the committed experiment config, with each attempt's raw output
  preserved as a branch in the benchmark repo.

## Sub-projects

This spec covers 1–3. Item 4 gets its own spec once 1–3 have produced a winning config.

1. Research
2. Public Godot benchmark repo
3. Harness and experiments
4. Production pipeline (later work)

## 1. Research

Desk research written to `research/`, with sources, producing shortlists for the experiments:

- **Runtimes** for the 890M on Linux: Ollama, llama.cpp `llama-server` (Vulkan, current build),
  ROCm status for gfx1150, and anything else credible (e.g. NPU/hybrid stacks), with known
  performance and stability on Strix/Gorgon Point iGPUs.
- **Memory configuration**: BIOS UMA sizes available on this board; using a minimal UMA plus a
  large GTT via kernel parameters (e.g. `ttm.pages_limit`/`amdgpu.gttsize`) and whether each
  shortlisted runtime can allocate from GTT.
- **Models**: coding models that fit in about 24 GB with context, preferring MoE (memory
  bandwidth of about 90 GB/s makes dense 27B+ models roughly 5 tok/s versus about 30–40 tok/s for
  ~3B-active MoE), with evidence on agentic tool-calling and GDScript ability.
- **Agent harnesses** that run headless against a local OpenAI- or Anthropic-compatible endpoint,
  and how well each works with local models' tool-calling.

## 2. Benchmark repo

New public repository, provisionally `YodaTheCoder/godot-agent-bench`. The owner creates it or
approves its creation.

- A small Godot 4 game project. `main` is the clean starting state for every task.
- About 12 tasks under `tasks/NNN-slug/issue.md`, worded like the issues the production frontier
  model will write:
  - small: single-script bug fix or added function/signal;
  - medium: multi-file feature (e.g. inventory pickup, save/load resource, new enemy behaviour
    with its scene);
  - large: cross-cutting change (e.g. refactor a system into an autoload, new scene plus scripts
    and wiring).
  The set covers GDScript logic, `.tscn`/`.tres` editing, signals, and writing tests.
- Every task is verifiable headless; none requires visual inspection.
- Hidden acceptance tests (GUT) live on a separate `tests` branch, never on the agent's branch,
  and are applied only for scoring.
- Each task has a reference solution (kept with the hidden tests) for the oracle check.
- The task set is versioned (`v1`, ...). Results always name the task-set version.
- Each attempt is pushed, unmodified, to `exp/<run-id>/<task>` as public evidence.

### Scoring an attempt

Pass requires all of:

- the project imports and parses headless with no script errors;
- all of the task's hidden GUT tests pass;
- the existing regression tests on `main` still pass;
- completed within the time budget (45 minutes wall clock).

Recorded per attempt: pass/fail, fraction of hidden tests passed, wall time, prompt and generated
tokens, prompt-processing and generation tok/s, peak memory, agent step count, timeout or crash.

### Run tiers

- **Screening**: 6 representative tasks × 1 run per config.
- **Finalists**: all 12 tasks × 3 runs per config.
- **Frontier review** (finalists only): a fixed rubric on the diff against the issue: would
  merge yes/no, quality 1–5.
- **Calibration**: one run of the full suite with a frontier model (Claude Code with Claude) to
  prove the tasks are solvable and the tests fair, and to give an upper bound.

## 3. Harness and experiments

### Layout of this repo

- `research/` — research notes and shortlists.
- `harness/` — Python package (managed with `uv`) run from the Mac.
- `experiments/<id>/` — `config.yaml`, `results.jsonl`, `README.md` (findings).
- `docs/` — specs, plans, and `FINDINGS.md` (current best config).

### On geekoma9

- The runtime under test, managed by systemd, one at a time.
- The agent under test, running locally against that runtime (as in production).
- Godot 4 headless and GUT for scoring.
- A deploy key that can push only to the benchmark repo.
- Nothing else heavy.

### Attempt lifecycle

`harness run experiments/<id>/config.yaml` performs, per attempt:

1. Over SSH, restart the runtime with the config's settings, warm it up, and verify nothing else
   is loaded or running.
2. Create a fresh single-branch clone of the benchmark's `main` (no `tests` branch or other
   refs, so the agent cannot read hidden tests or reference solutions), check out the task's base
   commit and create branch `exp/<run-id>/<task>`.
3. Run the agent with the issue text, timeout and token budget, sampling memory, temperatures and
   GPU/CPU clocks throughout.
4. Commit the agent's output unmodified and push the branch.
5. In a separate scratch copy, apply the hidden tests, run Godot headless and GUT, and append one
   JSONL record with all metrics and pinned versions (runtime build, model digest, harness
   version, sampling settings, task-set version).
6. Cool down before the next attempt.

Rerunning an experiment resumes, skipping attempts already recorded.

### Failure handling

- Agent timeout or step limit: counts as a fail for the config, recorded as `timeout`.
- Infrastructure failure (runtime crash, OOM, SSH drop): recorded as `infra_error`, retried once,
  never counted against the model. OOM is detected from the journal and kernel log.
- Thermal throttling: clock and temperature samples are stored per attempt, and throttled
  attempts are flagged.

### Experiment sequence

One variable per experiment, keeping the winner of each stage. The full config is recorded every
time.

- **E0 Baseline**: the current setup (24 GiB UMA, Ollama 0.34.4, qwen3-coder:30b, 64k context)
  with a reasonable default harness.
- **E1 Memory split**: 24 GiB UMA, 16 GiB UMA, and minimal UMA with a large GTT. Judged on fit,
  OS headroom for agent plus Godot, and speed.
- **E2 Runtime**: same model file under Ollama vs llama.cpp Vulkan (and ROCm if research supports
  it). Prompt-processing speed at 4k/32k/64k context and prefix caching weigh as much as
  generation speed.
- **E3 Model × harness grid**: about 3–4 shortlisted models × 2–3 harnesses on the screening
  tier, because tool-calling reliability depends on the pair.
- **E4 Quant and context**: for the top 2 pairs: quant (Q4 to Q6/Q8 where it fits), context
  (32k to 128k), KV-cache quantisation, flash attention.
- **E5 Finalists**: the finalist tier plus frontier review for the top 2–3 configs. The winner is
  written to `FINDINGS.md`.

If a later result undermines an earlier decision (e.g. the winning model prefers a different
memory split), the affected earlier stage is rerun rather than assumed.

### Owner actions

- BIOS UMA changes need a reboot at the machine, done by the owner.
- Kernel boot parameter changes (for the GTT approach) are made only after the owner confirms.
- Creating the public benchmark repo, and pushing to it for the first time, needs the owner's OK.

### Verifying the harness and benchmark

- **Oracle agent** applies each task's reference solution and must pass.
- **Null agent** makes no changes and must fail.
- Both run for every task before any real experiment.
- Unit tests cover scoring and result parsing.
- The frontier calibration run is the final check that tasks are realistic and fair.

## Later work (separate spec)

Production pipeline: geekoma9 as a self-hosted GitHub Actions runner that picks up labelled
issues overnight using the winning config, opens PRs, and triggers frontier-model review comments.
Also possible later: configs for other specialist models besides coding.
