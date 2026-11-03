<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 9 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.500 |
| wall_hours | 0.796 |
| solved_per_8h | 90.404 |
| median_tg_tps | 25.305 |
| median_pp_tps | 2419.559 |
| throttled | 0 |
| max_peak_mem_mib | 7524 |
| max_peak_swap_mib | 4497 |
| min_gpu_offload | 0.959 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.7 | 28.6 | 3434 | 464 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.4 | 33.1 | 4518 | 464 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.8 | 25.0 | 5597 | 464 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.5 | 24.6 | 6808 | 461 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.4 | 23.2 | 7472 | 4095 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 2.6 | 29.8 | 7480 | 4096 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 5.8 | 25.0 | 7507 | 4112 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 2.5 | 25.4 | 7501 | 4489 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 1.9 | 25.7 | 7487 | 4476 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/7 | 3.3 | 22.9 | 7487 | 4439 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | fail | 0/0 | 0.8 | 24.7 | 7483 | 4483 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | fail | 6/7 | 4.8 | 22.9 | 7490 | 4123 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/007-patrol-enemy-r3 |
| 009-event-bus | 1 | fail | 0/6 | 0.6 | 26.3 | 7507 | 4160 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.0 | 26.0 | 7504 | 4109 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.7 | 25.2 | 7524 | 4497 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/009-event-bus-r3 |
| 011-status-effects | 1 | pass | 8/8 | 3.5 | 35.7 | 7486 | 4314 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 1/8 | 8.2 | 41.6 | 7490 | 4412 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 2.3 | 23.3 | 7493 | 4280 | 0.96 | no | exp/e3-screen-qwen3-coder-20261102083913/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 screen comparison](../e3-screen.md).
