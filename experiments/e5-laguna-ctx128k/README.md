<!-- results:start -->
| metric | value |
|---|---|
| attempts | 36 |
| passes | 26 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.722 |
| wall_hours | 5.725 |
| solved_per_8h | 36.331 |
| median_tg_tps | 34.512 |
| median_pp_tps | 3848.923 |
| throttled | 0 |
| max_peak_mem_mib | 7116 |
| max_peak_swap_mib | 1502 |
| min_gpu_offload | 0.902 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 0.9 | 74.6 | 5799 | 749 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.1 | 82.2 | 6012 | 749 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 2.1 | 31.1 | 6340 | 749 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/001-health-clamp-r3 |
| 002-damage-signal | 1 | fail | 1/7 | 2.1 | 94.0 | 6731 | 749 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/002-damage-signal-r1 |
| 002-damage-signal | 2 | pass | 7/7 | 3.8 | 36.1 | 6727 | 760 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/002-damage-signal-r2 |
| 002-damage-signal | 3 | pass | 7/7 | 2.3 | 42.9 | 6707 | 764 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/002-damage-signal-r3 |
| 003-score-combo | 1 | pass | 4/4 | 4.7 | 26.9 | 6683 | 764 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/003-score-combo-r1 |
| 003-score-combo | 2 | pass | 4/4 | 1.1 | 39.4 | 6245 | 764 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/003-score-combo-r2 |
| 003-score-combo | 3 | pass | 4/4 | 2.2 | 45.6 | 6799 | 764 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/003-score-combo-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.3 | 141.3 | 6409 | 775 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.2 | 66.3 | 6105 | 775 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.2 | 45.9 | 6378 | 775 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | pass | 6/6 | 3.7 | 32.0 | 6758 | 776 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 3.2 | 187.9 | 6786 | 778 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 12.4 | 24.6 | 6817 | 779 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/005-inventory-pickup-r3 |
| 006-save-load | 1 | pass | 5/5 | 11.4 | 33.7 | 7010 | 1021 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/006-save-load-r1 |
| 006-save-load | 2 | pass | 5/5 | 2.1 | 93.7 | 6725 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/006-save-load-r2 |
| 006-save-load | 3 | pass | 5/5 | 3.6 | 48.3 | 6713 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/006-save-load-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 10.7 | 23.5 | 6729 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/7 | 13.0 | 23.2 | 6827 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 8.1 | 29.6 | 6773 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/007-patrol-enemy-r3 |
| 008-hud-health | 1 | pass | 6/6 | 8.4 | 26.6 | 6744 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/008-hud-health-r1 |
| 008-hud-health | 2 | pass | 6/6 | 11.8 | 25.3 | 6802 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/008-hud-health-r2 |
| 008-hud-health | 3 | pass | 6/6 | 20.9 | 19.8 | 6786 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/008-hud-health-r3 |
| 009-event-bus | 1 | pass | 6/6 | 1.9 | 98.5 | 6698 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 4.5 | 89.7 | 6800 | 900 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 2.7 | 86.7 | 6727 | 919 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/009-event-bus-r3 |
| 010-wave-spawner | 1 | timeout | 6/7 | 45.0 | 14.6 | 7045 | 1340 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/010-wave-spawner-r1 |
| 010-wave-spawner | 2 | fail | 6/7 | 34.9 | 16.2 | 6768 | 1280 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/010-wave-spawner-r2 |
| 010-wave-spawner | 3 | fail | 0/7 | 27.0 | 18.1 | 6775 | 1240 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/010-wave-spawner-r3 |
| 011-status-effects | 1 | fail | 0/8 | 29.3 | 19.5 | 7116 | 1038 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/0 | 29.8 | 18.6 | 6740 | 1502 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/011-status-effects-r2 |
| 011-status-effects | 3 | pass | 8/8 | 27.6 | 19.1 | 6829 | 1473 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/011-status-effects-r3 |
| 012-weapon-tests | 1 | pass | 11/11 | 2.8 | 33.7 | 7076 | 1323 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/012-weapon-tests-r1 |
| 012-weapon-tests | 2 | fail | 10/11 | 2.1 | 51.3 | 7047 | 1345 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/012-weapon-tests-r2 |
| 012-weapon-tests | 3 | pass | 11/11 | 2.8 | 35.3 | 7098 | 1404 | 0.90 | no | exp/e5-laguna-ctx128k-20261108204244/012-weapon-tests-r3 |
<!-- results:end -->

## Findings

See [the E5 comparison](../e5.md).
