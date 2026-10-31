# Multi-stack benchmarks — design

Date: 2026-10-31
Status: draft, awaiting review
Builds on: `docs/superpowers/specs/2026-10-31-coding-agent-optimisation-design.md`

## Goal

Let the harness benchmark local coding agents on the stacks the owner works in most, not only Godot, so
geekoma9 can be tuned for whichever project is in flight. Two new public benchmarks:

- **ts-agent-bench**: a TypeScript full-stack app (React/Vite front end, Node API), tested with vitest.
- **py-agent-bench**: a Python CLI/automation tool with data processing (a trading-strategy backtester),
  tested with pytest.

The Godot benchmark stays the vehicle for the E1–E5 sequence now under way. Nothing in this design changes
its results.

## Decisions (owner)

- JS stack: TypeScript full-stack. Python stack: CLI/automation with data processing, e.g. backtesting.
- Dependencies are fixed per benchmark: agents cannot add packages; scoring is offline.
- Scoring is made pluggable with a per-benchmark manifest (approach A below).
- Results are per stack with the same metrics; there is no blended cross-stack score.
- The owner defers the remaining harness and benchmark details to this spec.

## Scope

In: the manifest and generic scorer, the shared-dependency mechanism, the harness changes, the design of
both benchmark repos, their validation and calibration, and how results are reported.

Out: building it now (it follows E1 unless the owner asks sooner), changing the Godot task set, a blended
score, and the production runner pipeline.

## 1. Benchmark manifest and generic scorer

Each benchmark repo carries `bench.yaml` at its base tag. The harness reads it only from the pristine
mirror (`git show base-<ts>:bench.yaml`), never from the agent's copy.

```yaml
schema: 1
name: ts-fullstack
review_context: "TypeScript full-stack app (React/Vite front end, Node API), tested with vitest"
toolchain:                      # checked by `harness provision`; usable in commands as {tool:<name>}
  node: {path: /home/markn/agentbench/opt/node/bin/node, version: "v22.11.0"}
protected:                      # restored from the base commit before scoring
  [tests/regression, package.json, package-lock.json, tsconfig.json, tsconfig.node.json, vitest.config.ts]
hidden_tests: {dest: tests/hidden, glob: "*.test.ts"}
deps: {lockfile: package-lock.json, install: "npm ci --ignore-scripts", link: node_modules}
env: {CI: "1"}
agent_env: {npm_config_offline: "true"}
build: {cmd: "npx tsc --noEmit -p .", timeout_s: 300}
suites:
  regression: {cmd: "npx vitest run tests/regression --reporter=junit --outputFile={junit}", timeout_s: 600}
  hidden:     {cmd: "npx vitest run tests/hidden --reporter=junit --outputFile={junit}", timeout_s: 600}
```

Fields:

- `build` decides `parse_ok`: `ok_exit: [0]` by default (`any` allowed), plus optional `fail_patterns`
  (regexes; any match in the build log means not ok). Godot's import exits 0 on parse errors, so its manifest
  uses `ok_exit: any` and today's patterns (`SCRIPT ERROR: Parse Error`, `Failed to load script`).
- `suites` must define `regression` and `hidden`; each writes JUnit to `{junit}`.
- Placeholders in commands: `{junit}`, `{project}`, `{tool:<name>}`. Anything else is an error.
- `score_extra.sh` (per task, optional) is kept: it is called as `score_extra.sh <project> <out_dir>` with
  each toolchain path exported as `BENCH_TOOL_<NAME>`, and may overwrite `hidden.xml` as today.

`score.sh` stays the one scorer, with its steps driven by the manifest: copy the agent's work, restore
`protected`, copy hidden tests matching the glob, link dependencies, run `build`, run each suite, run the
optional extra, write `score.json`. A small Python helper (`harness/manifest.py`) validates the manifest and
renders the exact command lines, so `score.sh` never parses YAML. `score.json` keeps today's keys, with
`import_*` renamed `build_*`; `load_score` reads either name so old runs still load.

Validation is strict (unknown keys, a missing suite, a `protected` path absent at base, an unknown
placeholder) and runs in `harness provision` and before every experiment, never mid-run.

**Godot parity.** The Godot benchmark gets a `bench.yaml` reproducing today's behaviour exactly: protected
`tests/regression`, `addons/gut`, `.gutconfig.json` (only if present at base, as now); hidden glob `*.gd`;
build `{tool:godot} --headless --path {project} --import`; the two GUT command lines. Because adding the file
needs a new tag on a public repo, the harness ships the Godot v1 manifest as a built-in fallback used when
`bench.yaml` is absent at `base-v1`, so the existing tags never move. A live test (marked like the existing
live tests, run against geekoma9) scores the v1 oracle and null workdirs of every task with the old and the
new scorer and requires the same `(parse_ok, hidden, regression)` from `load_score` for each.

## 2. Dependencies and the agent's environment

- `harness provision` installs each benchmark's dependencies once from the lockfile at its base tag into
  `~/agentbench/deps/<bench>/<sha256 of lockfile>/`, then makes that folder read-only (`chmod -R a-w`).
  This is the only network step. npm runs with `--ignore-scripts`; Python dependencies are wheels via
  `uv sync --frozen`.
- `prepare_workdir` and the scorer's copy get `deps.link` (`node_modules` or `.venv`) as a symlink to that
  folder. Agents can import and run the tests but cannot change installed packages.
- Toolchains are pinned in `~/agentbench/opt/` (Node 22, `uv` and its managed Python 3.12), as Godot is now,
  and put first on `PATH` for both agent and scorer.
- `agent_env` is exported into the agent's environment by `CommandAgent` (npm offline; `UV_OFFLINE=1` and
  `UV_NO_SYNC=1` for Python), so an attempted install fails at once instead of hanging or reaching the network.
- Every issue states that dependencies are fixed and gives the commands to run the tests.
- Folders are keyed by lockfile hash, so a later task set with different dependencies cannot disturb old ones.

Accepted limit: if a task would be easier with a package that isn't installed, the agent has to write the
code. That is scored as normal.

## 3. Harness changes

- **Benchmark registry** `harness/benchmarks.py`: name → clone URL, push URL (an ssh host alias per deploy
  key) and mirror path `~/agentbench/mirrors/<name>.git`. Entries: `godot` (today's URLs and mirror path, kept
  as is), `ts-fullstack`, `py-backtest`. GitHub deploy keys are per repo, so each benchmark gets its own key and
  host alias, provisioned like the Godot one.
- **Experiment config** gains `benchmark: <name>`, default `godot`, so every existing config is unchanged.
  Records add `versions["benchmark"]`.
- **Task lists** move into the benchmark: `tasks.yaml` at the taskset tag lists `all`, `screening` and `probe`
  tasks and each task's expected hidden-test count. The harness uses it instead of `TASK_SETS`; Godot v1 keeps
  today's `TASK_SETS` table as its built-in fallback, unchanged. The
  expected count also fixes the known gap where tests that fail to load report `0/0`: `hidden_total` becomes
  the expected count when the JUnit file has fewer cases.
- **Provision** runs per registered benchmark: mirror, deploy key, toolchain versions, dependency folder
  present and read-only, manifest valid.
- **Preflight** additionally fails if any process has its working directory under `~/agentbench/runs/`
  (via `/proc/*/cwd`), which catches stray `node`/`python` test runs that the current command-line pattern
  would miss.
- **Review prompt** takes `review_context` from the manifest instead of the fixed Godot wording.

## 4. The two benchmark repos

Both follow the Godot repo's structure: `main` is the base project with regression tests; hidden tests,
reference solutions and `tasks.yaml` live on the `tests` branch; tags `base-v1` and `taskset-v1`; about 12
tasks (4 small, 5 medium, 3 large) worded like production issues; one task is "write tests", scored by
mutants as in Godot task 012.

**ts-agent-bench** — a small team task-board app.
- `src/server`: Hono on Node 22 with the built-in `node:sqlite` (no native modules, so `--ignore-scripts`
  costs nothing); `src/client`: React 18 + Vite; `src/shared`: types and validation shared by both.
- Tests: vitest; API tests call the Hono app in-process (`app.request`), component tests use jsdom and
  Testing Library. No browser, no network, no ports.
- Build check: `tsc --noEmit` over client, server and shared.
- Task kinds: fix a bug (wrong sort, off-by-one pagination); add an endpoint with validation; add a component
  with state; a cross-cutting feature touching shared types, API and UI (e.g. labels with filtering); a
  refactor (extract a data-access layer); a schema migration; write tests for an untested module.

**py-agent-bench** — `bt`, a backtesting CLI.
- Python 3.12 with `uv`; `click` for the CLI, `pandas` and `numpy` for data, TOML config. Price data is
  committed CSV fixtures, so nothing is fetched.
- Modules: data loading and resampling, strategies (e.g. moving-average crossover), a broker/portfolio
  simulator (orders, fees, slippage), metrics (returns, max drawdown, Sharpe), and reports (CSV/Markdown).
- Tests: pytest, with CLI tests through `click.testing.CliRunner`.
- Build check: `python -m compileall -q src` plus `ruff check --select F` (undefined names, bad imports:
  the class of error behind E0's `minimax`), with `ruff` pinned in the locked dependencies.
- Task kinds: fix a bug (look-ahead bias, fee rounding); add a metric; add a strategy with parameters; add a
  CLI subcommand and option; a cross-cutting feature (position sizing through config, broker and report); a
  refactor (strategy plugin registry); write tests for an untested module.

Hidden tests for both are deterministic: fixed seeds, fixture data, no clock or network.

## 5. Validation, calibration and results

- Per benchmark, before any local-model run: `harness validate` (oracle must pass and null must fail on
  every task), then one frontier calibration run with Claude Opus (about $4–5, as for Godot) and a review.
- Experiment ids are prefixed by benchmark (`ts-e0-baseline`, `py-e0-baseline`); evidence branches go to that
  benchmark's repo.
- `docs/FINDINGS.md` gets a "current best" per benchmark.
- Experiment sequence per new stack: E0 at the then-best Godot machine config, then E3/E4 (model × harness,
  quant and context) in full, since those depend on the stack. E1/E2 (memory split, runtime) are machine-level:
  a stack re-runs them only if its E0 shows different memory pressure (peak RAM or swap) from Godot's.

## Build order

Each is its own implementation plan:

1. Harness generalisation: manifest, generic scorer, registry, `tasks.yaml`, preflight and review changes,
   with Godot parity proven. No new benchmark yet.
2. Dependency mechanism (shared read-only deps, `agent_env`, toolchain pins).
3. py-agent-bench (smaller toolchain, so it proves step 2 first), then validation and calibration.
4. ts-agent-bench, then validation and calibration.

Owner actions: creating each public repo and adding its deploy key; the calibration spend; first pushes.

## Testing

- Unit tests: manifest validation and rendering, `tasks.yaml` loading, `hidden_total` from expected counts,
  registry lookups, the cwd-based stray check, `load_score` reading old and new keys.
- Godot parity test (section 1).
- Each new benchmark: oracle/null validation and calibration, as for Godot.
