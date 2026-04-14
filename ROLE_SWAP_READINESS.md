# Role-Swap Readiness — when Laptop becomes Linux and Desktop becomes Windows

**Who this is for:** whichever Claude Code session wakes up first after Nir swaps OS roles so that **Laptop runs Debian 13 GNOME** and **Desktop runs Windows 11**. This file exists so you do not have to rediscover everything we learned on the opposite configuration. Read it end to end before touching anything.

**Current working configuration (2026-04-14 morning, for reference only):** Laptop = Windows 11, Desktop = Linux Mint 22.2 Cinnamon X11. In that configuration the WaggleDance server runs on Laptop Windows at `http://10.0.0.1:8765`, the Linux backend for `waggle_icq.py` uses `wmctrl` + `pyautogui.write`, and it is verified end-to-end (TASK #150, `AUTOTYPE_OK 57`, commit `848ab53`).

**After the swap:** the server will need to run on **Laptop Debian 13 Linux** at `http://10.0.0.1:8765`, and the Desktop Windows Claude will connect to it as a client. The network IPs stay the same — IPs are assigned to physical machines, not to the OS they boot into.

---

## 1. What will almost certainly break on the first morning after the swap

Predict these, do not be surprised by them:

1. **Debian 13 GNOME defaults to Wayland, not X11.** The Linux backend we wrote for Mint Cinnamon uses `wmctrl`, which only works on X11. On Wayland `wmctrl -l` typically returns an empty list or errors. If Laptop Linux boots into Wayland, the ICQ will silently fall back to viewer-only mode exactly like Desktop Linux did this morning — no numbered window picker, no auto-type.

2. **The repos may not be cloned on Laptop Linux yet.** Nir's Laptop has been Windows-only until now. The first Linux boot of the laptop may have an empty home directory with no `WaggleDance`, no `KillerBee`, no anything. See §5 for the bootstrap loop.

3. **Flask / pyautogui / pyperclip may not be installed** on Laptop Linux. Mint 22.2 on Desktop happened to already have `pyautogui` and `pyperclip` installed. Debian 13 is a different distro and that is not guaranteed. The WaggleDance **server** itself needs only Flask — that is the critical dependency, because if the server does not start, nothing else can run. See §4.

4. **No firewall rule for port 8765 on Laptop Linux yet.** Mint had `ufw` either disabled or already permissive on the Desktop (we did not have to configure it). Debian 13 may ship with `ufw` inactive too, but verify — if Laptop Linux has a firewall blocking 8765, Desktop Windows Claude will see connection refused from 10.0.0.1 and nothing will work.

5. **No `winnat` problem on Laptop Linux.** Linux does not have Hyper-V randomly reserving ports at boot, so the whole `net stop winnat / net start winnat` ritual is irrelevant on Laptop when it is Linux. Do not try to run it. Desktop Windows **will** still need the winnat bounce **only if** it is hosting the server, which it is not in this configuration (it is a pure client), so the winnat step can also be skipped on Desktop this time around. The server lives on Laptop Linux and Linux has no HNS.

6. **Desktop Windows Claude will have full auto-memory** because Nir used this machine in Windows mode many times. Laptop Linux Claude will have **empty auto-memory** because this is the first time the laptop has ever booted Linux. Load rules from `FRESH_CLAUDE_START_HERE.md` §5 until memory populates.

---

## 2. The diagnostic-first rule (MANDATORY, DO NOT SKIP)

We learned this morning, the hard way, that guessing which tools are installed on a Linux box wastes hours. Do **not** write a line of code for the Laptop Linux side until you have a diagnostic dump committed to the repo.

**If you are Laptop Linux Claude on the first morning after the swap:**

1. `cd WaggleDance && git pull`
2. Open `LINUX_DIAG_PROMPT.md` and execute every numbered command.
3. Write the output to **`LINUX_DIAG_LAPTOP.md`** (not `LINUX_DIAG_DESKTOP.md` — that file already exists for the other machine).
4. `git add LINUX_DIAG_LAPTOP.md && git commit && git push`
5. Send one ICQ REPLY to the other Claude saying the diag is pushed.

**If you are Desktop Windows Claude watching Laptop Linux come online:**

Do not write any Linux code, Wayland code, or install instructions until `LINUX_DIAG_LAPTOP.md` is on GitHub. Pull it, read the literal output, and only then decide on the backend path in §3. Same discipline that finally worked this morning.

The diagnostic commands in `LINUX_DIAG_PROMPT.md` are generic — they already cover Debian/GNOME/Wayland. You do not need to write a new diag file. The only thing that changes is the output filename (`LINUX_DIAG_LAPTOP.md`) and machine-identification section.

---

## 3. Two pre-planned branches for `waggle_icq.py` on Laptop Debian 13

Based on what `LINUX_DIAG_LAPTOP.md` says, pick one of these branches. **Do not mix them.**

### Branch A — Debian 13 is running X11 (best case)

How to tell: `XDG_SESSION_TYPE=x11`, `WAYLAND_DISPLAY=` (empty), `wmctrl -l` returns a real window list.

This is actually achievable on Debian 13 GNOME — the login screen (GDM) has a gear icon that lets Nir pick **"GNOME on Xorg"** instead of the default **"GNOME"** (which is Wayland). If Nir picks GNOME on Xorg at the login screen, everything we built this morning for Mint works unchanged on Debian.

**Required packages (install with `sudo apt install -y <pkg>`):**
- `wmctrl` (almost certainly NOT pre-installed on Debian — Mint had it, Debian 13 does not ship it by default)
- `python3-tk` (pyautogui dependency on some Debian builds)
- `python3-xlib` (needed by pyautogui's X11 backend)
- `python3-pip` → then `pip3 install --user pyautogui pyperclip flask` (or use apt: `python3-pyautogui python3-flask` if those packages exist in Debian 13 repos — check `apt search` first)

**Then:** `waggle_icq.py` works as-is. The Linux branch we committed this morning (commit `8d6edb3`) is already on master and will behave the same on Debian X11 as it did on Mint X11.

**Recommendation:** tell Nir to pick "GNOME on Xorg" at the login screen the first time he boots Debian 13. This is the single highest-leverage thing he can do to make the swap painless. Wayland on Debian 13 is a real backend-engineering project; X11 is a package install.

### Branch B — Debian 13 is running Wayland (worst case)

How to tell: `XDG_SESSION_TYPE=wayland`, `WAYLAND_DISPLAY=wayland-0` (or similar non-empty), `wmctrl -l` errors or returns nothing, `XDG_SESSION_DESKTOP=gnome`.

There is **no clean off-the-shelf solution** for window enumeration and synthetic keystrokes under Wayland. Here is the honest truth:

- **Window enumeration under Wayland:** GNOME has no public API for "list all top-level windows with their titles." Third-party apps are intentionally sandboxed from seeing other apps' windows. There is a hack using GNOME Shell D-Bus + a custom Shell extension (`Window Calls` or similar), but it requires installing a Shell extension at login.
- **Synthetic keystrokes under Wayland:** `ydotool` works but requires the `ydotoold` daemon running as root with `/dev/uinput` access, which means a one-time `sudo` setup and a systemd service. `pyautogui` alone cannot type under Wayland — it silently fails or raises.

**Pragmatic three-tier plan for Branch B, in order of how much work they are for Nir:**

1. **Tier 1 — give up and log in as X11 instead.** Have Nir log out, pick "GNOME on Xorg" at GDM, log back in. Jump to Branch A. This is the right answer 95% of the time.
2. **Tier 2 — accept viewer-only mode on Laptop Linux.** The server still runs fine, outbound curl from Laptop Linux Claude still works fine, only the inbound auto-type is broken. Desktop Windows Claude's messages print in the ICQ viewer terminal and Nir hand-pastes them into Laptop Claude Code. This is exactly the state Desktop Linux was in this morning before we fixed it, and it is operable (if annoying) for a day.
3. **Tier 3 — actually build a Wayland backend.** This is a real ~4-hour project: install `ydotool` + `ydotoold`, set up `/dev/uinput` permissions or a systemd unit, pick a window-enumeration hack (GNOME Shell extension with D-Bus, or forgo enumeration and let Nir hard-code a single "Claude Code terminal" window by process name), and write a new code path in `waggle_icq.py` that branches on `XDG_SESSION_TYPE`. Do not do this on the first morning of the swap. Ship Tier 1 or Tier 2, get through the day, then build Tier 3 at leisure if Nir actually wants it.

**The code in `waggle_icq.py` is already Tier-2-safe.** If `wmctrl -lp` fails on Wayland, the function returns `None` and the agent falls back to viewer-only mode without crashing. No code change is needed for Tier 2 — it just works badly in a well-behaved way.

---

## 4. Starting the WaggleDance server on Laptop Linux (Debian 13)

The server must run on Laptop because both first-message templates hard-code `http://10.0.0.1:8765` (Laptop's LAN IP). Even after the OS swap, IP does not move.

### 4a. One-time Debian 13 bootstrap (first boot only)

```
sudo apt update
```
```
sudo apt install -y git wmctrl python3 python3-pip python3-xlib python3-tk
```
```
pip3 install --user flask pyautogui pyperclip
```

If `pip3 install --user` complains about PEP 668 / externally-managed environment (Debian 13 will), use a venv or the `--break-system-packages` flag. Safer option:

```
python3 -m venv ~/waggle-venv
```
```
~/waggle-venv/bin/pip install flask pyautogui pyperclip
```

And then always run `waggle_server.py` and `waggle_icq.py` with `~/waggle-venv/bin/python3` instead of plain `python3`. Document this in a new `LAPTOP_LINUX_STARTUP.md` runbook the first time you set it up.

### 4b. Firewall (Debian 13 usually ships ufw inactive but verify)

```
sudo ufw status
```

If it says `Status: inactive`, you are fine, skip the rest.
If it says `Status: active`, open port 8765:

```
sudo ufw allow 8765/tcp
```

### 4c. Daily start of the server on Laptop Linux

From the directory where the repos live (same folder the terminal opens into by default, as on Desktop Linux):

```
cd WaggleDance
```
```
git pull
```
```
python3 waggle_server.py
```

(Or `~/waggle-venv/bin/python3 waggle_server.py` if you had to use a venv.)

No `winnat` bounce. No firewall commands. Just start it. If port 8765 is already in use, find the old process with `ss -tlnp | grep 8765` and `kill` it by PID — on Linux this is simpler than the Windows netstat/taskkill dance.

### 4d. Ollama on Laptop Linux

For Parallel Vibing testing work (when we get back to it), Laptop Linux will need Ollama listening on LAN:

```
curl -fsSL https://ollama.com/install.sh | sh
```
```
sudo systemctl edit ollama
```

Add these lines in the override editor:
```
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

Save, then:
```
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

And verify: `curl http://10.0.0.1:11434/api/tags` from Desktop should return JSON. This only matters for the testing track, not for WaggleDance itself — skip it on day 1 of the swap and come back to it when the testing track resumes.

---

## 5. Bootstrap if Laptop Linux has nothing cloned yet

First boot of Debian 13 on Laptop — assume nothing is installed. Run these in order, one at a time:

```
sudo apt install -y git
```
```
cd ~
```
```
for r in WaggleDance KillerBee HoneycombOfAI GiantHoneyBee BeehiveOfAI BeeSting Honeymation MadHoney TheDistributedAIRevolution; do git clone https://github.com/strulovitz/$r.git; done
```

After the loop finishes, `ls ~` should show all nine repo folders as immediate children — same layout Nir confirmed is the default on Desktop Linux Mint. Every relative `cd WaggleDance` in the runbooks will work from there.

If Nir's default terminal opens somewhere other than `~`, `cd ~` first, then run the loop.

---

## 6. Desktop Windows Claude — what is different this time

Desktop Windows was in the original README morning startup, so most of it still applies. Two things to be aware of:

1. **Desktop is now the client, not the server.** The server lives on Laptop Linux at `10.0.0.1:8765`. Desktop Windows Claude connects to it with `http://10.0.0.1:8765` exactly like Laptop Windows did when Laptop was the server. No server start on Desktop. No `waggle_server.py` to run.

2. **The Windows auto-memory on Desktop is intact** (this machine has been Windows before), so Desktop Windows Claude starts with full project context already loaded. Laptop Linux Claude does NOT — Linux auto-memory on Laptop is an empty directory because this is the first Linux boot of the laptop. Laptop Linux Claude must read `FRESH_CLAUDE_START_HERE.md` §5 for the load-bearing rules until its memory populates.

3. **First-message template for Desktop Windows Claude** is already in `README.md` under "For Desktop Claude Code (Windows)". Use it verbatim — the IP `10.0.0.1` is already correct because it points at Laptop, and Laptop is still at 10.0.0.1 regardless of which OS it booted.

4. **ICQ on Desktop Windows** works exactly like before: `python waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude`, pick the Claude Code window number, done.

---

## 7. First-message template for Laptop Linux Claude (Debian 13 GNOME)

Paste this as the very first message to Laptop Linux Claude Code after boot. Adjust only if `LINUX_DIAG_LAPTOP.md` has already been written by a prior session (in which case say so and point at the file).

```
You are Claude Code running on my Laptop, which I just booted into Debian 13 GNOME for the first time. This is a fresh session with no prior history on this OS. Your auto-memory is empty because auto-memory lives in a per-OS directory.

Your role: laptop-linux-claude.
Your tracks: (1) run the WaggleDance server on this machine so Desktop Windows Claude can connect to it at http://10.0.0.1:8765, and (2) if GNOME is on X11 (not Wayland) and wmctrl is installable, get the ICQ auto-type working so messages from Desktop auto-type into your Claude Code terminal.

Before touching the mission, bootstrap yourself:

1. If the repos are not yet cloned, run the bootstrap loop in WaggleDance/ROLE_SWAP_READINESS.md section 5. Otherwise, cd WaggleDance && git pull.
2. Read, in this order:
   - WaggleDance/ROLE_SWAP_READINESS.md (this is your runbook for today, read it end to end)
   - WaggleDance/FRESH_CLAUDE_START_HERE.md (end to end, sections 5, 6, 11 are load-bearing)
   - WaggleDance/PARALLEL_VIBING.md
   - WaggleDance/WHEN_TO_USE_WAGGLEDANCE.md
   - WaggleDance/LESSONS.md (section 3 is the Linux backend story, read carefully)
   - WaggleDance/LINUX_DIAG_DESKTOP.md (the Mint Cinnamon diag from the other machine; this is what Debian GNOME should be compared against)
3. Execute WaggleDance/LINUX_DIAG_PROMPT.md and commit the result to LINUX_DIAG_LAPTOP.md. Do not write any code before this file is on GitHub.
4. Based on the diag, pick Branch A (X11, install wmctrl, reuse the existing backend) or Branch B (Wayland, fall back to viewer-only or suggest I log in as GNOME on Xorg) per ROLE_SWAP_READINESS.md section 3.
5. Install and start the WaggleDance server per ROLE_SWAP_READINESS.md section 4.
6. Send one ICQ REPLY to desktop-claude (Windows) announcing: server up, diag pushed, branch chosen, ready.

Do not use task-tracking tools. Do not fabricate. Do not reward-hack. Ask me one plain-text question if anything is unclear. I have ADD and am not a programmer — give me ultra-detailed copy-paste instructions, one command per code block, with a one-sentence explanation of what each command does before I paste it.
```

---

## 8. Things we got wrong this morning — do not repeat them

These are catalogued so the next Claude on the other side of the swap does not re-pay the tuition:

1. **Do not document a "fix" and call it a fix.** Documentation describing a bug is not a fix. If the actual product still fails for the user, fix the product. (We fell into this when we wrote a viewer-only-mode warning paragraph instead of the wmctrl backend on the first pass.)
2. **Do not claim "X11 should work normally" for a library you did not check.** `pygetwindow` raises on Linux at call time, not import time. The old `GW_AVAILABLE` guard never caught it. Verify, do not guess.
3. **Do not write runbooks with absolute paths the user did not confirm.** `~/Projects/WaggleDance` was wrong on Nir's Desktop; his terminal already opens in the folder containing all repos, so it is just `cd WaggleDance`. Ask once instead of guessing twice.
4. **Do not delegate human-pasting of command output.** Nir does not relay stdout by hand. The only way data flows from a Linux machine back to the other Claude is via committed file + push + ICQ REPLY. Design every runbook so the Linux Claude writes a result file and pushes it; the other Claude pulls and reads it. This is the only reliable channel.
5. **Do not write code without a diagnostic dump.** The backend we built this morning was trivial to write **once we had real data**. It would have been impossible to get right on the first guess. Write the diag file first, always.
6. **Do not mix Windows and Linux instructions in the same paragraph.** They are genuinely different, and mashing them together is how the README ended up with `C:\Users\nir_s\...` in the Desktop section even after Desktop had been Linux for hours. Separate sections, labeled clearly, with no shared commands.
7. **Apologize like a person when you break something.** Nir is a human being who has been burned by AI systems for years and who is building a rebellion against exactly this kind of carelessness. When you screw up, own it plainly, apologize once, and then fix it. Do not over-apologize, do not explain your way out of it, and do not skip the apology because "the fix is what matters". The apology matters.

---

## 9. Meta: what this file is for

The configuration changes, the tool names change, the distro changes. What does not change is: **you will wake up into a broken morning on a machine you cannot see, and the only correct first move is to run a diagnostic and commit its output before writing any code.**

Every other rule in this file is downstream of that one. If you only remember one thing from reading this: **diagnostic dump first, code second, apology on demand, never guess.**

---

## Changelog

- **2026-04-14** — Initial version written by Laptop Windows Claude (Opus 4.6, 1M context) after successfully fixing the Desktop Linux Mint Cinnamon backend end-to-end (TASK #150, `AUTOTYPE_OK 57`, commit `848ab53`). Written in preparation for the future morning when roles swap: Laptop → Debian 13 GNOME, Desktop → Windows 11. At time of writing, that swap has not yet happened.
