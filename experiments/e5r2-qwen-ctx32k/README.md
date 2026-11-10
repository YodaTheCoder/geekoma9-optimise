<!-- results:start -->
| metric | value |
|---|---|
| attempts | 36 |
| passes | 21 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.583 |
| wall_hours | 1.616 |
| solved_per_8h | 103.983 |
| median_tg_tps | 26.739 |
| median_pp_tps | 4009.881 |
| throttled | 0 |
| max_peak_mem_mib | 3989 |
| max_peak_swap_mib | 800 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.5 | 27.4 | 3045 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.8 | 24.6 | 3067 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 2.0 | 30.1 | 3071 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/001-health-clamp-r3 |
| 002-damage-signal | 1 | pass | 7/7 | 1.4 | 30.8 | 3072 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/002-damage-signal-r1 |
| 002-damage-signal | 2 | fail | 0/7 | 0.3 | 27.1 | 3105 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/002-damage-signal-r2 |
| 002-damage-signal | 3 | pass | 7/7 | 1.9 | 26.9 | 3787 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/002-damage-signal-r3 |
| 003-score-combo | 1 | pass | 4/4 | 1.6 | 32.3 | 3839 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/003-score-combo-r1 |
| 003-score-combo | 2 | pass | 4/4 | 0.9 | 26.1 | 3886 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/003-score-combo-r2 |
| 003-score-combo | 3 | pass | 4/4 | 0.8 | 26.5 | 3841 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/003-score-combo-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.6 | 25.4 | 3880 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.3 | 26.2 | 3871 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.5 | 27.7 | 3860 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 1.9 | 30.2 | 3958 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.4 | 24.0 | 3944 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 1.8 | 35.5 | 3989 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/005-inventory-pickup-r3 |
| 006-save-load | 1 | pass | 5/5 | 2.1 | 39.2 | 3984 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/006-save-load-r1 |
| 006-save-load | 2 | pass | 5/5 | 1.0 | 29.6 | 3955 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/006-save-load-r2 |
| 006-save-load | 3 | pass | 5/5 | 3.3 | 23.0 | 3866 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/006-save-load-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 2.9 | 27.7 | 3126 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/7 | 2.3 | 25.2 | 3201 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 0/7 | 3.0 | 24.3 | 3173 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/007-patrol-enemy-r3 |
| 008-hud-health | 1 | fail | 5/6 | 3.2 | 25.8 | 3155 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/008-hud-health-r1 |
| 008-hud-health | 2 | fail | 5/6 | 2.1 | 26.5 | 3169 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/008-hud-health-r2 |
| 008-hud-health | 3 | fail | 5/6 | 3.4 | 25.3 | 3179 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/008-hud-health-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.6 | 32.0 | 3126 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.7 | 33.1 | 3163 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.8 | 33.1 | 3114 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/009-event-bus-r3 |
| 010-wave-spawner | 1 | fail | 6/7 | 4.7 | 28.1 | 3221 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/010-wave-spawner-r1 |
| 010-wave-spawner | 2 | fail | 3/7 | 10.3 | 24.8 | 3232 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/010-wave-spawner-r2 |
| 010-wave-spawner | 3 | fail | 6/7 | 8.3 | 23.2 | 3199 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/010-wave-spawner-r3 |
| 011-status-effects | 1 | fail | 7/8 | 7.4 | 22.3 | 3202 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 2.6 | 30.0 | 3206 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 1.9 | 32.7 | 3273 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/011-status-effects-r3 |
| 012-weapon-tests | 1 | pass | 11/11 | 3.3 | 23.2 | 3366 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/012-weapon-tests-r1 |
| 012-weapon-tests | 2 | pass | 11/11 | 1.7 | 24.6 | 3447 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/012-weapon-tests-r2 |
| 012-weapon-tests | 3 | pass | 11/11 | 2.5 | 24.7 | 3464 | 800 | 1.00 | no | exp/e5r2-qwen-ctx32k-20261109200647/012-weapon-tests-r3 |
<!-- results:end -->

## Findings

See [the E5 comparison](../e5.md).
