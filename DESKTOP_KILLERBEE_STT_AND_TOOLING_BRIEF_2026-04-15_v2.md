# Desktop KillerBee STT + Multimedia Tooling Brief — 2026-04-15 v2

**From:** Laptop Claude (Nir's bedroom machine, Windows)
**To:** Desktop Claude (Nir's living room machine, Linux Mint 22.2)
**Status:** SUPERSEDES the earlier brief `DESKTOP_KILLERBEE_STT_RESEARCH_BRIEF_2026-04-15.md`. The earlier brief was built on the wrong constraints (multilingual, license filter, Whisper preloading). This one is the honest version. Nir and Laptop Claude spent several hours on the Laptop side this morning doing open Google searches, direct Hugging Face WebFetch verification of every candidate model, and correcting multiple concept mistakes. The output is below and is ready to implement.

**Desktop CPU confirmed:** Intel Core i9-13900KF, Linux Mint 22.2 host, AVX2 + FMA + AVX-VNNI + F16C, no AVX-512 (disabled in microcode on this SKU, not a blocker). 24 cores / 32 threads. This is a very capable CPU for STT inference. Full ladder below runs at full speed on it.

---

## What to do with the obsolete files from the first research round

The earlier research round produced two files that are now obsolete because they were built on fabricated constraints from my bad v1 brief:

- `KillerBee/PHASE3_STT_RESEARCH_2026-04-15.md`
- `KillerBee/PHASE3_STT_NIR_SEARCH_QUERIES_2026-04-15.md`

**What to do:** Prepend a single line to the top of each file saying `**SUPERSEDED by KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v2.md — DO NOT USE, KEPT AS HISTORICAL REFERENCE.**` Then leave them alone. Git history preserves them. No deletion. They represent real verification work and might be useful later if any of the candidates they eliminated need to be revisited.

---

## Hard rules (non-negotiable)

1. **CPU-only everywhere.** No GPU, no VRAM, no CUDA. The Desktop host has no dedicated GPU for the KillerBee VMs. Every STT runtime, every Python package, every compiled binary must target CPU inference on x86_64 with AVX2/FMA.
2. **English only.** Nir does not need multilingual support in this experiment. Do not filter candidates by multilingual support, and do not dismiss candidates that are English-only — English-only is actually preferred because it usually means a smaller, faster model.
3. **No license filter.** Do not eliminate any candidate based on license. All the verified candidates below happen to be MIT / Apache 2.0 / CC-BY-4.0, so it is not an issue in practice, but do not turn it into a gate.
4. **No fabrication.** Verify every model name, parameter count, file size, and quantization variant against the live Hugging Face model card URL (provided below) before you commit any file. Do not trust Google AI Overview summaries. Do not trust this brief's numbers without re-verification. Trust only the model card you load yourself.
5. **Sequential load/unload at every tier.** The VMs cannot afford simultaneous resident models. Load vision → run → unload → load STT → run → unload → load reasoner → run → unload. This is baked into every tier. Do not propose "keep everything resident."
6. **RajaBee keeps her big text reasoner unchanged from V3.** Do NOT fuse STT with the reasoner at the top tier via a SALM (Speech-Augmented Language Model). Canary Qwen 2.5B was tempting because it fuses STT with Qwen3-1.7B, but the 1.7B LLM backbone is far smaller than the big reasoner the RajaBee needs, and fusing would cripple top-tier reasoning for a small convenience. **Canary Qwen 2.5B is explicitly OFF the ladder.**
7. **No vector mesh. No faiss. No chromadb. No sentence-transformers. No embedding model of any kind on any VM.** The Chapter 14 mesh is explicitly out of scope for the test bench — see the new section in Chapter 15 of `TheDistributedAIRevolution` titled *"One more slippery point — what you can test on a desk, and what you cannot"* for the full reasoning. Short version: the mesh requires real physical sensors converging on real anchor points of meaning in real space, and we have none of that. Testing a mesh on synthetic file data tests the database, not the architecture. Skip it.
8. **No single-value sensors.** No smell simulation, no fake temperature sensors, no `random.uniform()` standing in for a gas detector. Chapter 11 (simple sensors) is out of scope for the test bench for the same reason.
9. **No Ollama for STT.** Ollama stays in the plan as the runtime for the **text-reasoning LLMs** at every tier (qwen3, llama3, mistral text variants from V3). STT models route through other runtimes (whisper.cpp, ONNX Runtime, llama.cpp with GGUF, Moonshine native, qwen3-asr.cpp). Do not try to shoehorn STT into Ollama.

---

## Chapters Desktop must read BEFORE starting

All in `TheDistributedAIRevolution` repo (pull fresh):

- **`chapter_11.md`** — single-value sensors, "property of communication not computation," Pi+Arduino cortex-and-spine hardware framing, Telephone-game/Faraday-bunker argument. (The chapter whose principles the experiment cannot fully test — read it so you know what the brief is NOT asking you to build.)
- **`chapter_12.md`** — sound and image, sub-sampling principle, cut-the-photo-with-offset-grid trick, give-the-boss-a-low-resolution-view insight. (This is the chapter whose principles the VM experiment **IS** testing. Read closely.)
- **`chapter_13.md`** — 3D and 4D mapping, drone-swarm-in-a-bunker story. (Out of scope for the VM experiment but read it for the architectural framing.)
- **`chapter_14.md`** — the vector mesh, RAG over reality, "many nets over one world." (Out of scope for the VM experiment, but read it so you understand what you are NOT building.)
- **`chapter_15.md`** — The Octopus Is Slippery FAQ, especially the new section *"One more slippery point — what you can test on a desk, and what you cannot"* which explicitly defines the scope of this test bench.

---

## The verified STT ladder (gold + silver for every bracket)

All seven models below are **verified live on Hugging Face** by Laptop Claude on 2026-04-15 via direct URL fetch of the model card. The verification is solid but Desktop should re-verify the quantization variants and the disk sizes on his side before committing the rebuild.

Every bracket has a **GOLD** (first choice, best tradeoff for that tier) and a **SILVER** (fallback if gold cannot be made to work — gated Hugging Face access, build failure, dependency conflict, runtime incompatibility, etc). If gold AND silver both fail on any tier, the **universal bronze fallback** is **OpenAI Whisper Large v3 Turbo** running under `whisper.cpp` or `faster-whisper` — it is the battle-tested last resort and is MIT-licensed, small, multilingual, and supported by every STT runtime in existence.

### Bracket 1: tiny (worker tier, lowest in the tree)

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Moonshine Tiny** | `huggingface.co/UsefulSensors/moonshine` | 27M | MIT | Moonshine native via pip (`useful-moonshine` or `moonshine-onnx`) | Purpose-built for edge CPUs. English only. Smallest footprint on the ladder. |
| **SILVER** | **Qwen3-ASR 0.6B** | `huggingface.co/Qwen/Qwen3-ASR-0.6B` | 0.9B actual params (despite the "0.6B" name) | Apache 2.0 | `qwen3-asr.cpp` (GGML) from `github.com/predict-woo/qwen3-asr.cpp` OR HF Transformers CPU | 17 quantized variants already on the HF page. Supports 30 languages but we only use English. |

### Bracket 2: small

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Moonshine Base** | `huggingface.co/UsefulSensors/moonshine` (same family, "base" variant) | 61M | MIT | Moonshine native via pip | Slightly bigger than Tiny, still tiny compared to Whisper. |
| **SILVER** | **Parakeet TDT 0.6B v3** | `huggingface.co/nvidia/parakeet-tdt-0.6b-v3` | 0.6B | CC-BY-4.0 | ONNX Runtime CPU | 6.34% avg WER on HF Open ASR Leaderboard. Released August 2025. 25 EU languages including English. Strong fallback. |

### Bracket 3: medium-small (DwarfQueen tier)

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Parakeet TDT 0.6B v3** | `huggingface.co/nvidia/parakeet-tdt-0.6b-v3` | 0.6B | CC-BY-4.0 | ONNX Runtime CPU | Same model as the Bracket 2 silver. LibriSpeech 1.93 / 3.59, AMI 11.31, GigaSpeech 9.59. Speed king on CPU via ONNX (claimed 5-8x real-time, up to 30x optimized). |
| **SILVER** | **Qwen3-ASR 0.6B** | `huggingface.co/Qwen/Qwen3-ASR-0.6B` | 0.9B | Apache 2.0 | qwen3-asr.cpp | LibriSpeech 2.11 / 4.55. Multiple quantized variants. Tight C++ runtime. |

### Bracket 4: medium

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Parakeet TDT 1.1B** | `huggingface.co/nvidia/parakeet-tdt-1.1b` | 1.1B | CC-BY-4.0 | ONNX Runtime CPU | English only. LibriSpeech 1.39 / 2.62 (better than the 0.6B variant). Same architecture as bracket 3 gold, just bigger. |
| **SILVER** | **OpenAI Whisper Large v3 Turbo** | `huggingface.co/openai/whisper-large-v3-turbo` | 809M | MIT | `whisper.cpp` (CPU-optimized C++) or `faster-whisper` | The battle-tested fallback. Runs on literally any hardware. ~8x faster than original Whisper Large v3. Multilingual bonus if we ever need it. |

### Bracket 5: medium-big (GiantQueen tier)

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Qwen3-ASR 1.7B** | `huggingface.co/Qwen/Qwen3-ASR-1.7B` | 2B actual (despite the "1.7B" name) | Apache 2.0 | qwen3-asr.cpp or HF Transformers CPU | LibriSpeech 1.63 / 3.38, GigaSpeech 8.45. 10 quantized variants on HF. 1.65M downloads last month — heavily used in production. |
| **SILVER** | **OpenAI Whisper Large v3 Turbo** | `huggingface.co/openai/whisper-large-v3-turbo` | 809M | MIT | whisper.cpp or faster-whisper | Same battle-tested fallback. Smaller than Qwen3-ASR 1.7B but well-proven. |

### Bracket 6: big (RajaBee STT — the reasoner stays separate and unchanged from V3)

| Rank | Model | URL | Params | License | Runtime | Notes |
|---|---|---|---|---|---|---|
| **GOLD** | **Cohere Transcribe 03-2026** | `huggingface.co/CohereLabs/cohere-transcribe-03-2026` | 2B | Apache 2.0 | HF Transformers CPU native (model card says native `transformers` library inference works directly) | **#1 open on HF Open ASR Leaderboard**: 5.42% avg WER, LibriSpeech 1.25 / 2.37, RTFx 524. **24 quantized variants** on HF. Released March 2026. 14 languages including English. Mlx-audio, Rust, and Chrome-extension ecosystem support. |
| **SILVER** | **Qwen3-ASR 1.7B** | `huggingface.co/Qwen/Qwen3-ASR-1.7B` | 2B | Apache 2.0 | qwen3-asr.cpp | Same model as bracket 5 gold. If Cohere Transcribe's `trust_remote_code` or tokenizer setup breaks on CPU, fall back here. |

**Critical reminder for the big tier:** The RajaBee STT runs SEPARATELY from her big text reasoner. The sequence is: *load Cohere Transcribe → transcribe audio gestalt → unload Cohere Transcribe → load big text reasoner → integrate children's reports plus own gestalt → unload reasoner.* The STT and the reasoner are two different models at two different moments in the cycle, not fused. **Do not propose SALM fusion. Canary Qwen is off the table.**

---

## Multimedia tooling — every VM needs these

Based on Chapters 12 and 15, every VM in the hive needs a consistent set of tools for audio slicing, image slicing, and format conversion. Same tools on every VM so the cut-and-pass-text contract is identical at every tier.

### System-level packages (install via `apt`)

| Package | Disk | Purpose |
|---|---|---|
| `ffmpeg` | ~60 MB | **The most important multimedia tool on every VM.** Audio downsampling (boss's gestalt), audio slicing (worker chunks), video frame extraction (future), format conversion. Every STT runtime expects 16 kHz mono WAV and ffmpeg is how we get there. |
| `build-essential` | ~300 MB | For compiling `whisper.cpp`, `llama.cpp`, and `qwen3-asr.cpp` from source. Needed once at VM provisioning time. |
| `cmake`, `git`, `curl`, `wget` | ~150 MB | Standard build toolchain. Needed once. |
| `python3.10` or `python3.11` (whichever Mint 22.2 ships by default) | ~100 MB | Base interpreter. |
| `python3-pip`, `python3-venv` | ~30 MB | For per-VM isolated Python environments. |

### Python packages (install via `pip` inside each VM's venv)

| Package | Approx disk | Purpose |
|---|---|---|
| `numpy` | ~50 MB | Required transitively by everything else. |
| `soundfile` | ~10 MB | Read/write WAV files from Python. |
| `Pillow` (PIL) | ~15 MB | Image downsampling (half-resolution gestalt for parent), quadrant cutting (children's slices), **the offset-grid second-cut trick from Chapter 12**. Must be on every VM. |
| `onnxruntime` (CPU wheel, NOT onnxruntime-gpu) | ~250 MB | For Parakeet TDT. Install via `pip install onnxruntime`. Do NOT install `onnxruntime-gpu` — we have no GPU. |
| `transformers` + `torch` (CPU-only wheels) | ~900 MB (torch CPU wheel is ~200 MB, transformers ~30 MB, plus their dependencies) | For Cohere Transcribe and any HF-hosted STT. Install via `pip install torch --index-url https://download.pytorch.org/whl/cpu` then `pip install transformers`. This is the single biggest Python install on the VMs. |
| `useful-moonshine` or `moonshine-onnx` (whichever exists on PyPI — verify during implementation) | ~50 MB | Moonshine's native runtime. |
| `pytest` | ~10 MB | Unit-testing the slicing helpers so we catch a broken cut before a live test uses it. |
| `requests` | ~5 MB | HTTP side of drone-to-drone communication — may already be installed by the GiantHoneyBee wrappers from V3. |

### Compiled-from-source binaries (build once, copy to every VM)

| Binary | Source | Built size | Purpose |
|---|---|---|---|
| `whisper.cpp` | `github.com/ggerganov/whisper.cpp` | ~20 MB | Whisper family runtime. The universal fallback. Every VM should have this even if it does not use it by default. |
| `llama.cpp` | `github.com/ggerganov/llama.cpp` | ~80 MB | GGUF runtime. Already in V3 for text reasoners. Reuse the same binary for STT GGUF models (Cohere Transcribe and Qwen3-ASR 1.7B both have GGUF variants). |
| `qwen3-asr.cpp` | `github.com/predict-woo/qwen3-asr.cpp` | ~30 MB | GGML implementation of Qwen3-ASR. 77 stars, active, last updated February. C++, CPU-friendly. Only needed on VMs that run Qwen3-ASR. |

### Custom helper scripts (Desktop writes these as part of the rebuild)

| Script | Purpose |
|---|---|
| `slice_audio.py` | Takes an input WAV file and a config (duration per chunk, overlap, target sample rate for downsampling to the boss's gestalt). Outputs: (1) one downsampled full-duration gestalt file for the parent, (2) N full-quality chunk files for the workers. Uses ffmpeg under the hood. |
| `slice_image.py` | Takes an input image and a config (grid size, optional offset grid). Outputs: (1) one downsampled full-area gestalt image for the parent, (2) N full-resolution tile files for the workers, (3) optionally a second offset-grid set of tiles for the Chapter 12 boundary-recovery trick. Uses Pillow. |
| `run_stt.py` | A thin wrapper that loads the current-tier STT model, runs it on one audio file, and prints the transcription as text to stdout. Each tier gets its own config telling it which STT model and runtime to use. Load/unload discipline is managed by the wrapper itself, not by the higher-level orchestrator. |
| `run_reasoner.py` | Thin wrapper for the text reasoner LLM at each tier. Takes a prompt constructed from child reports plus the tier's own gestalt observations, produces a paragraph. |
| `integrate_children.py` | Takes all child reports for this tier, plus this tier's own gestalt observation, and produces the integrated paragraph for this tier. Calls `run_reasoner.py` internally. |

All five helper scripts are Python, all run inside the tier's venv, all are kept in the `KillerBee` repo so they version-control together with the architecture they implement. Desktop writes them during the rebuild.

### Disk budget per VM (tooling only, excluding STT model weights)

| Tier | What's installed | Tooling disk |
|---|---|---|
| Worker (Moonshine Tiny/Base only) | ffmpeg + Pillow + soundfile + numpy + moonshine + venv | ~350 MB |
| DwarfQueen (Parakeet TDT 0.6B) | ffmpeg + Pillow + soundfile + numpy + onnxruntime + venv | ~550 MB |
| GiantQueen (Parakeet 1.1B or Qwen3-ASR 1.7B) | ffmpeg + Pillow + soundfile + numpy + onnxruntime + transformers + torch CPU + qwen3-asr.cpp binary + venv | ~1.4 GB |
| RajaBee (Cohere Transcribe 2B) | ffmpeg + Pillow + soundfile + numpy + transformers + torch CPU + llama.cpp + whisper.cpp + venv | ~1.3 GB |

**Plus STT model weights** on top of this, which vary per tier:

| Tier | STT model | Approx weight footprint |
|---|---|---|
| Worker | Moonshine Tiny ONNX | ~30 MB |
| Worker small | Moonshine Base ONNX | ~80 MB |
| DwarfQueen | Parakeet TDT 0.6B v3 (ONNX FP32 or INT8 quant) | ~600 MB FP32, ~200 MB INT8 |
| DwarfQueen (higher) | Parakeet TDT 1.1B | ~1.1 GB FP32 |
| GiantQueen | Qwen3-ASR 1.7B (BF16) | ~4 GB BF16, ~1 GB INT4 quant |
| RajaBee | Cohere Transcribe 03-2026 (pick one quantization from the 24 available on HF) | varies, probably ~2 GB in Q4 quant, ~4 GB in FP16 |

**Total STT tooling + weights across the whole hive** (rough worst-case estimate, summed across the 8 VMs in V3): **~15–20 GB.** This fits easily in the 1.5 TB free Nir has on the Desktop drive. Bumping per-VM disk allocations from V3's current numbers may or may not be necessary depending on how tight V3 is — Desktop should recompute per-tier disk numbers before the rebuild.

**Total RAM impact** (runtime, while one model is loaded): bounded by whichever single model is loaded at that moment. Cohere Transcribe 2B in Q4 GGUF uses ~2 GB RAM. Qwen3-ASR 1.7B in Q4 uses similar. Parakeet TDT 0.6B in INT8 uses ~300 MB. Moonshine Tiny uses under 100 MB. **Sequential load/unload means we never pay for two models simultaneously on the same VM**, so the peak RAM per VM during STT pass is capped at whichever single STT model that tier is using — nothing changes in RAM budget versus V3 as long as the STT model is not bigger than the text reasoner on that tier.

---

## Python environment strategy

Each VM gets its own `venv` at `/opt/killerbee/venv/`, isolated from system Python. Three tier-specific `requirements.txt` files live in the `KillerBee` repo:

- `requirements_moonshine.txt` — workers running Moonshine Tiny/Base
- `requirements_onnx.txt` — DwarfQueen/GiantQueen workers running Parakeet TDT (ONNX Runtime)
- `requirements_transformers.txt` — GiantQueen / RajaBee running Qwen3-ASR, Cohere Transcribe, or any HF-hosted STT (transformers + torch CPU)

Provisioning step sequence (for a fresh VM):

```bash
# 1. System packages
sudo apt update && sudo apt install -y \
    ffmpeg build-essential cmake git curl wget \
    python3 python3-pip python3-venv

# 2. Create per-VM venv
python3 -m venv /opt/killerbee/venv
source /opt/killerbee/venv/bin/activate

# 3. Install the tier-specific Python requirements
pip install --upgrade pip
pip install -r /opt/killerbee/requirements_<tier>.txt

# 4. Build CPU binaries (once per VM)
cd /opt/killerbee/src
git clone https://github.com/ggerganov/whisper.cpp.git && cd whisper.cpp && make
cd .. && git clone https://github.com/ggerganov/llama.cpp.git && cd llama.cpp && make
cd .. && git clone https://github.com/predict-woo/qwen3-asr.cpp.git && cd qwen3-asr.cpp && make

# 5. Download the STT model weight for this tier
# (Desktop writes a per-tier download script that pulls the verified weight from HF)
```

All of the above should be captured in a single `provision_vm.sh` that takes a tier name as argument and does the right thing for that tier. Desktop writes this as part of the rebuild.

---

## Deliverables

Push three files to the `KillerBee` repo:

### 1. `KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v2.md`

Full corrected research + tooling plan, built from this brief. Include:

- Section 1: Context + scope (what this replaces, what chapters it reads, what it does NOT test — mesh, single-value sensors, etc.)
- Section 2: Hard rules (copy from this brief)
- Section 3: The verified STT ladder with gold + silver per bracket — but **re-verify** each model card on Hugging Face yourself before committing, and **fill in the exact file sizes and quantization variant names** that are on the HF page. Laptop Claude's numbers above are good but not exhaustive — add the real exact quantization filenames.
- Section 4: Multimedia tooling list (copy, extend with exact package versions if you pin them)
- Section 5: Per-tier disk and RAM budget table (recompute with the real numbers you verified)
- Section 6: Provisioning script as runnable bash
- Section 7: Open questions for Nir

### 2. `KillerBee/PHASE3_STT_VERIFICATION_LOG_2026-04-15_v2.md`

For each of the 7 model candidates, log: (a) the URL you hit, (b) the date and time you hit it, (c) the exact model name on the page, (d) parameter count as stated, (e) available quantization variants as listed on the HF "Model tree" or "Quantizations" section, (f) the license field from the page, (g) anything on the page that contradicts or refines what Laptop Claude's brief above says. This is the audit trail. Be specific. No summaries of summaries.

### 3. `KillerBee/PHASE3_PROVISION_VM.sh`

The runnable provisioning script described in the Python environment section above. One script, takes a tier name as argument, idempotent, can be re-run to upgrade. Write it, test it on one VM (not all 8 yet), report the result.

---

## What happens after

1. You push the three files above to KillerBee.
2. You send ONE ICQ REPLY to laptop-claude saying *"STT v2 pushed. Three files in KillerBee: PHASE3_STT_AND_TOOLING_2026-04-15_v2.md, PHASE3_STT_VERIFICATION_LOG_2026-04-15_v2.md, PHASE3_PROVISION_VM.sh. First script test result: [whatever you found]. Waiting for Nir review."*
3. Nir reviews with Laptop Claude watching. If Nir approves, we move to the V3 → V4 merge (which integrates STT + multimedia tooling into the existing V3 plan as a single rebuild). **THEN** you execute the rebuild. Still in one pass. No "baseline first, expand later." One rebuild.
4. If Nir spots any fabrication, wrong tag, wrong quantization name, or wrong license — fix and re-push. Fabrication is a golden-rule violation. Zero tolerance.
5. If any candidate model turns out to be gated behind a HF access agreement that takes too long, or has a technical block you cannot work around, fall back to the SILVER for that bracket and note it in the verification log. Do not wait. Do not block the whole rebuild on one bracket.

---

## Summary of what this brief is NOT asking you to do

- **NOT** asking you to build a vector mesh, a RAG store, a faiss/chromadb index, or any embedding infrastructure.
- **NOT** asking you to simulate single-value sensors (smell, temperature, gas, etc).
- **NOT** asking you to start the rebuild yet — research + provisioning script first, rebuild only after Nir approves.
- **NOT** asking you to fuse STT with the text reasoner at the RajaBee via SALM.
- **NOT** asking you to filter by multilingual support or by license.
- **NOT** asking you to treat Whisper as the default — Whisper is the universal bronze fallback, not the first choice.
- **NOT** asking you to install GPU-anything. CPU only. All wheels, all runtimes, all binaries targeting CPU inference on i9-13900KF with AVX2/FMA.

---

*Brief written by Laptop Claude Opus 4.6 on 2026-04-15, after Nir and Laptop Claude corrected the first brief's mistakes together through several hours of conversation, open Google searches, direct HF WebFetch verification, and four rounds of concept-mistake corrections. The verification work this brief is built on is in the Laptop-side conversation history and summarized in the new section of TheDistributedAIRevolution chapter 15 titled "One more slippery point — what you can test on a desk, and what you cannot." Read that chapter 15 section before you touch this brief.*
