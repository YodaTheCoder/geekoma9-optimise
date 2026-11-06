<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 15 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.833 |
| wall_hours | 3.463 |
| solved_per_8h | 34.655 |
| median_tg_tps | 32.009 |
| median_pp_tps | 4211.898 |
| throttled | 0 |
| max_peak_mem_mib | 7095 |
| max_peak_swap_mib | 1971 |
| min_gpu_offload | 0.902 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.2 | 63.2 | 6322 | 466 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 1.2 | 50.3 | 5996 | 469 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.3 | 82.3 | 6699 | 541 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.4 | 43.5 | 5965 | 1971 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.5 | 36.5 | 6030 | 963 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.2 | 68.2 | 5540 | 960 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 6.9 | 27.5 | 6554 | 907 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | infra_error | 0/0 | 0.0 | - | - | - | - | no | exp/e4-laguna-ctx128k-20261106133215/005-inventory-pickup-r2 |
| 005-inventory-pickup | 2 | timeout | 3/6 | 45.0 | 17.5 | 6945 | 1021 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/005-inventory-pickup-r2-t2 |
| 005-inventory-pickup | 3 | fail | 3/6 | 11.2 | 21.9 | 6833 | 1194 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | pass | 7/7 | 11.0 | 24.3 | 6619 | 1121 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 15.3 | 20.8 | 6856 | 843 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 14.7 | 21.0 | 6726 | 860 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.6 | 148.6 | 6914 | 855 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 2.2 | 98.3 | 6927 | 946 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 3.0 | 65.2 | 6790 | 1055 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/009-event-bus-r3 |
| 011-status-effects | 1 | pass | 8/8 | 37.0 | 16.7 | 6864 | 1076 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/011-status-effects-r1 |
| 011-status-effects | 2 | pass | 8/8 | 19.7 | 21.2 | 6890 | 1197 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/011-status-effects-r2 |
| 011-status-effects | 3 | pass | 8/8 | 31.5 | 19.1 | 7095 | 1484 | 0.90 | no | exp/e4-laguna-ctx128k-20261106133215/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
