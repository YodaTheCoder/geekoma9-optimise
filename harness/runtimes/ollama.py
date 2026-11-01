from __future__ import annotations

import json
import shlex
import subprocess
import time

from harness.config import ConfigError, RuntimeConfig
from harness.remote import Remote, RemoteError
from harness.runtimes.base import RuntimeStartError

UNIT_NAME = "agentbench-runtime"
UNIT_PATH = f"/home/markn/.config/systemd/user/{UNIT_NAME}.service"
API = "127.0.0.1:11434"
# Non-interactive ssh has no user bus; point systemctl --user at it.
USER_BUS = "XDG_RUNTIME_DIR=/run/user/$(id -u)"
SYSTEMCTL = f"{USER_BUS} systemctl --user"
JOURNALCTL = f"{USER_BUS} journalctl --user"


def _fixed_env(cfg: RuntimeConfig) -> list[tuple[str, str]]:
    return [
        ("OLLAMA_HOST", API),
        ("OLLAMA_CONTEXT_LENGTH", str(cfg.context)),
        ("OLLAMA_KEEP_ALIVE", "-1"),
        ("OLLAMA_MAX_LOADED_MODELS", "1"),
        # system Ollama's model store; reused so models are not re-pulled
        ("OLLAMA_MODELS", "/usr/share/ollama/.ollama/models"),
        # Ollama drops the integrated GPU by default; CPU-only cannot fit the
        # models in this box's system RAM (OOM-killed), so always enable it.
        ("OLLAMA_IGPU_ENABLE", "1"),
    ]


def render_unit(cfg: RuntimeConfig) -> str:
    fixed = _fixed_env(cfg)
    clash = sorted({k for k, _ in fixed} & set(cfg.env))
    if clash:
        raise ConfigError(f"runtime.env: {clash[0]} is set by the harness and cannot be overridden")
    env = fixed + sorted(cfg.env.items())
    lines = ["[Unit]", "Description=agentbench Ollama runtime", "",
             "[Service]", "ExecStart=/usr/local/bin/ollama serve"]
    lines += [f"Environment={k}={v}" for k, v in env]
    lines += ["Restart=no", "", "[Install]", "WantedBy=default.target", ""]
    return "\n".join(lines)


class OllamaRuntime:
    def __init__(self, cfg: RuntimeConfig):
        self.cfg = cfg
        # normalise so /api/tags and /api/ps names (always tagged) match
        last = cfg.model.rsplit("/", 1)[-1]
        self.model = cfg.model if ":" in last else f"{cfg.model}:latest"
        self.upstream = f"http://{API}"

    def _get(self, remote: Remote, path: str) -> dict:
        return json.loads(remote.run(f"curl -sf {API}{path}", timeout=30).stdout)

    def _journal(self, remote: Remote) -> str:
        try:
            return remote.run(f"{JOURNALCTL} -u {UNIT_NAME} -n 20 --no-pager",
                              timeout=20, check=False).stdout.strip()
        except (RemoteError, OSError):
            return "(journal unavailable)"

    def start(self, remote: Remote) -> None:
        remote.run(f"mkdir -p {shlex.quote(UNIT_PATH.rsplit('/', 1)[0])}")
        remote.write_text(UNIT_PATH, render_unit(self.cfg))
        remote.run(f"{SYSTEMCTL} daemon-reload")
        remote.run(f"{SYSTEMCTL} restart {UNIT_NAME}")
        deadline = time.monotonic() + 60
        last_err = ""
        while True:
            try:
                r = remote.run(f"curl -sf {API}/api/version", timeout=15, check=False)
                if r.returncode == 0:
                    break
                last_err = r.stderr.strip()
            except RemoteError as e:
                last_err = str(e)
            if time.monotonic() >= deadline:
                raise RuntimeStartError(
                    f"ollama did not become ready within 60s ({last_err})\n{self._journal(remote)}")
            time.sleep(1)
        body = json.dumps({"model": self.model, "prompt": "hi",
                           "options": {"num_predict": 1}, "keep_alive": -1})
        try:
            remote.run(f"curl -sf --max-time 600 -X POST -d {shlex.quote(body)} {API}/api/generate",
                       timeout=620)
        except (subprocess.CalledProcessError, RemoteError) as e:
            detail = getattr(e, "stderr", None) or str(e)
            raise RuntimeStartError(
                f"warm-up of {self.model} failed: {detail}\n{self._journal(remote)}") from e

    def stop(self, remote: Remote) -> None:
        remote.run(f"{SYSTEMCTL} stop {UNIT_NAME}", check=False)

    def versions(self, remote: Remote) -> dict[str, str]:
        out = remote.run("/usr/local/bin/ollama --version", timeout=30).stdout.strip()
        out = out.removeprefix("ollama version is ").strip()
        for m in self._get(remote, "/api/tags").get("models", []):
            if m.get("name") == self.model and m.get("digest"):
                return {"runtime": f"ollama {out}", "model_digest": m["digest"]}
        raise RuntimeStartError(f"model {self.model} not found in /api/tags")

    def loaded_models(self, remote: Remote) -> list[str]:
        return [m["name"] for m in self._get(remote, "/api/ps").get("models", [])]

    def gpu_offload(self, remote: Remote) -> float | None:
        for m in self._get(remote, "/api/ps").get("models", []):
            if m.get("name") == self.model:
                size, vram = m.get("size"), m.get("size_vram")
                if not size or vram is None:
                    return None
                return round(vram / size, 3)
        return None
