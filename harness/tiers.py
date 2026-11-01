from __future__ import annotations

from harness.config import ConfigError, ExperimentConfig

TASK_SETS: dict[str, dict[str, list[str]]] = {
    "v1": {
        "all": [
            "001-health-clamp", "002-damage-signal", "003-score-combo",
            "004-weapon-cooldown", "005-inventory-pickup", "006-save-load",
            "007-patrol-enemy", "008-hud-health", "009-event-bus",
            "010-wave-spawner", "011-status-effects", "012-weapon-tests",
        ],
        "probe": ["004-weapon-cooldown"],
        "screening": [
            "001-health-clamp", "004-weapon-cooldown", "005-inventory-pickup",
            "007-patrol-enemy", "009-event-bus", "011-status-effects",
        ],
    },
}

# tier -> (task subset key, repeats)
_TIERS = {
    "probe": ("probe", 1),
    "screening": ("screening", 1),
    "screening3": ("screening", 3),
    "finalists": ("all", 3),
    "all": ("all", 1),
}


def tier_plan(cfg: ExperimentConfig) -> list[tuple[str, int]]:
    """Ordered (task, repeat) pairs, task-major then by repeat (repeats from 1)."""
    try:
        sets = TASK_SETS[cfg.task_set]
    except KeyError:
        raise ConfigError(f"task_set: unknown {cfg.task_set!r}") from None
    subset, repeats = _TIERS[cfg.tier]
    return [(t, r) for t in sets[subset] for r in range(1, repeats + 1)]
