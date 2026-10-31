import pytest
import yaml

from harness.config import ConfigError, load_config

MINIMAL = """id: e0-baseline
task_set: v1
tier: screening
runtime: {kind: ollama, model: "qwen3-coder:30b", context: 65536}
agent: {kind: command, name: opencode, command: "run {issue_file}"}
"""


def test_loads_minimal_config(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(MINIMAL)
    cfg = load_config(p)
    assert cfg.timeout_s == 2700 and cfg.cooldown_s == 120
    assert cfg.runtime.context == 65536 and cfg.agent.name == "opencode"


@pytest.mark.parametrize("bad", [
    "tier: nightly",
    "runtime: {kind: vllm, model: m, context: 1}",
    "agent: {kind: command, name: x}",  # command agent without command
])
def test_rejects_invalid(tmp_path, bad):
    data = yaml.safe_load(MINIMAL)
    data.update(yaml.safe_load(bad))
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(data))
    with pytest.raises(ConfigError):
        load_config(p)
