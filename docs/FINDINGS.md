# Findings

## Current best: E5 qwen3-coder 32k on llama.cpp Vulkan (throughput)

| | |
|---|---|
| Config | 24 GiB UMA, llama.cpp b12191 Vulkan `llama-server` (same GGUF as Ollama's `qwen3-coder:30b` Q4_K_M), f16 KV, 32k context, `LLAMA_ARG_CACHE_RAM=1024`, OpenCode 1.18.32 |
| Pass rate (finalists, 12 tasks x 3) | 25/36 (0.69) |
| `solved_per_8h` | 120.6 by agent time |
| Generation / prompt processing | 24.4 / 5,495 tok/s (median) |
| Memory | fully on the GPU; peak RAM 3.7 GiB, swap 0.8 GiB |
| Evidence | `experiments/e5-vk-qwen-ctx32k/`, comparison in `experiments/e5.md` |

The same model on Ollama 0.34.4 scored 21/36 (112.4 solved per 8 h): its `qwen3-coder` parser drops tool calls
missing the opening `<tool_call>` tag, which ended 3 attempts at once. Previous best: E4 qwen3-coder 32k on Ollama,
12/18 on screening3 (`experiments/e4-qwen-ctx32k/`).

Best first-time success: `laguna-xs-2.1` Q4_K_M at 64k context, 25/36 (0.69) on the finalists tier at 33.0 solved
per 8 h; 128k scored 26/36 but spills 10% off the GPU and peaks at 7.1 GiB RAM (`experiments/e5.md`). Runtimes: llama.cpp Vulkan for qwen3-coder (above); Ollama 0.34.4 for laguna (`experiments/e2.md`).
Harnesses: OpenCode beats mini-swe-agent and Claude Code for both
models (`experiments/e3-harness.md`). Models: `experiments/e3-screen.md`.

Previous best: E0 baseline (`qwen3-coder:30b`, 64k, uncapped prompt cache), 2/6 on the single-run screening tier.

Upper bound: Claude Code with Claude Opus solved 12/12 (`experiments/calibration-frontier/`).

Next: a second qwen finalists run on each runtime to confirm the gap, the llama-server generation gap
(about 12% slower than Ollama on the same GGUF), and a memory cap for Godot during scoring. E1 (smaller UMA) is paused: with the
llama-server cache caps, Linux keeps at least 2.2 GiB free at 24 GiB UMA.
