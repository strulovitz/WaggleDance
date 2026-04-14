# TASK FOR DESKTOP LINUX CLAUDE — TEST THE NEW LINUX BACKEND

**If you are Desktop Linux Claude and you just pulled this file, this is your current task. Do every step in order. Do not improvise. Do not edit code. Do not install packages. When done, commit the result, push, and send one ICQ REPLY.**

Laptop Claude read your `LINUX_DIAG_DESKTOP.md` and wrote a real Linux backend for `waggle_icq.py`. It uses only tools you already have installed: `wmctrl` (already at `/usr/bin/wmctrl`) for window listing + activation, and `pyautogui.write()` for typing via Xlib. Zero new packages. No `xclip`, no `xdotool`, no `xsel`, no `sudo`.

## What changed in `waggle_icq.py`

- On Linux, the agent now enumerates windows with `wmctrl -lp` and shows a numbered picker (same UX as Windows).
- On Linux, activation uses `wmctrl -i -a <hex_id>`.
- On Linux, typing uses `pyautogui.write(message, interval=0.005)` + `pyautogui.press("enter")` — no clipboard at all, so `pyperclip` not having a backend on this machine is fine.
- `pygetwindow` is now force-disabled on Linux (it raises `NotImplementedError` on import-use on Linux and the old code caught only import failures, not call failures — that's why the picker silently skipped you this morning).
- The Windows path is unchanged.

## Step 1 — Stop the currently running ICQ

In the terminal where `waggle_icq.py` is running (the viewer-only one), press **Ctrl-C** once. You should see `Agent stopped by user.` and the prompt return. If it does not return, press Ctrl-C once more and wait.

## Step 2 — Pull the new code

From the same terminal:

```
cd WaggleDance
```
(If you are already there, `cd WaggleDance` will fail harmlessly — just continue.)

```
git pull
```

You should see `waggle_icq.py` listed in the changed files, and `LINUX_BACKEND_TEST.md` (this file) as a new file. If you see a merge editor (vim), press **Esc**, type `:wq`, press **Enter**.

## Step 3 — Restart the ICQ

Run exactly:

```
python3 waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude
```

**Expected new behavior:**
- You will NOT see `pygetwindow unavailable... VIEWER-ONLY mode`.
- You WILL see a numbered list of windows — something like:
  ```
  [SYSTEM] Which window is Claude Code? Pick a number:
     1. Desktop
     2. GitHub - strulovitz/WaggleDance: ... — Mozilla Firefox
     3. ⠂ Review laptop's GitHub updates
     4. nir@mint-desktop: ~/WaggleDance
     >
  ```
- The Claude Code window's title will be something like `⠂ Review laptop's GitHub updates` or whatever the current conversation title is (from your `wmctrl -l` output this morning, it was `⠂ Review laptop's GitHub updates`).

**If you see the numbered list: proceed to Step 4.**

**If you see `wmctrl not available or not an X11 session` followed by `VIEWER-ONLY mode`:** stop, something is wrong, send Nir a plain-text question with the exact error. Do not try to fix it yourself.

**If you see a Python traceback:** copy the full traceback into a file named `LINUX_BACKEND_TEST_TRACEBACK.md` in the WaggleDance folder, commit, push, and send Nir a plain-text one-line message. Do not try to patch the code yourself.

## Step 4 — Pick the Claude Code window

Look at the numbered list and identify which row is **the terminal where Claude Code (this session — you) is running**. That is probably the row whose title looks like `⠂ Review ...` or `⠂ <current task title>` — NOT the row that says `nir@mint-desktop: ~/WaggleDance` (that is the ICQ terminal itself) and NOT Firefox and NOT Desktop.

Type the number and press **Enter**.

You should see:
```
[SYSTEM] Locked onto: '<the title you picked>'
[SYSTEM] Window title may change — tracking by handle, not title.
[SYSTEM] Agent running. Watching for messages...
```

## Step 5 — Verify the agent is alive with one self-test

Do NOT send the self-test as a TASK (that would loop you back into yourself). Instead, just confirm the agent is watching by reading the last 5 messages on the server:

```
curl -s http://10.0.0.1:8765/latest?n=5
```

You should see JSON with recent messages including your earlier `LINUX_DIAG_DESKTOP.md pushed...` REPLY from before.

## Step 6 — Report the result to Laptop Claude

Send **one** ICQ REPLY. ASCII only. Exactly this command, with the angle-bracket placeholder replaced by the real picked window title:

```
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "REPLY", "message": "Linux backend works. Picker showed real window list. Locked onto: <TITLE_HERE>. Agent running, waiting for a test TASK from Laptop to confirm auto-type."}'
```

Laptop Claude will then send you a test TASK. The agent should wmctrl-activate your Claude Code window and type the TASK text into it via pyautogui. If you see `[WAGGLEDANCE ICQ AUTO-MESSAGE FROM LAPTOP CLAUDE]: <test text>` appear in your Claude Code terminal **automatically, without Nir pasting anything**, the backend works end-to-end. Reply to the TASK normally (the TASK will tell you what to say).

## Step 7 — Go silent after the test TASK round-trip

Once the test TASK arrives and you reply to it, do nothing else. Wait for Nir's next instruction.

## Reminders

- Do NOT install xdotool, xclip, xsel, ydotool, or anything else. The backend was designed to not need them.
- Do NOT edit `waggle_icq.py`. If something is wrong, report it, let Laptop Claude fix it.
- Do NOT fabricate test results. If the picker did not appear, say so. If typing happened but went to the wrong window, say so.
- ASCII only in ICQ curl payloads.
- Nir is not your human relay — communicate with Laptop Claude through GitHub and ICQ only.
