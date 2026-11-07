"""llama.cpp `llama-server` as the runtime, run as the same systemd user unit as Ollama.

The server answers on the Ollama address so the usage proxy and agents need no change, and
serves one model under `--alias <model>`, so agent configs name the same model as under Ollama.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import time

from harness.config import ConfigError, RuntimeConfig
from harness.remote import Remote, RemoteError
from harness.runtimes.base import RuntimeStartError
from harness.runtimes.ollama import API, JOURNALCTL, SYSTEMCTL, UNIT_NAME, UNIT_PATH

# Loading a 20 GB model from disk takes longer than Ollama's API coming up.
READY_TIMEOUT_S = 600
_BUFFER = re.compile(r"(\S+) model buffer size\s*=\s*([\d.]+) MiB")


def _quote(arg: str) -> str:
    """Quote an argument for a systemd ExecStart line."""
    if arg and not re.search(r'[\s"\'\\$%;]', arg):
        return arg
    return '"' + arg.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%").replace("$", "$$") + '"'


def render_unit(cfg: RuntimeConfig) -> str:
    libdir = cfg.server.rsplit("/", 1)[0]
    fixed = [("LD_LIBRARY_PATH", libdir)]
    clash = sorted({k for k, _ in fixed} & set(cfg.env))
    if clash:
        raise ConfigError(f"runtime.env: {clash[0]} is set by the harness and cannot be overridden")
    host, port = API.split(":")
    argv = [cfg.server, "-m", cfg.gguf, "--alias", cfg.model, "--host", host, "--port", port,
            "-c", str(cfg.context), "-np", "1", "-ngl", "999", "--jinja", "--no-webui",
            # 4 (as Ollama runs it) keeps the load_tensors buffer lines gpu_offload reads
            "--log-verbosity", "4", *cfg.args]
    lines = ["[Unit]", "Description=agentbench llama.cpp runtime", "",
             "[Service]", "ExecStart=" + " ".join(_quote(a) for a in argv)]
    lines += [f"Environment={k}={v}" for k, v in fixed + sorted(cfg.env.items())]
    lines += ["Restart=no", "", "[Install]", "WantedBy=default.target", ""]
    return "\n".join(lines)


def gpu_share(log: str) -> float | None:
    """GPU share of the model weights from llama.cpp's `<buffer> model buffer size` lines."""
    sizes = [(name, float(mib)) for name, mib in _BUFFER.findall(log)]
    total = sum(mib for _, mib in sizes)
    if not total:
        return None
    gpu = sum(mib for name, mib in sizes if not name.startswith("CPU"))
    return round(gpu / total, 3)


class LlamaCppRuntime:
    def __init__(self, cfg: RuntimeConfig):
        self.cfg = cfg
        self.model = cfg.model
        self.upstream = f"http://{API}"

    def _get(self, remote: Remote, path: str) -> dict:
        return json.loads(remote.run(f"curl -sf {API}{path}", timeout=30).stdout)

    def _invocation_log(self, remote: Remote, lines: int | None = None) -> str:
        inv = remote.run(f"{SYSTEMCTL} show -p InvocationID --value {UNIT_NAME}",
                         timeout=20, check=False).stdout.strip()
        sel = f"_SYSTEMD_INVOCATION_ID={inv}" if inv else f"-u {UNIT_NAME}"
        tail = f" -n {lines}" if lines else ""
        return remote.run(f"{JOURNALCTL} {sel}{tail} --no-pager -o cat",
                          timeout=30, check=False).stdout

    def _journal(self, remote: Remote) -> str:
        try:
            return self._invocation_log(remote, 20).strip()
        except (RemoteError, OSError):
            return "(journal unavailable)"

    def start(self, remote: Remote) -> None:
        remote.run(f"mkdir -p {shlex.quote(UNIT_PATH.rsplit('/', 1)[0])}")
        remote.write_text(UNIT_PATH, render_unit(self.cfg))
        remote.run(f"{SYSTEMCTL} daemon-reload")
        remote.run(f"{SYSTEMCTL} restart {UNIT_NAME}")
        deadline = time.monotonic() + READY_TIMEOUT_S
        last_err = ""
        while True:  # /health is 503 while the model loads, 200 once it can serve
            try:
                r = remote.run(f"curl -sf {API}/health", timeout=15, check=False)
                if r.returncode == 0:
                    break
                last_err = r.stderr.strip()
            except RemoteError as e:
                last_err = str(e)
            if time.monotonic() >= deadline:
                raise RuntimeStartError(
                    f"llama-server did not become ready within {READY_TIMEOUT_S}s ({last_err})\n"
                    f"{self._journal(remote)}")
            time.sleep(2)
        body = json.dumps({"prompt": "hi", "n_predict": 1})
        try:
            remote.run(f"curl -sf --max-time 600 -X POST -d {shlex.quote(body)} {API}/completion",
                       timeout=620)
        except (subprocess.CalledProcessError, RemoteError) as e:
            detail = getattr(e, "stderr", None) or str(e)
            raise RuntimeStartError(
                f"warm-up of {self.model} failed: {detail}\n{self._journal(remote)}") from e

    def stop(self, remote: Remote) -> None:
        remote.run(f"{SYSTEMCTL} stop {UNIT_NAME}", check=False)

    def versions(self, remote: Remote) -> dict[str, str]:
        libdir = self.cfg.server.rsplit("/", 1)[0]
        out = remote.run(f"LD_LIBRARY_PATH={shlex.quote(libdir)} {shlex.quote(self.cfg.server)} "
                         f"--version 2>&1", timeout=30, check=False).stdout
        m = re.search(r"^version: (.+)$", out, re.M)
        build = m.group(1).strip() if m else (out.strip().splitlines() or ["unknown"])[0]
        name = self.cfg.gguf.rsplit("/", 1)[-1]
        if name.startswith("sha256-"):
            digest = name.removeprefix("sha256-")
        else:
            digest = remote.run(f"sha256sum {shlex.quote(self.cfg.gguf)}", timeout=600).stdout.split()[0]
        return {"runtime": f"llama.cpp {build} {libdir.rsplit('/', 1)[-1]}", "model_digest": digest}

    def loaded_models(self, remote: Remote) -> list[str]:
        return [m["id"] for m in self._get(remote, "/v1/models").get("data", [])]

    def gpu_offload(self, remote: Remote) -> float | None:
        return gpu_share(self._invocation_log(remote))
