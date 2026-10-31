from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class UsageSummary:
    requests: int
    prompt_tokens: int | None
    gen_tokens: int | None
    pp_tps: float | None
    tg_tps: float | None
    upstream_errors: int


def summarize_usage(jsonl_text: str) -> UsageSummary:
    """Aggregate usage.jsonl lines written by remote_scripts/usage_proxy.py."""
    requests = errors = 0
    prompt = gen = 0
    prompt_n = gen_n = 0
    pp_time = tg_time = 0.0
    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # partial tail from a killed proxy
        requests += 1
        if row.get("upstream_error"):
            errors += 1
        ttft = row.get("ttft_s")
        duration = row.get("duration_s")
        p, g = row.get("prompt_tokens"), row.get("gen_tokens")
        if p is not None:
            prompt += p
            prompt_n += 1
            pp_time += ttft or 0.0
        if g is not None:
            gen += g
            gen_n += 1
            tg_time += max((duration or 0.0) - (ttft or 0.0), 0.0)
    return UsageSummary(
        requests=requests,
        prompt_tokens=prompt if prompt_n else None,
        gen_tokens=gen if gen_n else None,
        pp_tps=prompt / pp_time if prompt_n and pp_time > 0 else None,
        tg_tps=gen / tg_time if gen_n and tg_time > 0 else None,
        upstream_errors=errors,
    )
