<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 13 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.722 |
| wall_hours | 3.144 |
| solved_per_8h | 33.077 |
| median_tg_tps | 25.002 |
| median_pp_tps | 10912.653 |
| throttled | 0 |
| max_peak_mem_mib | 5243 |
| max_peak_swap_mib | 614 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 3.8 | 28.0 | 4906 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 2.5 | 28.9 | 4965 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 2.1 | 29.2 | 4827 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.7 | 29.7 | 4327 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.6 | 28.0 | 5006 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 2.3 | 28.6 | 5009 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 1/6 | 7.5 | 23.5 | 5040 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 1/6 | 7.7 | 24.0 | 5074 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | pass | 6/6 | 15.7 | 21.9 | 5105 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 14.0 | 22.9 | 5094 | 614 | 1.00 | no | exp/e2-vk-laguna-20261108004840/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 27.3 | 20.9 | 5137 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 7.6 | 25.2 | 5114 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 4.7 | 25.9 | 5057 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 5.1 | 27.1 | 5137 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 7.2 | 24.8 | 5150 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/009-event-bus-r3 |
| 011-status-effects | 1 | timeout | 0/8 | 30.0 | 20.0 | 5119 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 28.0 | 20.1 | 5243 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 18.9 | 21.6 | 5187 | 610 | 1.00 | no | exp/e2-vk-laguna-20261108004840/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E2 comparison](../e2.md).
