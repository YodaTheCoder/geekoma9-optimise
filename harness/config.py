from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class RuntimeConfig:
    kind: Literal["ollama"]
    model: str
    context: int
    env: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentConfig:
    kind: Literal["null", "oracle", "command"]
    name: str
    command: str | None = None
    version: str = ""
    steps_regex: str | None = None
    env: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentConfig:
    id: str
    task_set: str
    tier: Literal["screening", "finalists", "all"]
    runtime: RuntimeConfig
    agent: AgentConfig
    timeout_s: int = 2700
    cooldown_s: int = 120
    sampling: dict[str, float] = field(default_factory=dict)
    notes: str = ""


_TIERS = ("screening", "finalists", "all")
# ids and run_ids become branch names and path parts.
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def check_safe_id(value: str, what: str) -> str:
    if not _SAFE_ID.match(value) or ".." in value:
        raise ConfigError(f"{what}: {value!r} must match {_SAFE_ID.pattern} and not contain '..'")
    return value
_RUNTIME_KINDS = ("ollama",)
_AGENT_KINDS = ("null", "oracle", "command")


def _mapping(data: Any, key: str) -> dict:
    if not isinstance(data, dict):
        raise ConfigError(f"{key}: expected a mapping")
    return data


def _require(data: dict, key: str, typ: type, prefix: str = "") -> Any:
    if key not in data:
        raise ConfigError(f"{prefix}{key}: missing")
    return _typed(data, key, typ, prefix)


def _typed(data: dict, key: str, typ: type, prefix: str = "") -> Any:
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, typ):
        raise ConfigError(f"{prefix}{key}: expected {typ.__name__}")
    return value


def _str_dict(data: dict, key: str, prefix: str, value_types: tuple) -> dict:
    value = data.get(key, {})
    if not isinstance(value, dict) or not all(
        isinstance(k, str) and isinstance(v, value_types) and not isinstance(v, bool)
        for k, v in value.items()
    ):
        raise ConfigError(f"{prefix}{key}: expected a mapping of str to {value_types[0].__name__}")
    return dict(value)


def _unknown(data: dict, allowed: set[str], prefix: str) -> None:
    extra = set(data) - allowed
    if extra:
        raise ConfigError(f"{prefix}{sorted(extra)[0]}: unknown key")


def _runtime(raw: Any) -> RuntimeConfig:
    d = _mapping(raw, "runtime")
    _unknown(d, {"kind", "model", "context", "env"}, "runtime.")
    kind = _require(d, "kind", str, "runtime.")
    if kind not in _RUNTIME_KINDS:
        raise ConfigError(f"runtime.kind: must be one of {list(_RUNTIME_KINDS)}, got {kind!r}")
    return RuntimeConfig(
        kind=kind,
        model=_require(d, "model", str, "runtime."),
        context=_require(d, "context", int, "runtime."),
        env=_str_dict(d, "env", "runtime.", (str,)),
    )


def _agent(raw: Any) -> AgentConfig:
    d = _mapping(raw, "agent")
    _unknown(d, {"kind", "name", "command", "version", "steps_regex", "env"}, "agent.")
    kind = _require(d, "kind", str, "agent.")
    if kind not in _AGENT_KINDS:
        raise ConfigError(f"agent.kind: must be one of {list(_AGENT_KINDS)}, got {kind!r}")
    command = d.get("command")
    if command is not None:
        command = _typed(d, "command", str, "agent.")
    if kind == "command" and not command:
        raise ConfigError("agent.command: required when agent.kind is 'command'")
    steps_regex = d.get("steps_regex")
    if steps_regex is not None:
        steps_regex = _typed(d, "steps_regex", str, "agent.")
    return AgentConfig(
        kind=kind,
        name=_require(d, "name", str, "agent."),
        command=command,
        version=str(d.get("version", "")),
        steps_regex=steps_regex,
        env=_str_dict(d, "env", "agent.", (str,)),
    )


def load_config(path: Path) -> ExperimentConfig:
    try:
        data = yaml.safe_load(Path(path).read_text())
    except (OSError, yaml.YAMLError) as e:
        raise ConfigError(f"{path}: {e}") from e
    d = _mapping(data, "config")
    _unknown(d, {"id", "task_set", "tier", "runtime", "agent", "timeout_s",
                 "cooldown_s", "sampling", "notes"}, "")
    tier = _require(d, "tier", str)
    if tier not in _TIERS:
        raise ConfigError(f"tier: must be one of {list(_TIERS)}, got {tier!r}")
    if "runtime" not in d:
        raise ConfigError("runtime: missing")
    if "agent" not in d:
        raise ConfigError("agent: missing")
    sampling = _str_dict(d, "sampling", "", (int, float))
    if sampling:
        raise ConfigError("sampling: not applied by any runtime yet; leave it empty")
    return ExperimentConfig(
        id=check_safe_id(_require(d, "id", str), "id"),
        task_set=_require(d, "task_set", str),
        tier=tier,
        runtime=_runtime(d["runtime"]),
        agent=_agent(d["agent"]),
        timeout_s=_typed(d, "timeout_s", int) if "timeout_s" in d else 2700,
        cooldown_s=_typed(d, "cooldown_s", int) if "cooldown_s" in d else 120,
        sampling={k: float(v) for k, v in sampling.items()},
        notes=_typed(d, "notes", str) if "notes" in d else "",
    )
