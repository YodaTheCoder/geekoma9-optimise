<!-- results:start -->
| metric | value |
|---|---|
| attempts | 37 |
| passes | 25 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.694 |
| wall_hours | 6.066 |
| solved_per_8h | 32.970 |
| median_tg_tps | 46.000 |
| median_pp_tps | 4089.838 |
| throttled | 0 |
| max_peak_mem_mib | 6332 |
| max_peak_swap_mib | 749 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.3 | 50.5 | 4780 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.7 | 64.7 | 5090 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.4 | 135.1 | 5046 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/001-health-clamp-r3 |
| 002-damage-signal | 1 | fail | 6/7 | 1.2 | 66.8 | 4571 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/002-damage-signal-r1 |
| 002-damage-signal | 2 | pass | 7/7 | 1.7 | 68.8 | 5081 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/002-damage-signal-r2 |
| 002-damage-signal | 3 | pass | 7/7 | 8.1 | 25.0 | 5345 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/002-damage-signal-r3 |
| 003-score-combo | 1 | pass | 4/4 | 1.1 | 86.6 | 4644 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/003-score-combo-r1 |
| 003-score-combo | 2 | pass | 4/4 | 2.1 | 90.6 | 5706 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/003-score-combo-r2 |
| 003-score-combo | 3 | pass | 4/4 | 0.7 | 75.9 | 4512 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/003-score-combo-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.0 | 54.0 | 3629 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 0.8 | 41.5 | 3326 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.1 | 61.1 | 4605 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | timeout | 5/6 | 45.0 | 16.8 | 6332 | 749 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 1/6 | 15.5 | 22.0 | 5168 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 18.2 | 17.1 | 5129 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/005-inventory-pickup-r3 |
| 006-save-load | 1 | pass | 5/5 | 1.8 | 84.3 | 5011 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/006-save-load-r1 |
| 006-save-load | 2 | pass | 5/5 | 3.3 | 71.2 | 5126 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/006-save-load-r2 |
| 006-save-load | 3 | pass | 5/5 | 1.8 | 94.6 | 5107 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/006-save-load-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 21.7 | 19.9 | 5128 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 10.4 | 24.3 | 5151 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 10.6 | 23.4 | 5156 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/007-patrol-enemy-r3 |
| 008-hud-health | 1 | pass | 6/6 | 14.9 | 24.7 | 5379 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/008-hud-health-r1 |
| 008-hud-health | 2 | pass | 6/6 | 17.9 | 19.5 | 5506 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/008-hud-health-r2 |
| 008-hud-health | 3 | pass | 6/6 | 7.7 | 29.1 | 5475 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/008-hud-health-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.9 | 92.3 | 5348 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.6 | 65.2 | 5468 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/009-event-bus-r2 |
| 009-event-bus | 3 | fail | 5/6 | 2.3 | 56.8 | 5428 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/009-event-bus-r3 |
| 010-wave-spawner | 1 | fail | 6/7 | 24.1 | 18.3 | 5450 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/010-wave-spawner-r1 |
| 010-wave-spawner | 2 | fail | 4/7 | 35.1 | 15.9 | 5498 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/010-wave-spawner-r2 |
| 010-wave-spawner | 3 | fail | 5/7 | 35.7 | 15.6 | 5509 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/010-wave-spawner-r3 |
| 011-status-effects | 1 | fail | 0/8 | 13.0 | 29.3 | 5465 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 19.5 | 21.3 | 5493 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 19.1 | 24.2 | 5523 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/011-status-effects-r3 |
| 012-weapon-tests | 1 | pass | 11/11 | 1.7 | 88.9 | 5331 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/012-weapon-tests-r1 |
| 012-weapon-tests | 2 | pass | 11/11 | 15.5 | 19.6 | 6252 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/012-weapon-tests-r2 |
| 012-weapon-tests | 3 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e5-laguna-ctx64k-20261108131407/012-weapon-tests-r3 |
| 012-weapon-tests | 3 | pass | 11/11 | 1.6 | 115.7 | 4441 | 748 | 1.00 | no | exp/e5-laguna-ctx64k-20261108131407/012-weapon-tests-r3-t2 |
<!-- results:end -->

## Findings

See [the E5 comparison](../e5.md).
