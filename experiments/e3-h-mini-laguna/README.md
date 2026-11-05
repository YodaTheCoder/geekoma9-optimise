<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 12 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 5.558 |
| solved_per_8h | 17.272 |
| median_tg_tps | - |
| median_pp_tps | - |
| throttled | 0 |
| max_peak_mem_mib | 5379 |
| max_peak_swap_mib | 413 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 5.8 | - | 4373 | 410 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 10.1 | - | 4398 | 410 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 12.2 | - | 4477 | 411 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 3.9 | - | 4432 | 411 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 11.5 | - | 4650 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 6.8 | - | 4449 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | timeout | 6/6 | 30.0 | - | 4455 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | pass | 6/6 | 25.8 | - | 5071 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | timeout | 3/6 | 30.0 | - | 5100 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 19.2 | - | 4738 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | timeout | 7/7 | 30.0 | - | 4738 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 0/0 | 26.2 | - | 5355 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 4.8 | - | 4735 | 413 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 6.1 | - | 4740 | 412 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 21.9 | - | 5047 | 412 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/009-event-bus-r3 |
| 011-status-effects | 1 | timeout | 8/8 | 30.0 | - | 4725 | 412 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/011-status-effects-r1 |
| 011-status-effects | 2 | timeout | 8/8 | 30.0 | - | 5168 | 412 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/011-status-effects-r2 |
| 011-status-effects | 3 | pass | 8/8 | 29.2 | - | 5379 | 412 | 1.00 | no | exp/e3-h-mini-laguna-20261104115219/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 harness comparison](../e3-harness.md).
