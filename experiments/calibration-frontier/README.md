<!-- results:start -->
| metric | value |
|---|---|
| attempts | 12 |
| passes | 12 |
| infra_errors | 0 |
| unscored | 0 |
| pass_rate | 1.000 |
| wall_hours | 0.189 |
| solved_per_8h | 508.899 |
| median_tg_tps | - |
| median_pp_tps | - |
| throttled | 0 |

| task | repeat | status | hidden | wall min | tg tok/s | throttled | branch |
|---|---|---|---|---|---|---|---|
| 001-health-clamp | 1 | pass | 5/5 | 0.5 | - | no | exp/calibration-frontier-202610311458/001-health-clamp-r1 |
| 002-damage-signal | 1 | pass | 7/7 | 1.1 | - | no | exp/calibration-frontier-202610311458/002-damage-signal-r1 |
| 003-score-combo | 1 | pass | 4/4 | 0.6 | - | no | exp/calibration-frontier-202610311458/003-score-combo-r1 |
| 004-weapon-cooldown | 1 | pass | 5/5 | 0.7 | - | no | exp/calibration-frontier-202610311458/004-weapon-cooldown-r1 |
| 005-inventory-pickup | 1 | pass | 6/6 | 0.9 | - | no | exp/calibration-frontier-202610311458/005-inventory-pickup-r1 |
| 006-save-load | 1 | pass | 5/5 | 1.0 | - | no | exp/calibration-frontier-202610311458/006-save-load-r1 |
| 007-patrol-enemy | 1 | pass | 7/7 | 1.0 | - | no | exp/calibration-frontier-202610311458/007-patrol-enemy-r1 |
| 008-hud-health | 1 | pass | 6/6 | 1.0 | - | no | exp/calibration-frontier-202610311458/008-hud-health-r1 |
| 009-event-bus | 1 | pass | 6/6 | 1.0 | - | no | exp/calibration-frontier-202610311458/009-event-bus-r1 |
| 010-wave-spawner | 1 | pass | 7/7 | 1.0 | - | no | exp/calibration-frontier-202610311458/010-wave-spawner-r1 |
| 011-status-effects | 1 | pass | 8/8 | 1.4 | - | no | exp/calibration-frontier-202610311458/011-status-effects-r1 |
| 012-weapon-tests | 1 | pass | 11/11 | 1.2 | - | no | exp/calibration-frontier-202610311458/012-weapon-tests-r1 |
<!-- results:end -->

## Findings

- Claude Code 2.1.309 with `claude-opus-5-5` solved all 12 v1 tasks on the first attempt, with no
  regressions, in 0.5–1.4 minutes each (4–8 tool calls). Total cost $4.15 ($0.35 per task, list
  price, from Claude Code's own `total_cost_usd`).
- The frontier review (`reviews.jsonl`) would merge all 12: quality 5 on 7 tasks, 4 on 5.
- So every v1 task is solvable from its issue text alone and the hidden tests accept a good
  independent solution, not just the reference one.
- Caveat: a 100% pass rate gives no headroom signal. If local models also land near 12/12, v1
  can't separate them on pass rate (throughput still separates them) and a harder v2 is needed.
- Token and tok/s columns are empty by design: they are measured at the local usage proxy, which
  frontier traffic doesn't pass through.
- Orchestrated from `newbuntu.local` in `tmux` (see `docs/provisioning.md`).
