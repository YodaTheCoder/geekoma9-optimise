<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 9 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.500 |
| wall_hours | 2.421 |
| solved_per_8h | 29.737 |
| median_tg_tps | 23.698 |
| median_pp_tps | 2204.450 |
| throttled | 0 |
| max_peak_mem_mib | 5004 |
| max_peak_swap_mib | 412 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 6.2 | 23.5 | 4594 | 412 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 7.7 | 24.1 | 4653 | 412 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 23.9 | 21.8 | 4883 | 412 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 9.5 | 23.6 | 4695 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 5.8 | 23.3 | 4677 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 5.7 | 22.5 | 4717 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 2/6 | 8.9 | 23.7 | 4788 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 2/6 | 8.8 | 24.7 | 4979 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 5.9 | 27.9 | 5004 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 9.7 | 22.7 | 4591 | 410 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/7 | 10.3 | 22.8 | 4833 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-ckpt-gemma4-20261103142510/007-patrol-enemy-r3 |
| 007-patrol-enemy | 3 | fail | 0/7 | 6.7 | 22.9 | 4520 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/007-patrol-enemy-r3-t2 |
| 009-event-bus | 1 | pass | 6/6 | 6.3 | 24.0 | 4775 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 4.2 | 25.1 | 4761 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 4.1 | 23.3 | 4774 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 5.8 | 25.5 | 4626 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/0 | 7.6 | 24.7 | 4982 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 8.1 | 24.5 | 4858 | 409 | 1.00 | no | exp/e3-ckpt-gemma4-20261103142510/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 screen comparison](../e3-screen.md).
