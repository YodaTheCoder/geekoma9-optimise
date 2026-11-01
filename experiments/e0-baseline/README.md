<!-- results:start -->
| metric | value |
|---|---|
| attempts | 7 |
| passes | 2 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.333 |
| wall_hours | 0.265 |
| solved_per_8h | 60.405 |
| median_tg_tps | 25.330 |
| median_pp_tps | 3827.538 |
| throttled | 0 |
| max_peak_mem_mib | 7494 |
| max_peak_swap_mib | - |
| min_gpu_offload | - |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | fail | 0/5 | 1.4 | 24.8 | 4038 | - | - | no | exp/e0-baseline-202610311713/001-health-clamp-r1 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.0 | 25.1 | 5112 | - | - | no | exp/e0-baseline-202610311713/004-weapon-cooldown-r1 |
| 005-inventory-pickup | 1 | fail | 3/6 | 2.5 | 33.7 | 6386 | - | - | no | exp/e0-baseline-202610311713/005-inventory-pickup-r1 |
| 007-patrol-enemy | 1 | pass | 7/7 | 3.3 | 21.7 | 7494 | - | - | no | exp/e0-baseline-202610311713/007-patrol-enemy-r1 |
| 009-event-bus | 1 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e0-baseline-202610311713/009-event-bus-r1 |
| 009-event-bus | 1 | fail | 6/6 | 2.2 | 25.6 | 3591 | - | - | no | exp/e0-baseline-202610311713/009-event-bus-r1 |
| 011-status-effects | 1 | fail | 0/0 | 4.5 | 30.6 | 5187 | - | - | no | exp/e0-baseline-202610311713/011-status-effects-r1 |
<!-- results:end -->

## Findings

Setup: 24 GiB UMA (7.4 GiB visible to Linux), Ollama 0.34.4 on ROCm gfx1150, `qwen3-coder:30b` (digest
`06c1097e…`) at 64k context, OpenCode 1.18.32. Screening tier (6 tasks, 1 run each), orchestrated from
`newbuntu.local`.

- **2 of 6 passed** (004 weapon cooldown, 007 patrol enemy). Calibration with Claude Opus passed all 12.
- Every failure is the model's, read from the scoring logs and the pushed branches:
  - 001 health clamp: called a nonexistent `minimax()` (GDScript has `clampi`/`mini`) and added an unrequested
    "can't heal at 0 HP" rule, so `health.gd` no longer parses. The dry run made the same mistake.
  - 005 inventory pickup: wrote an invalid `scenes/pickup.tscn` (bad resource id on line 9); the 3 tests not
    needing that scene passed.
  - 009 event bus: passed all 6 hidden tests but renamed ScoreManager's `add_points`, which breaks the existing
    regression tests.
  - 011 status effects: new scripts referenced undeclared `Slow`/`StatusEffects` types and do not parse (shown as
    0/0 because the hidden tests could not load).
- The failures are GDScript/Godot knowledge (API names, `.tscn` syntax, class registration) and not keeping the
  existing API intact, not tool calling: OpenCode's tool calls were clean (no Hermes-XML flip, no invalid-tool
  errors), 11–20 tool calls per task.
- Speed: generation 22–34 tok/s (median 25.3), prompt processing 1.0–4.8k tok/s (median 3.8k, prefix cache hits
  included). 150k–320k prompt tokens per attempt; each request re-sends ~12k+ tokens of context.
- Time: 1.4–4.5 min of agent time per task. `solved_per_8h` (60.4) counts agent time only; including runtime
  restart, warm-up and scoring the run took 33 min for 6 attempts, about 29 solved per 8 hours.
- **Memory headroom is the main concern.** The model plus 64k KV cache holds 23.7 GiB of the 24 GiB UMA carve-out,
  and system RAM peaked at 7.5 GiB of 7.4 GiB visible (Godot plus the agent) during 007. That points straight
  at E1 (memory split).
- No thermal throttling. One ssh connection timeout (newbuntu → geekoma9) was retried as `infra_error` and the
  retry ran normally.
