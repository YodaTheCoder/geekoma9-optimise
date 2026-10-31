from __future__ import annotations

from harness.agents.base import Agent
from harness.agents.command import CommandAgent
from harness.agents.null import NullAgent
from harness.agents.oracle import OracleAgent
from harness.config import AgentConfig, ConfigError


def make_agent(cfg: AgentConfig) -> Agent:
    if cfg.kind == "null":
        return NullAgent()
    if cfg.kind == "oracle":
        return OracleAgent()
    if cfg.kind == "command":
        return CommandAgent(cfg)
    raise ConfigError(f"agent.kind: unknown {cfg.kind!r}")
