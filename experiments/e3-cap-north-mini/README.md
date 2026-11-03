<!-- results:start -->
| metric | value |
|---|---|
| attempts | 20 |
| passes | 10 |
| infra_errors | 2 |
| unscored | 0 |
| pass_rate | 0.556 |
| wall_hours | 1.882 |
| solved_per_8h | 42.503 |
| median_tg_tps | 25.150 |
| median_pp_tps | 1569.057 |
| throttled | 0 |
| max_peak_mem_mib | 7527 |
| max_peak_swap_mib | 5783 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.5 | 29.0 | 5473 | 412 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 4.0 | 25.0 | 7518 | 4829 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 3.4 | 24.5 | 7510 | 4651 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | infra_error | 0/0 | 4.8 | - | - | - | 1.00 | no | exp/e3-cap-north-mini-20261103062007/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.8 | 27.4 | 4771 | 465 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/004-weapon-cooldown-r1-t2 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 4.2 | 25.1 | 7511 | 4112 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.3 | 27.5 | 7463 | 4096 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | pass | 6/6 | 10.5 | 23.0 | 7524 | 5181 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 3.2 | 25.2 | 7527 | 5219 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-cap-north-mini-20261103062007/005-inventory-pickup-r3 |
| 005-inventory-pickup | 3 | fail | 3/6 | 2.3 | 27.0 | 7353 | 1782 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/005-inventory-pickup-r3-t2 |
| 007-patrol-enemy | 1 | fail | 0/0 | 35.9 | 22.1 | 7513 | 5223 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/0 | 4.1 | 25.6 | 7498 | 5103 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 3.1 | 26.8 | 7317 | 4095 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 3.6 | 26.1 | 7510 | 4115 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/009-event-bus-r1 |
| 009-event-bus | 2 | fail | 0/0 | 5.4 | 23.2 | 7524 | 5717 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 5.7 | 23.5 | 7520 | 5783 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 0/0 | 2.0 | 26.9 | 7414 | 5717 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/0 | 10.5 | 22.8 | 7520 | 5449 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 10.4 | 24.0 | 7520 | 5533 | 1.00 | no | exp/e3-cap-north-mini-20261103062007/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 screen comparison](../e3-screen.md).
