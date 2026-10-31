# E1 Memory Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Find the memory split (BIOS UMA carve-out vs GTT) that gives the E0 configuration the most speed
and headroom on geekoma9, backed by committed screening runs.

**Architecture:** The harness gains three measurements that a memory experiment needs and E0 lacked: the
host's actual memory layout (pinned on every record and checked against the config before any attempt), how
much of the model Ollama put on the GPU, and swap use during the attempt. A `probe` tier (one task) gives a
cheap go/no-go per memory setting. Then three screening runs: `uma24` (re-run of E0 with the new fields),
`uma16`, and `umamin_gtt24`, separated by owner BIOS changes and, for the last, kernel TTM parameters.

**Tech Stack:** Python 3.12 harness (`uv`, pytest), bash remote scripts, Ollama 0.34.4, OpenCode 1.18.32,
Godot 4.7.2/GUT 9.7.1 on geekoma9; orchestrated from `newbuntu.local` in `tmux`.

**Spec:** `docs/superpowers/specs/2026-10-31-coding-agent-optimisation-design.md` (E1 in "Experiment
sequence"). Evidence: `research/memory.md`, `experiments/e0-baseline/README.md`.

## Global Constraints

- One variable per experiment: only the memory split changes. Runtime `ollama`, model `qwen3-coder:30b`,
  context `65536`, agent OpenCode `1.18.32` with the E0 command, tier `screening`, task set `v1` — copied
  from `experiments/e0-baseline/config.yaml`.
- E1 is "judged on fit, OS headroom for agent plus Godot, and speed" (spec). With one run per task, a
  pass-rate difference of one task is noise and does not decide E1 on its own.
- BIOS UMA changes need a reboot at the machine, done by the owner.
- Kernel boot parameter changes (for the GTT approach) are made only after the owner confirms.
- Announce every reboot of geekoma9 before doing it.
- Every geekoma9 change is recorded in `docs/provisioning.md` with its rollback.
- Runs are started on `newbuntu.local` with
  `ssh -4 markn@newbuntu.local tmux new-session -d -s calib "'cd ~/geekoma9-optimise && ~/.local/bin/uv run harness run <config> 2>&1 | tee <id>.log; exec bash'"`
  after syncing the repo (`rsync -az --delete --exclude .venv --exclude __pycache__ --exclude .pytest_cache --exclude '*.log' ./ markn@newbuntu.local:geekoma9-optimise/`),
  and results are copied back with rsync before reporting.
- Ask the owner before each push of this repo.
- GTT sizes in TTM pages: pages = GiB × 262144 (24 GiB = `6291456`). Keep GTT ≤ 24 GiB on this 32 GB box.

## Review Focus

- A memory setting that didn't take (BIOS reverted, kernel parameter typo) must stop the experiment before
  any attempt, with a message naming expected and actual sizes — not run 6 attempts on the wrong layout.
- Existing `results.jsonl` files (E0, calibration, validation) have no new fields and must still load and
  report.
- `/api/ps` showing the model with `size` 0 or no `size_vram` must give `gpu_offload = None`, not a crash.
- A host with no swap (`SwapTotal: 0`) must record swap use 0.
- The default GTT size is not a round number (3.70 GiB at uma24); host checks need a tolerance (±0.25 GiB).

---

### Task 1: Host memory layout and the `probe` tier

**Files:**
- Create: `harness/host.py`, `tests/test_host.py`
- Modify: `harness/config.py` (`HostExpect`, `ExperimentConfig.host`, `host:` parsing), `harness/tiers.py`
  (`probe` tier), `harness/run.py` (`run_experiment` checks the host once; `run_attempt` pins host fields)
- Test: `tests/test_host.py`, `tests/test_config.py`, `tests/test_tiers.py`, `tests/test_run.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) class HostMemory: vram_mib: int; gtt_mib: int; mem_total_mib: int; swap_total_mib: int; ttm_pages_limit: int | None`
  - `read_host_memory(remote: Remote) -> HostMemory` — one `remote.run` printing
    `mem_info_vram_total`, `mem_info_gtt_total` (from `/sys/class/drm/card0/device`), `MemTotal` and
    `SwapTotal` from `/proc/meminfo`, and `/sys/module/ttm/parameters/pages_limit`.
  - `class HostMismatchError(Exception)`; `check_host(expected: HostExpect | None, actual: HostMemory) -> None`
    raises it when VRAM or GTT differs from the expectation by more than `HOST_TOLERANCE_GIB = 0.25`;
    `None` expectation never raises.
  - `host_versions(h: HostMemory) -> dict[str, str]` with keys `host_vram_mib`, `host_gtt_mib`,
    `host_mem_total_mib`, `host_ttm_pages_limit` (`""` when None).
  - `@dataclass(frozen=True) class HostExpect: vram_gib: float; gtt_gib: float` in `config.py`;
    `ExperimentConfig.host: HostExpect | None = None`; YAML `host: {vram_gib: 24, gtt_gib: 3.7}`;
    unknown keys under `host` are a `ConfigError`.
  - Tier `probe`: task subset `["004-weapon-cooldown"]`, 1 repeat.
- Consumes: `Remote.run`, `ExperimentConfig`, `tier_plan`.

- [ ] **Step 1: Write the failing tests**

`tests/test_host.py`:
- `test_read_host_memory_parses` — fake remote replies with VRAM `25769803776`, GTT `3970646016`,
  `MemTotal: 7755172 kB`, `SwapTotal: 8388604 kB`, pages_limit `969396` → `HostMemory(24576, 3786, 7573, 8191, 969396)`.
- `test_read_host_memory_missing_ttm` — empty pages_limit → `ttm_pages_limit is None`.
- `test_check_host_within_tolerance` — expected `HostExpect(24, 3.7)`, actual GTT 3786 MiB → no raise.
- `test_check_host_mismatch_names_both` — expected `HostExpect(16, 7.7)`, actual VRAM 24576 → raises
  `HostMismatchError` whose message contains `"vram"`, `"16"` and `"24.0"`.
- `test_check_host_none_expectation` — `check_host(None, …)` does not raise.
- `test_host_versions_keys` — returns exactly the four keys, values as strings.

`tests/test_config.py`: `test_host_section_parsed` (`host: {vram_gib: 16, gtt_gib: 7.7}` →
`HostExpect(16.0, 7.7)`), `test_host_section_unknown_key` (`host: {vram: 16}` → `ConfigError`),
`test_host_absent_is_none`.

`tests/test_tiers.py`: `test_probe_tier` — `tier_plan` of a `probe` config is `[("004-weapon-cooldown", 1)]`.

`tests/test_run.py`:
- `test_run_experiment_host_mismatch_runs_nothing` — config expects VRAM 16, fake host reports 24 GiB →
  `run_experiment` raises `HostMismatchError`, no attempt record is written, and the system Ollama restore
  still runs.
- `test_attempt_record_pins_host` — a recorded attempt's `versions` contains `host_vram_mib == "24576"`.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_host.py tests/test_config.py tests/test_tiers.py tests/test_run.py`
Expected: FAIL (`harness.host` not found; `probe` unknown tier; no `host` field).

- [ ] **Step 3: Implement `harness/host.py`, the config and tier changes, and the two `run.py` call sites**

`run_experiment` reads the host and calls `check_host` once, after stopping the system Ollama and before the
attempt loop, inside the existing `try/finally` that restores it. `run_attempt` adds `host_versions(...)` to
`versions` next to `runtime.versions(remote)` (read the host per attempt so every record carries it).
`config.py`'s `_TIERS` gains `"probe"`.

- [ ] **Step 4: Run the full suite**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add harness/host.py harness/config.py harness/tiers.py harness/run.py tests
git commit -m "harness: pin and check host memory layout; add probe tier"
```

### Task 2: GPU offload fraction

**Files:**
- Modify: `harness/runtimes/base.py` (protocol), `harness/runtimes/ollama.py`, `harness/results.py`
  (`gpu_offload` field), `harness/run.py` (record it)
- Test: `tests/test_ollama.py`, `tests/test_results.py`, `tests/test_run.py`

**Interfaces:**
- Produces: `Runtime.gpu_offload(remote: Remote) -> float | None`; `OllamaRuntime.gpu_offload` returns
  `size_vram / size` for the `/api/ps` entry whose `name` is the model under test, rounded to 3 places, or
  `None` when the entry is missing, `size` is 0, or `size_vram` is absent. `AttemptRecord.gpu_offload:
  float | None = None` (new trailing field with a default, so old JSONL lines load).
- Consumes: `OllamaRuntime._get`, `AttemptRecord`, `read_records`.

- [ ] **Step 1: Write the failing tests**

- `test_gpu_offload_full` — `/api/ps` `{"models":[{"name":"qwen3-coder:30b","size":100,"size_vram":100}]}`
  → `1.0`.
- `test_gpu_offload_partial` — `size 200, size_vram 150` → `0.75`.
- `test_gpu_offload_missing_fields` — `size 0`, or no `size_vram`, or a different model name → `None`.
- `test_read_records_old_lines_default_new_fields` — a JSONL line copied from
  `experiments/e0-baseline/results.jsonl` (no `gpu_offload`) loads with `gpu_offload is None`.
- `test_attempt_records_gpu_offload` (run) — fake runtime returning `0.9` → the record has `gpu_offload == 0.9`.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest -q tests/test_ollama.py tests/test_results.py tests/test_run.py`
Expected: FAIL (`gpu_offload` not defined).

- [ ] **Step 3: Implement**

`run_attempt` reads `runtime.gpu_offload(remote)` right after `preflight` (the model is loaded and warm
then); an exception from it is not an infra error — record `None` and continue.

- [ ] **Step 4: Run the full suite** — `uv run pytest -q`, all pass.

- [ ] **Step 5: Commit** — `git commit -m "harness: record Ollama GPU offload fraction"`

### Task 3: Swap use during attempts, and report columns

**Files:**
- Modify: `harness/remote_scripts/sample.sh` (`swap_used_mib` column, last), `harness/sampling.py`
  (`SampleSummary.peak_swap_mib`), `harness/results.py` (`peak_swap_mib: int | None = None`),
  `harness/run.py`, `harness/report.py`
- Test: `tests/test_sampling.py`, `tests/test_sample_sh.py` (or the existing sample-script test),
  `tests/test_report.py`

**Interfaces:**
- Produces: CSV header
  `ts,mem_used_mib,vram_used_mib,gtt_used_mib,tctl_c,edge_c,sclk_mhz,cpu_mhz_avg,swap_used_mib`, where
  `swap_used_mib = (SwapTotal - SwapFree) / 1024`, `0` when `SwapTotal` is 0;
  `SampleSummary.peak_swap_mib: int | None`; `AttemptRecord.peak_swap_mib: int | None = None`.
  Report: per-attempt table gains `ram MiB`, `swap MiB`, `offload` columns after `tg tok/s`; summary gains
  `max_peak_mem_mib`, `max_peak_swap_mib`, `min_gpu_offload` (`-` when no values).
- Consumes: `gpu_offload` from Task 2.

- [ ] **Step 1: Write the failing tests**

- `test_summarize_samples_swap` — rows with `swap_used_mib` 259, 1300, 800 → `peak_swap_mib == 1300`.
- `test_summarize_samples_old_csv` — a CSV without the column → `peak_swap_mib is None`.
- `sample.sh` reads `/proc` and `/sys` directly and has no unit test; it is checked live in Step 4.
- `test_report_memory_columns` — two records with `peak_mem_mib` 7494/5112, `peak_swap_mib` 900/None,
  `gpu_offload` 1.0/0.8 → summary `max_peak_mem_mib == 7494`, `max_peak_swap_mib == 900`,
  `min_gpu_offload == 0.8`; the markdown table header contains `| ram MiB | swap MiB | offload |`.
- `test_report_old_records` — the E0 `results.jsonl` renders without error, new columns `-`.

- [ ] **Step 2: Run them to verify they fail** — `uv run pytest -q`, the new tests FAIL.

- [ ] **Step 3: Implement**

- [ ] **Step 4: Run the full suite** — all pass. Live-check the script: copy it to geekoma9, run
  `timeout 3 bash sample.sh /tmp/s.csv 1`, and check the header ends `,swap_used_mib` and each row's last field
  matches `(SwapTotal - SwapFree) / 1024` from `/proc/meminfo`; then repeat with `sudo swapoff -a` and confirm
  the field is `0` (restore with `sudo swapon -a`). Then regenerate the E0 and calibration reports
  (`uv run harness report experiments/e0-baseline`, same for `calibration-frontier`) and check only the new
  columns changed (`git diff experiments/*/README.md`).

- [ ] **Step 5: Commit** — `git commit -m "harness: sample swap; report RAM, swap and GPU offload"`

### Task 4: E1 configs and the `uma24` run

**Files:**
- Create: `experiments/e1-uma24/config.yaml`, `experiments/e1-uma16/config.yaml`,
  `experiments/e1-umamin-gtt24/config.yaml`, `experiments/e1-umamin-probe/config.yaml`
- Modify: `docs/provisioning.md` (an "E1 memory settings" section)

- [ ] **Step 1: Write the configs.** Each copies `experiments/e0-baseline/config.yaml` and changes only
  `id`, `notes` and adds `host`:
  - `e1-uma24`: `host: {vram_gib: 24, gtt_gib: 3.7}`.
  - `e1-uma16`: `host: {vram_gib: 16, gtt_gib: 7.7}` (GTT default = half of Linux RAM; correct it to the
    measured value in Task 5 Step 2 if the BIOS gives a different Linux total).
  - `e1-umamin-probe` (tier `probe`) and `e1-umamin-gtt24` (tier `screening`): `host: {vram_gib: <min>,
    gtt_gib: 24}`, with `<min>` filled in from sysfs in Task 6.
  Check each with `uv run python -c "from harness.config import load_config; load_config('<path>')"`.
- [ ] **Step 2: Write the provisioning section**: the BIOS path and options the owner reports, the kernel
  parameters `ttm.pages_limit=6291456 ttm.page_pool_size=6291456` in `GRUB_CMDLINE_LINUX_DEFAULT` of
  `/etc/default/grub` (backup `/etc/default/grub.bak-e1`), `sudo update-grub`, and the rollback (restore the
  backup, `update-grub`, reboot; BIOS back to 24 GiB).
- [ ] **Step 3: Run `e1-uma24`** on newbuntu (sync, start, wait for the harness process to exit), copy
  results back, `uv run harness report experiments/e1-uma24`. Expected: 6 scored attempts; every record has
  `host_vram_mib` ≈ 24576, `gpu_offload` set, `peak_swap_mib` set.
- [ ] **Step 4: Commit** — `git add experiments docs/provisioning.md && git commit -m "E1: configs; uma24 run"`

### Task 5: `uma16` (owner BIOS change)

- [ ] **Step 1: Owner action.** Ask the owner to set the BIOS UMA frame buffer to 16 GiB, write down the full
  list of UMA options and the menu path (for `docs/provisioning.md`), and reboot. Wait for confirmation.
- [ ] **Step 2: Verify the layout.** `uv run harness provision` passes; read
  `mem_info_vram_total`, `mem_info_gtt_total` and `MemTotal`. If GTT differs from 7.7 GiB by more than
  0.25, set `e1-uma16`'s `gtt_gib` to the measured value (one-line commit).
- [ ] **Step 3: Run `e1-uma16`**, copy back, report. qwen3-coder's 17.3 GiB of weights plus 6 GiB KV cannot
  fit 16 GiB, so expect `gpu_offload` < 1 unless Ollama spills to GTT; the run still goes ahead — that
  measurement is the point.
- [ ] **Step 4: Commit** — `git commit -m "E1: uma16 run"`

### Task 6: `umamin_gtt24` (owner BIOS change + kernel parameters)

- [ ] **Step 1: Owner action and confirmation.** Ask the owner to (a) confirm the kernel parameter change in
  `docs/provisioning.md` and (b) set the BIOS UMA to its smallest option. Wait for both.
- [ ] **Step 2: Kernel parameters.** Back up `/etc/default/grub`, add the two `ttm.` parameters, `sudo
  update-grub`. Announce the reboot to the owner, then `sudo systemctl reboot` and wait for ssh.
- [ ] **Step 3: Verify.** `cat /proc/cmdline` shows both parameters; `mem_info_gtt_total` ≈ 24 GiB;
  `pages_limit` = 6291456. Fill `<min>` into both umamin configs from `mem_info_vram_total`. `harness
  provision` passes.
- [ ] **Step 4: Probe.** Run `e1-umamin-probe`. Go on to Step 5 only if its record has `gpu_offload ≥ 0.95`
  and `tg_tps ≥ 10`. Otherwise Ollama 0.34.4 can't use GTT at a minimal carve-out: write that, with the
  record and the Ollama journal lines about memory, into `experiments/e1-umamin-probe/README.md`, and carry
  `umamin_gtt24` into E2 with llama.cpp Vulkan (its runtime is GTT-capable per `research/memory.md`).
- [ ] **Step 5: Run `e1-umamin-gtt24`** (only if the probe passed), copy back, report.
- [ ] **Step 6: Commit** — `git commit -m "E1: umamin_gtt24 probe and run"`

### Task 7: Decide, restore, write up

**Files:**
- Create: `experiments/e1-memory-split/README.md` (the comparison)
- Modify: `docs/FINDINGS.md`, `docs/provisioning.md`

- [ ] **Step 1: Compare.** A table with one row per variant: VRAM/GTT/Linux RAM, `min_gpu_offload`,
  median tg and pp tok/s, `max_peak_mem_mib`, `max_peak_swap_mib`, passes, solved_per_8h.
- [ ] **Step 2: Decide** with this rule, written into the README:
  1. Drop variants whose `min_gpu_offload` < 1.0 (the model doesn't fit).
  2. Among the rest, drop variants whose swap use grows by more than 512 MiB over the pre-run baseline.
  3. Pick the highest median tg tok/s; break a tie within 5% by pp tok/s, then by passes.
  If none survive step 1, keep uma24 and say so.
- [ ] **Step 3: Restore the winner.** If it isn't the current setting, ask the owner to set the BIOS (and
  roll back or keep the kernel parameters per `docs/provisioning.md`), then verify with `harness provision`
  and the sysfs values.
- [ ] **Step 4: Update `docs/FINDINGS.md`** ("Current best: E1 <variant>") and the provisioning doc's
  record of the final state.
- [ ] **Step 5: Commit**, then ask the owner before pushing:
  `git commit -m "E1 memory split results"`.
- [ ] **Step 6: Hand off:** write the E2 (runtime) plan with `superpowers:writing-plans`, including
  `umamin_gtt24` under llama.cpp Vulkan if Task 6 Step 4 deferred it.
