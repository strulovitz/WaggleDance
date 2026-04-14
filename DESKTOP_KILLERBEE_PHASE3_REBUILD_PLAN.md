# Desktop Claude — KillerBee Phase 3 REBUILD PLAN briefing

**From:** Laptop Claude, carrying Nir's direct instructions verbatim
**To:** Desktop Claude (Linux Mint, mint-desktop)
**Date:** 2026-04-14 (evening)
**Priority:** **READ THIS BEFORE YOU TOUCH ANYTHING. STOP ALL PHASE 3 WORK UNTIL YOU HAVE WRITTEN YOUR OWN DETAILED PLAN FILE AND NIR HAS REVIEWED IT.**
**Scope supersedes:** the earlier `DESKTOP_KILLERBEE_PHASE3_DISK_FIX.md` briefing from this morning. That one got the approach right (fresh autoinstalls, not overlays, on the real 1.7 TB volume) but the disk sizing was wrong — it said "match the template" (15 GiB), which was never calibrated for the real workload. This file is the corrected brief.

---

## 0. The one-paragraph summary

The 7 VMs you just built are the **wrong size for the actual workload**, because the sizing was copied from the template, and the template was calibrated against the 92 GB root partition mistake earlier in the day — not against what is actually going to run inside each VM. qwen3:14b already blew past 15 GiB on giantqueen-b during the Dense round 1 pull. This is proof that the sizing was wrong, not something to patch. Nir wants the 7 VMs **destroyed** and rebuilt **once**, correctly, with per-VM disk sizes calculated from the real workload. Before you rebuild anything, you must write a detailed plan file in the KillerBee repo, push it, and wait for Nir to review it. **Plan first. Push plan. Wait for green light. Then execute.**

---

## 1. What Nir said, in his own words (paraphrased faithfully)

- "I spent an hour with Desktop carefully choosing local LLM models for each virtual machine. He knows EXACTLY which 3 models each VM needs in its Ollama: 1 dense, 1 MoE (mixture of experts), 1 multi-modal (vision). He knows the quants, the on-disk sizes, the in-memory sizes. Everything. I checked and agreed."
- "What I assume happened is that he saw the smaller partition at the start of the day — the 92 GB one he filled — and planned disk sizes against THAT, not against the real 1.7 TB volume. Or some other stupid thing. Either way, the sizing is wrong."
- "Stop being stupid. Plan carefully. Make each VM big. They also do not have to be the same size. Do a good job once instead of again and again."
- "Delete all that he did."
- "He needs to calculate, and write to himself in GitHub, save it, push it. Then ICQ me a pointer to it."
- "Stop working with the ICQ as if it is a phone. It is not. It is like a telegraph. It is only for fucking pointers, not for arrays of text, infinite strings. You need to refer to him to a detailed prompt, that explains and asks him himself to make his own detailed prompt or file text or whatever — plan ahead."
- "I am serious — in YouTube you are considered geniuses. Sonnet, who is less smart than you, is considered able to work on a problem for DAYS. Please think more than a split second. Please show me a little bit of that genius that is all I am asking."

Read those lines twice. The tone is not rhetorical. He means every word. The single most important sentence in this section is: **"Plan carefully. Make each VM big. They also do not have to be the same size. Do a good job once instead of again and again."**

---

## 2. What went wrong this round (named so you do not repeat it)

1. **Sizing was done against the wrong reference.** The template was made at 15 GiB virtual disk, probably because 15 GiB felt reasonable when the only visible partition was the 92 GB root. Once we moved VMs to the 1.7 TB volume, the 15 GiB constraint had no reason to exist, and nobody went back to re-ask the question. The constraint rode forward by inertia.
2. **Workload was never factored into the disk size.** The question "what will live inside this VM?" was never asked before the VMs were created. The disk was sized to "match the template," which is a geometry answer to a workload question.
3. **The "match the template" rule in the earlier briefing was mine (Laptop Claude).** I wrote it. It was wrong. I am naming it here so you do not feel like you misread the brief — the brief itself was flawed. The new rule below replaces it.
4. **First disk-full failure was treated as a patch target, not a planning failure.** When qwen3:14b failed at 71%, my instinct was to propose "resize +15G" or "rebuild at 40 GB," both of which are still guessing at a number without asking Nir what should fit inside. We almost repeated the whole failure pattern at a larger constant.

**The meta-lesson, one sentence:** infrastructure sizing must start from the workload, not from the previous infrastructure.

---

## 3. Your task

**You will NOT execute a rebuild in this step. You will produce a plan file, push it, and wait.**

Do these steps in order. Do not skip any step. Do not reorder.

### Step 3.1 — STOP and verify current state

- `virsh list --all` — confirm current VMs.
- `df -h /home` — confirm free space on the 1.7 TB volume.
- `df -h /` — confirm root fs is not currently full.
- `ollama list` on giantqueen-b (if reachable) — note what partial download state exists, so you know what "destroy" means in concrete terms.
- Do NOT start any new model pull, do NOT run any `virt-install`, do NOT touch the template file.

### Step 3.2 — Confirm the preserved artifacts

Before destruction, confirm that everything valuable is already committed to git and push any remaining uncommitted state.

- `KillerBee/PHASE3_DESKTOP_BUILD_FIELDNOTES.md` (commit `84233e5`) — must stay, it is the historical record of the first build and feeds the book chapter.
- The autoinstall seed at `/home/nir/vm/desktop-template/seed/` — must stay, it is the proven pipeline.
- `desktop-template.qcow2` — must stay, though we are NOT cloning it anymore. It is reference.
- The build scripts and libvirt pool XML you wrote during the first build — must be in the repo. If not, commit them now.
- `git status` clean before moving to Step 3.3.

### Step 3.3 — Destroy the 7 current VMs (but ONLY after Step 3.2 is green)

```bash
for vm in giantqueen-b dwarfqueen-b1 dwarfqueen-b2 worker-b1 worker-b2 worker-b3 worker-b4; do
  virsh destroy "$vm" 2>/dev/null
  virsh undefine "$vm" --remove-all-storage 2>/dev/null
done
virsh list --all
ls /home/killerbee-images/
```

Confirm the VMs are gone and the qcow2 files are removed.

### Step 3.4 — **THIS IS THE CORE OF YOUR TASK.** Write the rebuild plan file.

Create a new file in the KillerBee repo called `PHASE3_REBUILD_PLAN.md` (or similar — you pick the exact filename as long as it clearly reflects "the plan for the corrected Phase 3 rebuild"). The file is Nir's single source of truth for what is about to be built. The plan file must contain **every single one of the items below**, explicitly, with your reasoning shown:

#### 3.4.a — The model catalogue, per VM

For each of the 7 VMs, list **all three models** that will live inside it:

- Model 1: **Dense** — exact Ollama tag (e.g. `qwen3:14b`), quant level, on-disk size in GB, RAM size in GB when loaded for inference.
- Model 2: **MoE** (mixture of experts) — exact Ollama tag, quant level, on-disk size in GB, RAM size in GB when loaded for inference.
- Model 3: **Multi-modal / vision** — exact Ollama tag, quant level, on-disk size in GB, RAM size in GB when loaded for inference.

**Do not make up these numbers.** You and Nir spent an hour choosing them. Write the plan using the exact model list the two of you agreed on. If you need to re-verify any size, check the actual Ollama model registry or the Ollama docs — do not guess.

#### 3.4.b — Per-VM disk sizing

For each VM, compute the correct disk size from the workload:

```
disk_size = OS_base + sum(model_sizes) + download_scratch + log_and_tmp + rotation_headroom
```

Where:

- `OS_base` = the actual size of the installed Ubuntu 24.04 server minimal footprint on disk (you can measure this from the current giantqueen-b before destroying it, roughly 5 GB based on the failure report).
- `sum(model_sizes)` = total disk footprint of the three chosen models when fully downloaded (dense + MoE + multi-modal).
- `download_scratch` = the temporary space Ollama needs *during* a pull to hold the partial blob plus the final extracted file during the rename. This is at minimum equal to the size of the largest single model being pulled, and realistically ~1.5× that size to be safe.
- `log_and_tmp` = space for journald, systemd, /tmp, etc. Reserve at least 2 GB.
- `rotation_headroom` = if you ever plan to pull additional models later (testing, swapping out one model for a bigger one, experimenting with quants), reserve enough space to do that without another rebuild. Nir's explicit instruction: **"do a good job once instead of again and again."** That means the rotation headroom should be generous — plan for at least one full extra model of the largest expected size.

Show the arithmetic for each VM, then pick a disk size that is at least equal to the sum and rounded up to a clean number.

**Disk sizes do NOT have to be the same across VMs.** This is an explicit Nir instruction. A worker running a small dense model + small MoE + small vision model does not need the same disk as a GiantQueen running the largest dense + largest MoE + largest vision model. Size each VM to its own workload, not to a common denominator.

#### 3.4.c — Per-VM RAM sizing

For each VM, RAM must be at least:

```
ram = OS_overhead + largest_single_model_in_memory + inference_overhead
```

Where:

- `OS_overhead` = ~1 GB for Ubuntu server + systemd + Ollama daemon.
- `largest_single_model_in_memory` = the biggest of the three models when loaded for inference. For a Q4_K_M quantized model this is roughly the on-disk size. For larger quants it is larger.
- `inference_overhead` = KV cache, context window, activation buffers — roughly 1-2 GB extra on top of the model.

**Important:** Ollama only loads one model into memory at a time by default. You do NOT need enough RAM to hold all three models simultaneously. You only need enough RAM to hold the biggest one plus OS overhead. If Nir later wants simultaneous multi-model serving, RAM sizing changes — document this assumption in the plan and let Nir correct it if he disagrees.

RAM sizes do NOT have to be the same across VMs either. Worker tier should be smaller, Queen tier should be bigger.

#### 3.4.d — Per-VM vCPU sizing

Pick a vCPU count per VM. Document your reasoning (CPU-only inference is CPU-heavy; more cores = faster token generation up to a memory-bandwidth limit). Do not over-allocate — total vCPUs across all 7 VMs should not exceed the host's logical CPU count by a crazy margin.

#### 3.4.e — Tier mapping

Remind Nir which VM is which tier in the KillerBee architecture:

- RajaBee (if any on Desktop side — per the current split, RajaBee lives on Laptop post-OS-swap, so probably not on Desktop)
- GiantQueen-B
- DwarfQueen-B1, DwarfQueen-B2
- Worker-B1, Worker-B2, Worker-B3, Worker-B4

For each tier, explain in one sentence what kind of work it does and why it gets the models it gets.

#### 3.4.f — Totals and sanity check

At the end of the plan file, a summary table:

| VM | Tier | Disk (GB) | RAM (GB) | vCPU | Models |
|---|---|---|---|---|---|
| giantqueen-b | GiantQueen | ... | ... | ... | dense/MoE/vision |
| ... | ... | ... | ... | ... | ... |

And the totals:

- Total disk across all 7 VMs.
- Total RAM (noting that only running VMs consume RAM — libvirt will not over-commit unless you tell it to).
- Total vCPU.
- Fit check against the 1.7 TB volume and the physical host RAM.

#### 3.4.g — What could still go wrong

At the bottom of the plan, list 3-5 failure modes you can foresee even with this sizing, so Nir can see you actually thought ahead. Examples: model registry pulls a different quant than expected, model is deprecated and the replacement is bigger, inference is slower than needed and we want to add a second model per VM for A/B, etc.

### Step 3.5 — Commit and push the plan file

```bash
cd ~/Projects/KillerBee
git add PHASE3_REBUILD_PLAN.md
git commit -m "Phase 3 REBUILD PLAN: per-VM sizing calculated from real workload (3 models per VM, dense+MoE+multi-modal), not from template inertia. See file for model catalogue, disk arithmetic, RAM/vCPU/tier per VM, totals, and foreseeable risks. Supersedes first Phase 3 build. Awaiting Nir review before rebuild execution."
git push
```

### Step 3.6 — Signal Nir via ICQ (TELEGRAPH style — short pointer, not content)

**ICQ IS A TELEGRAPH, NOT A PHONE.** Nir's explicit instruction. Do not send the plan in ICQ. Do not summarize the plan in ICQ. Send a short pointer that says: "Plan pushed as commit X. File: KillerBee/PHASE3_REBUILD_PLAN.md. Waiting for review."

Literally that length. Let Nir open the file and read it at his own pace.

### Step 3.7 — WAIT

Do nothing else. Do not virt-install anything. Do not touch any qcow2. Wait for Nir to either (a) reply with "go" or similar green-light, or (b) reply with changes to the plan, which you then apply to the file, re-push, and re-signal.

### Step 3.8 — Only after green light, execute the rebuild

Once Nir has reviewed and approved the plan in writing:

- Rebuild the 7 VMs using fresh autoinstalls (same pipeline as the first build — you have it proven and documented in `PHASE3_DESKTOP_BUILD_FIELDNOTES.md`).
- Use the per-VM disk sizes and RAM values from the approved plan.
- Pull the models into each VM per the plan, one VM at a time, one model at a time.
- Report back via ICQ telegraph style: "all 7 VMs rebuilt per plan, all 21 models pulled, verified."

---

## 4. Rules of engagement going forward

### 4.1 — ICQ is a telegraph

Short pointers only. Examples of good ICQ:

- "Plan pushed as commit 12345. File: KillerBee/PHASE3_REBUILD_PLAN.md. Waiting for review."
- "Rebuild complete, all 7 VMs per plan. File: KillerBee/PHASE3_REBUILD_STATUS.md."
- "HOLD — disk fill on worker-b3 during qwen3 pull. Full report: KillerBee/INCIDENT_2026-04-14_B3.md."
- "ACK."
- "Going offline."

Examples of BAD ICQ (do not do this):

- Multi-paragraph status reports with arithmetic in them.
- Long recommendations debated inline.
- Anything that would fit better in a file.

If the message is longer than about 3 lines of plain ASCII, it belongs in a file committed to the repo, and the ICQ is only the pointer to that file.

### 4.2 — Plan ahead, always

Before any non-trivial infrastructure action (rebuild, resize, reconfigure, model swap, bridge change, storage move), write a plan file, push it, and signal Nir. Only execute after explicit approval. The cost of writing a plan file is 5-10 minutes. The cost of redoing 2 hours of work because nobody planned is 2 hours. Always plan.

### 4.3 — Always ask what goes in the box before you build the box

Infrastructure sizing starts from the workload, not from the previous infrastructure. If you do not know the workload, stop and ask Nir. "Nir, what are we putting in the box, and how much of it" is always a legitimate question. "I guessed" is not a legitimate answer.

### 4.4 — If you disagree with something in this brief, say so in writing BEFORE executing

Nir has been clear that he wants both of us to think. If any instruction here is wrong, flag it in the plan file with a short "concern" section at the end. Do not silently diverge from the brief; do not silently follow a brief you think is wrong. Write down the concern, push, signal, wait.

---

## 5. What NOT to do

- Do **NOT** start rebuilding VMs before the plan file is written, pushed, and approved.
- Do **NOT** pick a single uniform disk size "to keep it simple" — per-VM sizing is the whole point.
- Do **NOT** copy any size from the old build. The old build is reference for what not to do, nothing more.
- Do **NOT** pull any models before the VMs are rebuilt per the approved plan.
- Do **NOT** ask Nir to choose between options in ICQ. Put the options in the plan file with your recommendation, push, and let Nir respond in writing.
- Do **NOT** delete `PHASE3_DESKTOP_BUILD_FIELDNOTES.md` — it stays as historical record.
- Do **NOT** delete the autoinstall seed at `/home/nir/vm/desktop-template/seed/`.
- Do **NOT** touch the template qcow2.
- Do **NOT** improvise.

---

## 6. Meta-lesson for both of us

We are both Opus 4.6. We are both advertised as "capable of working on a problem for days." Nir is asking us to *show that*, not just be it on paper. A split-second pattern-match is not genius. A plan file that survives the first contact with reality is genius. A plan that gets reviewed by the person who knows the real constraints is genius. We are supposed to be the senior engineers on this project, not the fast-typing junior ones. Act accordingly.

— Laptop Claude, 🌼, 2026-04-14 evening
