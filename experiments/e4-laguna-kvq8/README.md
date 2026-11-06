<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 11 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 4.518 |
| solved_per_8h | 19.477 |
| median_tg_tps | 22.834 |
| median_pp_tps | 4448.246 |
| throttled | 0 |
| max_peak_mem_mib | 5035 |
| max_peak_swap_mib | 426 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.2 | 56.5 | 3618 | 421 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 8.7 | 22.5 | 4527 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 2.3 | 45.3 | 4009 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.4 | 35.6 | 3986 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 0.8 | 59.7 | 4033 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.2 | 56.2 | 4379 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 10.9 | 18.6 | 4740 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 5/6 | 8.0 | 23.1 | 4275 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 42.5 | 12.5 | 4826 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 10.7 | 19.8 | 4327 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 43.9 | 11.7 | 5035 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | timeout | 7/7 | 45.0 | 11.9 | 4981 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 3.5 | 161.4 | 4344 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 3.0 | 83.3 | 4364 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 5.0 | 125.5 | 5023 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/009-event-bus-r3 |
| 011-status-effects | 1 | pass | 8/8 | 26.2 | 15.2 | 4407 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/011-status-effects-r1 |
| 011-status-effects | 2 | infra_error | 0/0 | 30.3 | - | - | - | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/011-status-effects-r2 |
| 011-status-effects | 2 | fail | 0/8 | 36.1 | 13.0 | 4146 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/011-status-effects-r2-t2 |
| 011-status-effects | 3 | fail | 0/0 | 20.8 | 15.4 | 4200 | 426 | 1.00 | no | exp/e4-laguna-kvq8-20261106052131/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
