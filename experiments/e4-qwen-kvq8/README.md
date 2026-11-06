<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 11 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 0.782 |
| solved_per_8h | 112.507 |
| median_tg_tps | 22.624 |
| median_pp_tps | 3651.130 |
| throttled | 0 |
| max_peak_mem_mib | 3831 |
| max_peak_swap_mib | 411 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 2.8 | 20.9 | 2961 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.4 | 22.3 | 3640 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.6 | 21.7 | 3448 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.5 | 22.7 | 3550 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.0 | 22.5 | 3585 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.6 | 22.8 | 3514 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 2.2 | 39.2 | 3515 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.3 | 24.7 | 3586 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 0/0 | 0.4 | 22.8 | 3550 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 3.7 | 20.0 | 3366 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 5.5 | 19.8 | 3754 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 0/7 | 1.9 | 20.6 | 3825 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/007-patrol-enemy-r3 |
| 009-event-bus | 1 | fail | 0/6 | 0.7 | 24.4 | 3553 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 5.2 | 22.4 | 3758 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 2.1 | 23.8 | 3789 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 0/0 | 4.0 | 29.6 | 3642 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/011-status-effects-r1 |
| 011-status-effects | 2 | pass | 8/8 | 3.9 | 19.4 | 3804 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 3.1 | 26.8 | 3831 | 411 | 1.00 | no | exp/e4-qwen-kvq8-20261105231146/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
