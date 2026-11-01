import pytest
import yaml

from harness.config import ConfigError, HostExpect, load_config

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


def _load(tmp_path, **over):
    data = yaml.safe_load(MINIMAL)
    data.update(over)
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(data))
    return load_config(p)


def test_non_empty_sampling_rejected(tmp_path):
    # nothing applies sampling yet; recording it would misattribute results
    with pytest.raises(ConfigError, match="sampling: not applied by any runtime yet; leave it empty"):
        _load(tmp_path, sampling={"temperature": 0.2})
    assert _load(tmp_path, sampling={}).sampling == {}


@pytest.mark.parametrize("bad", ["", "E0", "../x", "a..b", "-x", "a/b", "a b", ".x"])
def test_id_must_be_ref_safe(tmp_path, bad):
    with pytest.raises(ConfigError, match="id"):
        _load(tmp_path, id=bad)


def test_ref_safe_id_accepted(tmp_path):
    assert _load(tmp_path, id="e1-split.16g_x").id == "e1-split.16g_x"


def test_host_section_parsed(tmp_path):
    assert _load(tmp_path, host={"vram_gib": 16, "gtt_gib": 7.7}).host == HostExpect(16.0, 7.7)


def test_host_section_unknown_key(tmp_path):
    with pytest.raises(ConfigError, match="host.vram: unknown key"):
        _load(tmp_path, host={"vram": 16})


def test_host_absent_is_none(tmp_path):
    assert _load(tmp_path).host is None
