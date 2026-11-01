from __future__ import annotations

import pytest

from harness.config import HostExpect
from harness.host import HostMemory, HostMismatchError, HostReadError, check_host, host_versions, read_host_memory

VRAM, GTT = "25769803776", "3970646016"


def host_remote(fake_remote, pages_limit="969396"):
    out = f"{VRAM}\n{GTT}\nMemTotal:        7755172 kB\nSwapTotal:       8388604 kB\n{pages_limit}\n"
    fake_remote.reply("mem_info_vram_total", stdout=out)
    return fake_remote


def mem(**over):
    return HostMemory(**{**dict(vram_mib=24576, gtt_mib=3786, mem_total_mib=7573,
                                swap_total_mib=8191, ttm_pages_limit=969396), **over})


def test_read_host_memory_parses(fake_remote):
    assert read_host_memory(host_remote(fake_remote)) == HostMemory(24576, 3786, 7573, 8191, 969396)


def test_read_host_memory_missing_ttm(fake_remote):
    assert read_host_memory(host_remote(fake_remote, pages_limit="")).ttm_pages_limit is None


def test_check_host_within_tolerance():
    check_host(HostExpect(24, 3.7), mem())


def test_check_host_mismatch_names_both():
    with pytest.raises(HostMismatchError) as e:
        check_host(HostExpect(16, 7.7), mem())
    assert "vram" in str(e.value) and "16" in str(e.value) and "24.0" in str(e.value)


def test_check_host_none_expectation():
    check_host(None, mem())


def test_host_versions_keys():
    assert host_versions(mem()) == {"host_vram_mib": "24576", "host_gtt_mib": "3786",
                                    "host_mem_total_mib": "7573", "host_ttm_pages_limit": "969396"}
    assert host_versions(mem(ttm_pages_limit=None))["host_ttm_pages_limit"] == ""


def test_read_host_memory_tolerates_missing_ttm_file(fake_remote):
    # the fake ignores exit codes: pin the shell guard that keeps a missing file from failing the run
    fake_remote.reply("mem_info_vram_total",
                      stdout=f"{VRAM}\n{GTT}\nMemTotal: 7755172 kB\nSwapTotal: 8388604 kB\n")
    assert read_host_memory(fake_remote).ttm_pages_limit is None
    assert "pages_limit 2>/dev/null || true" in fake_remote.calls[0]


def test_read_host_memory_unparsable(fake_remote):
    fake_remote.reply("mem_info_vram_total", stdout="")
    with pytest.raises(HostReadError):
        read_host_memory(fake_remote)


def test_check_host_gtt_only_mismatch():
    with pytest.raises(HostMismatchError, match="gtt"):
        check_host(HostExpect(24, 7.7), mem())
