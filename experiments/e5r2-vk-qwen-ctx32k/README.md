<!-- results:start -->
| metric | value |
|---|---|
| attempts | 37 |
| passes | 24 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 2.820 |
| solved_per_8h | 68.088 |
| median_tg_tps | 24.602 |
| median_pp_tps | 5080.303 |
| throttled | 0 |
| max_peak_mem_mib | 3839 |
| max_peak_swap_mib | 800 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 2.3 | 25.7 | 3812 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.8 | 25.2 | 3824 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.5 | 25.6 | 2978 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/001-health-clamp-r3 |
| 002-damage-signal | 1 | pass | 7/7 | 2.0 | 25.0 | 2975 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/002-damage-signal-r1 |
| 002-damage-signal | 2 | pass | 7/7 | 1.6 | 25.8 | 2961 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/002-damage-signal-r2 |
| 002-damage-signal | 3 | pass | 7/7 | 1.8 | 25.1 | 3839 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/002-damage-signal-r3 |
| 003-score-combo | 1 | pass | 4/4 | 38.5 | 18.3 | 3074 | 800 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/003-score-combo-r1 |
| 003-score-combo | 2 | pass | 4/4 | 38.8 | 18.4 | 3076 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/003-score-combo-r2 |
| 003-score-combo | 3 | pass | 4/4 | 1.7 | 25.0 | 3097 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/003-score-combo-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.0 | 25.0 | 3061 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.8 | 25.1 | 3007 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.7 | 25.3 | 3065 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 1.8 | 25.3 | 3042 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 3.1 | 23.7 | 3119 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 2.3 | 24.9 | 3100 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/005-inventory-pickup-r3 |
| 006-save-load | 1 | pass | 5/5 | 1.4 | 25.3 | 3088 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/006-save-load-r1 |
| 006-save-load | 2 | pass | 5/5 | 2.7 | 23.3 | 3142 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/006-save-load-r2 |
| 006-save-load | 3 | pass | 5/5 | 2.8 | 23.6 | 3110 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/006-save-load-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 4.4 | 21.8 | 3111 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 6.0 | 22.3 | 3162 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 2.6 | 23.9 | 3121 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/007-patrol-enemy-r3 |
| 008-hud-health | 1 | fail | 4/6 | 2.2 | 24.6 | 3114 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/008-hud-health-r1 |
| 008-hud-health | 2 | fail | 5/6 | 3.7 | 21.0 | 3146 | 792 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/008-hud-health-r2 |
| 008-hud-health | 3 | fail | 5/6 | 2.4 | 24.6 | 3189 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/008-hud-health-r3 |
| 009-event-bus | 1 | pass | 6/6 | 3.2 | 21.3 | 3115 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.4 | 24.5 | 3111 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 3.1 | 23.1 | 3175 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/009-event-bus-r3 |
| 010-wave-spawner | 1 | fail | 4/7 | 2.5 | 24.6 | 3126 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/010-wave-spawner-r1 |
| 010-wave-spawner | 2 | fail | 5/7 | 4.0 | 23.1 | 3142 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/010-wave-spawner-r2 |
| 010-wave-spawner | 3 | fail | 0/7 | 6.0 | 22.7 | 3187 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/010-wave-spawner-r3 |
| 011-status-effects | 1 | pass | 8/8 | 3.9 | 23.7 | 3181 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 1/8 | 4.0 | 23.3 | 3232 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 3.2 | 23.4 | 3167 | 782 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/011-status-effects-r3 |
| 012-weapon-tests | 1 | infra_error | 0/0 | 0.0 | - | - | - | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/012-weapon-tests-r1 |
| 012-weapon-tests | 1 | pass | 11/11 | 2.0 | 25.1 | 2958 | 783 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/012-weapon-tests-r1-t2 |
| 012-weapon-tests | 2 | pass | 11/11 | 2.3 | 24.6 | 3012 | 783 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/012-weapon-tests-r2 |
| 012-weapon-tests | 3 | pass | 11/11 | 1.8 | 24.9 | 3044 | 783 | 1.00 | no | exp/e5r2-vk-qwen-ctx32k-20261109230932/012-weapon-tests-r3 |
<!-- results:end -->

## Findings

See [the E5 comparison](../e5.md).
