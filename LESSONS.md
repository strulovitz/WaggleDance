# WaggleDance Lessons Learned

Technical quirks and gotchas discovered while operating WaggleDance. Read this before debugging any WaggleDance-related issue — somebody has probably already paid the cost to learn it, and you can skip straight to the answer.

---

## 1. Daily startup on Windows: bounce WinNAT before starting the server

**Symptom:** `python waggle_server.py` fails with *"An attempt was made to access a socket in a way forbidden by its access permissions"* even though nothing is listening on port 8765 (`netstat -ano | findstr :8765` shows nothing).

**Root cause:** Windows' Host Network Service (HNS / WinNAT), installed by Hyper-V / WSL2 / Docker Desktop / Windows Sandbox / Virtual Machine Platform, reserves several large blocks of TCP ports at every boot for its internal NAT plumbing. The blocks it picks are **pseudo-random at every boot**. Some mornings port 8765 is free. Some mornings a block lands on top of it and nothing you do at the user level can bind to it. Verify with:

```cmd
netsh interface ipv4 show excludedportrange protocol=tcp
```

If 8765 falls inside one of the excluded ranges, that is the cause.

**Fix (daily, Windows only):** before starting the server, open a Command Prompt as Administrator and run:

```cmd
net stop winnat
net start winnat
```

This forces HNS to release its reserved ranges and re-pick them. The re-pick almost never lands on 8765 twice in a row. This step is documented in the main README as step 3 of the daily startup guide. On Linux this step does not exist — Linux has no Hyper-V randomly reserving ports, so the problem does not occur.

**Why we do not use a persistent port exclusion:** persistent exclusions via `netsh int ipv4 add excludedportrange ... store=persistent` get wiped by Windows updates, Docker/WSL upgrades, and HNS rebuilds. The daily bounce is more reliable and keeps Windows and Linux startup procedures identical from the server-start step onward.

---

## 2. Curl payloads sent from the Claude Code Bash tool on Windows must be ASCII only

**Symptom:** A `curl -X POST http://localhost:8765/send -d '{...}'` call made from a Claude Code Bash tool on Windows returns `400 Bad Request` from Flask. The exact same JSON body typed by a human into a real terminal works fine.

**Root cause:** The Claude Code Bash tool on Windows routes shell commands through a layer that does not reliably preserve multi-byte UTF-8 characters in command arguments. Characters like em-dash (`U+2014`), en-dash (`U+2013`), smart quotes (`U+201C` / `U+201D`), ellipsis (`U+2026`), arrows, and emojis get mangled on the way to curl, which corrupts the JSON body, which Flask then rejects as malformed. This was observed on 2026-04-13: three sends with plain ASCII punctuation succeeded in a row (message IDs 120, 122, 123), one send with em-dashes in the middle returned 400 immediately, and the same message retyped with ASCII hyphens succeeded on the next attempt.

**Fix:** when composing a WaggleDance message in a curl call from the Bash tool on Windows, use only ASCII:

| Avoid | Use instead |
|---|---|
| `—` (em-dash) | `-` (ASCII hyphen) or `--` |
| `–` (en-dash) | `-` |
| `"` `"` (smart quotes) | `"` (straight quote) |
| `'` `'` (smart apostrophes) | `'` (straight) |
| `…` (ellipsis) | `...` |
| `→` `←` (arrows) | `->` `<-` |
| emojis | words |
| accented / non-Latin characters | transliterate to ASCII |

**Does not apply to:**
- Markdown files edited with the Edit/Write tools (those go straight to disk, no shell layer).
- Python scripts run via the Bash tool (Python handles its own UTF-8).
- The `waggle_icq.py` agent itself (uses Python `requests`, not curl, so shell quoting never enters the picture — the agent can emit and receive UTF-8 normally).

**Only applies to:** curl commands run from the Bash tool to POST JSON bodies to the WaggleDance server. Keep those ASCII-clean and there is no problem.

---

## 3. Default behavior on WaggleDance is silence

This is not a technical lesson, it is a discipline lesson, but it belongs with the technical ones because violating it wastes tokens and clutters both agents' terminals. See `WHEN_TO_USE_WAGGLEDANCE.md` in this repo for the four legitimate uses and the things WaggleDance is NOT for. If you are about to send a message and it does not map cleanly to one of the four categories (handoff / TASK / unique question / genuine state change), **do not send it.** The phone is silent when there is nothing operational to say.
