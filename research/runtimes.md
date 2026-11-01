# Runtimes for the Radeon 890M (gfx1150) on Linux

Research for E2. The target is a Radeon 890M iGPU (16 CU, RDNA 3.5, GC 11.5.0 = gfx1150) with
about 90 GB/s of DDR5-5600 bandwidth, on Ubuntu 24.04.5 and kernel 7.0.

## What geekoma9 runs today (measured, 2026-10-31)

- **Ollama 0.34.4** bundles its own `llama-server` (llama.cpp `0.4.1-dev`, commit `161755f29`) with
  ROCm 7.2 (`rocm_v7_2`, with gfx1150 rocBLAS kernels), Vulkan, and CPU backends.
- Under `OLLAMA_IGPU_ENABLE=1` it picks **ROCm**: `library=ROCm compute=gfx1150 … total="24.0 GiB"`.
  All layers are offloaded (`offloaded 66/66 layers to GPU`) and `flash_attn = auto`.
  Before the iGPU flag was set, Vulkan was detected (`AMD Radeon 890M (RADV GFX1150)`) and then dropped.
- The speeds below were parsed from the Ollama journal (`slot print_timing`) for September 24–27
  usage. They come from real traffic, so load, context and concurrency were not controlled.
  Read them as indicative only.

| Model (arch) | TG tok/s (median) | PP tok/s at <2k prompt | PP at 2–8k | PP at 8–24k | PP at 24–70k |
|---|---|---|---|---|---|
| qwen3-coder:30b (qwen3moe, 3.3B active) | 13.2 | 153 | 567 | 193 | 279 (38.9k) |
| gemma4:26b-a4b (gemma4) | 22.0 | 176 | 434 | 452 | 327 (up to 58.9k) |
| gpt-oss:20b | 20.2 | 265 | 740 | – | – |
| laguna-xs-2.1 | 26.8 | 96 | 529 | – | – |
| north-mini-code-1.0 (cohere2moe) | 27.1 | 264 | 570 | – | – |
| qwen3.8:27b (dense) | 4.5 | 72 | 101 | 116 | 91 |
| muse-glimmer:30b (dense) | 5.1 | 127 | 147 | – | – |

This confirms the spec's premise: dense 27B runs at about 4–5 tok/s, against 13–27 tok/s for
3–4B-active MoE. Prompt processing is the bottleneck for agents. A 30k-token agent prefix at
about 250 tok/s costs about 2 minutes on every cache miss, so prefix caching matters as much as
TG.

## Candidates

### 1. Ollama (current, ROCm 7.2 backend)
- Pros: already installed and tuned, handles multiple models and loading on demand, and speaks
  the OpenAI, Anthropic Messages (v0.14+) and native APIs. Since it now runs `llama-server` internally, slot
  prompt caching applies.
- Cons: the llama.cpp build lags upstream. The memory sizer counts only the carve-out (24.0 GiB), so it
  may not use GTT with a small UMA (see `memory.md`). Tool-call parsing has been the weak point for
  several models (Gemma 4 and qwen3-coder XML reports, see `models.md`). The latest release is
  **v0.40.13 (2026-10-28)**. An upgrade is an option in its own right, but it is not part of E2's "same model file" comparison.
- gfx1150: works with ROCm 7.2 (verified on geekoma9). In January 2026 (Ollama 0.13–0.14), Strix Point
  users needed `HSA_OVERRIDE_GFX_VERSION` workarounds, and Vulkan was faster than ROCm.

### 2. llama.cpp `llama-server`, Vulkan (RADV), upstream build
- Current release **b12020 (2026-10-31)** ships `llama-b12020-bin-ubuntu-vulkan-x64.tar.gz`,
  a prebuilt that needs only the Mesa RADV already installed (`mesa-vulkan-drivers 25.2.8`).
- Performance: a Strix Point HX 370 / 890M user (NixOS, January 2026) measured Qwen3-Coder-30B-A3B at
  **31.5 tok/s with Vulkan against 28–28.7 tok/s with ROCm**, and found that "Vulkan was consistently fastest" on that
  iGPU. Across AMD hardware the pattern is that Vulkan wins TG and ROCm often wins PP and TTFT
  (llama.cpp discussion #10879; Phoronix, October 2026: Vulkan "consistently better" overall, while ROCm had
  "consistently lower" time to first token).
- GTT: RADV can allocate GTT-backed memory, so this is the first runtime to try in the minimal-UMA plus large-GTT
  variant. If performance drops, use `RADV_PERFTEST=nogttspill`.
- Prefix caching: `cache_prompt` slot reuse is on by default. `--cache-ram N` (MiB) keeps extra
  prompt-cache slots in host RAM. The default is reportedly 8192 MiB, which is **more than Linux
  has at 24 GiB UMA**, so set `--cache-ram 0` or a small value there. `--cache-reuse N` enables
  KV shifting for chunk reuse. One known issue: erasing slots does not clear the RAM cache (discussion #30746),
  so restart the server between benchmark runs.
- APIs: OpenAI-compatible `/v1/chat/completions`, and the Anthropic Messages API `/v1/messages`
  since January 2026 (Hugging Face blog). Use `--jinja` for model tool templates.

### 3. llama.cpp `llama-server`, ROCm/HIP (lemonade-sdk `llamacpp-rocm`, gfx1150 build)
- The upstream `ubuntu-rocm-10.0-x64` prebuilt does not state its gfx targets. lemonade-sdk publishes
  per-target builds with ROCm bundled: **b1359 (2026-10-30)**,
  `llama-b1359-ubuntu-rocm-gfx1150-x64.zip`, built on ROCm 10.3.0a20261030 and llama.cpp `aa588a3`,
  with a per-archive qualification record.
- Pros: same build age as upstream, so it isolates "ROCm vs Vulkan" from "Ollama vs llama.cpp".
  ROCm's PP advantage matters for long agent prefixes.
- Cons: for gfx1150 the README says OOM despite free VRAM needs `ttm.pages_limit=12582912`.
  Lemonade's FAQ says ROCm cannot split memory across pools. In January 2026 a Strix Point user hit
  `ROCm error: invalid device function` on an older llama.cpp ROCm build.
- Upstream PR #27083 (2026-08-17) fixed HIP builds that under-reported memory on APUs. The
  lemonade build is newer than that fix.

### Considered and not shortlisted
- **NPU / hybrid (Ryzen AI SW, FastFlowLM):** NPU+iGPU hybrid is Windows-only. On Linux, NPU-only
  inference runs through FastFlowLM, which supports the XDNA2 NPU on Gorgon Point, but its model catalogue
  and speed do not cover 30B-class coding MoE. It is not credible for this workload. (Lemonade FAQ.)
- **vLLM ROCm:** Lemonade lists `vllm:rocm` as experimental and gfx1151-only. gfx1150 is not listed.

## Shortlist

`ollama` (baseline), `llamacpp-vulkan`, `llamacpp-rocm`. E2 should load the same GGUF in all three
and measure PP at 4k, 32k and 64k, TG, and the prefix-cache hit time for a repeated agent prefix.

## Sources

- geekoma9 `journalctl -u ollama` and `/usr/local/lib/ollama` listing (2026-10-31).
- https://discourse.nixos.org/t/how-to-llama-on-amd-strix-halo/74363
- https://github.com/ggml-org/llama.cpp/discussions/10879
- https://github.com/ggml-org/llama.cpp/discussions/15021
- https://www.phoronix.com/review/lemonade-vulkan-rocm/2
- https://github.com/lemonade-sdk/llamacpp-rocm
- https://github.com/lemonade-sdk/llamacpp-rocm/releases/tag/b1359
- https://github.com/ggml-org/llama.cpp/releases/tag/b12020
- https://github.com/ggml-org/llama.cpp/issues/18159
- https://github.com/ggml-org/llama.cpp/discussions/30746
- https://github.com/ggml-org/llama.cpp/discussions/13606
- https://huggingface.co/blog/ggml-org/anthropic-messages-api-in-llamacpp
- https://docs.ollama.com/api/anthropic-compatibility
- https://github.com/ollama/ollama/releases/tag/v0.40.13
- https://lemonade-server.ai/docs/guide/faq/
