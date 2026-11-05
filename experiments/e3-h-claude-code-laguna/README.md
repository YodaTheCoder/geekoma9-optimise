<!-- results:start -->
| metric | value |
|---|---|
| attempts | 20 |
| passes | 10 |
| infra_errors | 2 |
| unscored | 0 |
| pass_rate | 0.556 |
| wall_hours | 5.490 |
| solved_per_8h | 14.573 |
| median_tg_tps | 21.242 |
| median_pp_tps | 8688.761 |
| throttled | 0 |
| max_peak_mem_mib | 5071 |
| max_peak_swap_mib | 412 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 6.5 | 31.0 | 4902 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 5.0 | 30.3 | 4921 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 5.5 | 31.6 | 4286 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 19.8 | 21.4 | 4381 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 3.1 | 33.7 | 4357 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 6.1 | 31.2 | 4807 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 27.9 | 20.1 | 5034 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | pass | 6/6 | 23.6 | 20.1 | 5027 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | timeout | 1/6 | 30.0 | 21.0 | 4389 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | timeout | 7/7 | 30.0 | 19.4 | 5071 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-h-claude-code-laguna-20261104180654/007-patrol-enemy-r2 |
| 007-patrol-enemy | 2 | timeout | 7/7 | 30.0 | 19.3 | 4966 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/007-patrol-enemy-r2-t2 |
| 007-patrol-enemy | 3 | timeout | 7/7 | 30.0 | 20.1 | 4371 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 8.9 | 27.8 | 4427 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/009-event-bus-r1 |
| 009-event-bus | 2 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-h-claude-code-laguna-20261104180654/009-event-bus-r2 |
| 009-event-bus | 2 | pass | 6/6 | 5.1 | 31.6 | 4280 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/009-event-bus-r2-t2 |
| 009-event-bus | 3 | pass | 6/6 | 7.7 | 31.0 | 4885 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/009-event-bus-r3 |
| 011-status-effects | 1 | timeout | 0/8 | 30.0 | 14.5 | 4439 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/011-status-effects-r1 |
| 011-status-effects | 2 | timeout | 8/8 | 30.0 | 19.1 | 4446 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/011-status-effects-r2 |
| 011-status-effects | 3 | timeout | 0/8 | 30.0 | 19.5 | 4464 | 412 | 1.00 | no | exp/e3-h-claude-code-laguna-20261104180654/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 harness comparison](../e3-harness.md).
