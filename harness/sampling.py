from __future__ import annotations

import csv
import io
from dataclasses import dataclass

THROTTLE_TCTL_C = 95.0


@dataclass(frozen=True)
class SampleSummary:
    peak_mem_mib: int | None
    peak_gpu_mem_mib: int | None
    max_tctl_c: float | None
    throttled: bool
    peak_swap_mib: int | None = None


def _num(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


def summarize_samples(csv_text: str) -> SampleSummary:
    """Peak memory / GPU memory (vram + gtt) and max Tctl over sample.sh output."""
    mem: list[float] = []
    gpu: list[float] = []
    tctl: list[float] = []
    swap: list[float] = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        m = _num(row.get("mem_used_mib"))
        if m is not None:
            mem.append(m)
        vram = _num(row.get("vram_used_mib"))
        gtt = _num(row.get("gtt_used_mib"))
        if vram is not None or gtt is not None:
            gpu.append((vram or 0.0) + (gtt or 0.0))
        sw = _num(row.get("swap_used_mib"))
        if sw is not None:
            swap.append(sw)
        t = _num(row.get("tctl_c"))
        if t is not None:
            tctl.append(t)
    max_tctl = max(tctl) if tctl else None
    return SampleSummary(
        peak_mem_mib=int(max(mem)) if mem else None,
        peak_gpu_mem_mib=int(max(gpu)) if gpu else None,
        max_tctl_c=max_tctl,
        throttled=max_tctl is not None and max_tctl >= THROTTLE_TCTL_C,
        peak_swap_mib=int(max(swap)) if swap else None,
    )
