<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 11 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 1.031 |
| solved_per_8h | 85.320 |
| median_tg_tps | 20.008 |
| median_pp_tps | 4214.670 |
| throttled | 0 |
| max_peak_mem_mib | 4819 |
| max_peak_swap_mib | 632 |
| min_gpu_offload | 0.952 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.8 | 21.2 | 3795 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/001-health-clamp-r1 |
| 001-health-clamp | 2 | fail | 1/5 | 0.4 | 21.0 | 4366 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.5 | 21.6 | 4791 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.9 | 19.2 | 4788 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.5 | 20.6 | 4456 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 2.2 | 18.9 | 4488 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 2.9 | 21.5 | 4407 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 1.9 | 23.6 | 4524 | 632 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 5/6 | 2.5 | 24.3 | 4460 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 4.3 | 18.3 | 4457 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.1 | 19.4 | 4759 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 4.6 | 18.6 | 4622 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 3.0 | 21.2 | 4639 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.5 | 18.5 | 4602 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 3.0 | 25.3 | 4522 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 4/8 | 8.5 | 16.6 | 4752 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/0 | 5.6 | 16.9 | 4819 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 8.7 | 17.9 | 4813 | 631 | 0.95 | no | exp/e4-qwen-udq5t-kvq8-20261106190610/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
