# Coding models for about 24 GB with context

Research for E3 and E4. The constraint is about 90 GB/s of bandwidth, so MoE with about 3–4B active
parameters is essential. The dense 27–28B models already on the box measure 4–5 tok/s, against
13–27 tok/s for the MoE models (`runtimes.md`). Weights plus KV plus compute buffers must fit in the GPU
pool (24 GiB today) while leaving Linux room for the harness and headless Godot.

The sizes in GB below are decimal file sizes (Ollama `/api/tags` or Hugging Face). The KV figures were
measured from the Ollama logs on geekoma9 (`memory.md`).

## Shortlist

| Model | Ollama ref (pulled) | Total / active | Weights | KV at 64k | Vendor SWE-bench Verified | Measured TG / PP (geekoma9, Ollama ROCm) |
|---|---|---|---|---|---|---|
| Qwen3-Coder-30B-A3B-Instruct | `qwen3-coder:30b` (Q4_K_M) | 30.5B / 3.3B | 18.6 GB | 6.0 GiB | not on the model card | 13.2 / ~200–280 at 15–39k |
| Laguna XS 2.1 (poolside) | `laguna-xs-2.1:q4_K_M` | 33.4B / 3B | 20.3 GB | ~2.7 GiB (est.) | 70.9 | 26.8 / 529 at 6k |
| North Mini Code 1.0 (Cohere) | `north-mini-code-1.0:q4_K_M` | 30.5B / 3B | 18.6 GB | ~2.2 GiB (est.) | 67.6 | 27.1 / 570 at 6k |
| gpt-oss-20b (OpenAI) | `gpt-oss:20b` (MXFP4) | 20.9B / 3.6B | 13.8 GB | ~1.5 GiB (est.) | 60.7 (high reasoning) | 20.2 / 740 at 6k |

### Qwen3-Coder-30B-A3B (E0 baseline model)
- Context: 262144 native (YaRN to 1M). Recommended sampling: temp 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05.
- Tool calling: Qwen's own "specially designed function call format" (XML). llama.cpp added a dedicated
  Qwen3-Coder XML parser (PR #16755), though the model "occasionally" drops the `<tool_call>` prefix.
  In OpenCode through Ollama, large XML-heavy system prompts can push it into Hermes-style XML that OpenCode
  cannot parse (opencode #24824, April 2026, closed without a fix). An independent MCP test
  (PromptQuorum, September 2026, Cline and Goose through Ollama) measured about 96% well-formed calls on code tools
  and about 91% on others.
- GDScript: no local benchmark found. Qwen-family evidence is indirect: Qwen3.6-35B-A3B was the top
  local model (8.7/10) in an informal Godot 4 test (note.com, May 2026). Qwen3.7 Max scored 13/15 first try
  on Flockbay's headless Godot bench.
- Memory: full attention, so at 64k f16 KV it is about 23.5 GiB, the tightest fit of the four. E4 should
  test q8_0 KV. Unsloth GGUF quants include UD-Q4_K_XL (17.7 GB), Q4_K_M (18.6) and Q5_K_M (21.7).

### Laguna XS 2.1 (poolside)
- 33B total, 3B active, 256 experts plus a shared expert, 262144 context, OpenMDW-1.1 licence.
  Vendor figures: SWE-bench Verified 70.9, SWE-bench Multilingual 63.1, SWE-Bench Pro 47.6, Terminal-Bench 2.0 37.5.
- Tool calling: own `poolside_v1` parser in vLLM (or `glm47` on older builds). Ollama says reasoning and
  tool calls "work out of the box" via its built-in template. Upstream llama.cpp **needs a PR build** for
  this architecture (model card), so check that the E2 llama.cpp builds load it before relying on it.
  Benchmarks were run with thinking on, at temp 1.0 and top_k 20.
- GDScript: its larger sibling **Laguna S 2.1 scored only 9/15 first try and 12/15 after one fix** on Flockbay's
  headless Godot 4.7.2 bench (October 2026). DeepSeek, Kimi and GLM scored 14–15/15 there. This is a warning
  sign for the XS model.
- Memory: largest weights (20.3 GB) but cheap KV. Only an official Q4_K_M or BF16 GGUF exists.

### North Mini Code 1.0 (Cohere, 2026-06-09)
- 30B total, 3B active MoE, Apache-2.0, 256K input and 64K output (the GGUF metadata reports 500000).
  Model card: SWE-bench Verified 67.6 (SWE-Agent v1.1.0), SWE-Bench Pro 40.2, Terminal-Bench 2 36.
  Sampling: temp 1.0, top_p 0.95.
- Tool calling: "specifically trained for compatibility with OpenCode, but it works with most coding agents".
  The vLLM parser is `cohere_command4`. No llama.cpp parser is documented, so verify tool calls under
  `llama-server --jinja` in E2.
- GDScript: no evidence found.
- Memory: Unsloth GGUFs include UD-Q4_K_XL (19.3 GB), MXFP4_MOE (18.7) and UD-Q5_K_M (23.0).

### gpt-oss-20b (OpenAI)
- 21B total, 3.6B active, MXFP4 native, 131072 context. SWE-bench Verified 60.7 at high reasoning (model card),
  independently reproduced at 60.4 (arXiv 2604.00362).
- Tool calling: Harmony format, supported in Ollama and llama.cpp. Earlier GGUF tool-call bugs were reported fixed
  over time. It is weak at forced JSON output (glukhov.org). One mini-swe-agent user with gpt-oss:120b on Ollama
  got far below published scores (mini-swe-agent #798).
- GDScript: no evidence found.
- Why it is here: smallest footprint (13.8 GB). It is the only candidate that fits a **16 GiB UMA** with context
  (E1 variant `uma16`), and it gives the most room for 128k context.

## Considered, not shortlisted
- `gemma4:26b-a4b-it-q4_K_M` (pulled, 25.8B, about 4B active, 18.0 GB): the best measured PP on geekoma9
  (430–510 tok/s at 1–16k) at 22 tok/s TG. It is the **first reserve**. Tool calling was broken in Ollama 0.20 (#15241),
  and community setups needed `llama.cpp --jinja` plus patches. In an informal GDScript test it scored 6.5/10 against 8.7 for Qwen3.6-35B-A3B.
- `Qwen3.6-35B-A3B`: SWE-bench Verified 73.4 (vendor) and the best informal GDScript result, but the Q4 download is about 24 GB, so it does
  not fit 24 GiB with context. It is a candidate for the minimal-UMA plus 24 GiB GTT variant at an IQ4_XS or Q3-class quant
  (`unsloth/Qwen3.6-35B-A3B-GGUF`). Revisit after E1. It is not pulled.
- `GLM-4.7-Flash` (30B/3B, 19 GB, SWE-V 59.2): not pulled, and Unsloth flagged Ollama template problems.
- Dense `qwen3.8:27b` and `muse-glimmer:30b` (pulled): 4–5 tok/s measured, too slow.
- `Qwen3-Coder-Next` (80B/3B): 52 GB at Q4, which does not fit.

## GDScript evidence (summary)
There is no published GDScript benchmark that includes any of the shortlisted local models. The best harness is
Flockbay's `godot-llm-bench` (15 tasks, run headless on Godot 4.7.2). Common failures are Godot 3 idioms
(`KinematicBody2D`, `move_and_slide()` with arguments, `export var` without `@`) and changed APIs (`FileAccess`,
`JSON`, lambda capture). Our own benchmark is the real test. The task set should include those traps.

## Sources
- geekoma9 `ollama show`, `/api/tags` and journal (2026-10-31).
- https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct
- https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF
- https://ollama.com/library/qwen3-coder
- https://github.com/ggml-org/llama.cpp/pull/16755
- https://github.com/anomalyco/opencode/issues/24824
- https://www.promptquorum.com/power-local-llm/best-local-models-tool-calling-2026
- https://www.promptquorum.com/prompt-bites/best-moe-models-local-coding
- https://huggingface.co/poolside/Laguna-XS-2.1
- https://huggingface.co/poolside/Laguna-XS-2.1-GGUF
- https://cohere.com/blog/north-mini-code
- https://huggingface.co/CohereLabs/North-Mini-Code-1.0
- https://huggingface.co/unsloth/North-Mini-Code-1.0-GGUF
- https://arxiv.org/pdf/2508.10925
- https://arxiv.org/pdf/2604.00362
- https://huggingface.co/ggml-org/gpt-oss-20b-GGUF
- https://www.glukhov.org/llm-performance/ollama/ollama-gpt-oss-structured-output-issues/
- https://github.com/SWE-agent/mini-swe-agent/issues/798
- https://codex.danielvaughan.com/2026/04/10/gemma-4-local-model-codex-cli
- https://github.com/flockbay/godot-llm-bench
- https://flockbay.com/blog/best-ai-for-godot/
- https://note.com/dapper_crab2524/n/n1d72e66c9e46
- https://www.morphllm.com/best-ollama-models
- https://insiderllm.com/guides/best-local-coding-models-2026/
