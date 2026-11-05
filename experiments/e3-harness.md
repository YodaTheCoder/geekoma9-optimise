# E3 harness comparison (2026-11-04)

Same setup as the capped model screen ([e3-screen.md](e3-screen.md)): 24 GiB UMA, Ollama 0.34.4, 64k context,
`LLAMA_ARG_CACHE_RAM=1024`, screening3 tier (tasks 001, 004, 005, 007, 009, 011, three repeats each). Only the
agent harness changes. The OpenCode rows are the `e3-cap-*` runs; the new runs have a 30-minute limit per attempt
instead of 45. No OpenCode attempt took longer than 30 minutes, so the limit does not change its numbers.

| model | harness | experiment | pass | timeouts | timeouts with hidden tests passing | median min/attempt | median gen tokens | agent hours | solved per 8h |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-coder:30b | OpenCode 1.18.32 | `e3-cap-qwen3-coder` | 11/18 | 0 | 0 | 2.2 | 2360 | 0.67 | 131.6 |
| qwen3-coder:30b | mini-swe-agent 2.4.6 | `e3-h-mini-qwen3-coder` | 11/18 | 0 | 0 | 2.1 | 3199 | 0.73 | 121.0 |
| qwen3-coder:30b | Claude Code 2.1.316 | `e3-h-claude-code-qwen3-coder` | 6/18 | 5 | 4 | 3.3 | 4832 | 3.04 | 15.8 |
| laguna-xs-2.1 | OpenCode 1.18.32 | `e3-cap-laguna` | 14/18 | 0 | 0 | 9.0 | 8968 | 3.29 | 34.0 |
| laguna-xs-2.1 | mini-swe-agent 2.4.6 | `e3-h-mini-laguna` | 12/18 | 5 | 4 | 20.5 | 15461 | 5.56 | 17.3 |
| laguna-xs-2.1 | Claude Code 2.1.316 | `e3-h-claude-code-laguna` | 10/18 | 7 | 4 | 21.7 | 20216 | 5.49 | 14.6 |

Infra errors: 1 in `e3-cap-qwen3-coder`, 2 in `e3-h-claude-code-laguna` (ssh timeouts from newbuntu, retried).
mini-swe-agent does not stream, so it has no tok/s figures. Claude Code's PP tok/s is not comparable
(Anthropic-style prompt caching makes the counted prompt much larger than what is processed).

## Findings

- **OpenCode is the best harness for both models.** It has the highest pass count for each model, the fewest
  tokens per attempt and no timeouts. Nothing here argues for switching.
- **mini-swe-agent ties OpenCode on qwen3-coder** (11/18, similar time and tokens) but loses on laguna: laguna
  writes about 1.7x the tokens under mini and takes over twice as long per attempt.
- **Claude Code is the worst fit for these local models.** qwen3-coder solved 6/18 and took 4.5x as long as under
  OpenCode; laguna solved 10/18 at 5.5 hours. Its long system prompt and tool set make each turn more expensive,
  and both models often fail to stop.
- **"Won't stop" is the main failure under the non-OpenCode harnesses.** 12 of the 17 timeouts already passed every
  hidden test when the limit hit: the model had fixed the bug and kept going (re-running tests, echoing status,
  tidying). Counting those as solved would give mini-laguna 16/18 and Claude Code 10/18 (qwen) and 14/18 (laguna),
  but an unattended runner needs the agent to finish, so they stay failures here.
- **Memory is not a factor.** Peak RAM stayed between 4.2 and 5.4 GiB with under 0.5 GiB swap for every run, and
  there were no OOM kills.
- **Recommendation:** keep OpenCode. Pick the model by goal: qwen3-coder for throughput on an overnight queue
  (about 4x more solved per hour), laguna when each issue should be solved first time.
- Proposed next: E4 (quantisation and context length) with OpenCode on laguna and qwen3-coder; E2 (runtime, e.g.
  llama.cpp directly or Vulkan) after that.
