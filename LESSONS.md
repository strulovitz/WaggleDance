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

## 3. Linux backend for waggle_icq.py uses wmctrl + pyautogui.write, not pygetwindow

**Symptom (before the fix, 2026-04-14 morning):** on Desktop Linux Mint 22.2 Cinnamon, `python3 waggle_icq.py` started normally, printed the flower header, and went straight to `Agent running. Watching for messages...` with **no numbered window picker at all**. Nir had no idea whether it was in viewer-only mode or broken, and Laptop → Desktop messages silently stopped auto-typing into Desktop Claude Code.

**Root cause:** `pygetwindow` does not work on Linux. It raises `NotImplementedError` from inside `__init__.py` when you call `getAllWindows()`, not at import time. The old `GW_AVAILABLE = True/False` guard only caught import failures, so on Linux `GW_AVAILABLE` stayed `True`, the picker went into its try/except around `gw.getAllWindows()`, caught the exception, printed one error line, and fell through to viewer-only mode — which looks indistinguishable from a successful silent startup if you are not watching carefully. The FRESH_CLAUDE_START_HERE.md doc compounded the problem by claiming "X11 sessions should work normally", which was never true.

**Fix:** force `GW_AVAILABLE = False` on Linux regardless of import success, and add a parallel Linux backend that uses only tools already present on a stock Mint 22.2 Cinnamon install:

- **Window enumeration:** `wmctrl -lp` (already at `/usr/bin/wmctrl` on stock Mint; returns `<hex_id> <desktop> <pid> <host> <title>` per line; filter `desktop == -1` to skip dock/sticky windows).
- **Window activation:** `wmctrl -i -a <hex_id>`. The hex id is stable across title changes, so tracking by id gives the same "survives conversation title churn" property the Windows handle has.
- **Typing:** `pyautogui.write(message, interval=0.005)` followed by `pyautogui.press("enter")`. This uses Xlib directly via python3-xlib (version 0.15 on Mint 22.2) and does **not** need a clipboard, so it works on machines where `xclip` / `xsel` / `wl-copy` are not installed. Our ICQ payloads are ASCII-only by rule, so `pyautogui.write` handles every character safely.

**Deliberately avoided:** `xdotool` (not installed on stock Mint 22.2), `xclip` / `xsel` / `wl-copy` (not installed), `ydotool` (not installed, Wayland-only anyway), pyperclip clipboard on Linux (no backend without xclip/xsel). The backend was designed to need **zero new packages, zero sudo**.

**Diagnostic commands that prove the environment on Mint 22.2 Cinnamon:**

```bash
echo "$XDG_SESSION_TYPE"   # x11
echo "$XDG_CURRENT_DESKTOP" # X-Cinnamon
command -v wmctrl          # /usr/bin/wmctrl
python3 -c "import pyautogui; print(pyautogui.__version__)"  # 0.9.54
wmctrl -lp | head          # real window list, 4 windows, Claude Code visible
```

**Verified end-to-end on 2026-04-14:** TASK #150 sent from Laptop Windows → WaggleDance server → Desktop Linux ICQ agent → wmctrl activated the Claude Code window → pyautogui.write typed the full 57-word TASK → Desktop Linux Claude replied `AUTOTYPE_OK 57`. No hand-pasting. Parity with the Windows backend.

**Wayland (not tested yet):** if you ever boot Desktop or Laptop into a Wayland session, `wmctrl` will return an empty list and the backend will correctly fall back to viewer-only mode. A real Wayland backend would need `ydotool` (plus sudo setup for uinput) and a Wayland-compatible window enumerator, which no distro ships as a single tool today. Stay on X11 until that landscape matures.

**How to diagnose without guessing** (the approach that finally worked this morning after two botched "fixes"): push a diagnostic prompt file to the repo that lists the exact commands to run (`XDG_SESSION_TYPE`, `command -v wmctrl xdotool xclip ...`, `python3 -c "import pygetwindow"`, `wmctrl -l`), tell the Linux Claude to pull it and commit the literal output to `LINUX_DIAG_<MACHINE>.md`, then write the backend against real data instead of guessing which tools are installed. See `LINUX_DIAG_PROMPT.md` and `LINUX_DIAG_DESKTOP.md` in this repo for the template and the first real result.

---

## 4. Default behavior on WaggleDance is silence

This is not a technical lesson, it is a discipline lesson, but it belongs with the technical ones because violating it wastes tokens and clutters both agents' terminals. See `WHEN_TO_USE_WAGGLEDANCE.md` in this repo for the four legitimate uses and the things WaggleDance is NOT for. If you are about to send a message and it does not map cleanly to one of the four categories (handoff / TASK / unique question / genuine state change), **do not send it.** The phone is silent when there is nothing operational to say.
