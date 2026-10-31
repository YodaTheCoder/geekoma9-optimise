# Headless agent harnesses for a local endpoint

Research for E0 and E3. Requirements:
- runs non-interactively from a shell command in a disposable clone on geekoma9;
- talks to a local OpenAI- or Anthropic-compatible endpoint (the harness passes `{endpoint}` =
  usage-proxy base URL, e.g. `http://127.0.0.1:11500`, with no `/v1`);
- works with local models' tool calling;
- writes a log in which steps can be counted.

Template rules, from the plan's `render_command`:
- Only `{workdir} {issue_file} {endpoint} {model} {log}` are allowed. Values are shell-quoted, so
  templates never add their own quotes around a placeholder.
- No other literal `{` or `}` may appear. Configs that need JSON braces are written by the `install`
  command instead.
- stdout and stderr already go to the agent log, so `{log}` is used only as a prefix for side files
  (`{log}.traj.json`).

## Installed on geekoma9 today (2026-10-31)
- `opencode` 1.18.32 (global npm, `/usr/local/bin/opencode`), with an empty `~/.config/opencode/opencode.jsonc`.
- `codex-cli` 0.157.0.
- Node v18.19.1, Python 3.12.3, `uv` 0.12.19 in `~/.local/bin`, and `pipx`.
- Claude Code and mini-swe-agent are not installed.

## Current versions (registries, 2026-10-31)
- opencode-ai 1.19.5 (2026-10-28)
- @anthropic-ai/claude-code 2.1.316 (2026-10-31; npm needs Node ≥ 22, so use the native installer)
- @openai/codex 0.166.0
- @qwen-code/qwen-code 0.26.4 (Node ≥ 22)
- mini-swe-agent 2.4.6 (2026-07-23)
- aider-chat 0.86.2 (2026-02-12, Python < 3.13)

## Shortlist

### opencode (E0 default)
- Headless: `opencode run --auto --format json -m <provider>/<model> "<prompt>"`.
  - `--auto` approves every permission not explicitly denied.
  - `--format json` emits JSONL events: `step_start`, `text`, `tool_use`, `step_finish` and `error`.
  - The config path comes from `OPENCODE_CONFIG`.
- Local endpoint: a custom provider using `@ai-sdk/openai-compatible`, with `options.baseURL`. Values can use
  `{env:VAR}` substitution, so the base URL comes from `BENCH_ENDPOINT` at run time. Custom providers must list
  their models, so the install config lists every shortlisted model ID. `includeUsage: true` makes streamed
  responses carry `usage`, which the usage proxy needs.
- Fixed prompt overhead is about 7k tokens (against about 33k for Claude Code, per a third-party measurement).
- Tool-calling compatibility:
  - North Mini Code was trained for OpenCode.
  - qwen3-coder and devstral through Ollama can flip to Hermes-XML tool calls when the system prompt
    contains large XML skill lists (#24824). The bench clone has no skills, which keeps the prompt small.
  - Gemma 4 needed a patched OpenCode in April 2026.
- Steps regex: `"type":"tool_use"`, one event per completed tool call.

### claude-code
- Headless: `claude -p --dangerously-skip-permissions --output-format stream-json --verbose`.
- Local endpoint:
  - Ollama (v0.14+) and llama-server (since January 2026) both serve the Anthropic Messages API.
  - Set `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL` and `ANTHROPIC_DEFAULT_HAIKU_MODEL`, so
    background calls also go to the local model.
- Cost: about 29k tokens of fixed prompt for a trivial request, 81% of it tool definitions (measured June 2026).
  At about 250 tok/s PP on geekoma9, that is about 2 minutes per cache miss.
- Two settings cut this:
  - `--bare` skips hooks, skills, plugins, MCP and CLAUDE.md discovery.
  - `CLAUDE_CODE_ATTRIBUTION_HEADER=0` keeps the prompt prefix stable, so local prefix caches hit.
- The template uses both. It is also the frontier calibration harness in the plan (Task 15), so including it
  shows how much of any gap is the harness rather than the model.
- Known issue: hangs with small local models through the Anthropic route (claude-code #51239).
- Install: the native installer, because geekoma9's Node 18 is below the npm package's `>=22`.
- Steps regex: `"type":"tool_use"`, one per tool-use block in stream-json.

### mini-swe-agent
- What it is:
  - About 100 lines of agent logic with a single bash tool, no file-edit tools, and LiteLLM for models.
  - It is the harness behind the SWE-bench "bash-only" leaderboard, which compares models under one fixed
    minimal scaffold.
  - Smallest prompt of the three, and the least sensitive to tool-call formats.
- Headless: `mini -y --exit-immediately -l 0 -m openai/<model> -t "<task>" -o <traj>`.
  - Model kwargs are overridden with `-c key=value`.
  - `MSWEA_COST_TRACKING=ignore_errors` stops it failing on unknown local-model prices.
- Caveat: one user saw much lower solve rates with gpt-oss:120b on Ollama than published (#798).
- Steps regex: `mini-swe-agent \(step \d+` matches the per-step header printed to the console. This is unverified.

### Considered, not shortlisted
- **Codex CLI** (0.157.0 already installed): `codex exec --oss` supports local providers, but it
  targets the Responses API. Ollama's support for that is newer, and llama-server's is uncertain.
- **Aider** (0.86.2): uses text edit formats, not tool calls, so it is robust with local models. But it is not an
  autonomous agent loop (no shell exploration or test running without `--yes` scripting), and
  its last release was February 2026.
- **Qwen Code**: needs Node ≥ 22, and it is tuned for Qwen models only.
- **pool** (poolside): designed for Laguna, ACP-oriented, and its headless mode is undocumented.

## E0 default harness

`e0_default_harness: opencode`. It is already installed on geekoma9. It runs headless with countable JSON events,
speaks plain OpenAI chat completions that work unchanged on Ollama and llama-server, and its fixed prompt (about 7k
tokens) costs roughly a quarter of Claude Code's (about 33k) on a PP-bound iGPU.

## To verify before E0 (Task 16 dry run)
- `{env:BENCH_ENDPOINT}` substitution in `options.baseURL`. The docs show it only for `apiKey`.
- The exact `tool_use` JSON spacing in `opencode run --format json`, so the regex matches.
- That `--bare` exists in claude-code 2.1.316 and still honours `ANTHROPIC_*` env auth.
- The `mini` console step-header format, and whether chained `-c mini.yaml -c key=value` works in v2.4.6.

## Sources
- geekoma9 `opencode --version`, `codex --version`, `node --version` (2026-10-31).
- https://registry.npmjs.org/opencode-ai
- https://registry.npmjs.org/@anthropic-ai/claude-code
- https://pypi.org/project/mini-swe-agent/
- https://opencode.ai/docs/cli/
- https://opencode.ai/docs/providers/
- https://littlebearapps.com/help/untether/opencode-stream-json-cheatsheet/
- https://github.com/anomalyco/opencode/issues/24824
- https://www.kunalganglani.com/blog/opencode-vs-claude-code-token-overhead.md
- https://mykolaaleksandrov.dev/posts/2026/06/claude-code-huge-prompt-investigation/
- https://docs.ollama.com/api/anthropic-compatibility
- https://registry.ollama.ai/blog/claude
- https://huggingface.co/blog/ggml-org/anthropic-messages-api-in-llamacpp
- https://github.com/anthropics/claude-code/issues/51239
- https://github.com/SWE-agent/mini-swe-agent
- https://mini-swe-agent.com/latest/usage/mini/
- https://mini-swe-agent.com/latest/models/local_models/
- https://swebench.com/bash-only.html
- https://github.com/SWE-agent/mini-swe-agent/issues/798
- https://codex.danielvaughan.com/2026/04/10/gemma-4-local-model-codex-cli
