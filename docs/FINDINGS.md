# Findings

## Current best: E4 qwen3-coder 32k (throughput)

| | |
|---|---|
| Config | 24 GiB UMA, Ollama 0.34.4 (ROCm), `qwen3-coder:30b` Q4_K_M, f16 KV, 32k context, `LLAMA_ARG_CACHE_RAM=1024`, OpenCode 1.18.32 |
| Pass rate (screening3, 6 tasks x 3) | 12/18 (0.67) |
| `solved_per_8h` | 147.7 by agent time |
| Generation / prompt processing | 27.8 / 4,126 tok/s (median) |
| Memory | fully on the GPU; peak RAM 3.9 GiB, swap 0.4 GiB |
| Evidence | `experiments/e4-qwen-ctx32k/`, comparison in `experiments/e4.md` |
| Finalists (12 tasks x 3) | 21/36 (0.58), 112.4 solved per 8 h (`experiments/e5.md`) |

Best first-time success: `laguna-xs-2.1` Q4_K_M at 64k context, 25/36 (0.69) on the finalists tier at 33.0 solved
per 8 h; 128k scored 26/36 but spills 10% off the GPU and peaks at 7.1 GiB RAM (`experiments/e5.md`). Runtimes: Ollama 0.34.4 matches or beats llama.cpp Vulkan and ROCm run directly (`experiments/e2.md`).
Harnesses: OpenCode beats mini-swe-agent and Claude Code for both
models (`experiments/e3-harness.md`). Models: `experiments/e3-screen.md`.

Previous best: E0 baseline (`qwen3-coder:30b`, 64k, uncapped prompt cache), 2/6 on the single-run screening tier.

Upper bound: Claude Code with Claude Opus solved 12/12 (`experiments/calibration-frontier/`).

Next: qwen3-coder on llama.cpp Vulkan at the finalists tier (its tool-call parser accepts a missing
`<tool_call>` tag that Ollama's rejects), and a memory cap for Godot during scoring. E1 (smaller UMA) is paused: with the
llama-server cache caps, Linux keeps at least 2.2 GiB free at 24 GiB UMA.
