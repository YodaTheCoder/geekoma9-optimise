from __future__ import annotations

from typing import Protocol

from harness.remote import Remote


class Runtime(Protocol):
    upstream: str  # URL on geekoma9
    model: str

    def start(self, remote: Remote) -> None:
        """Start the runtime and warm up the model."""

    def stop(self, remote: Remote) -> None: ...

    def versions(self, remote: Remote) -> dict[str, str]: ...

    def loaded_models(self, remote: Remote) -> list[str]: ...
