<!-- results:start -->
| metric | value |
|---|---|
| attempts | 37 |
| passes | 21 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.583 |
| wall_hours | 1.494 |
| solved_per_8h | 112.420 |
| median_tg_tps | 26.936 |
| median_pp_tps | 4099.139 |
| throttled | 0 |
| max_peak_mem_mib | 3944 |
| max_peak_swap_mib | 752 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | fail | 1/5 | 0.3 | 27.7 | 3039 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.5 | 26.4 | 3749 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.2 | 25.9 | 3756 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/001-health-clamp-r3 |
| 002-damage-signal | 1 | fail | 0/7 | 0.4 | 27.1 | 3257 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/002-damage-signal-r1 |
| 002-damage-signal | 2 | fail | 4/7 | 1.7 | 26.4 | 3813 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/002-damage-signal-r2 |
| 002-damage-signal | 3 | pass | 7/7 | 0.7 | 26.5 | 3799 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/002-damage-signal-r3 |
| 003-score-combo | 1 | pass | 4/4 | 0.8 | 26.3 | 3873 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/003-score-combo-r1 |
| 003-score-combo | 2 | fail | 0/0 | 0.3 | 27.2 | 3898 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/003-score-combo-r2 |
| 003-score-combo | 3 | pass | 4/4 | 4.7 | 25.6 | 3820 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/003-score-combo-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.3 | 24.2 | 3944 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.2 | 24.8 | 3907 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.2 | 28.7 | 3930 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 2.4 | 29.0 | 3856 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 1.7 | 28.9 | 3101 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 2.5 | 28.7 | 3105 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/005-inventory-pickup-r3 |
| 006-save-load | 1 | pass | 5/5 | 1.0 | 32.6 | 3084 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/006-save-load-r1 |
| 006-save-load | 2 | pass | 5/5 | 2.1 | 27.2 | 3869 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/006-save-load-r2 |
| 006-save-load | 3 | pass | 5/5 | 1.9 | 26.9 | 3124 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/006-save-load-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 2.2 | 25.4 | 3094 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 4.1 | 24.5 | 3128 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 1.8 | 27.7 | 3122 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/007-patrol-enemy-r3 |
| 008-hud-health | 1 | fail | 5/6 | 1.7 | 27.0 | 3116 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/008-hud-health-r1 |
| 008-hud-health | 2 | fail | 5/6 | 2.3 | 94.1 | 3836 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/008-hud-health-r2 |
| 008-hud-health | 3 | pass | 6/6 | 1.8 | 27.0 | 3487 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/008-hud-health-r3 |
| 009-event-bus | 1 | pass | 6/6 | 1.9 | 24.8 | 3486 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.9 | 33.5 | 3829 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.7 | 26.4 | 3530 | 612 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/009-event-bus-r3 |
| 010-wave-spawner | 1 | infra_error | 0/0 | 16.3 | - | - | - | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/010-wave-spawner-r1 |
| 010-wave-spawner | 1 | fail | 0/0 | 3.0 | 44.0 | 3014 | 752 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/010-wave-spawner-r1-t2 |
| 010-wave-spawner | 2 | fail | 0/0 | 2.4 | 26.5 | 3022 | 752 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/010-wave-spawner-r2 |
| 010-wave-spawner | 3 | fail | 3/7 | 15.6 | 22.2 | 3062 | 752 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/010-wave-spawner-r3 |
| 011-status-effects | 1 | pass | 8/8 | 2.9 | 27.6 | 3112 | 752 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 1/8 | 7.0 | 31.2 | 3130 | 752 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 3.0 | 28.8 | 3133 | 751 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/011-status-effects-r3 |
| 012-weapon-tests | 1 | fail | 10/11 | 1.7 | 25.4 | 3283 | 749 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/012-weapon-tests-r1 |
| 012-weapon-tests | 2 | pass | 11/11 | 2.8 | 25.0 | 3322 | 749 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/012-weapon-tests-r2 |
| 012-weapon-tests | 3 | pass | 11/11 | 1.7 | 24.4 | 3330 | 749 | 1.00 | no | exp/e5-qwen-ctx32k-20261108100312/012-weapon-tests-r3 |
<!-- results:end -->

## Findings

See [the E5 comparison](../e5.md).
