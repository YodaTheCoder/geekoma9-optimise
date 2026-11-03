<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 12 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 3.441 |
| solved_per_8h | 27.903 |
| median_tg_tps | 35.843 |
| median_pp_tps | 4858.085 |
| throttled | 0 |
| max_peak_mem_mib | 7496 |
| max_peak_swap_mib | 5865 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.6 | 58.6 | 4490 | 382 | 1.00 | no | exp/e3-screen-laguna-20261102001258/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 0.8 | 52.6 | 5596 | 382 | 1.00 | no | exp/e3-screen-laguna-20261102001258/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 0.9 | 156.9 | 7076 | 882 | 1.00 | no | exp/e3-screen-laguna-20261102001258/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.3 | 51.8 | 7348 | 2698 | 1.00 | no | exp/e3-screen-laguna-20261102001258/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.1 | 64.4 | 7388 | 4314 | 1.00 | no | exp/e3-screen-laguna-20261102001258/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.3 | 84.8 | 7406 | 4486 | 1.00 | no | exp/e3-screen-laguna-20261102001258/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-screen-laguna-20261102001258/005-inventory-pickup-r1 |
| 005-inventory-pickup | 1 | pass | 6/6 | 8.3 | 30.8 | 4718 | 388 | 1.00 | no | exp/e3-screen-laguna-20261102001258/005-inventory-pickup-r1-t2 |
| 005-inventory-pickup | 2 | fail | 3/6 | 20.9 | 20.2 | 7421 | 3308 | 1.00 | no | exp/e3-screen-laguna-20261102001258/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 0/6 | 6.8 | 34.4 | 7491 | 5388 | 1.00 | no | exp/e3-screen-laguna-20261102001258/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | timeout | 7/7 | 45.0 | 17.8 | 7491 | 5631 | 1.00 | no | exp/e3-screen-laguna-20261102001258/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/7 | 17.8 | 20.3 | 7496 | 4095 | 1.00 | no | exp/e3-screen-laguna-20261102001258/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 18.0 | 20.1 | 7477 | 4392 | 1.00 | no | exp/e3-screen-laguna-20261102001258/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 4.8 | 77.2 | 7493 | 5401 | 1.00 | no | exp/e3-screen-laguna-20261102001258/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 1.8 | 101.6 | 7449 | 5518 | 1.00 | no | exp/e3-screen-laguna-20261102001258/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 6.8 | 37.3 | 7466 | 4719 | 1.00 | no | exp/e3-screen-laguna-20261102001258/009-event-bus-r3 |
| 011-status-effects | 1 | pass | 8/8 | 33.1 | 16.9 | 7444 | 4410 | 1.00 | no | exp/e3-screen-laguna-20261102001258/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 18.1 | 24.5 | 7462 | 5697 | 1.00 | no | exp/e3-screen-laguna-20261102001258/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 18.1 | 27.6 | 7446 | 5865 | 1.00 | no | exp/e3-screen-laguna-20261102001258/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 screen comparison](../e3-screen.md).
