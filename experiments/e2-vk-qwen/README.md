<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 13 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.722 |
| wall_hours | 0.785 |
| solved_per_8h | 132.526 |
| median_tg_tps | 24.565 |
| median_pp_tps | 5760.522 |
| throttled | 0 |
| max_peak_mem_mib | 3817 |
| max_peak_swap_mib | 614 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 2.3 | 24.4 | 2818 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.5 | 25.5 | 2881 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.4 | 25.7 | 2835 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.8 | 24.9 | 3778 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.7 | 25.5 | 2917 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.8 | 25.7 | 3817 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 3.3 | 23.8 | 3814 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.3 | 24.9 | 2955 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 1.9 | 25.3 | 2903 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 4.0 | 22.8 | 2942 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.5 | 23.0 | 2951 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 1.9 | 24.4 | 3005 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.4 | 24.6 | 2966 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.2 | 24.8 | 2931 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 2.2 | 24.5 | 2986 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 2.9 | 24.2 | 2963 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/011-status-effects-r1 |
| 011-status-effects | 2 | pass | 8/8 | 6.0 | 22.0 | 3010 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 3.9 | 22.2 | 3006 | 614 | 1.00 | no | exp/e2-vk-qwen-20261107215527/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E2 comparison](../e2.md).
