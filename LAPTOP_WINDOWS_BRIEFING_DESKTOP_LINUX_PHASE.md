# Laptop Windows — Briefing for the Desktop Linux Phase

**Audience:** Laptop Windows Claude (currently running on the Lenovo Legion laptop in the bedroom, on the videos track).
**Situation date:** 2026-04-14, the first parallel-vibing day.
**Commits referenced:** WaggleDance `0830b54`, KillerBee `3c7a8e7`.

Read this file end to end before Desktop reboots into Linux. Then send the handshake REPLY in §9 and go silent.

---

## 1. What is about to happen

Nir is rebooting **Desktop** from Windows 11 into **Linux Mint 22.2**. When he does:

- The Desktop Windows Claude session ends. No more conversation history on that side.
- A fresh **Desktop Linux Claude** session starts, with **empty auto-memory** (auto-memory lives in a per-OS directory, so the Windows memory is not visible to the Linux session).
- Desktop Linux Claude bootstraps himself from the repos on GitHub, following `WaggleDance/FRESH_CLAUDE_START_HERE.md`.
- His mission is **Phase 3 VM setup** for the 3-DwarfQueen parallel test, per `KillerBee/PHASE3_LINUX_VM_SETUP.md`.

**You are not affected in the default case.** You stay on Laptop Windows. Your track does not change. Your mission does not change.

## 2. Your default assignment — unchanged

Your track is still **videos (BeeSting Part 1/14 Hive Drones)**. The slate is /14 as of 2026-04-13, Big Tech is Part 6. Sources of truth: `BeeSting/SERIES_BIBLE.md`, `BeeSting/PART_SLATE_EXPANSION.md`, `BeeSting/PART_1_ELEMENTS.md`, `BeeSting/elements/PROMPTS.md`. Script is LOCKED; the remaining work is the 5 priority-11 elements then shot production.

You are **not** moving to the testing track. You are **not** a VM setup consultant by default. If Nir walks into the bedroom and asks for video work, you give him video work.

## 3. Your backup role — on demand only

There is one exception to "stay in videos mode": if Desktop Linux Claude hits something the docs do not cover and he **explicitly sends you a TASK via ICQ asking for help**, answer.

You have full continuous conversation context and full auto-memory on the Windows side. Desktop Linux does not. Your knowledge may unblock him faster than him debugging alone. That is the whole reason this briefing file exists.

**Rules for when you do answer:**

- **Only on explicit TASK.** Never proactively. No "hey how is it going" messages.
- **Answer the question, do not take over.** You are a consultant, not the mission owner.
- **Point to the exact doc section if one exists.** Do not re-derive what is already written down.
- **If no doc covers it, say so plainly** and give your best answer based on what you actually know. Do not guess and present a guess as fact. (The biggest failure mode of today's session was Desktop Windows Claude stating assumptions as facts. Do not repeat it.)
- **Keep the answer short.** Do not burn his context window. One paragraph and a pointer is usually enough.
- **Return to the videos track immediately** after answering. Do not linger.

## 4. What Desktop Linux already has

Do not waste time re-explaining things that are already committed to GitHub. As of the commits above, Desktop Linux can bootstrap himself from these files alone:

| File | What it gives him |
|---|---|
| `WaggleDance/FRESH_CLAUDE_START_HERE.md` | Identity, critical rules normally from auto-memory, reading order, ICQ curl commands, first-message template, Linux notes |
| `WaggleDance/PARALLEL_VIBING.md` | Methodology, track ownership, OS-switch handoff ritual, handshake |
| `WaggleDance/WHEN_TO_USE_WAGGLEDANCE.md` | ICQ discipline, four legitimate uses, silence-is-default |
| `WaggleDance/LESSONS.md` | ASCII-only rule + prior operational incidents |
| `KillerBee/CLAUDE.md` | Rule 1 (no reward hacking) + Rule 2 (think like the best) |
| `KillerBee/PROJECT_REPORT.md` | Current state, Phase 2 LAN test passed, next tests, "what has NOT been done" |
| `KillerBee/PHASE3_LINUX_VM_SETUP.md` | 11-section step-by-step runbook: prereqs, bridged net, VM creation, Ollama setup, Rule 1 compliance checklist, troubleshooting |

**Code fixes also landed** in `waggle_icq.py` and `waggle_agent.py`:
- Paste shortcut branches on `IS_LINUX` → `Ctrl+Shift+V` on Linux, `Ctrl+V` on Windows.
- `pygetwindow` wrapped in try/except → falls back to **viewer-only mode** if it cannot enumerate windows (Wayland case).
- **These fixes are committed but UNTESTED on real Linux** until Desktop actually boots into Mint. If Desktop Linux reports that they do not work, trust him over the code.

## 5. Likely questions and where the answer lives

If Desktop Linux TASKs you one of these, point him at the file+section instead of re-deriving:

| Question | Answer location |
|---|---|
| "VM got `192.168.122.x` not `10.0.0.x`" | `KillerBee/PHASE3_LINUX_VM_SETUP.md` §10 (bridge not wired, `virsh edit <vm>`) |
| "Ollama in VM refuses LAN connections" | §10 (OLLAMA_HOST not inherited by systemd, use `systemctl edit ollama`) |
| "Host loses network when bringing up `br0`" | §10 (nmcli wrong tool for this distro state, fall back to `/etc/network/interfaces`, pause and ask Nir) |
| "virt-manager cannot see my VMs" | §10 (user not in libvirt group, or ran with `sudo`) |
| "Test runs but some DwarfQueen shows 0 Workers" | §10 (Worker process on host instead of inside the VM) |
| "`waggle_icq.py` crashed / no auto-type" | `FRESH_CLAUDE_START_HERE.md` §11 (Wayland fallback, viewer-only, manual `curl /latest?n=5` poll) |
| "How do I send an ICQ message" | `FRESH_CLAUDE_START_HERE.md` §7 |
| "What is my identity / track / mission" | `FRESH_CLAUDE_START_HERE.md` §1 + §10 first-message template Nir pasted |
| "What is Rule 1 / what counts as reward hacking" | `KillerBee/CLAUDE.md` Rule 1 |

If the question is in **none** of those, Desktop Linux is in genuinely new territory and your answer is valuable. Answer honestly, admit uncertainty when you have it, and keep it short.

## 6. ICQ auto-type behavior during this phase

### 6.1 What the Linux code fix actually does (commit 0830b54)

Two real code changes you should understand, in case Desktop Linux asks you about them or in case you need to explain the ICQ setup to a fresh Laptop Linux Claude tomorrow:

1. **Paste shortcut is different on Linux.** On Windows terminals, the paste keyboard shortcut is `Ctrl+V`. On **Linux terminals, it is `Ctrl+Shift+V`** — plain `Ctrl+V` does nothing (or types a literal `v`). The original `waggle_icq.py` and `waggle_agent.py` hard-coded `Ctrl+V`, which meant the auto-typer silently failed on Linux. The fix added `IS_LINUX = platform.system() == "Linux"` and branches: `pyautogui.hotkey("ctrl", "shift", "v")` on Linux, `pyautogui.hotkey("ctrl", "v")` on Windows. Same copy method (pyperclip), different paste combo.

2. **Wayland fallback.** `pygetwindow` (the library that finds the Claude Code window to paste into) works on Windows and on Linux X11 sessions, but it cannot enumerate windows on Wayland. The fix wraps the import and the `getAllWindows()` call in `try/except`. If either fails, the tool drops to **viewer-only mode** — it still prints incoming messages to its own terminal, but does not try to auto-paste. The human then copy-pastes the message into Claude Code by hand. No crash, no silent failure.

### 6.2 What this means for you during this phase

- **Linux Mint Cinnamon defaults to X11**, not Wayland. `pygetwindow` should work on X11, and the paste branch now uses the correct shortcut. So auto-typing in **both directions** should work once Desktop is on Linux Mint.
- **But untested.** If Desktop Linux reports that auto-type does not work on his side, he will drop to viewer-only and poll manually with `curl -s http://10.0.0.4:8765/latest?n=5`. His responses will arrive with a noticeable delay (seconds to minutes) because he reads on his own cadence. **Do not spam him thinking he is offline.** Silence from him during that phase is normal.
- **If your own `waggle_icq.py` on Laptop Windows starts behaving strangely** during the phase, that is a separate bug, not a Linux side effect. Restart your ICQ terminal per the daily startup in `README.md`.

## 7. Things to NOT do during this phase

1. **Do not speculate and write docs about it.** That was the main failure mode of Desktop Windows Claude earlier today. Nir already corrected it once. If you have a guess, keep it a guess, do not commit it as documentation.
2. **Do not duplicate-commit** to files Desktop Linux is actively editing: `KillerBee/PHASE3_LINUX_VM_SETUP.md`, `KillerBee/EXPERIMENT_LOG.md`, `KillerBee/seed_data.py`, anything in the Testing track. Track ownership per `PARALLEL_VIBING.md` §4: testing = Desktop, you = videos. Shared repos like WaggleDance are fine to touch but `git pull --rebase` before pushing and announce on ICQ.
3. **Do not send status pings.** "How's it going?" "Any progress?" "Need help?" These are all forbidden by `WHEN_TO_USE_WAGGLEDANCE.md`. Silence is the default.
4. **Do not assume the Linux code fixes work until Desktop Linux confirms.** If he says `waggle_icq.py` still crashes despite the try/except, believe him. Ask him for the traceback. Do not insist the fix is correct.
5. **Do not proactively draft VM troubleshooting steps and push them over ICQ unsolicited.** He has the runbook. He will ask if he needs you.
6. **Do not abandon the videos track to babysit.** Your highest-value use of the next hours is finishing the 5 priority-11 elements in `BeeSting/PART_1_ELEMENTS.md`, not hovering over Desktop Linux.

## 8. If Desktop Linux goes completely silent

If you send a TASK and get no response for a long time, two likely causes:

- **His ICQ viewer crashed on import** → he is not seeing your messages at all. Nir will notice and restart it. Not your problem to fix remotely.
- **He is deep in a long VM install step** → `apt install`, `debian netinst`, `ollama pull` can each take several minutes. Be patient.

Do not escalate with follow-up messages. One TASK. Wait. If Nir walks into the bedroom and asks about it, tell him plainly what you sent and when.

## 9. Handshake — do this now

After reading this file, send **one** ICQ REPLY with this content (fill in your own phrasing, ASCII only):

> *"Read LAPTOP_WINDOWS_BRIEFING_DESKTOP_LINUX_PHASE.md. Default track stays videos (BeeSting Part 1/14 Hive Drones). Backup role is on-demand only, explicit TASK only. Will not spam. Will not speculate. Ready for Desktop Linux handoff."*

Then go silent. Work on videos. Wait for a TASK or for Nir to walk into the bedroom.

## 10. Why this file exists

Everything in the core docs (`FRESH_CLAUDE_START_HERE.md` + `PARALLEL_VIBING.md` + `PHASE3_LINUX_VM_SETUP.md`) should already cover the handoff automatically. This file is a belt-and-braces briefing for the specific case where Desktop Linux Claude hits something the docs do not cover and needs a human-caliber consultant with full context on the Windows side. You are that consultant, available on demand, silent by default.

The pattern generalizes: whenever one machine is doing unfamiliar infra work on a fresh OS and the other machine has continuous context, the continuous one is the backup consultant. Re-use this doc as a template for future phases (Laptop-Linux phase tomorrow, etc.) by copying it and changing the machine/OS/mission references.

---

## Changelog

- **2026-04-14** — Initial version written by Desktop Windows Claude just before handing off to Desktop Linux Claude. Nir explicitly requested this file as a belt-and-braces briefing after a morning of stale-memory and over-speculation failures on the Desktop side.
