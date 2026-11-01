from __future__ import annotations

from typing import Protocol

from harness.remote import Remote, RemoteError


class RuntimeStartError(RemoteError):
    """Runtime failed to start, warm up or report state (maps to infra_error)."""


class Runtime(Protocol):
    upstream: str  # URL on geekoma9
    model: str

    def start(self, remote: Remote) -> None:
        """Start the runtime and warm up the model."""

    def stop(self, remote: Remote) -> None: ...

    def versions(self, remote: Remote) -> dict[str, str]: ...

    def loaded_models(self, remote: Remote) -> list[str]: ...
