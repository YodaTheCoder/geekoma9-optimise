# Findings

## Current best: E0 baseline

| | |
|---|---|
| Config | 24 GiB UMA, Ollama 0.34.4 (ROCm), `qwen3-coder:30b`, 64k context, OpenCode 1.18.32 |
| Pass rate (screening, 6 tasks) | 2/6 (0.33) |
| `solved_per_8h` | 60.4 by agent time (about 29 including per-attempt setup and scoring) |
| Generation / prompt processing | 25.3 / 3,828 tok/s (median) |
| Evidence | `experiments/e0-baseline/` and the `exp/e0-baseline-202610311713/*` branches of `YodaTheCoder/godot-agent-bench` |

Upper bound: Claude Code with Claude Opus solved 12/12 (`experiments/calibration-frontier/`).

Next: E1, memory split. E0 leaves almost no headroom: 23.7 of 24 GiB of GPU memory used, and system RAM at the
limit while Godot and the agent run.
