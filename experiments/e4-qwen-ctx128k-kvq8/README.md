<!-- results:start -->
| metric | value |
|---|---|
| attempts | 18 |
| passes | 11 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.611 |
| wall_hours | 0.722 |
| solved_per_8h | 121.906 |
| median_tg_tps | 23.139 |
| median_pp_tps | 3679.810 |
| throttled | 0 |
| max_peak_mem_mib | 5233 |
| max_peak_swap_mib | 412 |
| min_gpu_offload | 0.936 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 2.2 | 20.4 | 4362 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 2.3 | 23.2 | 4960 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 1.5 | 21.1 | 5184 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.7 | 23.7 | 4888 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 2.0 | 21.3 | 4882 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 1.8 | 22.1 | 4895 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | fail | 3/6 | 1.9 | 27.0 | 4916 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 3.1 | 25.2 | 4954 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | fail | 5/6 | 2.5 | 27.1 | 5229 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | fail | 0/0 | 0.4 | 22.1 | 5001 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/007-patrol-enemy-r1 |
| 007-patrol-enemy | 2 | pass | 7/7 | 3.4 | 21.2 | 4800 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 4.0 | 19.5 | 5113 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 2.3 | 23.2 | 5233 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 1.9 | 29.5 | 5116 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 2.6 | 23.1 | 4920 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/009-event-bus-r3 |
| 011-status-effects | 1 | fail | 1/8 | 3.3 | 19.9 | 5230 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/011-status-effects-r1 |
| 011-status-effects | 2 | fail | 0/8 | 3.4 | 30.9 | 5182 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/0 | 3.1 | 244.5 | 5170 | 412 | 0.94 | no | exp/e4-qwen-ctx128k-kvq8-20261106020400/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E4 comparison](../e4.md).
