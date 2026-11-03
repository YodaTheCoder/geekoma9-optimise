<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 11 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 0.669 |
| solved_per_8h | 131.605 |
| median_tg_tps | 27.399 |
| median_pp_tps | 4352.566 |
| throttled | 0 |
| max_peak_mem_mib | 4650 |
| max_peak_swap_mib | 483 |
| min_gpu_offload | 0.959 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.7 | 27.2 | 3473 | 483 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.6 | 25.3 | 3517 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 0.5 | 26.3 | 3584 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.5 | 28.4 | 4354 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | fail | 0/5 | 0.3 | 26.9 | 4315 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | fail | 0/5 | 0.3 | 26.4 | 4309 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 0.9 | 494.1 | 4336 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 4.6 | 19.7 | 4534 | 482 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 5.3 | 29.6 | 4650 | 480 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 2.3 | 24.9 | 4040 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e3-cap-qwen3-coder-20261103130229/007-patrol-enemy-r2 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.2 | 24.2 | 3614 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/007-patrol-enemy-r2-t2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 3.1 | 24.7 | 3695 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.2 | 29.6 | 3624 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 1.3 | 27.6 | 3644 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 1.7 | 27.6 | 3661 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 2.3 | 28.2 | 3699 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/011-status-effects-r1 |
| 011-status-effects | 2 | pass | 8/8 | 3.1 | 34.1 | 3740 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 1/8 | 3.0 | 28.6 | 3762 | 412 | 0.96 | no | exp/e3-cap-qwen3-coder-20261103130229/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E3 screen comparison](../e3-screen.md).
