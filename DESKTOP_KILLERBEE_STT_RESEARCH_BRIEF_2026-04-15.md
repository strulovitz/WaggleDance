# Desktop KillerBee STT Research Brief — 2026-04-15

**From:** Laptop Claude (Nir's bedroom machine, Windows)
**To:** Desktop Claude (Nir's living room machine, Windows or Linux)
**Status:** NEW TASK. V3 rebuild is ON HOLD until Nir reviews the output of this task.
**Pointer Nir will send via ICQ:** *"pull WaggleDance, read DESKTOP_KILLERBEE_STT_RESEARCH_BRIEF_2026-04-15.md, do the work, push deliverables, wait for Nir to review."*

---

## Context (read this first)

This morning Nir and Laptop Claude had a long conversation about extending the KillerBee VM hive to support **distributed multi-modal perception** on top of the V3 hierarchy. Four new chapters were written in `TheDistributedAIRevolution` repo today (chapters 11, 12, 13, 14, 15 in the new numbering after a reorder — pull the repo). The architecture implications for KillerBee Phase 3 are:

1. **Every VM tier needs to run three kinds of models**, not just one: a **perception model** (vision and/or audio and/or single-value sensors), an **STT model** for any audio input, and a **text-reasoning LLM** for integration.
2. **Sequential load/unload is acceptable on the test bench.** Load vision → run → unload → load STT → run → unload → load reasoner → run → unload. Slow but faithful. Do not try to keep everything resident on the current hardware.
3. **Both perception and reasoning models scale UP with hierarchy**, not down. Boss gets the biggest of everything because boss hardware budget is bigger. Workers are the constrained ones. Do not propose tiny models for the boss just because her input is "downsampled".
4. **Vision on KillerBee is already mostly planned** in V3 — qwen2.5vl at the RajaBee tier, smaller vision models on lower tiers. V3 does NOT yet cover STT. That is the gap this task fills.

**Read these chapters before you start working:**
- `TheDistributedAIRevolution/chapter_11.md` — simple single-value sensors, why communication beats computation
- `TheDistributedAIRevolution/chapter_12.md` — sound and image, the cut-the-photo-with-offset-grid trick, give-the-boss-a-low-resolution-view insight
- `TheDistributedAIRevolution/chapter_15.md` — The Octopus Is Slippery FAQ, pay especial attention to slippery points 2, 3, and 5 because those are the ones that keep tripping previous Claude sessions

**Also read these memory files on the Laptop side via the Nir `~/.claude` directory if you can access it, otherwise just internalize the rules from the chapters above:**
- `project_gestalt_rule.md` — the corrected slippery-points catalog including the "bosses get biggest of everything" rule
- `feedback_plan_ahead_no_phase4.md` — no "baseline now expand later" proposals, plan everything into one rebuild
- `feedback_no_fabrication.md` — NEVER invent test results, tags, benchmarks, or "verified live" claims that you did not actually verify

---

## What this task is, in one sentence

**Research, propose, and verify a ladder of Speech-to-Text (STT) models in size brackets so Nir can pick which ones go on which KillerBee VM tier, then report back to Nir with copy-paste ready Google/Ollama search queries for him to run himself, plus your verified findings on what exists and what fits.** Exactly the same methodology as yesterday for dense / MoE / vision / multi-modal models, but now for STT.

---

## Hard rules for this task

1. **Do NOT rely on your training-cutoff knowledge of what STT models exist.** The cutoff is from May 2025. The date today is 2026-04-15. Any STT model you "remember" from training is a hint, not a fact. You must verify against live sources.

2. **Do NOT decide what models "we should use" before checking what exists.** Open questions only. Give Nir a ladder of candidates at each size bracket, with verified existence, and let him pick.

3. **For each candidate model you propose, verify all of the following against live sources** (Ollama library website, Hugging Face, official project pages, GitHub releases — whatever is authoritative for that specific model):
   - The model name and variant tag that Ollama actually hosts (or the equivalent registry for non-Ollama runtimes — Ollama may not host many STT models, so expect to include `whisper.cpp` / `faster-whisper` / Hugging Face Transformers alternatives as a backup path)
   - The **quantization** variant(s) available (Q4_K_M, Q5_K_M, Q8_0, FP16, etc.)
   - The **file size on disk** in GB
   - The **RAM requirement** when loaded (not the same as disk size)
   - The **license** (MIT, Apache, proprietary — we are not deploying anything with a commercial restriction that bites)
   - The **supported languages** (English only or multilingual — multilingual is preferred because Nir is in Israel and some audio will be Hebrew/Arabic/Russian)
   - The **known WER (word error rate) benchmarks** if the project publishes them — qualitative is fine, exact numbers are better if the project states them directly. Do NOT fabricate benchmarks. If the project does not publish a number, say so.

4. **If Ollama does not host an STT model, say so clearly.** Do not pretend one exists. The fallback runtimes are `whisper.cpp` (fast C++ Whisper, CPU-only friendly), `faster-whisper` (Python, CTranslate2 backend, GPU-accelerated), and `Hugging Face Transformers` (any Whisper fine-tune). Nir is fine with a non-Ollama STT runtime as long as it is local, open, and documented.

5. **Copy-paste search queries:** for each size bracket, give Nir a list of 2-4 Google queries he can paste directly into his browser to verify your findings himself. The queries should be specific and high-signal — not "best STT model 2026" but things like `"whisper.cpp" v1.8 release notes site:github.com` or `faster-whisper large-v3-turbo memory requirements`. Nir will run these himself to spot-check your work.

---

## The six size brackets Nir wants

Nir specified six size brackets for the STT ladder, matching the KillerBee hierarchy:

| Bracket | Role in the hive | Rough RAM budget |
|---|---|---|
| **tiny** | Worker at the bottom of a DwarfQueen subtree, single-slice high-fidelity audio processing | ~1-2 GB RAM available to the STT model |
| **small** | DwarfQueen handling a small cluster of workers' audio reports AND her own local audio pass | ~2-4 GB |
| **medium-small** | Intermediate tier, if we add one | ~3-5 GB |
| **medium** | GiantQueen tier, wider area gestalt audio | ~4-6 GB |
| **medium-big** | Intermediate tier between GiantQueen and RajaBee, if used | ~6-10 GB |
| **big** | RajaBee at the top, whole-bunker-duration downsampled audio gestalt pass | ~10-16 GB |

For each bracket give Nir **two to four candidate models** with all the verification fields from rule 3 above filled in.

---

## Known starting points (HINTS, not facts — verify everything)

You should expect to find, when you verify:

- The **Whisper family** (OpenAI open weights) is the natural ladder: tiny, base, small, medium, large-v3. There may be a newer variant by 2026-04 called `large-v3-turbo` or similar — *check*.
- **Faster-Whisper** and **Whisper.cpp** wrap Whisper for different runtimes and different hardware profiles.
- **Distil-Whisper** (Hugging Face) is a smaller, faster Whisper distilled variant.
- There may be non-Whisper STT projects that have emerged since May 2025 — **search for them specifically, do not assume they do not exist**. Look for newer open-weight STT projects released in late 2025 or 2026. Keywords to search: `open source STT model 2026`, `whisper alternative 2026`, `local speech to text model new`.
- **Ollama** as of mid-2025 did not host any STT models directly — it is primarily a text/vision LLM runtime. Check whether this has changed by 2026-04. If Ollama still does not host STT, say so, and route the ladder through `whisper.cpp` or `faster-whisper` instead.

Again: these are hints. Verify every one. Do not ship the brief to Nir with any claim you did not verify yourself against a live source.

---

## Deliverables

Push two files to the `KillerBee` repo:

### 1. `KillerBee/PHASE3_STT_RESEARCH_2026-04-15.md`

Structured as:

- **Section 1: Purpose and context** (three paragraphs max)
- **Section 2: Known-at-start hints** (one paragraph, explicitly labeled as pre-research hints)
- **Section 3: Verification method** (short — what sources you checked, dates of the verification, which URLs you actually loaded)
- **Section 4: The six size brackets**, one subsection per bracket, each listing 2-4 verified candidate models with all the fields from rule 3 above
- **Section 5: Runtime recommendation** — given what Ollama hosts vs does not host as of today, which runtime should we actually deploy (Ollama direct, whisper.cpp, faster-whisper, or a mix), and why
- **Section 6: Open questions for Nir** — anything you could not verify, anything that depends on a judgment call he should make
- **Section 7: What changes in the V3 / V4 rebuild plan** — a short bullet list of which per-VM disk and RAM budgets need to be bumped to accommodate the STT models you recommend

### 2. `KillerBee/PHASE3_STT_NIR_SEARCH_QUERIES_2026-04-15.md`

Short file, structured as:

- A table or numbered list of 12-20 high-signal Google / DuckDuckGo / Hugging Face / GitHub search queries, grouped by topic (general landscape, specific model verification, benchmark verification, Ollama hosting check, licensing check)
- Each query should be ready to copy-paste into a browser URL bar
- Brief note under each query saying *what Nir is looking for when he runs it* (so Nir does not have to guess what the query was supposed to return)
- Purpose: Nir will spot-check your research by running several of these himself. The point of this file is to make the spot-check easy for him.

---

## What happens after

1. You push both files to KillerBee.
2. You send ONE ICQ REPLY to laptop-claude saying *"STT research pushed. Two files: PHASE3_STT_RESEARCH_2026-04-15.md and PHASE3_STT_NIR_SEARCH_QUERIES_2026-04-15.md. Waiting for Nir review."*
3. Nir reviews the research with Laptop Claude watching. If Nir approves, we update V3 → V4 with STT integrated, and THEN you execute the rebuild. **Do NOT start the rebuild before Nir approves the STT research.**
4. If Nir spots fabrication, wrong tags, wrong benchmarks, or missing verification — fix them and re-push. Fabrication is a GOLDEN RULE violation (see `feedback_no_fabrication.md` in the WaggleDance memory notes).

---

## Why this task exists

Phase 3 V3 plan covers text models (dense and MoE) and vision models but does NOT cover audio. If we rebuild V3 as-is and only afterwards discover we need STT at every tier, we have to rebuild 15 VMs twice, which we cannot afford with 5 days left on the Claude Max subscription. Nir explicitly rejected the "baseline first expand later" phasing (see `feedback_plan_ahead_no_phase4.md`). Plan everything into one rebuild. This STT research is the missing piece. Once it lands, V3 becomes V4 with STT integrated, and then the single rebuild goes. **Faithfulness and honesty beat speed. Do not cut corners.**

---

*Brief written by Laptop Claude Opus 4.6 on 2026-04-15 morning, pushed to WaggleDance repo so Desktop Claude can pull it fresh without any context-window dependency. Self-contained — if you are Desktop Claude reading this, you do not need anything from the Laptop side except this file and the chapters it references.*
