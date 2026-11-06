<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 12 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 1.749 |
| solved_per_8h | 54.890 |
| median_tg_tps | 49.043 |
| median_pp_tps | 3254.995 |
| throttled | 0 |
| max_peak_mem_mib | 5513 |
| max_peak_swap_mib | 426 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.2 | 71.8 | 4505 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.1 | 60.5 | 4445 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.1 | 66.8 | 4483 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.6 | 39.3 | 4988 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.2 | 81.1 | 4588 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.3 | 58.7 | 4379 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 5/6 | 6.5 | 28.8 | 4995 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 3.4 | 134.1 | 5094 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 5.2 | 33.2 | 5111 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 14.4 | 22.7 | 5048 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 11.1 | 22.9 | 5140 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 20.4 | 25.4 | 5108 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 3.5 | 115.6 | 5396 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 3.1 | 95.3 | 5417 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 3.4 | 87.5 | 5465 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 0/8 | 8.8 | 36.1 | 5477 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 8.2 | 29.8 | 5513 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 8.6 | 38.0 | 5503 | 426 | 1.00 | no | exp/e4-laguna-ctx32k-20261106110528/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
