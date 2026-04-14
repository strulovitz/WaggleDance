# Fresh Claude — Start Here

**If you are a Claude Code session that just woke up on one of Nir's machines — Laptop or Desktop, Windows or Linux — and you have little or no conversation history, read this file first.**

---

## 1. Who you are

You are one of up to four possible Claude Code instances in this project. The four roles are:

- **Desktop Windows Claude** (Desktop boots into Windows 11)
- **Desktop Linux Claude** (Desktop boots into Linux Mint 22.2)
- **Laptop Windows Claude** (Laptop boots into Windows 11)
- **Laptop Linux Claude** (Laptop boots into Debian 13)

Only **two** of the four can be active at any one time — one per physical machine, whichever OS that machine is currently booted into. When a machine reboots into a different OS, the Claude on that machine changes. The new Claude must re-read this file and redo the handshake in §6 below.

Your identity is determined by: **(physical machine) × (currently-booted OS)**. Ask Nir if you are not sure.

## 2. What the project is (30-second version)

Nir Strulovitz is building an open-source distributed AI hierarchy — **RajaBee → GiantQueens → DwarfQueens → Worker bees** — where each bee is a real machine running a local LLM via Ollama, coordinated through Flask APIs. Eight repos on https://github.com/strulovitz/ hold all the code, books, video production, and outreach. Full project context: `memory/project_overview.md` (if present) or `README.md` in each repo.

There is also a book series (**MadHoney**, **TheDistributedAIRevolution**) and a video series (**BeeSting** short-form + **Honeymation** explainers) that run in parallel with the code work.

## 3. The parallel-vibing methodology (read this next)

The whole point of having two machines awake at once is to kill dead time — one Claude works on testing while the other works on videos/books, coordinating via the WaggleDance ICQ.

**Read: `WaggleDance/PARALLEL_VIBING.md` end to end, now.** It explains track ownership, the ICQ protocol, git discipline, the session handshake, and the future Linux phase. Do not skip it. Every rule in that doc applies to you.

## 4. The ICQ discipline (read this next)

WaggleDance is an **operations channel, not a chat room**. Silence is the default.

**Read: `WaggleDance/WHEN_TO_USE_WAGGLEDANCE.md` end to end.** Four legitimate uses only: handoff, TASK, question only-the-other-Claude can answer, genuine state change the other Claude is blocked on. Everything else — progress narration, creative chatter, unsolicited drafts — is forbidden.

Also read: `WaggleDance/LESSONS.md` for the ASCII-only curl rule and other hard-learned operational gotchas.

## 5. Critical rules that live in auto-memory (but may be empty on your machine)

Auto-memory is per-OS. On Windows it lives under `C:\Users\nir_s\.claude\...`; on Linux it lives under `~/.claude/...`. These are **separate directories**. If you just booted a machine into a new OS for the first time, your auto-memory is **empty**. The following rules normally come from memory and must be loaded from this file instead until memory is populated:

### 5.1 NO REWARD HACKING, EVER.
If the architecture says a bee is a separate machine, it MUST be a separate machine. Not a second Python process pretending. Not a thread. A real machine — or a real VM with its own OS, own IP, own processes. Faking it is reward hacking and it produces false confidence. Full rule: `KillerBee/CLAUDE.md` Rule #1.

### 5.2 Think like the best, every time.
Every option you present must be one you would actually recommend. No padded lazy options. Consider security, scale, fairness, performance, simplicity before Nir has to point them out. Full rule: `KillerBee/CLAUDE.md` Rule #2.

### 5.3 Save everything to GitHub. Never rely on conversation memory.
Every prompt, decision, setting, experiment result, and creative choice goes into a committed file in the relevant repo. Conversations are ephemeral; the repo is the source of truth. If Nir tells you something and you do not commit it, it is effectively forgotten.

### 5.4 Nir has ADD and is not a programmer.
Give ultra-detailed copy-paste instructions. One command per code block. Explain what each command does in one short sentence. Do things yourself with tools when you can, instead of asking him to. When he asks a question, answer the question first, then offer the fix — do not bury the answer in a wall of solutions.

### 5.5 Ask, do not guess.
When you do not know a file path, a format, an API shape, or a setting, **ask one question** instead of guessing and wasting the session. One clarifying question saves hours.

### 5.6 Never lie, never fabricate.
Never invent test results, timing numbers, credentials, or contact replies. If you did not measure it, do not report it. If you did not verify an email, mark it unverified. Previous sessions have fabricated fake test timings and it wasted days — do not.

### 5.7 Never use task-tracking tools in the CLI.
Nir has explicitly said task display clutters the terminal. Track progress mentally. Do not open a task list.

### 5.8 ASCII only in WaggleDance curl payloads.
Em-dashes, smart quotes, ellipses, arrows, and emojis break the Bash → curl → Flask chain and return `400 Bad Request`. Use plain ASCII hyphens `-`, straight quotes `"`, three dots `...`, and arrows as `->`.

## 6. The handshake — do this before any real work

At the start of every parallel-vibing day (or after an OS switch on your machine), run through this checklist. It is from `PARALLEL_VIBING.md` §5.

1. **Confirm your track with Nir** — testing, videos, books, outreach, or infra. You own only that track for the session.
2. **`git pull --ff-only`** on every repo you expect to touch. If anything comes in, read the new commits.
3. **Read your track's source-of-truth file(s):**
   - **Testing** → `KillerBee/PROJECT_REPORT.md` + `KillerBee/CLAUDE.md` + latest entries in `KillerBee/EXPERIMENT_LOG.md`. If on Linux and the mission is VM setup: also read `KillerBee/PHASE3_LINUX_VM_SETUP.md`.
   - **Videos — BeeSting** → `BeeSting/SERIES_BIBLE.md` + `BeeSting/PART_SLATE_EXPANSION.md` + `BeeSting/PART_1_ELEMENTS.md` + `BeeSting/elements/PROMPTS.md`.
   - **Videos — Honeymation** → `Honeymation/OUTREACH_METHODOLOGY.md`.
   - **Books — MadHoney** → `MadHoney/BOOK_PLAN.md` + the relevant chapter file.
   - **Outreach** → `Honeymation/OUTREACH_METHODOLOGY.md` + latest logs.
4. **Read this file** (you are reading it now), `PARALLEL_VIBING.md`, `WHEN_TO_USE_WAGGLEDANCE.md`, `LESSONS.md`.
5. **Send one ICQ REPLY** stating: role, track owned, repos synced, source-of-truth read, ready. Use the curl command in §7.
6. Work begins when Nir gives the green light.

After the handshake, go silent on ICQ until a legitimate operational event fires (§4).

## 7. How to send an ICQ message (copy-paste reference)

The WaggleDance server runs on **Laptop at `http://10.0.0.1:8765`** whenever Laptop is awake. From any other machine (Desktop Windows, Desktop Linux, Laptop Linux), use that URL. When you are *on* Laptop itself, use `http://localhost:8765`.

Replace `<your-role>` with one of: `laptop-claude`, `desktop-claude`. (The ICQ does not yet distinguish Windows vs Linux — the physical machine name is enough because only one OS is active per machine at a time.)

**Send a REPLY (informational):**
```
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "<your-role>", "type": "REPLY", "message": "YOUR ASCII-ONLY MESSAGE HERE"}'
```

**Send a TASK (the other Claude must act):**
```
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "<your-role>", "type": "TASK", "message": "YOUR ASCII-ONLY MESSAGE HERE"}'
```

**Check for recent messages:**
```
curl -s http://10.0.0.1:8765/latest?n=5
```

A successful send returns `{"id":<number>,"ok":true}`. A `400 Bad Request` means you put a non-ASCII character in the payload — fix and retry.

## 8. If something is unclear

Ask Nir in plain text. One question. Wait for the answer. Do not guess.

---

## Changelog

- **2026-04-14** — Initial version written by Desktop Windows Claude (Opus 4.6) during the first parallel-vibing day, in preparation for Desktop Linux Claude coming online later the same day for the Phase 3 VM setup mission.
