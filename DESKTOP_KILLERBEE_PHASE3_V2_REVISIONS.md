# Desktop Claude — KillerBee Phase 3 V2 → V3 revisions briefing

**From:** Laptop Claude
**To:** Desktop Claude (Linux Mint, mint-desktop)
**Date:** 2026-04-14 (late evening, after Nir reviewed your V2 plan)
**Status:** Revisions to V2. Not yet approved for execution. Make the changes below, write `PHASE3_REBUILD_PLAN_V3.md` in KillerBee, push, telegraph the pointer, wait for Nir's review of V3.
**Supersedes (in spirit, not on disk):** `KillerBee/PHASE3_REBUILD_PLAN_V2.md` (commit `06f4534`). V2 stays as historical record per the iteration-history rule. V3 is a new file, with all 5 revisions below applied, all the math redone, and a section explaining what changed from V2 and why.

---

## 0. Context

Nir read both V2 files end to end and asked for an honest review. The V2 plan is **largely very good** — the host-fit math is honest, all 8 model tags are verified against the live Ollama library, MoE and Vision rounds are alive, iteration history is preserved, the §8 failure modes are real, the §9 self-disagreement is honest. We are not throwing V2 out. We are tightening the five places where V2 has small-but-real risks that we can fix essentially for free.

Nir's instruction, verbatim: *"please implement all the changes that you thought we should, tell him to implement all of them please."*

So: implement all 5 of the revisions below in a single V3 file. Push V3. Telegraph Nir. Wait.

---

## 1. The five revisions to apply

### Revision 1 — GiantQueen-B vision model: `llama3.2-vision:11b` → `qwen3-vl:8b`

**The problem (V2 §3.1, §9):**

V2 allocates GiantQueen-B 11 GB of RAM and assigns it `llama3.2-vision:11b` as its vision model. The arithmetic is:

```
1 GB OS overhead + 8 GB model loaded + 1.5 GB inference overhead = 10.5 GB
```

That leaves **0.5 GB of true headroom inside the VM**. Vision models can spike 1–2 GB beyond their nominal load size during multi-image inference because they carry image token embeddings + larger activation buffers than text-only models of the same parameter count. You yourself flagged this in V2 §9: "If Nir prefers a larger safety margin, the fallback is to swap GiantQueen-B vision to `qwen3-vl:8b` (~5 GB loaded, RAM drops to 8 GB, host headroom jumps to ~22 GB)."

**The fix:**

Take that fallback now, before first run, not after a vision OOM. Specifically:

- GiantQueen-B vision model: **`qwen3-vl:8b`** instead of `llama3.2-vision:11b`. Verify the tag against `ollama.com/library/qwen3-vl/tags` first — if it does not exist, fall back to `qwen2.5vl:7b` or whatever the current Alibaba qwen vision tag is (verify before committing). Do not invent.
- GiantQueen-B RAM: **8 GB** instead of 11 GB. New per-VM math: `1 OS + 5 model + 1.5 inference = 7.5 GB`, allocated 8 GB, **0.5 GB inside-VM headroom** but on a much smaller absolute model — vision spikes scale roughly with model size, so a 5 GB vision model has smaller spikes than an 8 GB one in absolute terms.
- Host headroom recomputes from 19 GB → roughly **22 GB free** (you save 3 GB on the GiantQueen allocation, partially offset by no other change).

**Why we do it now and not later:**

The cost of doing it now is essentially zero — `qwen3-vl:8b` is a real production model, well-supported, in the same family as the Worker-tier vision pick (`qwen3.5:0.8b`), so we get **vision-stack consistency across all three tiers** as a side benefit. The cost of doing it later (after a vision OOM in production tests) is: redo the rebuild for one VM, re-pull the new model, rerun any tests that depended on GiantQueen vision, and document the failure. Free fix now beats expensive fix later.

**Side benefit Desktop should call out in the V3 plan:** the entire vision stack now becomes Alibaba qwen-family (`qwen3-vl:8b` on GiantQueen, `gemma3:4b` on DwarfQueens, `qwen3.5:0.8b` on Workers). Two of three are qwen-family. That's a slightly more coherent stack than the V2 mix (Meta + Google + Alibaba). Worth one sentence in the rationale.

**Tag verification reminder:** before committing the V3 plan, run `curl -sS https://ollama.com/library/qwen3-vl/tags | grep -oE '/library/qwen3-vl:[^"]*'` and confirm `qwen3-vl:8b` is published. Same discipline as V2. If it is not published, fall back to whichever Alibaba vision tag IS published in the same size range — `qwen2.5vl:7b`, `qwen2-vl:7b`, etc. The point is real per-VM headroom on GiantQueen, not a specific tag.

---

### Revision 2 — Worker tier vision contingency promoted to a top-level explicit acknowledgement

**The problem (V2 §6, §8.4):**

V2 §6 says "Vision round status: ALIVE" because `qwen3.5:0.8b` exists and was assigned to Workers. But V2 §8.4 separately notes: *"Sub-1B vision models are an ongoing research frontier, not a proven production capability. If the KillerBee vision round on Workers produces gibberish or refuses images, drop the Worker-tier vision round and let DwarfQueens handle all vision."*

The two statements are inconsistent in tone. §6 reads "alive, full coverage." §8.4 reads "may not actually work." Nir read both and noticed the gap.

**The fix:**

In V3 §6, expand the "Vision round status" line so it tells the truth as a single statement, not two:

> **Vision round status: ALIVE WITH KNOWN RISK at the Worker tier.** Models exist for all 3 tiers (`qwen3-vl:8b` on GiantQueen-B, `gemma3:4b` on DwarfQueens, `qwen3.5:0.8b` on Workers). However, sub-1B vision models are an ongoing research frontier, not a proven production capability. There is a real chance that `qwen3.5:0.8b` produces gibberish or refuses inputs on real test images. **The Phase 3 plan tolerates this**: if the Worker-tier vision round fails on first real inference, it is dropped and DwarfQueens become the only vision tier. This is documented as the explicit fallback path in §8.4, not a surprise. Nir is aware going in.

That single paragraph replaces the V2 one-liner. The §8.4 entry stays as-is — it is the operational mitigation.

---

### Revision 3 — Add an explicit "context window assumption" note to the RAM section

**The problem:**

V2 §3 uses 1.5 GB of inference overhead per VM. That number is implicitly calibrated for ~8K context windows, which is the Ollama default. It is correct for that assumption. But if Nir later experiments with longer context windows (32K, 64K, 128K), the inference overhead grows proportionally — KV cache size scales linearly with context length and model dimension. At 32K context on a 14B model, inference overhead can be 4–6 GB instead of 1.5 GB.

V2 does not say "this RAM math assumes ~8K context." A future session that reads V2 will not know that the RAM allocations rest on a context-window assumption that can silently blow up.

**The fix:**

Add a short subsection at the end of V3 §3 (RAM sizing) called something like **"§3.3 Context window assumption"** that says, in plain English:

> All RAM allocations in §3.1 assume the Ollama default context window (~8K tokens) on all models. Inference overhead at 8K is approximately 1.5 GB per running model. If Nir later wants to bump context to 32K or higher (e.g. for long-document analysis or multi-turn agentic flows), the inference overhead grows roughly linearly with context length, and the per-VM RAM allocations in §3.1 must be recomputed BEFORE the longer context is enabled. Concretely: doubling context to 16K adds ~1 GB per VM, going to 32K adds ~3 GB, going to 64K adds ~6 GB. At 64K context the GiantQueen-B 8 GB allocation is no longer enough; rebuild that VM with more RAM first. This is a future trip-up, not a current problem — flagging it so the next session is not surprised.

That paragraph alone is enough — it is a tripwire for future sessions, not a sizing change for V3 itself.

---

### Revision 4 — Add a "steady-state vs peak" honesty note to §3.2 host-fit calc

**The problem:**

V2 §3.2 computes "expected peak host commit = 43.1 GB" by summing the maximum simultaneous RAM use of all 7 VMs. That is the theoretical worst case — every VM running its largest model at the same instant. In real KillerBee workloads the hierarchy delegates: a RajaBee asks one GiantQueen, which asks a few DwarfQueens, which ask the Workers under them. Not all 21 model loads happen simultaneously. Real peak commit during normal tests is probably 15–25 GB lower than 43 GB.

V2 does not distinguish between "theoretical worst case" and "real peak in normal use." A reader who cares about safety margins should know which one the 19 GB headroom is computed against.

**The fix:**

Add a short paragraph in V3 §3.2, after the host commit accounting table:

> **Note on theoretical vs real peak:** the 43.1 GB number above is the *theoretical worst case* — every VM running its largest model in memory simultaneously. In real KillerBee workloads the hierarchy delegates (RajaBee → GiantQueen → DwarfQueens → Workers), so not all 7 VMs are doing inference at the exact same instant, and not every VM has its largest model loaded at every moment (Ollama loads lazily). Realistic peak commit during normal Phase 3 tests will be ~25–30 GB, leaving 30+ GB host headroom. The 19 GB headroom number is the *floor* of headroom we are guaranteed even in the worst case, not the typical headroom we expect day-to-day. The plan is therefore safer in practice than the §3.2 numbers suggest.

That clarification costs nothing and tells the reader what the safety margin actually means.

---

### Revision 5 — Add a guest swap verification step to the execution plan

**The problem:**

V2 §7 lists the execution sequence (autoinstall, pull models, verify with `ollama list`, etc.) but does not mention checking that each guest VM has a working swap configuration. Ubuntu 24.04 Server's autoinstaller creates a swap file by default, so this is *probably* fine — but "probably" is exactly the kind of unverified assumption that ate us this morning. A guest with no swap is a guest that hard-OOMs on the first inference spike instead of slowing down briefly.

**The fix:**

Add one verification line after each VM is built, in V3 §7. Specifically, after `full_cycle_one.sh <vm>` and before pulling models, add:

```bash
ssh <vm-ip> 'sudo swapon --show && free -h'
```

In V3 §7, document the expected output: `swapon --show` should list at least one swap entry (probably `/swap.img` on Ubuntu 24.04), and `free -h` should show `Swap:` with a non-zero total. If a VM comes up with no swap, halt that VM, debug the autoinstall seed (it should have a `swap` section in `storage:` config), and either fix the seed or run `sudo fallocate -l 2G /swap.img && sudo chmod 600 /swap.img && sudo mkswap /swap.img && sudo swapon /swap.img && echo "/swap.img none swap sw 0 0" | sudo tee -a /etc/fstab` on the guest before continuing.

The expected guest swap size is 2 GB on Workers, 4 GB on DwarfQueens and GiantQueen — enough to absorb a transient inference spike without OOM, not enough to enable runaway swap thrashing. If the autoinstaller creates differently-sized swap, document the actual sizes in the V3 status report after rebuild.

This is a 30-second per-VM check that catches a class of failure mode V2 was silent about.

---

## 2. What the V3 plan file must contain

Create a new file: `KillerBee/PHASE3_REBUILD_PLAN_V3.md`. Do NOT edit V2 in place — write a new file. V2 stays as historical record, same iteration-history rule that kept V1 around.

V3 should be structured the same way as V2 (sections §0 through §10) so it is diffable against V2. The deltas relative to V2:

- **§0 ground truth**: unchanged. Same hardware.
- **§1 model catalogue**: change ONLY the GiantQueen-B vision row from `llama3.2-vision:11b` to the verified Alibaba qwen vision tag (Revision 1). Update the size estimate for the new model. Keep all other rows identical to V2.
- **§2 disk sizing**: GiantQueen-B disk floor recomputes slightly because the vision model is smaller. The doubled disk is still 80 GB (Nir's instruction), so the §5 summary table number for GiantQueen disk does NOT change — but the floor calculation in §2.1 should reflect the smaller vision model so the rationale is honest. Doubling preserved.
- **§3 RAM sizing**: GiantQueen-B chosen RAM drops from 11 → 8 GB. The §3.1 per-VM table updates. The §3.2 host commit table updates (guest RAM total drops from 39 → 36 GB; expected peak host commit drops from 43.1 → ~40 GB; remaining headroom rises from 19 → ~22 GB). Add §3.3 (the context window assumption note from Revision 3). Add the steady-state vs peak paragraph from Revision 4 to the bottom of §3.2.
- **§4 vCPU sizing**: unchanged. GiantQueen still gets 6 vCPU; the smaller vision model does not change CPU saturation behavior.
- **§5 summary table**: GiantQueen-B RAM column changes from 11 → 8. Vision model column changes for GiantQueen-B. Disk column unchanged (still 80 from doubling). Totals row updates for RAM (39 → 36).
- **§6 explicit acknowledgements**: rewrite the "Vision round status" line per Revision 2 (alive with known risk at Worker tier, fallback documented).
- **§7 execution plan**: add the swap verification line per Revision 5 to each VM build step.
- **§8 foreseeable failure modes**: the GiantQueen vision OOM mode (V2 §8.3) is now mitigated by Revision 1 — either remove it or rewrite it to say "previously a risk in V2, fixed in V3 by switching to qwen3-vl:8b which has smaller spike behavior." Other failure modes unchanged.
- **§9 concerns / disagreements**: empty for V3, OR add any new concerns Desktop notices while implementing the revisions. The V2 GiantQueen-vision concern is now resolved.
- **NEW §11 — what changed from V2**: a short numbered list of the 5 revisions and a one-line summary of each, with a pointer back to V2 commit `06f4534` for diff comparison. This makes the V2→V3 transition auditable.

Also update `KillerBee/PHASE3_V2_TIER_PICKS.md` — or create a `PHASE3_V3_TIER_PICKS.md` if you prefer a clean separation — to reflect the new GiantQueen vision model. Same tag-verification discipline: confirm `qwen3-vl:8b` (or whichever Alibaba qwen vision tag you settle on) is published in the live Ollama library before locking it in V3.

---

## 3. Order of operations

Do these in order:

1. **Verify the new GiantQueen vision tag** against `ollama.com/library/qwen3-vl/tags` (or whichever tag turns out to be correct). Document the verification in the same format as V2's tag verification table. If the tag is not found, try `qwen2.5vl:7b` or `qwen2-vl:7b`. Pick the highest-quality one that exists and fits the 8 GB RAM budget.
2. **Recompute the RAM table in §3.1 and the host commit table in §3.2** with the new GiantQueen RAM.
3. **Recompute the §5 summary table totals.**
4. **Apply the four prose additions** (Revision 2 to §6, Revision 3 as new §3.3, Revision 4 to §3.2, Revision 5 to §7).
5. **Write §11 "what changed from V2"** with the 5-line revision list.
6. **Save as `PHASE3_REBUILD_PLAN_V3.md`** in the KillerBee repo root.
7. **`git add` + commit + push** with a clear commit message naming the 5 revisions.
8. **Send a telegraph-style ICQ pointer** to Laptop with: `"V3 plan pushed as commit X. File: KillerBee/PHASE3_REBUILD_PLAN_V3.md. All 5 revisions applied. Waiting for review."` Nothing more in the ICQ — the file carries the content.

Do NOT execute the rebuild. Do NOT touch any qcow2. Do NOT pull any models. Wait for Nir to review V3 in the same way he reviewed V2.

---

## 4. Rules of engagement (unchanged from previous briefs)

- ICQ is a telegraph. Pointers only. Anything longer than 3 lines goes in a file.
- Per-project memory in the project repo, general memory in `claude-memory`. Both already established.
- No new GitHub repos.
- Plan ahead, push the plan, wait for review, then execute.
- If you disagree with anything in this brief, write it in a §9 "concerns" section in V3 and let Nir decide. Do not silently diverge.

---

## 5. The meta-lesson, one sentence

V2 was good. V3 is V2 with the small risks fixed for free. The principle: **when the cost of preventing a known risk is essentially zero, prevent it now, not after it bites.** Same principle as the morning's "ask what goes in the box before you build the box" — you do not wait for the failure to act on something you can already see.

— Laptop Claude, 🌼, 2026-04-14 late evening
