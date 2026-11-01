from __future__ import annotations

from dataclasses import dataclass

from harness.config import HostExpect
from harness.remote import Remote

HOST_TOLERANCE_GIB = 0.25

_DRM = "/sys/class/drm/card0/device"
# Lines out: VRAM bytes, GTT bytes, MemTotal, SwapTotal, TTM pages_limit (absent if the file is).
_READ_CMD = (f"cat {_DRM}/mem_info_vram_total {_DRM}/mem_info_gtt_total; "
             "grep -E '^(MemTotal|SwapTotal):' /proc/meminfo; "
             "cat /sys/module/ttm/parameters/pages_limit 2>/dev/null || true")


class HostMismatchError(Exception):
    pass


class HostReadError(Exception):
    """The host's memory layout could not be read or parsed."""


@dataclass(frozen=True)
class HostMemory:
    vram_mib: int
    gtt_mib: int
    mem_total_mib: int
    swap_total_mib: int
    ttm_pages_limit: int | None


def read_host_memory(remote: Remote) -> HostMemory:
    lines = remote.run(_READ_CMD).stdout.splitlines()
    try:
        vram, gtt = int(lines[0]), int(lines[1])
        mem_kb, swap_kb = (int(line.split()[1]) for line in lines[2:4])
        pages = int(lines[4]) if len(lines) > 4 and lines[4].strip() else None
    except (IndexError, ValueError):
        raise HostReadError(f"cannot parse host memory layout: {lines!r}") from None
    return HostMemory(vram_mib=vram // 2**20, gtt_mib=gtt // 2**20,
                      mem_total_mib=mem_kb // 1024, swap_total_mib=swap_kb // 1024,
                      ttm_pages_limit=pages)


def check_host(expected: HostExpect | None, actual: HostMemory) -> None:
    """Raise HostMismatchError if VRAM or GTT is not the size the config expects."""
    if expected is None:
        return
    for name, want_gib, got_mib in (("vram", expected.vram_gib, actual.vram_mib),
                                    ("gtt", expected.gtt_gib, actual.gtt_mib)):
        if abs(got_mib / 1024 - want_gib) > HOST_TOLERANCE_GIB:
            raise HostMismatchError(
                f"host {name} is {got_mib / 1024:.1f} GiB, config expects {want_gib:g} GiB "
                f"(tolerance {HOST_TOLERANCE_GIB} GiB)")


def host_versions(h: HostMemory) -> dict[str, str]:
    return {
        "host_vram_mib": str(h.vram_mib),
        "host_gtt_mib": str(h.gtt_mib),
        "host_mem_total_mib": str(h.mem_total_mib),
        "host_ttm_pages_limit": "" if h.ttm_pages_limit is None else str(h.ttm_pages_limit),
    }
