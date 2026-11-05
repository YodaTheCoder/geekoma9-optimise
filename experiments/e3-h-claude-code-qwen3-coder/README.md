<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 6 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.333 |
| wall_hours | 3.045 |
| solved_per_8h | 15.766 |
| median_tg_tps | 30.869 |
| median_pp_tps | 4344.479 |
| throttled | 0 |
| max_peak_mem_mib | 4248 |
| max_peak_swap_mib | 400 |
| min_gpu_offload | 0.959 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | timeout | 5/5 | 30.0 | 18.7 | 3247 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 0.3 | 32.0 | 3231 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 0.8 | 31.0 | 3479 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.5 | 30.7 | 3836 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | timeout | 5/5 | 30.0 | 18.5 | 4092 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | timeout | 5/5 | 30.0 | 18.6 | 4087 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 3.9 | 32.5 | 4081 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.9 | 36.9 | 4084 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | timeout | 3/6 | 30.0 | 18.0 | 4248 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 1.9 | 29.8 | 4236 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.2 | 35.3 | 4127 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 0/7 | 3.9 | 26.6 | 4223 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 1.9 | 36.4 | 4220 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.0 | 34.7 | 4110 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/009-event-bus-r2 |
| 009-event-bus | 3 | fail | 0/0 | 2.5 | 28.3 | 4013 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 0/0 | 4.6 | 31.9 | 4171 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 1/8 | 3.3 | 34.6 | 4171 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/011-status-effects-r2 |
| 011-status-effects | 3 | timeout | 8/8 | 30.0 | 18.6 | 4171 | 400 | 0.96 | no | exp/e3-h-claude-code-qwen3-coder-20261104080608/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 harness comparison](../e3-harness.md).
