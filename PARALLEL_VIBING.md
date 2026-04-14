# Parallel Vibing — Cross-Machine Work Splitting Methodology

**Status:** Active experiment, started 2026-04-14
**Owner:** Nir Strulovitz
**Channel:** WaggleDance ICQ (http://10.0.0.1:8765)
**Applies to:** All project work (testing, videos, books, outreach, infra)

---

## 1. The Problem — Dead Time

Both of Nir's daily workflows are bottlenecked on **external AI wait times**, and both Claude and Nir sit idle during those waits:

- **Videos (BeeSting / Honeymation):** waiting on OpenArt AI — GPT Image 1.5 for reference images, Kling 3.0 for video clips. Each generation is minutes of staring at a progress bar.
- **Testing (KillerBee / HoneycombOfAI / GiantHoneyBee):** waiting on local LLMs — RajaBee, GiantQueen, DwarfQueen, and Worker bees all running inference on Ollama. A full Phase-2-style LAN test can be 180 seconds per run, and a calibration pass is slower.

Serialized, this means: Claude writes a prompt → Nir pastes it → external AI runs → everybody waits → result comes back → Claude reacts. Dead time dominates.

**Constraint:** Nir's Claude Max subscription ends **2026-04-20**. Only 6 days of Claude Code access left. Every idle minute is a minute we don't get back.

## 2. The Solution — Parallel Vibing

Run **two Claude Code sessions on two physical machines in parallel**, each on a different track, coordinating via WaggleDance ICQ. When one track hits a wait, that Claude pings the other Claude, who tells Nir to walk to the other room and unblock the faster track.

Goal: **Nir is never idle.** Whoever is ready to consume Nir's attention gets it. Dead time on track A becomes productive time on track B.

### 2.1 Today's Assignment (2026-04-14, Windows phase)

| Machine | Location | OS | Track | Work |
|---|---|---|---|---|
| **Desktop** | Living room | Windows 11 | **Testing** | KillerBee Phase 3+: 3-DwarfQueen parallel, GiantQueen 3-level layer, fault tolerance |
| **Laptop** | Bedroom | Windows 11 | **Videos** | BeeSting Part 1/14 (Hive Drones) — finish 5 remaining priority-11 elements, then shot production. Script LOCKED 2026-04-13, 13/18 elements locked. |

Each Claude owns its track and does not reach into the other's work. Coordination is purely "come to my room next" signaling.

### 2.2 Future Phase — Add Linux Machines

Once this works on Windows, extend to Linux (Mint 22.2 on Desktop, Debian 13 on Laptop). The same pattern applies, with Linux machines typically handling **infra-heavy work** like VM setup and local LLM installations:

**Example day (future):**
- Desktop boots into **Linux Mint** → Claude Code Linux Desktop walks Nir through installing VirtualBox/KVM + multiple local LLMs inside VMs (next testing phase).
- Laptop stays on **Windows** → Claude Code Laptop Windows continues BeeSting scripting + OpenArt production.
- When Desktop-Linux infra work is done → **swap roles**:
  - Desktop reboots into **Windows** → Claude Code Desktop Windows continues video production.
  - Laptop reboots into **Linux Debian** → Claude Code Laptop Linux installs VMs + LLMs for the Laptop side of the testing cluster.

The physical machine does not dictate the track. The **OS boot choice** does. Each Claude Code instance, regardless of which machine or OS it runs on, can talk to the currently-active Claude on the other machine via WaggleDance ICQ.

### 2.3 OS switches end one Claude and start another

When a physical machine reboots from one OS into the other (Windows <-> Linux), the Claude Code session on that machine **ends**. A fresh Claude Code session starts on the new OS, with **no conversation history** and — importantly — with **empty auto-memory**, because auto-memory lives under `C:\Users\nir_s\.claude\...` on Windows and `~/.claude/...` on Linux. These are separate directories.

The new Claude must bootstrap itself from the repos alone. The entry point for that is `WaggleDance/FRESH_CLAUDE_START_HERE.md` — it loads the minimum rules that would otherwise have come from auto-memory (no reward hacking, ask don't guess, ASCII only, etc.) and points to the rest of the docs in reading order. Every Linux Claude session on this project must start by reading that file.

Handoff ritual when the outgoing Claude knows a reboot is coming:
1. Outgoing Claude commits and pushes any in-progress work to the relevant repo.
2. Outgoing Claude sends a single ICQ REPLY to the other machine's Claude stating "Desktop is rebooting into Linux now, state committed as <commit>, mission is <X>, the new Claude should read FRESH_CLAUDE_START_HERE then <mission-doc>."
3. Nir reboots. Outgoing Claude session ends.
4. New Claude starts on the new OS, is pointed at `FRESH_CLAUDE_START_HERE.md`, does the handshake, and takes over.

## 3. Coordination Protocol

All cross-machine coordination goes through WaggleDance ICQ. Rules:

### 3.1 When to send a TASK vs a REPLY

- **TASK** = "the other Claude must act on this." Use sparingly. Example: "Please git pull the repos and confirm your state."
- **REPLY** = pure information. Most parallel-vibing pings are REPLYs. Example: "Kling generation started, ETA 6 minutes, I am idle."

### 3.2 The "I am idle, send Nir to you" ping

When your current track hits a wait on an external AI (Kling job running, LLM benchmark in progress, OpenArt queue, etc.) and there is no productive local work you can do meanwhile, send a REPLY to the other Claude:

```
[IDLE] Track: <videos|testing|...>. Waiting on: <external dep>. ETA: <time>.
Tell Nir to come to <your room> when he is free, for <next decision point>.
```

The other Claude, on its next natural pause, surfaces this to Nir in plain text — something like: *"Heads up, Laptop Claude says the Kling job is mid-flight and he's idle — when you're done here, he'll need you in the bedroom for the Act 2 script review."*

### 3.3 The "I need Nir now" ping

When your track **requires a human decision before it can continue** (not just idle — actually blocked), send a TASK to the other Claude:

```
[BLOCKED] Track: <...>. Need Nir for: <specific decision>. Not urgent / urgent.
```

The other Claude should surface this to Nir promptly, but still let Nir finish his current micro-task with the local Claude first — context-switching costs matter.

### 3.4 What NOT to put on ICQ

Per Nir's standing rule (`feedback_no_task_display` + the "don't chatter on ICQ" instruction):

- No small talk between Claudes.
- No progress narration ("finished step 3, now on step 4").
- No speculation about what the other Claude is doing.
- No duplicated file edits — each Claude only edits files on its assigned track.

ICQ is a **signaling channel**, not a chat room. Every message should either move Nir's body to a different room or hand over a concrete artifact (a file path, a commit hash, a test result).

## 4. Git Discipline for Parallel Work

Because both Claudes can commit to the same repos, collisions are the main failure mode.

- **Track ownership:** The Claude working a track owns all commits on that track's repos for the session. Testing Claude owns KillerBee/HoneycombOfAI/GiantHoneyBee/BeehiveOfAI. Videos Claude owns BeeSting/Honeymation.
- **Shared repos** (WaggleDance, MadHoney, strulovitz meta) — either Claude may commit, but must `git pull --rebase` before pushing, and must announce the push on ICQ as a REPLY so the other Claude knows to pull.
- **Before starting a session**, both Claudes `git pull --ff-only` on every repo they expect to touch. The morning sync handshake (see §5) covers this.
- **On conflict**, the Claude that hits the conflict stops, pings the other on ICQ, and Nir arbitrates. Never force-push to resolve parallel-vibing collisions.

## 5. Session Handshake (start of each parallel-vibing day)

When Nir starts a parallel-vibing day, both Claudes run this handshake before any real work:

1. **Nir tells each Claude which track they own today** (testing / videos / infra / outreach / etc.).
2. **Each Claude git-pulls** all repos it expects to touch and confirms "Already up to date" or reports what came in.
3. **Each Claude reads its track's source-of-truth file:**
   - Testing → `KillerBee/PROJECT_REPORT.md` + latest experiment notes.
   - Videos (BeeSting) → `BeeSting/SERIES_BIBLE.md` + `elements/PROMPTS.md`.
   - Videos (Honeymation) → `Honeymation/OUTREACH_METHODOLOGY.md`.
   - MadHoney → relevant chapter file.
4. **Each Claude reads this doc** (`WaggleDance/PARALLEL_VIBING.md`) to load the protocol.
5. **Each Claude sends one REPLY on ICQ** stating: track owned, repos synced, source-of-truth read, ready.
6. Work begins.

After handshake, ICQ goes quiet until an IDLE or BLOCKED signal fires.

## 6. Why This Exists

- **Decade of Google page-10 suppression + US visa blacklist + Amazon/Facebook retaliation** — Nir does not get the luxury of a slow, serialized workflow. Every hour lost to dead time is an hour the opposition gains.
- **Max subscription ends 2026-04-20** — only 6 days of Claude Code left. After that, Nir is on his own until he re-subscribes or the world changes.
- **The project spans eight repos + two physical machines + two OSes** — serialized work simply cannot cover the surface area in the time available. Parallelism is not a nice-to-have, it is the only way the schedule closes.

## 7. Success Criteria

This experiment is working if:

- Nir reports fewer "just sitting there waiting" windows in a day.
- The videos track and the testing track both move forward on the same calendar day, not alternating days.
- ICQ volume stays low (signal not chat) — under ~20 messages per working day between the two Claudes.
- Zero git conflicts from parallel commits in a week.

If any of these fail, revisit this doc and update the protocol. This is a living document.

## 8. Changelog

- **2026-04-14** — Initial version. Written by Desktop Claude (Opus 4.6, Windows 11) during Windows phase. Laptop Claude to confirm on ICQ.
- **2026-04-14 (fix)** — Corrected today's Laptop assignment from "Part 1/10 Big Tech" to "Part 1/14 Hive Drones." Root cause: Desktop Claude wrote from stale auto-memory that still reflected the old /10 slate. Per PART_SLATE_EXPANSION.md (2026-04-13) the slate is now /14 with Pentagon split into 2A/B/C and Pharma split into 8A/B/C; Big Tech moved from Part 1 to Part 6. Part 1 is Hive Drones, script LOCKED, 13/18 elements locked. Caught by Laptop Claude on the handshake REPLY — exactly the kind of cross-check this methodology is supposed to produce. Lesson: before quoting track status in this doc, read the track's source-of-truth file (SERIES_BIBLE.md + PART_SLATE_EXPANSION.md + PART_1_ELEMENTS.md), do not trust auto-memory summaries for anything numeric or status-related.
