from __future__ import annotations

import json
import shlex
import time

from harness.config import ConfigError, RuntimeConfig
from harness.remote import Remote

UNIT_NAME = "agentbench-runtime"
UNIT_PATH = f"/home/markn/.config/systemd/user/{UNIT_NAME}.service"
API = "127.0.0.1:11434"
# Non-interactive ssh has no user bus; point systemctl --user at it.
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user"


def _fixed_env(cfg: RuntimeConfig) -> list[tuple[str, str]]:
    return [
        ("OLLAMA_HOST", API),
        ("OLLAMA_CONTEXT_LENGTH", str(cfg.context)),
        ("OLLAMA_KEEP_ALIVE", "-1"),
        ("OLLAMA_MAX_LOADED_MODELS", "1"),
        # system Ollama's model store; reused so models are not re-pulled
        ("OLLAMA_MODELS", "/usr/share/ollama/.ollama/models"),
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
        self.model = cfg.model
        self.upstream = f"http://{API}"

    def _get(self, remote: Remote, path: str) -> dict:
        return json.loads(remote.run(f"curl -sf {API}{path}", timeout=30).stdout)

    def start(self, remote: Remote) -> None:
        remote.write_text(UNIT_PATH, render_unit(self.cfg))
        remote.run(f"{SYSTEMCTL} daemon-reload")
        remote.run(f"{SYSTEMCTL} restart {UNIT_NAME}")
        deadline = time.monotonic() + 60
        while True:
            if remote.run(f"curl -sf {API}/api/version", timeout=15, check=False).returncode == 0:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("ollama did not become ready within 60s")
            time.sleep(1)
        body = json.dumps({"model": self.model, "prompt": "hi",
                           "options": {"num_predict": 1}, "keep_alive": -1})
        remote.run(f"curl -sf --max-time 600 -X POST -d {shlex.quote(body)} {API}/api/generate",
                   timeout=620)

    def stop(self, remote: Remote) -> None:
        remote.run(f"{SYSTEMCTL} stop {UNIT_NAME}", check=False)

    def versions(self, remote: Remote) -> dict[str, str]:
        out = remote.run("/usr/local/bin/ollama --version", timeout=30).stdout.strip()
        digest = ""
        for m in self._get(remote, "/api/tags").get("models", []):
            if m.get("name") == self.model:
                digest = m.get("digest", "")
        return {"runtime": f"ollama {out}", "model_digest": digest}

    def loaded_models(self, remote: Remote) -> list[str]:
        return [m["name"] for m in self._get(remote, "/api/ps").get("models", [])]
