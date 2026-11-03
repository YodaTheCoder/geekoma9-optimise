# E3 model screen at uma24 (2026-11-01 to 2026-11-03)

Five models, same setup otherwise: BIOS UMA 24 GiB (Linux 7.4 GiB RAM, 8 GiB swap), Ollama 0.34.4 (ROCm),
64k context, OpenCode 1.18.32, screening tasks x 3 runs (`screening3`, 18 scored attempts each).
Per-attempt tables are in each `e3-screen-<model>/README.md`.

| model | pass | 001 | 004 | 005 | 007 | 009 | 011 | median min/attempt | median gen tokens | gen tok/s | solved per 8h (agent time) | GPU offload | OOM retries |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| laguna-xs-2.1 | 12/18 | 3 | 3 | 1 | 1 | 3 | 1 | 6.8 | 6822 | 35.8 | 27.9 | 1.00 | 0 |
| north-mini-code-1.0 | 10/18 | 2 | 3 | 1 | 0 | 3 | 1 | 4.1 | 4478 | 24.7 | 41.3 | 1.00 | 7 |
| qwen3-coder:30b | 9/18 | 3 | 3 | 0 | 0 | 2 | 1 | 2.0 | 1900 | 25.3 | 90.4 | 0.96 | 0 |
| gemma4:26b-a4b | 9/18 | 3 | 3 | 0 | 1 | 2 | 0 | 8.1 | 8485 | 22.1 | 39.2 | 1.00 | 16 |
| gpt-oss:20b | 4/18 | 2 | 1 | 0 | 1 | 0 | 0 | 2.5 | 2455 | 22.6 | 23.7 | 1.00 | 0 |

## Findings

- **The runs were memory-starved, and the cause is Ollama's prompt cache, not the model's fit.** Ollama starts
  `llama-server` with its default host-RAM prompt cache ("prompt cache is enabled, size limit: 8192 MiB"),
  larger than the 7.4 GiB Linux has. Every killed `llama-server` held 5.8–6.3 GB of anonymous RAM although
  `/api/ps` showed the whole model on the GPU. The kernel logged 157 OOM kills over the screen (23
  `llama-server`, 12 `ollama`, 7 `opencode`, the rest system daemons); the harness retried the 23 affected
  attempts plus 3 ssh timeouts as `infra_error`. Swap peaked at 4.3–6.2 GiB for every model except gpt-oss.
  Results are therefore usable for ranking but slowed by swapping, and an overnight runner cannot run like this.
- **Quality:** laguna 12/18, north-mini 10/18, qwen3-coder and gemma4 9/18, gpt-oss 4/18. Only gpt-oss is
  clearly worse; 12 vs 9 of 18 is within noise. Tasks 005 (`.tscn` scene) and 007 (patrol enemy) separate
  the models least well: nobody passes them reliably.
- **Throughput is a different order:** qwen3-coder solves the most per hour (90 per 8 h of agent time) because it
  writes 3–4x fewer tokens per attempt. Laguna and gemma4 write the most (median 6.8k and 8.5k tokens),
  which makes them the slowest per attempt even though laguna generates fastest (35.8 tok/s).
- gpt-oss is dropped. The four others go forward once the prompt cache is capped and the screen re-run.
