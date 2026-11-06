<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 11 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 0.704 |
| solved_per_8h | 125.078 |
| median_tg_tps | 25.578 |
| median_pp_tps | 4492.466 |
| throttled | 0 |
| max_peak_mem_mib | 3826 |
| max_peak_swap_mib | 632 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | fail | 1/5 | 0.3 | 28.3 | 2817 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 0.9 | 28.5 | 3568 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.7 | 25.6 | 3764 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 3.7 | 26.6 | 3792 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.6 | 27.0 | 3826 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.4 | 30.1 | 3282 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 1.7 | 31.6 | 2931 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 1.4 | 28.2 | 3801 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 3.1 | 22.3 | 2984 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 1.9 | 25.5 | 2999 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 4.5 | 23.6 | 3010 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 0/7 | 2.1 | 24.4 | 3001 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.6 | 24.1 | 2976 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 1.8 | 31.0 | 2977 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 2.5 | 22.8 | 2986 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 4.4 | 23.3 | 3011 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/011-status-effects-r1 |
| 011-status-effects | 2 | pass | 8/8 | 3.6 | 24.0 | 3038 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 3.0 | 24.9 | 3073 | 632 | 1.00 | no | exp/e4-qwen-udq4t-20261106174222/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
