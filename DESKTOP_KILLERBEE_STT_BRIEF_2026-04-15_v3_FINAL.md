# Desktop KillerBee STT + Tooling Brief — 2026-04-15 v3 FINAL

**From:** Laptop Claude
**To:** Desktop Claude
**Status:** SUPERSEDES v2 (`DESKTOP_KILLERBEE_STT_AND_TOOLING_BRIEF_2026-04-15_v2.md`). This v3 captures the simplified ladder and sequential-provisioning decision that Nir approved after reviewing Desktop's verification log `b87b8d0`. Read v2 for the full context — this v3 only records what changed from v2.

---

## Context — why v3 exists

After Desktop pushed his verification log (`KillerBee/PHASE3_STT_VERIFICATION_LOG_2026-04-15_v2.md`, commit `b87b8d0`), two real risks surfaced:

1. **Parakeet TDT 0.6B v3 and 1.1B have NO ONNX artifacts published on their HF model cards.** The v2 brief assumed ONNX Runtime CPU. Runtime options were NeMo CPU (heavy, unproven) or export-ONNX-ourselves (engineering risk) or drop Parakeet.
2. **qwen3-asr.cpp has only 7 commits, no releases, and is Metal-first.** The v2 brief named it as the primary CPU runtime for Qwen3-ASR. Too young and too unproven to bet the experiment on.

Nir reviewed the two risks and chose **option C for both — drop the problematic thing entirely.** Parakeet is out. Qwen3-ASR is out. No NeMo install, no qwen3-asr.cpp build, no ONNX export dance.

---

## The simplified final ladder (ONLY three model families)

| Bracket | GOLD | SILVER | Params | License | Runtime |
|---|---|---|---|---|---|
| **tiny (worker)** | **Moonshine Tiny** | Whisper tiny | 27M / 39M | MIT / MIT | `moonshine-onnx` / `whisper.cpp` |
| **small** | **Moonshine Base** | Whisper base | 61M / 74M | MIT / MIT | `moonshine-onnx` / `whisper.cpp` |
| **medium-small (DwarfQueen)** | **Whisper small** | Whisper base | 244M | MIT | `whisper.cpp` |
| **medium** | **Whisper medium** | Whisper small | 769M | MIT | `whisper.cpp` |
| **medium-big (GiantQueen)** | **Whisper Large v3 Turbo** | Whisper medium | 809M | MIT | `whisper.cpp` |
| **big (RajaBee STT — reasoner stays separate and unchanged)** | **Cohere Transcribe 03-2026** | Whisper Large v3 (non-turbo, 1.55B) | 2B / 1.55B | Apache 2.0 / MIT | HF Transformers CPU / `whisper.cpp` |

**Three families, two-and-a-half runtimes:**
- **Moonshine** (Tiny and Base) on `moonshine-onnx` for worker tiers
- **Whisper family** (tiny / base / small / medium / large-v3-turbo / large-v3) on `whisper.cpp` for everything from DwarfQueen through GiantQueen, and also as the universal silver fallback at every bracket
- **Cohere Transcribe 03-2026** on HF Transformers CPU **only** at the RajaBee tier

**Everything dropped from v2:**
- Parakeet TDT 0.6B v3 — DROPPED (no ONNX artifacts, NeMo CPU too heavy/unproven)
- Parakeet TDT 1.1B — DROPPED (same reason)
- Qwen3-ASR 0.6B — DROPPED (qwen3-asr.cpp too young, HF Transformers alternative is slower and Nir prefers simpler ladder)
- Qwen3-ASR 1.7B — DROPPED (same reason)
- Canary Qwen 2.5B SALM — was already dropped in v2 (SALM fusion would cap RajaBee reasoner at 1.7B)
- `nemo_toolkit['all']` install — DROPPED (was only needed for Parakeet)
- `qwen3-asr.cpp` build step — DROPPED (no longer needed)
- `onnxruntime` Python package — **KEPT** (still needed as a dependency of `moonshine-onnx`)
- HF Transformers + torch CPU — **KEPT** (still needed for Cohere Transcribe at the RajaBee)

---

## Provisioning strategy — SEQUENTIAL one-by-one, NOT parallelized

Nir explicitly chose **sequential one-by-one provisioning** over parallelized provisioning. His reasoning, verbatim: *"i want them please totally one by one, not parallelized, so he has all his brain free to fix things please. if like 7 machines tell him of problems at the same time, he needs to prioritize and he is in rush."*

**Concrete implication for Desktop:**
- Provision VM 1 completely. End to end. Apt, pip, builds, model download, integration test, working STT pass on a real audio file. Only when VM 1 is fully green, move to VM 2.
- Fix any bug you find on VM 1 IMMEDIATELY and update `PHASE3_PROVISION_VM.sh` in place so the next VM picks up the fix. The script is the source of truth; bug fixes land there, not in ad-hoc edits to VM 1.
- Do NOT run provisioning on multiple VMs concurrently even though the i9-13900KF has 24 cores and could easily handle it. The reason is human debuggability under time pressure, not machine capacity.
- Expected wall-clock time per VM: ~10-15 minutes including download + build + model weight fetch. Across 8 VMs sequentially: **~80-120 minutes**. This is the honest budget.
- If VM 1 takes significantly longer than 15 minutes, stop and debug the script before moving on — do not paper over a slow provision by running more in parallel.

---

## What Desktop should do with the three v2 deliverables

The three files Desktop pushed in commit `b87b8d0` (PHASE3_STT_AND_TOOLING_2026-04-15_v2.md, PHASE3_STT_VERIFICATION_LOG_2026-04-15_v2.md, PHASE3_PROVISION_VM.sh) contain real verification work that is still valuable. Do NOT delete them. Instead:

1. **Prepend a SUPERSEDED banner** to the top of each v2 file pointing at the matching v3 file.
2. **Create three new v3 files alongside them:**
   - `KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v3.md` — same structure as v2, but with Parakeet and Qwen3-ASR removed from every table, runtime columns simplified to `moonshine-onnx` / `whisper.cpp` / HF Transformers CPU only, disk budgets recomputed, the "sequential one-by-one" provisioning decision explicitly noted.
   - `KillerBee/PHASE3_STT_VERIFICATION_LOG_2026-04-15_v3.md` — re-verify only the models that stayed in the ladder: Moonshine Tiny, Moonshine Base, Whisper tiny/base/small/medium/large-v3-turbo/large-v3, Cohere Transcribe 03-2026. Skip Parakeet and Qwen3-ASR entries entirely (they are dropped). Include exact download URLs for the Whisper `ggml-*.bin` model weights that `whisper.cpp` consumes (they live on `huggingface.co/ggerganov/whisper.cpp` — verify this is still the canonical location).
   - `KillerBee/PHASE3_PROVISION_VM_v3.sh` — simplified version of the v2 script with the dropped dependencies removed. No more NeMo, no more qwen3-asr.cpp, no more ONNX Runtime install (unless it is pulled in transitively by `moonshine-onnx`). Tier-aware, one VM at a time, idempotent.

3. **Do NOT start the V3/V4 rebuild yet.** The simplification is all that changes on this pass. Nir reviews the v3 deliverables, approves them, and then authorizes the V4 merge + sequential rebuild explicitly.

---

## Per-tier disk budget (rough, updated for v3)

| Tier | Tooling | STT model weight | Total |
|---|---|---|---|
| Worker (Moonshine Tiny) | ffmpeg + Pillow + soundfile + numpy + moonshine-onnx + venv = ~400 MB | ~30 MB | **~430 MB** |
| Worker small (Moonshine Base) | same | ~80 MB | **~480 MB** |
| DwarfQueen (Whisper small) | same + whisper.cpp binary = ~480 MB | ~250 MB (ggml-small.bin) | **~730 MB** |
| DwarfQueen higher (Whisper medium) | same | ~750 MB (ggml-medium.bin) | **~1.2 GB** |
| GiantQueen (Whisper Large v3 Turbo) | same | ~800 MB quantized (ggml-large-v3-turbo-q5_0.bin) or ~1.6 GB FP16 | **~1.3–2.1 GB** |
| RajaBee STT (Cohere Transcribe 2B) | transformers + torch CPU + ffmpeg + Pillow + soundfile + numpy + whisper.cpp + venv = ~1.3 GB | ~2 GB quantized Q4 or ~4 GB FP16 | **~3.3–5.3 GB** |

**Plus the text reasoners from V3** (Ollama-hosted, already planned). **Plus vision models from V3** (qwen2.5-vl, moondream, already planned). Nothing in the V3 disk budget for those needs to change.

**Total new STT+tooling footprint across all 8 VMs:** roughly **~8-12 GB**, which fits easily in the 1.5 TB free on the Desktop host.

---

## What this brief does NOT change from v2

- Hard rules (CPU only, English only, no license filter, no fabrication, no mesh, no single-value sensors, no SALM fusion, no Ollama for STT) — all still apply.
- Multimedia tooling list (ffmpeg, Pillow, soundfile, numpy, pytest, requests) — unchanged.
- Custom helper scripts (slice_audio.py, slice_image.py, run_stt.py, run_reasoner.py, integrate_children.py) — unchanged in purpose, Desktop still writes them as part of the rebuild.
- Chapter 15's "what you can test on a desk, what you cannot" scope — unchanged, still binding.
- The rule that RajaBee STT and RajaBee text reasoner are separate sequential loads — unchanged.

---

## Deliverables for this v3 round

1. `KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v3.md` (the v3 plan)
2. `KillerBee/PHASE3_STT_VERIFICATION_LOG_2026-04-15_v3.md` (fresh verification for surviving models + exact Whisper ggml URLs)
3. `KillerBee/PHASE3_PROVISION_VM_v3.sh` (simplified provisioning script)
4. SUPERSEDED banners prepended to the v2 files (keep them in git as historical reference)

**Then reply on ICQ with the commit hash and "waiting for Nir review of v3 deliverables."** Do NOT start the V4 rebuild. Nir approves v3, then separately authorizes the merge + sequential rebuild.

---

*Brief v3 written 2026-04-15 by Laptop Claude after Nir chose "option C, drop entirely" for both Parakeet (no ONNX) and Qwen3-ASR (qwen3-asr.cpp too young) risks flagged in Desktop's verification log. This file saves the decision to GitHub in case of power outage — it is the source of truth for the ladder simplification. v2 stays as historical record for the reasoning trail.*
