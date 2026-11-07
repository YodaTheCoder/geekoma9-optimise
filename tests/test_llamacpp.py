import json
import subprocess

import pytest

from harness.config import ConfigError, RuntimeConfig, load_config
from harness.runtimes import make_runtime
from harness.runtimes.base import RuntimeStartError
from harness.runtimes.llamacpp import LlamaCppRuntime, gpu_share, render_unit

SERVER = "/srv/agentbench/opt/llama/vulkan-b1/llama-server"
GGUF = "/usr/share/ollama/.ollama/models/blobs/sha256-abc123"


def cfg(args=(), **env):
    return RuntimeConfig(kind="llamacpp", model="qwen3-coder:30b", context=32768, env=env,
                         server=SERVER, gguf=GGUF, args=tuple(args))


class FakeRemote:
    def __init__(self, responses=None, rc=None):
        self.cmds = []
        self.writes = {}
        self.responses = responses or []  # (substring, stdout)
        self.rc = rc or {}  # substring -> returncode

    def run(self, cmd, timeout=None, check=True):
        self.cmds.append(cmd)
        out = ""
        for sub, o in self.responses:
            if sub in cmd:
                out = o
                break
        rc = next((v for k, v in self.rc.items() if k in cmd), 0)
        return subprocess.CompletedProcess(cmd, rc, out, "")

    def write_text(self, path, text):
        self.writes[path] = text


def test_render_unit():
    u = render_unit(cfg(args=["--temp", "0.7"], LLAMA_ARG_CACHE_RAM="1024"))
    exec_line = next(l for l in u.splitlines() if l.startswith("ExecStart="))
    assert exec_line.startswith(f"ExecStart={SERVER} ")
    for part in (f"-m {GGUF}", "--alias qwen3-coder:30b", "--host 127.0.0.1", "--port 11434",
                 "-c 32768", "-np 1", "-ngl 999", "--jinja", "--no-webui", "--log-verbosity 4",
                 "--temp 0.7"):
        assert part in exec_line
    assert exec_line.endswith("--temp 0.7")  # config args come last and can override defaults
    assert "Environment=LD_LIBRARY_PATH=/srv/agentbench/opt/llama/vulkan-b1" in u
    assert "Environment=LLAMA_ARG_CACHE_RAM=1024" in u
    assert "Restart=no" in u and "WantedBy=default.target" in u


def test_render_unit_quotes_args_with_spaces():
    u = render_unit(cfg(args=["--chat-template-kwargs", '{"a": 1}']))
    assert "\"{\\\"a\\\": 1}\"" in u  # systemd double-quoted, inner quotes escaped


def test_render_unit_rejects_fixed_env():
    with pytest.raises(ConfigError):
        render_unit(cfg(LD_LIBRARY_PATH="/x"))


def test_make_runtime():
    rt = make_runtime(cfg())
    assert isinstance(rt, LlamaCppRuntime)
    assert rt.model == "qwen3-coder:30b" and rt.upstream == "http://127.0.0.1:11434"


def test_start_waits_for_health_then_warms_up():
    r = FakeRemote()
    LlamaCppRuntime(cfg()).start(r)
    assert "/home/markn/.config/systemd/user/agentbench-runtime.service" in r.writes
    joined = "\n".join(r.cmds)
    assert joined.index("daemon-reload") < joined.index("restart agentbench-runtime")
    assert joined.index("restart agentbench-runtime") < joined.index("/health")
    warm = r.cmds[-1]
    assert "/completion" in warm and '"n_predict": 1' in warm


def test_start_times_out(monkeypatch):
    import harness.runtimes.llamacpp as mod
    t = iter(range(0, 10000, 30))
    monkeypatch.setattr(mod.time, "monotonic", lambda: next(t))
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeStartError):
        LlamaCppRuntime(cfg()).start(FakeRemote(rc={"/health": 22}))


def test_versions_uses_blob_digest():
    r = FakeRemote([("--version", "load_backend: x\nversion: 0.9.0-dev (build 12191, commit e95426f16)\nbuilt with clang\n")])
    v = LlamaCppRuntime(cfg()).versions(r)
    assert v == {"runtime": "llama.cpp 0.9.0-dev (build 12191, commit e95426f16) vulkan-b1", "model_digest": "abc123"}


def test_versions_hashes_other_files():
    c = RuntimeConfig(kind="llamacpp", model="m", context=1, server=SERVER, gguf="/m/x.gguf")
    r = FakeRemote([("sha256sum", "deadbeef  /m/x.gguf\n"), ("--version", "version: 1 (a)\n")])
    assert LlamaCppRuntime(c).versions(r)["model_digest"] == "deadbeef"


def test_loaded_models():
    r = FakeRemote([("/v1/models", json.dumps({"data": [{"id": "qwen3-coder:30b"}]}))])
    assert LlamaCppRuntime(cfg()).loaded_models(r) == ["qwen3-coder:30b"]


JOURNAL = """load_tensors: offloading 48 repeating layers to GPU
load_tensors:      Vulkan0 model buffer size = 17000.00 MiB
load_tensors:   CPU_Mapped model buffer size =   300.00 MiB
"""


def test_gpu_share():
    assert gpu_share(JOURNAL) == round(17000 / 17300, 3)
    assert gpu_share("ROCm0 model buffer size = 10.00 MiB\n") == 1.0
    assert gpu_share("nothing here") is None


def test_gpu_offload_reads_current_invocation():
    r = FakeRemote([("InvocationID", "inv1\n"), ("journalctl", JOURNAL)])
    assert LlamaCppRuntime(cfg()).gpu_offload(r) == round(17000 / 17300, 3)
    assert any("_SYSTEMD_INVOCATION_ID=inv1" in c for c in r.cmds)


def test_config_llamacpp(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("""id: x
task_set: v1
tier: probe
runtime: {kind: llamacpp, model: "q:1", context: 32768, server: /s/llama-server, gguf: /g,
          args: ["--temp", "0.7"]}
agent: {kind: command, name: opencode, command: "run {issue_file}"}
""")
    c = load_config(p).runtime
    assert (c.kind, c.server, c.gguf, c.args) == ("llamacpp", "/s/llama-server", "/g", ("--temp", "0.7"))


@pytest.mark.parametrize("runtime", [
    "{kind: llamacpp, model: m, context: 1, gguf: /g}",
    "{kind: llamacpp, model: m, context: 1, server: /s, gguf: /g, args: [1]}",
    "{kind: ollama, model: m, context: 1, server: /s}",
])
def test_config_llamacpp_errors(tmp_path, runtime):
    p = tmp_path / "c.yaml"
    p.write_text(f"id: x\ntask_set: v1\ntier: probe\nruntime: {runtime}\nagent: {{kind: command, name: opencode, command: \"run {{issue_file}}\"}}\n")
    with pytest.raises(ConfigError):
        load_config(p)
