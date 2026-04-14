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

## 9. Bootstrap: what to do if nothing is cloned yet

You may wake up on a machine where none of the repos have been cloned yet (typical on a fresh Linux boot). You need the repos before anything else. Run, in order:

```
sudo apt install -y git
```
```
mkdir -p ~/Projects && cd ~/Projects
```
```
for r in WaggleDance KillerBee HoneycombOfAI GiantHoneyBee BeehiveOfAI BeeSting Honeymation MadHoney TheDistributedAIRevolution; do git clone https://github.com/strulovitz/$r.git; done
```

If even `git` is not installed and you cannot wait for the apt install, you can read this single file with `curl` before cloning:

```
curl -s https://raw.githubusercontent.com/strulovitz/WaggleDance/master/FRESH_CLAUDE_START_HERE.md | less
```

But you will need the full clones eventually — start the `apt install` + loop above as the first thing you do.

---

## 10. For Nir — first-message template to paste into a fresh Linux Claude Code session

When you start Claude Code on a freshly-booted Linux machine, paste **this entire block** as your very first message. Fill in the two bracketed placeholders. Everything else is ready to copy as-is.

```
You are Claude Code running on my [Desktop | Laptop] machine, which I just booted into [Linux Mint 22.2 | Debian 13]. This is a fresh session with no prior history on this OS. Your auto-memory is empty because auto-memory lives in a per-OS directory.

Your role: [desktop-linux-claude | laptop-linux-claude].
Your track today: testing (Phase 3 VM setup) per WaggleDance/PARALLEL_VIBING.md.
Your mission: guide me through KillerBee/PHASE3_LINUX_VM_SETUP.md step by step, one command at a time, so we end the session with at least one working bridged VM running Ollama on the LAN, confirmed reachable from the other physical machine.

Before touching the mission, bootstrap yourself:

1. Install git and clone all repos under ~/Projects per the loop in WaggleDance/FRESH_CLAUDE_START_HERE.md section 9.
2. Read, in this order:
   - WaggleDance/FRESH_CLAUDE_START_HERE.md (end to end, including sections 5 and 6)
   - WaggleDance/PARALLEL_VIBING.md (end to end)
   - WaggleDance/WHEN_TO_USE_WAGGLEDANCE.md
   - WaggleDance/LESSONS.md
   - KillerBee/CLAUDE.md (Rule 1 and Rule 2 are load-bearing)
   - KillerBee/PROJECT_REPORT.md (latest state, especially "What Has NOT Been Done")
   - KillerBee/PHASE3_LINUX_VM_SETUP.md (this is your runbook)
3. Send one ICQ REPLY on WaggleDance to laptop-claude announcing: role, track, repos synced, docs read, ready to start at section 4 of PHASE3_LINUX_VM_SETUP.md. Use the ASCII-only curl format from FRESH_CLAUDE_START_HERE section 7. The WaggleDance server is on the Laptop at http://10.0.0.1:8765.
4. Report back to me in plain text summarizing what you read and confirm you are ready.
5. Wait for me to say "go" before running any real commands on the system.

Do not use task-tracking tools. Do not fabricate. Do not reward-hack. Ask me if anything is unclear — one question at a time. I have ADD and am not a programmer, so give me ultra-detailed copy-paste instructions, one command per code block, with a one-sentence explanation of what each command does before I paste it.
```

That single paste is enough to get Desktop Linux Claude (or Laptop Linux Claude) fully briefed and on-mission with nothing else. Edit only the two bracketed placeholders, nothing else.

---

## 11. Linux notes (short)

- **Paste shortcut:** `waggle_icq.py` and `waggle_agent.py` now branch on `IS_LINUX` and use `Ctrl+Shift+V` on Linux instead of `Ctrl+V`. No action needed — just run the same commands as on Windows.
- **Wayland fallback:** if `pygetwindow` cannot enumerate windows (default on Debian 13 / GNOME Wayland), the ICQ tools drop to **viewer-only** mode automatically — they print incoming messages to the terminal they are running in, and you paste them by hand into Claude Code. No crash. No silent failure. On X11 sessions (Linux Mint Cinnamon default) window detection should work normally.
- **No `winnat` step:** skip step 3 of the Laptop daily startup in `README.md` — Hyper-V does not exist on Linux and there is no port reservation to bounce.
- **ASCII-only rule still applies.** Same reason as Windows — keep curl payloads plain ASCII.
- **Server restart after reboot** is already part of the normal morning WaggleDance startup (see `README.md` "Nir's Daily Startup Guide"). When a machine reboots into a new OS, run the full morning startup again on whichever machine hosts the server. Nothing special, no new procedure.

---

## Changelog

- **2026-04-14** — Initial version written by Desktop Windows Claude (Opus 4.6) during the first parallel-vibing day, in preparation for Desktop Linux Claude coming online later the same day for the Phase 3 VM setup mission.
