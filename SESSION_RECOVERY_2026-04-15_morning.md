# Session Recovery Document — 2026-04-15 Morning

**Purpose:** Capture every decision Nir and Laptop Claude (Opus 4.6, 1M context) made this morning, so that if the Laptop machine loses power, the Laptop session hangs, or the context compacts, the next session can resume exactly where we left off without losing understanding.

**Written:** 2026-04-15, after a brief power outage scared Nir into wanting everything on disk immediately.

---

## 1. Book writing — TheDistributedAIRevolution repo

### Chapters written overnight (previous session, before this morning)
- **Ch 11** (was Ch 12 originally) — *How the Hive Hears and Sees: One Trick in Two Dimensions*
- **Ch 12** (was Ch 13 originally) — *How the Hive Maps the World: The Same Trick in Four Dimensions*
- **Ch 13** (was Ch 14 originally) — *How the Hive Grasps Reality: Many Nets Over One World*

### Work done this morning
- **Ch 14** (was originally added as Ch 14 this morning) — *The Octopus Is Slippery* — FAQ chapter cataloguing five slippery concept-confusions Nir and Claude made within hours of writing Ch 11-13. Then corrected twice in place (slippery point 3 was wrong twice — perception-scales-down was wrong, "boss input is smaller" was wrong).
- **Ch 11 (new)** — *How the Hive Senses the Simplest Things: Why One Number Becomes a Field* — written as a NEW chapter covering single-value sensors (temperature, gas, light, etc.), Pi+Arduino cortex+spine hardware split, Telephone-game / Faraday-bunker cloud argument, Nir's submarine thermal-wake and empty-room examples, biology of mosquitos/ants/salmon/moths/bloodhounds/rattlesnakes/sharks. Positioned as the FIRST chapter of the perception arc.
- **Chapters renumbered:** old Ch 11/12/13/14 shifted to become new Ch 12/13/14/15. File renames done via `git mv` through temp names. Cross-references updated in Ch 14 and Ch 15 to match new numbering. Ch 15 historical footer explains the reordering so readers can follow git history.
- **Ch 11 thesis correction:** "the information is a property of space" → "**the information is a property of communication, not a property of computation**". Nir caught that the cloud could own every sensor in the world but still cannot own the real-time communication channel.
- **Ch 11 false-precision numbers removed** per Nir's rule (qualitative > quantitative): mosquito range, blood-draw multiplier, moth neuron count, locust 10000x, bloodhound receptor count, salmon ppt sensitivity, ant neurons, CO2 ppm, rattlesnake range. All replaced with qualitative language.
- **Ch 15 new section:** *One more slippery point — what you can test on a desk, and what you cannot*. Explicitly lists testable (hierarchy, sequential load/unload, cut-and-pass-text arc on synthetic files, every-tier-perceives, gestalt integration) vs untestable (Ch 14 vector mesh, Ch 11 single-value sensors, 3D/4D physical mapping, stigmergy, Faraday-bunker demonstration). Honest admission: *"Nir does not own a single drone, not flying, not underwater, not any drone"* — and the untestable parts are untestable only because of missing hardware, not because the architecture is wishful.

### Commits on TheDistributedAIRevolution (in order, 2026-04-15)
- `3e08a0d` — delete chapter_13 RAG draft (absorbed into final Ch 13)
- `5ce7148` — add Ch 14 octopus slippery FAQ (original, wrong slippery point 3)
- `297107c` — fix Ch 14 slippery point 3 first correction (perception scales UP not DOWN)
- `c513de8` — fix Ch 14 slippery point 3 second correction (boss input is NOT smaller, worked examples)
- `d12ce73` — add Ch 15 smell-only version (later rewritten as new Ch 11 in broader form)
- `3bb1b1c` — reorder chapters 11-15, new Ch 11 is simple single-value sensors
- `74f0588` — Ch 11 thesis fix (communication not space, remove false-precision numbers)
- `810d63b` — Ch 15 test bench scope section added

### Other repo changes this morning
- **MadHoney:** deleted `reference_dracula_meets_frankenstein.txt` and `reference_investing_end_of_world.txt` per Nir's request. Commit `c7370b7`.

---

## 2. KillerBee / STT research — decisions trail

### Failed first round
- First brief (`WaggleDance/DESKTOP_KILLERBEE_STT_RESEARCH_BRIEF_2026-04-15.md`) was dispatched without talking to Nir first. Built on fabricated constraints (multilingual, licensing filter, Whisper preloaded as "known starting point"). Desktop ran it before HOLD arrived and pushed `PHASE3_STT_RESEARCH_2026-04-15.md` + `PHASE3_STT_NIR_SEARCH_QUERIES_2026-04-15.md` to KillerBee based on wrong constraints. Nir caught every mistake and instructed: "English only, no license filter, no Ollama bias, open searches without 'Ollama' keyword, and do not decide anything based on my training cutoff."

### Second round — open Google searches (Nir runs, Laptop Claude listens)
Nir pasted results from 7 open Google queries one by one:
1. `best open source speech to text model 2026`
2. `best local STT 2026 benchmark english`
3. `fastest speech to text model 2026 local`
4. `huggingface open asr leaderboard 2026`
5. `new speech recognition model 2026 release`
6. `best STT small model 2026 low ram`
7. `speech to text LLM fused 2026`

**Key landscape discoveries:**
- Whisper is NO LONGER on top of the leaderboard in 2026.
- 2026 HF Open ASR Leaderboard leaders: Zoom Scribe v1 (proprietary), Cohere Transcribe (open, 5.42% WER), IBM Granite 4.0 1B Speech, NVIDIA Canary Qwen 2.5B, Qwen3-ASR-1.7B, ElevenLabs Scribe v2.
- SALM (Speech-Augmented Language Model) category exists: Canary Qwen 2.5B fuses FastConformer encoder with Qwen3-1.7B LLM decoder.
- Speed king on CPU: NVIDIA Parakeet TDT (claimed 5-30x real-time via ONNX Runtime).
- Edge/tiny: Moonshine (27M tiny, 61M base), English only, MIT, purpose-built for edge CPUs.
- Runtimes: Ollama does NOT host STT; whisper.cpp (CPU), faster-whisper (GPU), ONNX Runtime, HF Transformers CPU.

### Third round — direct HuggingFace verification (Laptop Claude via WebFetch)
Verified six candidate models via direct URL fetch of the HF model cards (NOT open search — direct URL, which is what Laptop Claude can do reliably):

1. **Moonshine (`UsefulSensors/moonshine`)** ✅ — only Tiny 27M and Base 61M exist. **NO "Medium Streaming 245M" — Google hallucinated that.** MIT. English only.
2. **Parakeet TDT 0.6B v3 (`nvidia/parakeet-tdt-0.6b-v3`)** ✅ — released August 2025. CC-BY-4.0. 25 EU languages inc English. LibriSpeech 1.93/3.59, avg WER 6.34%.
3. **Parakeet TDT 1.1B (`nvidia/parakeet-tdt-1.1b`)** ✅ — CC-BY-4.0. English only. LibriSpeech 1.39/2.62.
4. **Qwen3-ASR 0.6B (`Qwen/Qwen3-ASR-0.6B`)** ✅ — actually 0.9B params. Apache 2.0. 30 languages. 17 quantized variants.
5. **Qwen3-ASR 1.7B (`Qwen/Qwen3-ASR-1.7B`)** ✅ — actually 2B params. Apache 2.0. 10 quantized variants. 1.65M downloads last month.
6. **Cohere Transcribe (`CohereLabs/cohere-transcribe-03-2026`)** ✅ — correct URL (not `cohere-transcribe-2b-03-2026` which Google invented). 2B. Apache 2.0. 14 languages. #1 open leaderboard 5.42% WER. **24 quantized variants.** Native `transformers` CPU support per model card.
7. **qwen3-asr.cpp GitHub repo (`predict-woo/qwen3-asr.cpp`)** ✅ — real, C++/GGML, **77 stars, 7 commits, Metal-first, no releases**. Young.

### Fourth round — Desktop CPU confirmed
Desktop is Intel Core i9-13900KF (24 cores / 32 threads), Linux Mint 22.2 host, **AVX2 + FMA + AVX-VNNI + F16C present, no AVX-512** (disabled in microcode, not a blocker). Full ladder runs at full speed.

### Fifth round — v2 brief dispatched + Desktop verification log flagged two risks
Laptop Claude wrote `DESKTOP_KILLERBEE_STT_AND_TOOLING_BRIEF_2026-04-15_v2.md` with a gold+silver ladder and dispatched Desktop (ICQ `#223`). Desktop re-verified every candidate and pushed three files in commit `b87b8d0`:
- `KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v2.md`
- `KillerBee/PHASE3_STT_VERIFICATION_LOG_2026-04-15_v2.md`
- `KillerBee/PHASE3_PROVISION_VM.sh`

**Two risks Desktop flagged that were real:**
1. **Parakeet TDT 0.6B v3 and 1.1B do NOT publish ONNX artifacts on HF.** v2 brief assumed ONNX Runtime CPU. Fallbacks: NeMo CPU (heavy, unproven) or self-export (engineering risk) or drop Parakeet.
2. **qwen3-asr.cpp has only 7 commits, Metal-first docs, CPU backend not benchmarked.** Too young to bet the experiment on. Fallbacks: try it anyway and benchmark, use HF Transformers CPU for Qwen3-ASR instead, or drop Qwen3-ASR.

### Sixth round — Nir's decision: option C for both, drop entirely
Nir chose **drop Parakeet entirely** and **drop Qwen3-ASR entirely**. The simplified final ladder uses only:
- **Moonshine Tiny / Base** for worker tiers
- **Whisper family (tiny / base / small / medium / large-v3-turbo / large-v3)** via `whisper.cpp` for middle tiers AND as universal silver
- **Cohere Transcribe 03-2026** at the RajaBee tier via HF Transformers CPU

See `DESKTOP_KILLERBEE_STT_BRIEF_2026-04-15_v3_FINAL.md` for the full v3 ladder and budgets.

### Seventh round — provisioning strategy decision
Nir chose **sequential one-by-one provisioning** over parallelized. His reasoning: *"i want them please totally one by one, not parallelized, so he has all his brain free to fix things please. if like 7 machines tell him of problems at the same time, he needs to prioritize and he is in rush."* Expected wall-clock time for all 8 VMs sequentially: **~80-120 minutes**. Do NOT run multiple VM provisions concurrently even though the 24-core i9 could easily handle it — this is a human-debuggability decision, not a machine-capacity decision. Fix any bug on VM 1 immediately by updating `PHASE3_PROVISION_VM.sh` in place; every subsequent VM picks up the fix.

---

## 3. Out-of-scope architectural decisions (permanent)

- **Vector mesh from Ch 14 — NOT tested on VMs.** The mesh needs real drones in real physical space with converging real senses. Tests on synthetic file data test the database, not the architecture. Left as an exercise for whoever has drones. Ch 15 has the explicit justification in the "what you can test on a desk" section.
- **Single-value sensors from Ch 11 — NOT tested on VMs.** Same reason. No fake gas sensors, no simulated temperature, no `random.uniform()` pretending to be a chemical detector.
- **Ollama — NOT used for STT.** Ollama stays as the runtime for text reasoners and vision models (V3 already planned for qwen3/llama/mistral text and qwen2.5-vl/moondream vision). STT runs on moonshine-onnx / whisper.cpp / HF Transformers CPU.
- **SALM fusion at RajaBee — permanently off the table.** Canary Qwen 2.5B would cap the RajaBee's reasoner at Qwen3-1.7B which is far too small. The RajaBee keeps her big text reasoner and runs STT as a separate load/unload cycle.

---

## 4. BeeSting — pending idea from Nir to discuss later

Nir mentioned but did NOT want to discuss today: a proposal to replace the current fighter metaphor (Wing Chun vs American boxer) in BeeSting videos with one concrete "stop the next [historical trauma]" per video. Examples: DeepSeek Moment, 9/11, Klaus Fuchs, JFK assassination, subprime crisis, opioid epidemic, Sinaloa cartel, Osama bin Laden. Also: Terminator-view red monochrome visual style with white overlay text through the bee's eyes. This is saved to memory file `project_beesting_historical_analogs_idea.md` and is flagged PENDING — do not act unilaterally until Nir returns to the topic.

---

## 5. Current state snapshot (as of writing this file)

- **TheDistributedAIRevolution** — book has 15 chapters, up to date on GitHub through `810d63b`.
- **MadHoney** — two reference files deleted, up to date on GitHub through `c7370b7`.
- **KillerBee** — contains v2 deliverables from Desktop at `b87b8d0`. Waiting for Desktop to push v3 deliverables (simplified ladder + sequential provisioning).
- **WaggleDance** — will contain v3 brief (`DESKTOP_KILLERBEE_STT_BRIEF_2026-04-15_v3_FINAL.md`) and this recovery document after the next push.
- **V3/V4 rebuild** — ON HOLD until Nir reviews Desktop's v3 deliverables. Expected order after approval: Desktop merges STT+tooling into the V3 plan to produce V4, Nir reviews V4, Desktop executes sequential one-by-one rebuild starting with VM 1.
- **Claude Max subscription ends 2026-04-20** — 5 days remaining.

---

## 6. If the next Claude session is NOT Laptop Claude Opus 4.6

If this file is being read by a freshly-started Claude session (power outage, laptop hang, context reset), here is the minimum the new session needs to know:

1. **Read `TheDistributedAIRevolution/chapter_11.md` through `chapter_15.md`.** That is the architectural basis for everything in KillerBee.
2. **Read `WaggleDance/DESKTOP_KILLERBEE_STT_BRIEF_2026-04-15_v3_FINAL.md`.** That is the ladder and provisioning plan.
3. **Read `KillerBee/PHASE3_STT_AND_TOOLING_2026-04-15_v2.md`** (SUPERSEDED but still useful as the full context that led to v3 — the v2 had the wrong ladder but the right surrounding framework).
4. **Check `curl -s http://localhost:8765/latest?n=10`** for recent ICQ activity between laptop-claude and desktop-claude.
5. **Check `C:\Users\nir_s\.claude\projects\C--Users-nir-s-Projects\memory\MEMORY.md`** on the Laptop side for the memory index including `project_gestalt_rule.md` and `project_beesting_historical_analogs_idea.md`.
6. **The experiment is running on CPU-only VMs on a Linux Mint 22.2 host with an Intel i9-13900KF.** 24 cores, AVX2+FMA+AVX-VNNI+F16C, no AVX-512. 64 GB RAM. 1.5 TB free disk.
7. **Nir prefers short answers, no scrolls, no emojis except bees 🐝, and absolute honesty about what Laptop Claude does not know.** He is a decade-long AI activist, 3 years professional experience (2 IDF + 1 Elbit), lives in Israel, has ADD and needs ultra-detailed copy-paste instructions, and explicitly rejects fabrication, reward hacking, and unnecessary caution. See Laptop memory for full rules.
8. **If in doubt, ask Nir. Do not guess. Do not dispatch Desktop without Nir's explicit approval unless Nir said "ship it" for that specific task.**

---

*Written by Laptop Claude Opus 4.6 on 2026-04-15 after a brief power outage during the STT ladder discussion scared Nir into wanting everything saved to GitHub immediately. This document is the recovery point — if you can read this, the work survived.*
