import pytest

from harness.config import AgentConfig, ConfigError, ExperimentConfig, RuntimeConfig
from harness.tiers import tier_plan


def cfg(**over):
    base = dict(
        id="t",
        task_set="v1",
        tier="screening",
        runtime=RuntimeConfig(kind="ollama", model="m", context=1),
        agent=AgentConfig(kind="null", name="null"),
    )
    base.update(over)
    return ExperimentConfig(**base)


def test_screening_is_six_by_one():
    assert len(tier_plan(cfg(tier="screening"))) == 6


def test_finalists_is_twelve_by_three():
    plan = tier_plan(cfg(tier="finalists"))
    assert len(plan) == 36 and {r for _, r in plan} == {1, 2, 3}


def test_all_is_twelve_by_one():
    assert len(tier_plan(cfg(tier="all"))) == 12


def test_unknown_task_set_raises():
    with pytest.raises(ConfigError):
        tier_plan(cfg(task_set="v9"))


def test_probe_tier():
    assert tier_plan(cfg(tier="probe")) == [("004-weapon-cooldown", 1)]
