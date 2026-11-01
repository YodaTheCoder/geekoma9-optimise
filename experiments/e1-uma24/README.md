<!-- results:start -->
| metric | value |
|---|---|
| attempts | 6 |
| passes | 4 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 0.667 |
| wall_hours | 0.232 |
| solved_per_8h | 137.993 |
| median_tg_tps | 26.597 |
| median_pp_tps | 3976.694 |
| throttled | 0 |
| max_peak_mem_mib | 7493 |
| max_peak_swap_mib | 4140 |
| min_gpu_offload | 0.959 |

| task | repeat | status | hidden | wall min | tg tok/s | ram MiB | swap MiB | offload | throttled | branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 1.6 | 27.3 | 4035 | 0 | 0.96 | no | exp/e1-uma24-20261101145853/001-health-clamp-r1 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 1.5 | 25.9 | 5050 | 0 | 0.96 | no | exp/e1-uma24-20261101145853/004-weapon-cooldown-r1 |
| 005-inventory-pickup | 1 | fail | 3/6 | 2.1 | 26.3 | 6091 | 0 | 0.96 | no | exp/e1-uma24-20261101145853/005-inventory-pickup-r1 |
| 007-patrol-enemy | 1 | pass | 7/7 | 2.1 | 26.9 | 7145 | 162 | 0.96 | no | exp/e1-uma24-20261101145853/007-patrol-enemy-r1 |
| 009-event-bus | 1 | pass | 6/6 | 2.8 | 27.8 | 7493 | 4140 | 0.96 | no | exp/e1-uma24-20261101145853/009-event-bus-r1 |
| 011-status-effects | 1 | fail | 0/8 | 3.7 | 26.3 | 7480 | 4096 | 0.96 | no | exp/e1-uma24-20261101145853/011-status-effects-r1 |
<!-- results:end -->

## Findings

- Same layout as E0 (BIOS UMA 24 GiB; Linux 7.4 GiB RAM, 8 GiB swap; GTT 3.70 GiB, TTM pages_limit 969396),
  now measured: every attempt passed the host check.
- The model does not fit in the carve-out. Ollama's `/api/ps` reports 25.4 GB for qwen3-coder:30b at 64k
  context, 95.9% of it on the GPU, so about 1 GB of weights and cache sits in system RAM.
- System RAM is the bottleneck. Peak use reaches the 7.4 GiB ceiling from task 007 on, and swap climbs to
  4.1 GiB in tasks 009 and 011 (Godot plus the agent plus the CPU-side part of the model).
- Generation speed: median 26.6 tok/s against E0's 25.3; prompt processing 3977 tok/s against 3828.
- 4/6 pass against E0's 2/6 (one run per task: a difference of this size is noise and does not decide E1).
