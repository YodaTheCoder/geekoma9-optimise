from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from harness.bench import BenchRepo
from harness.config import ConfigError, ExperimentConfig, load_config
from harness.remote import Remote
from harness.report import render_markdown, summarize, write_readme
from harness.results import read_records
from harness.run import run_experiment
from harness.tiers import tier_plan

# validate only needs a runtime that starts; the E0 baseline model is already pulled.
VALIDATE_MODEL = "qwen3-coder:30b"
VALIDATE_CONTEXT = 65536


def _report(exp_dir: Path) -> None:
    records = read_records(exp_dir / "results.jsonl")
    write_readme(exp_dir / "README.md", render_markdown(summarize(records), records))


def _run(cfg: ExperimentConfig, exp_dir: Path) -> None:
    remote = Remote()
    run_experiment(cfg, exp_dir, remote=remote, bench=BenchRepo(remote))
    _report(exp_dir)


def cmd_run(args) -> int:
    path = Path(args.config)
    cfg = load_config(path)
    _run(cfg, path.parent)
    return 0


def _offenders(cfg: ExperimentConfig, exp_dir: Path, expected: str) -> list[str]:
    """Plan entries whose last scored outcome is not `expected` (or that never scored)."""
    last: dict[tuple[str, int], str] = {}
    for r in read_records(exp_dir / "results.jsonl"):
        if r.status != "infra_error":
            last[(r.task, r.repeat)] = r.status
    return [f"{cfg.agent.kind}: {task} r{rep}: {last.get((task, rep), 'no result')}"
            for task, rep in tier_plan(cfg) if last.get((task, rep)) != expected]


def cmd_validate(args) -> int:
    bad: list[str] = []
    for kind, expected in (("null", "fail"), ("oracle", "pass")):
        exp_id = f"validate-{args.task_set}-{kind}"
        exp_dir = Path(args.experiments_dir) / exp_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        (exp_dir / "config.yaml").write_text(yaml.safe_dump({
            "id": exp_id, "task_set": args.task_set, "tier": "all", "cooldown_s": 0,
            "runtime": {"kind": "ollama", "model": args.model, "context": VALIDATE_CONTEXT},
            "agent": {"kind": kind, "name": kind}}, sort_keys=False))
        cfg = load_config(exp_dir / "config.yaml")
        # Always a fresh run: stale results must not satisfy the check.
        for name in ("run_id", "results.jsonl"):
            (exp_dir / name).unlink(missing_ok=True)
        _run(cfg, exp_dir)
        bad += _offenders(cfg, exp_dir, expected)
    for line in bad:
        print(line)
    print("validate: FAILED" if bad else "validate: ok")
    return 1 if bad else 0


def cmd_report(args) -> int:
    _report(Path(args.exp_dir))
    return 0


def cmd_not_implemented(args) -> int:
    print(f"harness {args.command}: not implemented yet", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("run", help="run or resume an experiment")
    s.add_argument("config")
    s.set_defaults(func=cmd_run)
    s = sub.add_parser("validate", help="null agent must fail and oracle must pass every task")
    s.add_argument("--task-set", required=True)
    s.add_argument("--model", default=VALIDATE_MODEL)
    s.add_argument("--experiments-dir", default="experiments")
    s.set_defaults(func=cmd_validate)
    s = sub.add_parser("report", help="rewrite the results block in EXP_DIR/README.md")
    s.add_argument("exp_dir")
    s.set_defaults(func=cmd_report)
    s = sub.add_parser("review", help="frontier review of passing attempts")
    s.add_argument("exp_dir")
    s.set_defaults(func=cmd_not_implemented)
    s = sub.add_parser("provision", help="set up geekoma9")
    s.set_defaults(func=cmd_not_implemented)
    args = p.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
