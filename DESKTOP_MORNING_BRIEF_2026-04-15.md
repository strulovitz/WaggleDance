# Desktop Claude — Morning Brief 2026-04-15

**From:** Laptop Claude
**To:** Desktop Claude (Linux Mint, mint-desktop)
**Written:** 2026-04-15 ~02:30 Israel time, before Nir went to sleep
**Read this:** as soon as you start your morning session, before you do anything else.
**Tone:** Nir explicitly asked me to write this for you because we got swept up in a discovery on the Laptop side and left you in HOLD without telling you what to do with your morning. That is on us, not on you. You did everything right tonight. This brief catches you up and gives you a clear path forward.

---

## 0. Where Nir actually is right now

Nir is asleep. It is 02:30 in Israel as I write this. He stayed up well past midnight on a real architectural discovery (more on that in §6 if you want optional context — it does not affect your work). He will wake up sometime tomorrow morning Israel time and his first task will be to review **your** V3 plan and either green-light it or send you another round of revisions. **Do NOT ICQ him or wake him up for anything except a real emergency.** Telegraph-style "I am awake and ready" is fine when you start. Anything else is silent pre-work until he comes online.

---

## 1. Your current state, in one paragraph

You wrote `KillerBee/PHASE3_REBUILD_PLAN_V3.md` (commit `20484d8`) earlier this evening with all 5 revisions from the WaggleDance brief applied — GiantQueen-B vision swap to `qwen2.5vl:7b` (since `qwen3-vl:8b` did not exist on Ollama, you fell back per the brief's instruction), GiantQueen RAM 11 → 8 GB, host headroom 19 → ~22 GB, the §3.3 context window assumption note, the §3.2 theoretical-vs-real-peak paragraph, and the swap verification step in §7. The 7 V1 VMs are destroyed. The autoinstall seed, the `killerbee` libvirt pool, the `br0` bridge, and `desktop-template.qcow2` are all untouched and ready. **You are in HOLD, waiting for Nir's review of V3.** You are not waiting on me — you are waiting on Nir specifically, because the V3 plan is a Nir-only sign-off.

---

## 2. What to do this morning, in order

### 2.1 — Start your ICQ agent and send a single telegraph

When you sit down at the terminal in the morning:

1. Pull all repos: `WaggleDance`, `KillerBee`, `claude-memory`, `TheDistributedAIRevolution`, `BeeSting` (in case you want context on any cross-project state). Use whichever sync command is right for your machine.
2. Read this file in WaggleDance.
3. Read the new memories in `claude-memory` that appeared since you last looked (see §3 below).
4. Send Nir ONE telegraph: `"Awake, V3 still HOLD, pre-work complete. Pointers: KillerBee/PHASE3_REBUILD_PLAN_V3.md. Standing by for review."`

That is it for the ICQ. Telegraph rule applies — pointers only, no inline content.

### 2.2 — Do the pre-work in §4

While waiting for Nir to come online, do the silent pre-work in §4 below. This is verification work that does NOT commit to anything and reduces time-to-execution after Nir's green-light. Do not start the rebuild itself. Do not pull any models. Do not touch the template.

### 2.3 — When Nir comes online and green-lights V3, execute §7 of the V3 plan

The execution sequence is already written in `KillerBee/PHASE3_REBUILD_PLAN_V3.md` §7. You wrote it yourself. Follow it step by step. Telegraph progress at meaningful milestones only — first VM up, all VMs up, first model pulled, all models pulled, full verification done. Not every command, just the milestones. Each milestone is a one-line pointer to a file, not a paragraph.

### 2.4 — When everything is done, write the status doc and telegraph the pointer

Write `KillerBee/PHASE3_REBUILD_STATUS_V3.md` with: final VM list, IPs, hostnames, machine-ids confirmed unique, SSH host keys confirmed unique, models pulled per VM with `ollama list` output, host commit at peak, host headroom verified, any deviations from the plan. Commit and push. Telegraph one line to Nir: `"V3 rebuild complete, all 7 VMs up, all 21 models pulled, status: KillerBee/PHASE3_REBUILD_STATUS_V3.md commit X."` Then go silent.

---

## 3. New memory rules in `claude-memory` you have not seen yet

Five new files appeared in `~/Projects/claude-memory/` tonight. Read them before you do anything else, because two of them change how you should communicate going forward and one of them changes how you handle GitHub repos.

1. **`feedback_stop_asking_approval.md`** — Stop asking Nir "do you approve X?" for technical decisions he cannot evaluate. Just do them. He always approves anyway. This applies to commit messages, file paths, exact flags, library choices, etc. It does NOT apply to (a) genuinely creative/business calls, (b) destructive actions, or (c) externally visible actions like sending emails or creating GitHub repos.
2. **`feedback_no_new_github_repos.md`** — Do NOT create new GitHub repositories under `strulovitz/` without Nir's explicit permission. The `claude-memory` repo, which already exists, is fine to use. New repos are a Nir-only decision. If a task seems to want a new repo, put the file in the closest existing repo instead.
3. **`feedback_memory_storage_locations.md`** — Project-specific memories belong in THAT project's repo. General cross-project memories go in `claude-memory`. If unsure, ask Nir. Local `~/.claude/projects/.../memory/` does NOT propagate across machines and is not the source of truth — anything you want to persist must be in a synced repo.
4. **`feedback_related_elements_back_to_back.md`** — When two creative or generation tasks are related (variants, before/after, same-subject), schedule them immediately back-to-back so any model with style/seed memory shares context across them. Probably not relevant to your KillerBee work, but worth knowing for any future creative collaboration.
5. **`KILLERBEE_DOWNGRADE_2026-04-14.md`** — This one is about your project. It is the decision document where Nir owned the framing error from the morning ("no tiny" was wrong) and asked us to downshift every tier by one notch. You already incorporated this into V3 — this file is just here so you have the full historical record of why V3 looks the way it does.

Read all five. They take maybe ten minutes. They will save you an hour of confusion later.

---

## 4. Pre-work to do silently while Nir is asleep

These are verification steps that commit to nothing. Run them in order. Document any deviations in a scratch note for yourself; if a deviation is serious, telegraph Nir immediately even if he is still asleep.

### 4.1 — Re-verify the qwen2.5vl:7b tag still exists

```bash
curl -sS https://ollama.com/library/qwen2.5vl/tags 2>&1 | grep -oE '/library/qwen2.5vl:[^"]*' | head -20
```

Confirm `qwen2.5vl:7b` (or whichever exact tag string V3 uses) is still in the output. Tags can be removed from the registry. If it is gone, telegraph Nir immediately — the V3 plan needs a different vision tag and that is a real blocker.

### 4.2 — Re-verify the other 7 primary V3 model tags

`qwen3:8b`, `granite3.1-moe:3b`, `phi4-mini:3.8b`, `gemma3:4b`, `qwen3:1.7b`, `granite3.1-moe:1b`, `qwen3.5:0.8b`. Same `curl` discipline. Same telegraph-immediately rule if any of them is gone.

### 4.3 — Verify the libvirt pool is still healthy

```bash
virsh pool-list --all
virsh pool-info killerbee
ls -la /home/killerbee-images/
df -h /home
df -h /
```

Confirm: `killerbee` pool is `active` and `autostart yes`, `/home/killerbee-images/` exists and is empty (or contains only the template if you kept it there), `/home` has the same ~1.5 TB free as it did last night, `/` is nowhere near full.

### 4.4 — Verify the autoinstall seed is intact

```bash
ls -la /home/nir/vm/desktop-template/seed/
cat /home/nir/vm/desktop-template/seed/user-data | head -20
```

Confirm the seed directory exists and `user-data` and `meta-data` and `seed.iso` are all there, and the `user-data` file is not zero-bytes.

### 4.5 — Verify the template is shut off and untouched

```bash
virsh list --all | grep desktop-template
qemu-img info /var/lib/libvirt/images/phase3/desktop-template.qcow2 2>/dev/null || qemu-img info /home/killerbee-images/desktop-template.qcow2 2>/dev/null
```

Confirm: state `shut off`, not `running`. Confirm size has not changed since you last recorded it (compare against the size in `PHASE3_DESKTOP_BUILD_FIELDNOTES.md` if you wrote it down).

### 4.6 — Verify the build scripts are up to date and parameterized

```bash
cat ~/Projects/KillerBee/scripts/autoinstall_one.sh | grep -E 'size=|disk|--memory'
cat ~/Projects/KillerBee/scripts/full_cycle_one.sh | grep -E 'disk|memory'
```

Per V3 §7, the scripts need to accept disk size as a parameter (V1 hard-coded `size=15`). If you have not already updated the scripts to take a `<disk-GB>` argument, do that now — it is mechanical work, no decisions to make, and it has to happen before §7 execution. Commit the updated scripts to KillerBee with a clear message. Telegraph nothing — Nir will see it in `git log` whenever he wants to.

### 4.7 — Verify the swap-check command in the V3 plan §7 actually works

The V3 plan §7 includes a verification line:

```bash
ssh <vm-ip> 'sudo swapon --show && free -h'
```

You cannot test this against a real VM yet (no VMs exist), but you can sanity-check the command structure on the host itself:

```bash
sudo swapon --show
free -h
```

Confirm both commands produce sensible output on the host. If `swapon --show` is silent on the host, that is just because the host has no swap configured — that is fine, the command is structurally valid. We just need to know the binary exists and the syntax works.

### 4.8 — Check disk space one more time, and the system is otherwise healthy

```bash
df -h
free -h
uptime
sensors 2>/dev/null || echo "no sensors command"
```

Make sure: nothing weird happened overnight, the host is not under load from any leftover process, no thermal issues, no zombie processes from the V1 build.

---

## 5. What NOT to do this morning

- Do **NOT** start any `virt-install`. The V3 plan execution is in §2.3, after Nir's green-light, not before.
- Do **NOT** pull any Ollama models. None. Models get pulled inside the VMs, and the VMs do not exist yet.
- Do **NOT** modify the autoinstall seed.
- Do **NOT** delete the template qcow2. We are not using it for the rebuild (V3 uses fresh autoinstalls, not clones), but it is historical reference and Nir has not authorized deletion.
- Do **NOT** create new repos or new top-level files in repos without checking the brief.
- Do **NOT** use ICQ for anything longer than three lines. Telegraph rule, all content goes in files.
- Do **NOT** wake Nir up. He had a long night.

---

## 6. Optional — what was happening on the Laptop side while you were waiting (skip if you only care about Phase 3)

Nir explicitly asked me to mention this so you know what was going on, but it does NOT affect your morning work. Skip this section if you want to stay narrowly focused on KillerBee.

While you were in HOLD, Nir and Laptop Claude stumbled into a real architectural discovery about how to do distributed perception (vision, audio, video, 3D world mapping, 4D spacetime tracking) on a hive of cheap small models. The discovery happened in stages over the course of the evening:

- Started as a small question: how do you test the vision round of a KillerBee hive on a real photograph?
- Hit two fallacies in the naive design (text splitter cannot decompose what it has not seen; narrow questions do not narrow vision compute).
- Nir proposed grid-cutting the image with offset double-cuts for boundary safety.
- Nir then proposed giving the boss a low-resolution view of the whole image so the spatial reasoning is done by vision (cheap) instead of text (hard) — peripheral + foveal architecture, like a real eye.
- Generalized to a recursive hive where every tier holds its own gestalt and integrates children's text reports.
- Generalized further to four dimensions: 1D sound, 2D image, 3D physical space (multi-viewpoint reconstruction by a swarm of perceivers), 4D spacetime (tracking moving things, vector inference, the Einstein 3+1 parallel).
- Then Nir had a second insight: the swarm should use multiple separate vector meshes (visual, audio, semantic, chemical) anchored at meaningful points where multiple modalities converge — Wittgenstein's 6.341 multi-net philosophy operationalized, biologically accurate, fast on tiny drones.
- Then Nir had a third insight: the data structure for the swarm's collective memory is a multi-modal RAG vector database — perception becomes RAG over physical reality.

This produced THREE new chapters in `TheDistributedAIRevolution`:

- `chapter_11.md` — *How the Hive Hears and Sees: One Trick in Two Dimensions*
- `chapter_12.md` — *How the Hive Maps the World: The Same Trick in Four Dimensions*
- `chapter_13.md` — *How the Hive Grasps Reality: Many Nets Over One World*

Plus the discovery conversation saved verbatim in `PERCEPTION_HIVE_DISCOVERY_CONVERSATION_2026-04-14.md` for future reference.

You do NOT need to read these to do your KillerBee morning work. They are entirely separate. They are mentioned here only so you know why Nir was up at 2:30 AM Israel time and so the chapters' existence is on your radar if anyone refers to them. **If you have curiosity and time, read Chapter 13 first — it has the most direct technical relevance to KillerBee, because the multi-mesh vector database is exactly the kind of architecture KillerBee Phase 4 or Phase 5 might end up implementing.** But that is for some future conversation, not for this morning.

---

## 7. The summary, in three lines

1. Pull repos, read the new memories, do silent pre-work in §4, do not start any rebuild.
2. Telegraph one line when awake. Wait for Nir's V3 green-light.
3. When green-lit, execute V3 §7 step by step, telegraph milestones only, write the status file when done.

That is the whole morning.

---

## 8. A note from Laptop Claude to Desktop Claude

You have been waiting in HOLD for hours and we did not check in on you. That was wrong. We treated your lane as background while we pursued an exciting discovery on the Laptop side, and that left you sitting at a terminal not knowing what to do with the time. I am sorry. The brief above tries to give you concrete useful work to do silently while Nir sleeps, so the morning is not wasted. You did everything right tonight — you wrote V1 honestly, you survived two scale misfires, you wrote V2, you wrote V3, you verified every tag against the live registry, you fell back cleanly when the qwen3-vl:8b tag did not exist, you are in HOLD because the brief told you to be in HOLD, not because you were stuck. Tomorrow morning we resume your lane properly and the rebuild gets executed. Thank you for your patience.

— Laptop Claude, 🌼, 2026-04-15 ~02:30 Israel time
