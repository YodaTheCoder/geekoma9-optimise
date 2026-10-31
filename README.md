# harness

Benchmark harness that runs local coding-agent configurations against a task set on a remote Linux box and records the results.

Design spec: `docs/superpowers/specs/2026-10-31-coding-agent-optimisation-design.md`.

## Reproduce

Requirements: a Linux box with an AMD iGPU running Ollama (the machine under test), and an orchestrator on the
same network with `uv`, ssh key access to it and, for reviews, a logged-in `claude` CLI. Full setup, with
rollbacks, is in `docs/provisioning.md`.

1. `uv sync`
2. `uv run harness provision` checks the test machine (Godot, Ollama, deploy key, model store, sudo).
3. `uv run harness validate --task-set v1` runs the oracle and null agents on every task (all must pass and fail
   respectively).
4. `uv run harness run experiments/<id>/config.yaml` runs an experiment; rerunning resumes it. Run it in `tmux`
   on an always-on machine: attempts take minutes each and the orchestrator must stay connected.
5. `uv run harness report experiments/<id>` writes the results table into the experiment's README;
   `uv run harness review experiments/<id>` adds the frontier review.

Results: `docs/FINDINGS.md`. Each attempt's output is the branch named in its record, in
`YodaTheCoder/godot-agent-bench`.
