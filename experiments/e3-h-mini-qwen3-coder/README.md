<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 11 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 0.727 |
| solved_per_8h | 121.042 |
| median_tg_tps | - |
| median_pp_tps | - |
| throttled | 0 |
| max_peak_mem_mib | 4297 |
| max_peak_swap_mib | 400 |
| min_gpu_offload | 0.959 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.6 | - | 3249 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.4 | - | 3827 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 2.2 | - | 4274 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.8 | - | 4273 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.3 | - | 3893 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 2.1 | - | 3889 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 0/0 | 2.2 | - | 4012 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.0 | - | 4081 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 5/6 | 1.7 | - | 4153 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 2.6 | - | 4124 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.6 | - | 4233 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 3.5 | - | 4228 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 1.9 | - | 4297 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 1.0 | - | 4274 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.3 | - | 4049 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 3/8 | 4.9 | - | 3921 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 3/8 | 3.7 | - | 3936 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 3/8 | 3.9 | - | 3932 | 400 | 0.96 | no | exp/e3-h-mini-qwen3-coder-20261104064132/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 harness comparison](../e3-harness.md).
