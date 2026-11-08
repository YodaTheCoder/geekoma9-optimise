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

Best first-time success: `laguna-xs-2.1` Q4_K_M at 128k context, 15/18 (0.83) but 34.7 solved per 8 h and up to
7.1 GiB RAM (`experiments/e4-laguna-ctx128k/`). Runtimes: Ollama 0.34.4 matches or beats llama.cpp Vulkan and ROCm run directly (`experiments/e2.md`).
Harnesses: OpenCode beats mini-swe-agent and Claude Code for both
models (`experiments/e3-harness.md`). Models: `experiments/e3-screen.md`.

Previous best: E0 baseline (`qwen3-coder:30b`, 64k, uncapped prompt cache), 2/6 on the single-run screening tier.

Upper bound: Claude Code with Claude Opus solved 12/12 (`experiments/calibration-frontier/`).

Next: E5 finalists. E1 (smaller UMA) is paused: with the
llama-server cache caps, Linux keeps at least 2.2 GiB free at 24 GiB UMA.
