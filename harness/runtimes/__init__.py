from __future__ import annotations

from harness.config import RuntimeConfig
from harness.runtimes.base import Runtime
from harness.runtimes.llamacpp import LlamaCppRuntime
from harness.runtimes.ollama import OllamaRuntime


def make_runtime(cfg: RuntimeConfig) -> Runtime:
    if cfg.kind == "ollama":
        return OllamaRuntime(cfg)
    if cfg.kind == "llamacpp":
        return LlamaCppRuntime(cfg)
    raise ValueError(f"unknown runtime kind: {cfg.kind!r}")
