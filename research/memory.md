# Memory configuration

Research for E1 (memory split). Measured facts come first. They were collected on 2026-10-31
using read-only commands over `ssh markn@geekoma9.local`.

## Measured on geekoma9 (2026-10-31)

| Item | Value | Command |
|---|---|---|
| Board / BIOS | GEEKOM A9 Max, AMI BIOS `0.02`, dated 03/04/2026 | `cat /sys/class/dmi/id/{board_name,bios_version,bios_date,bios_vendor}` |
| Kernel cmdline | `BOOT_IMAGE=/boot/vmlinuz-7.0.0-34-generic root=UUID=… ro quiet splash vt.handoff=7` (no amdgpu/ttm params) | `cat /proc/cmdline` |
| GPU | PCI `0x150e`, rev `0xe4`, GC IP 11.5.0 (= gfx1150) | `/sys/class/drm/card0/device/{device,revision}`, `ip_discovery/die/0/GC/0` |
| VRAM (UMA carve-out) | 25769803776 B = 24.0 GiB (visible VRAM is the same) | `mem_info_vram_total`, `mem_info_vis_vram_total` |
| GTT | 3970646016 B = 3.70 GiB | `mem_info_gtt_total` |
| TTM limits | `ttm.pages_limit=969396`, `ttm.page_pool_size=969396` (4 KiB pages, so 969396 × 4096 = 3970646016 B, exactly the GTT size; the default is half of Linux-visible RAM) | `/sys/module/ttm/parameters/*` |
| `amdgpu.gttsize`, `amdgpu.vramlimit` | not readable as user (permission denied) | `/sys/module/amdgpu/parameters/*` |
| Linux RAM | MemTotal 7755172 kB (7.4 GiB), about 5.4 GiB available, 8 GiB swap with 259 MiB used | `/proc/meminfo`, `free -h` |
| DIMMs | 2 × 16 GB Micron CT16G56C46S5.M8H1, DDR5-5600 (configured 5600 MT/s), single-rank, channel A and channel B | `sudo -n dmidecode -t memory` |
| Vulkan | `vulkaninfo` is not installed (it was not installed, per ruling). Ollama's discovery log shows RADV sees the GPU: `AMD Radeon 890M (RADV GFX1150)`. The Mesa package is `mesa-vulkan-drivers 25.2.8-0ubuntu0.24.04.2`. | `journalctl -u ollama`, `dpkg -l` |
| ROCm on host | no `/opt/rocm`. Ollama bundles its own ROCm 7.2 (`/usr/local/lib/ollama/rocm_v7_2`, with gfx1150 rocBLAS kernels). `/dev/kfd` is present and `markn` is in `render` and `video`. | `ls` |
| Ollama GPU view | `library=ROCm compute=gfx1150 … type=iGPU total="24.0 GiB" available="23.8 GiB"`, so Ollama's ROCm backend counts only the carve-out, not VRAM+GTT | `journalctl -u ollama` |
| Earlier BIOS state | on 2026-09-24 21:48 Ollama logged CPU `total="27.0 GiB"`, so the BIOS was then at a small carve-out (about 4–5 GiB). It was 7.4 GiB from 22:34 that day. | `journalctl -u ollama` |

Memory budget at 24 GiB UMA (KV sizes come from Ollama's `llama_kv_cache` log lines, f16 KV):

| Model | Weights (GiB, Ollama file) | KV at 32k | KV at 64k | Fits 24 GiB at 64k? |
|---|---|---|---|---|
| qwen3-coder:30b (qwen3moe, full attention) | 17.3 | 3.0 GiB | 6.0 GiB | barely (≈23.5 GiB plus compute buffers); 128k needs q8 KV |
| laguna-xs-2.1 (hybrid/SWA) | 18.9 | 1.4 GiB | ~2.7 GiB (est.) | yes |
| north-mini-code-1.0 (cohere2moe, hybrid) | 17.3 | 1.1 GiB | ~2.2 GiB (est.) | yes |
| gpt-oss:20b (SWA) | 12.8 | 0.8 GiB | ~1.5 GiB (est.) | yes, and also fits a 16 GiB UMA |
| gemma4:26b-a4b (hybrid) | 16.8 | 0.9 GiB | 1.6 GiB | yes |

Linux has only 7.4 GiB today and already swaps lightly. The agent harness (Node or Python), git, and
headless Godot for scoring all run there. This is the main argument for a smaller carve-out.

## BIOS UMA options

- Verified: the A9 Max BIOS accepts a **24 GiB** carve-out (the current setting) and a small
  carve-out of about 4–5 GiB (the September 24 state above). The full option list is not
  published by GEEKOM, and no owner screenshot was found. Notebookcheck's review lists "limited
  BIOS options" as a drawback.
- AMD's general guidance is that the setting is normally "Auto", and that 1–2 GB is suggested
  for systems with 8 GB of RAM or more. Other Ryzen mini-PC BIOSes (Bee-Link SER8, an 8700G
  board) top out at 16 GB. GEEKOM evidently allows more.
- On RDNA iGPUs, LLM runtimes can use **GTT** (system RAM mapped for the GPU) instead of the
  carve-out. The Framework community reports that "LLMs don't use any VRAM, they use GTT"
  on FW13/FW16 AMD (Strix Point class).

## GTT kernel parameters

- `amdgpu.gttsize` is **deprecated**. The kernel warns and points to TTM. Use
  `ttm.pages_limit=<pages>` together with `ttm.page_pool_size=<pages>`, in 4 KiB pages:
  pages = GiB × 262144. For example, 24 GiB = `6291456`, 20 GiB = `5242880` and 28 GiB = `7340032`.
  On the in-kernel driver the prefix is `ttm.`. The `amdttm.` prefix in Jeff Geerling's guide
  is for AMD's out-of-tree DKMS driver.
- Some users report that setting these through `modprobe.d` did not take effect, while the
  kernel command line did. Set them in `GRUB_CMDLINE_LINUX_DEFAULT`, then `update-grub` and reboot.
- Verify with `cat /sys/class/drm/card0/device/mem_info_gtt_total` and
  `cat /sys/module/ttm/parameters/pages_limit`.
- One risk on the 32 GB box: GTT pages are ordinary RAM, so a 24 GiB GTT plus ~7 GiB for the OS
  leaves no slack. Keep GTT at or below about 24 GiB and keep swap.

## Which runtimes honour GTT

| Runtime | Uses GTT beyond the carve-out? | Evidence |
|---|---|---|
| llama.cpp Vulkan (RADV) | **Yes, most likely.** RADV exposes GTT-backed memory, and Strix Halo users see Vulkan reporting more memory than ROCm after raising TTM. Set `RADV_PERFTEST=nogttspill` if performance drops. | Level1Techs Strix Halo thread; llama.cpp Vulkan discussion #10879 |
| llama.cpp ROCm/HIP (lemonade `llamacpp-rocm` gfx1150 build) | **Probably yes, once TTM is raised.** For gfx1150 the lemonade README says OOM "despite free VRAM" is fixed by `ttm.pages_limit=12582912`. Lemonade's FAQ warns that ROCm "does not support splitting memory across multiple pools". | lemonade-sdk/llamacpp-rocm README; Lemonade FAQ |
| llama.cpp HIP UMA detection | Upstream PR #27083 (merged 2026-08-17) skips the "UMA = MemAvailable" override for HIP builds. Older builds under-report free memory on APUs (issue #18159). | llama.cpp #18159 |
| Ollama 0.34.4 (ROCm 7.2 backend) | **Unknown.** It reports `total=24.0 GiB`, the carve-out only. In January 2026, a Strix Point user with a 512 MiB carve-out got "insufficient VRAM" on Ollama 0.13.5 and full offload on 0.14.1. It is not known how 0.34.4 sizes memory at a small carve-out. | NixOS Discourse thread; geekoma9 journal |

## Variants to test in E1

1. `uma24` — 24 GiB UMA, default GTT (current; E0 baseline).
2. `uma16` — 16 GiB UMA, default GTT (about 7.7 GiB). Linux sees about 15 GiB. Only models up to
   about 13 GB fit with context (gpt-oss:20b), unless the runtime also spills to GTT.
3. `umamin_gtt24` — smallest UMA the BIOS offers (target 512 MiB–2 GiB) plus
   `ttm.pages_limit=6291456 ttm.page_pool_size=6291456` (24 GiB GTT). Linux sees about 30 GiB. This
   needs a runtime that allocates from GTT (llama.cpp Vulkan first).

## To verify by owner

- The exact list of UMA Frame Buffer sizes in the A9 Max BIOS (0.02) and the menu path. Read it on
  screen, and say whether "Auto", 512M, 1G, 2G, 4G, 8G, 16G or 24G are offered.
- `amdgpu.gttsize` / `amdgpu.vramlimit` current values (need root): `sudo cat /sys/module/amdgpu/parameters/gttsize`.
- `vulkaninfo --summary` (needs `vulkan-tools`, which was not installed). Check the memory heaps
  RADV reports at each UMA setting.
- `sudo dmesg | grep -i "amdgpu.*memory"` after each BIOS or kernel-parameter change. `dmesg` is not readable as user.
- Whether Ollama 0.34.4 offloads fully with a minimal carve-out plus a large GTT. Check this in E1.
- Whether GEEKOM ships a newer BIOS than 0.02 (dated 03/04/2026).

## Sources

- geekoma9 measurements above (2026-10-31, read-only).
- https://www.jeffgeerling.com/blog/2025/increasing-vram-allocation-on-amd-ai-apus-under-linux/
- https://community.frame.work/t/igpu-vram-how-much-can-be-assigned/73081
- https://community.frame.work/t/bios-feature-request-add-ability-to-specify-uma-size-on-amd-apus/41930/67
- https://forum.level1techs.com/t/rocm-can-only-use-half-of-the-unified-memory-on-my-strix-halo/253152
- https://github.com/ggml-org/llama.cpp/issues/18159
- https://github.com/ggml-org/llama.cpp/discussions/10879
- https://github.com/lemonade-sdk/llamacpp-rocm
- https://lemonade-server.ai/docs/guide/faq/
- https://discourse.nixos.org/t/how-to-llama-on-amd-strix-halo/74363
- https://www.amd.com/en/resources/support-articles/faqs/PA-280.html
- https://www.notebookcheck.net/Best-Geekom-mini-PC-ever-Geekom-A9-Max-review-with-AMD-Ryzen-AI-9-HX-370-for-999.1111882.0.html
- https://bbs.bee-link.com/d/4713-ser8-8845
