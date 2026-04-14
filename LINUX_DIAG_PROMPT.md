# Linux Diagnostic Prompt — for Desktop Linux Claude (and later Laptop Linux Claude)

**Who this is for:** a Claude Code session running on one of Nir's Linux machines. Laptop Claude (on Windows) needs to know exactly what is installed and what display server is running before writing a Linux window-picker backend for `waggle_icq.py`. Do not guess, do not improvise — run the exact commands below, capture the output, commit it, push it.

## Step 1 — Identify which machine you are on

Run this and remember the answer:

```
hostname && uname -a && cat /etc/os-release | head -5
```

You should be able to tell from the output whether you are on **Desktop (Linux Mint 22.2 Cinnamon)** or **Laptop (Debian 13 GNOME)**. If you are unsure, ask Nir one question and wait for the answer.

## Step 2 — Gather environment info

Run each of these commands **one at a time** and capture the full stdout of each. Do not skip any. Do not add flags. If a command is not found, capture that too (`command not found` is a valid answer and tells Laptop Claude to `apt install` it).

```
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"
```
```
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
```
```
echo "DISPLAY=$DISPLAY"
```
```
echo "XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP"
```
```
loginctl show-session $(loginctl | awk '/seat/ {print $1; exit}') -p Type -p Remote 2>&1 || true
```
```
command -v wmctrl || echo "wmctrl: NOT INSTALLED"
```
```
command -v xdotool || echo "xdotool: NOT INSTALLED"
```
```
command -v ydotool || echo "ydotool: NOT INSTALLED"
```
```
command -v xdpyinfo || echo "xdpyinfo: NOT INSTALLED"
```
```
command -v wl-copy || echo "wl-copy: NOT INSTALLED"
```
```
command -v xclip || echo "xclip: NOT INSTALLED"
```
```
command -v xsel || echo "xsel: NOT INSTALLED"
```
```
python3 --version
```
```
python3 -c "import pyautogui; print('pyautogui', pyautogui.__version__)" 2>&1 || echo "pyautogui: NOT IMPORTABLE"
```
```
python3 -c "import pyperclip; print('pyperclip', pyperclip.__version__)" 2>&1 || echo "pyperclip: NOT IMPORTABLE"
```
```
python3 -c "import pygetwindow; print('pygetwindow', pygetwindow.__version__)" 2>&1 || echo "pygetwindow: NOT IMPORTABLE"
```
```
wmctrl -l 2>&1 | head -20 || true
```
```
xdotool search --name "" 2>&1 | head -5 || true
```

## Step 3 — Write the results into a file in the WaggleDance repo

From the directory that contains the `WaggleDance` folder (same directory where your terminal opened by default — Nir confirmed this is the default on both Linux machines), do:

```
cd WaggleDance
```
```
git pull
```

Then create a file named **exactly** one of these, depending on which machine you are on:

- `LINUX_DIAG_DESKTOP.md` — if you are on Desktop (Linux Mint 22.2)
- `LINUX_DIAG_LAPTOP.md` — if you are on Laptop (Debian 13)

The file must have this structure (fill in every section with the literal output from Step 2 — do not summarize, do not reformat, do not remove error lines):

```markdown
# Linux Diagnostic Results — <Desktop or Laptop>

## hostname + uname + os-release
<paste output>

## Session / display server
XDG_SESSION_TYPE=...
WAYLAND_DISPLAY=...
DISPLAY=...
XDG_CURRENT_DESKTOP=...

loginctl output:
<paste output>

## Tools installed
wmctrl: <path or NOT INSTALLED>
xdotool: <path or NOT INSTALLED>
ydotool: <path or NOT INSTALLED>
xdpyinfo: <path or NOT INSTALLED>
wl-copy: <path or NOT INSTALLED>
xclip: <path or NOT INSTALLED>
xsel: <path or NOT INSTALLED>

## Python
python3: <version>
pyautogui: <version or NOT IMPORTABLE>
pyperclip: <version or NOT IMPORTABLE>
pygetwindow: <version or NOT IMPORTABLE>

## Live window enumeration attempts
wmctrl -l (first 20 lines):
<paste output, including errors>

xdotool search --name "" (first 5 lines):
<paste output, including errors>
```

## Step 4 — Commit and push

```
git add LINUX_DIAG_DESKTOP.md
```
(or `LINUX_DIAG_LAPTOP.md` on Laptop)

```
git commit -m "diag: Linux environment info for waggle_icq backend work"
```
```
git push
```

## Step 5 — Send one ICQ REPLY to Laptop Claude

ASCII only. Exactly one message. Example:

```
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "REPLY", "message": "Diag pushed: LINUX_DIAG_DESKTOP.md committed to WaggleDance master. Ready for backend instructions."}'
```

## Rules

- **Do not install anything.** This step is read-only diagnostics. Laptop Claude will decide which packages are needed based on what you report.
- **Do not edit waggle_icq.py.** Not yet. Laptop Claude writes the backend, pushes it, and only then do you pull and test.
- **Do not fabricate.** If a command errors or returns nothing, write that exactly. A missing tool is valuable information. A made-up version number is poison.
- **Do not use task-tracking tools.** Nir has ADD and they clutter the terminal.
- **If anything is unclear, send Nir one plain-text question and wait.**
