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

## Re-run with memory caps (2026-11-03)

Same setup plus two `llama-server` limits passed through `runtime.env` (Ollama forwards its environment):
`LLAMA_ARG_CACHE_RAM=1024` (prompt cache 1 GiB instead of 8 GiB) for all models, and
`LLAMA_ARG_CTX_CHECKPOINTS=4` (instead of 32) for the sliding-window models. gpt-oss was not re-run.

| model | experiment | pass | 001 | 004 | 005 | 007 | 009 | 011 | median min/attempt | median gen tokens | gen tok/s | PP tok/s | peak RAM MiB | peak swap MiB | solved per 8h (agent time) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| laguna-xs-2.1 | `e3-cap-laguna` | 14/18 | 3 | 3 | 2 | 3 | 3 | 0 | 9.0 | 8968 | 34.4 | 4619 | 5016 | 397 | 34.0 |
| qwen3-coder:30b | `e3-cap-qwen3-coder` | 11/18 | 3 | 1 | 0 | 3 | 3 | 1 | 2.2 | 2360 | 27.4 | 4353 | 4650 | 483 | 131.6 |
| gemma4:26b-a4b | `e3-ckpt-gemma4` | 9/18 | 3 | 3 | 0 | 0 | 3 | 0 | 7.2 | 8411 | 23.7 | 2204 | 5004 | 412 | 29.7 |
| north-mini-code-1.0 | `e3-ckpt-north-mini` | 8/18 | 3 | 3 | 0 | 0 | 2 | 0 | 4.1 | 5543 | 26.6 | 2609 | 5221 | 478 | 42.1 |

`e3-cap-north-mini` (prompt cache capped, checkpoints not) is kept as the evidence for the second leak: 10/18,
peak RAM 7.5 GiB, swap 5.8 GiB, no OOM kills. A prompt-cache-only gemma4 run was stopped in its first attempt
once the cause was found and has no results.

### Findings

- **Both leaks are in `llama-server`'s host-RAM caches, not the model's fit.** The 8 GiB prompt cache hit every
  model; context checkpoints (32 x ~200 MiB for gemma4) hit the sliding-window models only. With both capped,
  every model peaks at 4.6–5.2 GiB RAM and under 0.5 GiB swap at the 24 GiB UMA split, with no OOM kills in
  72 attempts. Only ssh timeouts from newbuntu remain as infra errors (2).
- **The caps cost nothing measurable:** pass counts and speeds are the same or better than uncapped. Prompt
  processing rose for every model (qwen 2420 -> 4353, north-mini 1534 -> 2609 tok/s), most likely because
  nothing is swapping.
- **Quality, pooling both screens (36 attempts each):** laguna 26/36, qwen3-coder 20/36, gemma4 18/36,
  north-mini 18/36 (+10/18 in the cache-only run). Laguna is ahead on both screens; the others are within noise
  of each other.
- **Throughput:** qwen3-coder solves about 4x as many tasks per hour of agent time as laguna (131.6 vs 34.0 per
  8 h) because it writes about 4x fewer tokens per attempt (2.4k vs 9.0k), at a lower pass rate. For an overnight
  queue of issues this favours qwen3-coder; for issues that must be solved first time it favours laguna.
- **For E1:** with the caps, Linux has about 2.3 GiB to spare at 24 GiB UMA, so the case for giving the GPU less
  memory is now weak for these models. A smaller UMA remains relevant only for models that do not fit 24 GiB
  (qwen3-coder spills 4% at 64k; Qwen3.6-35B needs GTT).
- Proposed next: E3 harness comparison (OpenCode vs Claude Code vs mini-swe-agent) for laguna and qwen3-coder
  with both caps, and add the caps to every later config.
