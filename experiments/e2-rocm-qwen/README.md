<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 12 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 0.729 |
| solved_per_8h | 131.754 |
| median_tg_tps | 24.323 |
| median_pp_tps | 6516.892 |
| throttled | 0 |
| max_peak_mem_mib | 4059 |
| max_peak_swap_mib | 614 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.6 | 24.8 | 3005 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 0.7 | 25.7 | 3029 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 0.7 | 25.9 | 3936 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.9 | 24.7 | 3944 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.1 | 24.3 | 3911 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 2.0 | 24.6 | 3934 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 2.1 | 24.7 | 3972 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.2 | 23.9 | 3978 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 3.1 | 22.6 | 3962 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 6.5 | 23.8 | 4020 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 1.9 | 23.9 | 4059 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 2.6 | 23.6 | 4009 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 1.7 | 24.4 | 3965 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.0 | 24.4 | 3987 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.4 | 24.9 | 3975 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 3.0 | 23.4 | 3837 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 2.9 | 23.4 | 3288 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 5.4 | 22.6 | 3215 | 614 | 1.00 | no | exp/e2-rocm-qwen-20261107232355/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E2 comparison](../e2.md).
