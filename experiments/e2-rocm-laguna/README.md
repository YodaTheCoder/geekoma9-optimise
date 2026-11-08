<!-- results:start -->
| metric | value |
|---|---|
| attempts | 19 |
| passes | 13 |
| infra_errors | 1 |
| unscored | 0 |
| pass_rate | 0.722 |
| wall_hours | 4.187 |
| solved_per_8h | 24.839 |
| median_tg_tps | 16.456 |
| median_pp_tps | 13267.069 |
| throttled | 0 |
| max_peak_mem_mib | 5841 |
| max_peak_swap_mib | 664 |
| min_gpu_offload | 1.000 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.8 | 24.7 | 4684 | 610 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/001-health-clamp-r1 |
| 001-health-clamp | 2 | pass | 5/5 | 2.5 | 23.6 | 5171 | 610 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/001-health-clamp-r2 |
| 001-health-clamp | 3 | pass | 5/5 | 5.2 | 21.2 | 5456 | 664 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/001-health-clamp-r3 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 2.5 | 22.9 | 4881 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/004-weapon-cooldown-r1 |
| 004-weapon-cooldown | 2 | pass | 5/5 | 1.4 | 23.8 | 4458 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/004-weapon-cooldown-r2 |
| 004-weapon-cooldown | 3 | pass | 5/5 | 3.0 | 22.2 | 5160 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/004-weapon-cooldown-r3 |
| 005-inventory-pickup | 1 | pass | 6/6 | 17.6 | 13.2 | 5791 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/005-inventory-pickup-r1 |
| 005-inventory-pickup | 2 | fail | 3/6 | 19.7 | 13.4 | 5322 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/005-inventory-pickup-r2 |
| 005-inventory-pickup | 3 | timeout | 6/6 | 30.0 | 12.0 | 5841 | 653 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/005-inventory-pickup-r3 |
| 007-patrol-enemy | 1 | infra_error | 0/0 | 0.0 | - | - | - | 1.00 | no | exp/e2-rocm-laguna-20261108043825/007-patrol-enemy-r1 |
| 007-patrol-enemy | 1 | pass | 7/7 | 23.3 | 13.8 | 5238 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/007-patrol-enemy-r1-t2 |
| 007-patrol-enemy | 2 | pass | 7/7 | 14.0 | 15.6 | 5250 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/007-patrol-enemy-r2 |
| 007-patrol-enemy | 3 | pass | 7/7 | 24.5 | 13.5 | 5260 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/007-patrol-enemy-r3 |
| 009-event-bus | 1 | pass | 6/6 | 6.6 | 17.9 | 5667 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/009-event-bus-r1 |
| 009-event-bus | 2 | pass | 6/6 | 7.0 | 17.3 | 5505 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/009-event-bus-r2 |
| 009-event-bus | 3 | pass | 6/6 | 4.7 | 18.9 | 5280 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/009-event-bus-r3 |
| 011-status-effects | 1 | timeout | 0/8 | 30.0 | 12.5 | 5253 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/011-status-effects-r1 |
| 011-status-effects | 2 | timeout | 0/8 | 30.0 | 12.6 | 5308 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/011-status-effects-r2 |
| 011-status-effects | 3 | fail | 0/8 | 27.7 | 13.0 | 5320 | 612 | 1.00 | no | exp/e2-rocm-laguna-20261108043825/011-status-effects-r3 |
<!-- results:end -->

## Findings

See [the E2 comparison](../e2.md).
