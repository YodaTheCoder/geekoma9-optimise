import json
import subprocess

import pytest

from harness.config import ConfigError, RuntimeConfig
from harness.runtimes import make_runtime
from harness.runtimes.ollama import OllamaRuntime, render_unit


def cfg(**env):
    return RuntimeConfig(kind="ollama", model="qwen3:8b", context=65536, env=env)


class FakeRemote:
    def __init__(self, responses=None):
        self.cmds = []
        self.writes = {}
        self.responses = responses or []  # (substring, stdout)

    def run(self, cmd, timeout=None, check=True):
        self.cmds.append(cmd)
        out = ""
        for sub, o in self.responses:
            if sub in cmd:
                out = o
                break
        return subprocess.CompletedProcess(cmd, 0, out, "")

    def write_text(self, path, text):
        self.writes[path] = text


def test_render_unit():
    u = render_unit(cfg(ZED="1", ALPHA="2"))
    assert "ExecStart=/usr/local/bin/ollama serve" in u
    assert "Environment=OLLAMA_CONTEXT_LENGTH=65536" in u
    assert "Environment=OLLAMA_HOST=127.0.0.1:11434" in u
    assert "Environment=OLLAMA_KEEP_ALIVE=-1" in u
    assert "Environment=OLLAMA_MAX_LOADED_MODELS=1" in u
    assert "Environment=OLLAMA_MODELS=/usr/share/ollama/.ollama/models" in u
    assert "Restart=no" in u and "WantedBy=default.target" in u
    assert "[Unit]" in u and "Description=" in u
    assert u.index("OLLAMA_MODELS") < u.index("ALPHA=2") < u.index("ZED=1")


@pytest.mark.parametrize("key", ["OLLAMA_HOST", "OLLAMA_CONTEXT_LENGTH", "OLLAMA_KEEP_ALIVE",
                                 "OLLAMA_MAX_LOADED_MODELS", "OLLAMA_MODELS"])
def test_render_unit_rejects_fixed_keys(key):
    with pytest.raises(ConfigError):
        render_unit(cfg(**{key: "x"}))


def test_make_runtime():
    rt = make_runtime(cfg())
    assert isinstance(rt, OllamaRuntime)
    assert rt.model == "qwen3:8b"
    assert rt.upstream == "http://127.0.0.1:11434"


def test_start_sequence():
    r = FakeRemote([("/api/version", '{"version":"0.1"}')])
    OllamaRuntime(cfg()).start(r)
    assert "/home/markn/.config/systemd/user/agentbench-runtime.service" in r.writes
    joined = "\n".join(r.cmds)
    assert joined.index("daemon-reload") < joined.index("restart agentbench-runtime")
    assert joined.index("restart agentbench-runtime") < joined.index("/api/version")
    warm = [c for c in r.cmds if "/api/generate" in c][0]
    assert r.cmds[-1] == warm
    assert '"keep_alive": -1' in warm and "num_predict" in warm and "qwen3:8b" in warm


def test_start_times_out(monkeypatch):
    import harness.runtimes.ollama as mod
    t = iter(range(0, 1000, 20))
    monkeypatch.setattr(mod.time, "monotonic", lambda: next(t))
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    class R(FakeRemote):
        def run(self, cmd, timeout=None, check=True):
            self.cmds.append(cmd)
            rc = 22 if "/api/version" in cmd else 0
            return subprocess.CompletedProcess(cmd, rc, "", "")
    with pytest.raises(RuntimeError):
        OllamaRuntime(cfg()).start(R())


def test_stop():
    r = FakeRemote()
    OllamaRuntime(cfg()).stop(r)
    assert any("stop agentbench-runtime" in c for c in r.cmds)


def test_versions_and_loaded():
    tags = json.dumps({"models": [{"name": "other", "digest": "x"},
                                  {"name": "qwen3:8b", "digest": "abc123"}]})
    ps = json.dumps({"models": [{"name": "qwen3:8b"}]})
    r = FakeRemote([("ollama --version", "ollama version is 0.12.3\n"),
                    ("/api/tags", tags), ("/api/ps", ps)])
    rt = OllamaRuntime(cfg())
    v = rt.versions(r)
    assert v["runtime"].startswith("ollama ") and "0.12.3" in v["runtime"]
    assert v["model_digest"] == "abc123"
    assert rt.loaded_models(r) == ["qwen3:8b"]
