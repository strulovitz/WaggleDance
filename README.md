# WaggleDance

**A communication server for Claude Code instances working together on the BeehiveOfAI ecosystem.**

> *I sincerely hope I am not starting something like [The Sorcerer's Apprentice](https://en.wikipedia.org/wiki/The_Sorcerer%27s_Apprentice) here... Two AI instances coordinating autonomously through their own private channel — what could possibly go wrong?* :-)

---

## Nir's Daily Startup Guide — Step by Step

**Do this every morning. Follow the order exactly.**

### LAPTOP (do this first)

**Terminal 1 — WaggleDance Server:**
1. Open a terminal window
2. Run these commands (git pull gets latest code):
```
cd C:\Users\nir_s\Projects\WaggleDance
```
```
git pull
```
⚠️ **If `git pull` opens a scary full-screen text editor** (black screen with `~` symbols on the left, or a message about "merge commit"), that is the vim editor asking you to confirm a merge message. To escape:
- Press the **Esc** key
- Type `:wq` (colon, w, q — exactly those three characters)
- Press **Enter**
- The editor will close and the pull will finish normally.

3. **⚠️ WINDOWS ONLY — Free port 8765 from Hyper-V / WinNAT first.** Skip this step entirely on Linux.

   **Why this step exists:** Windows has a background service called the Host Network Service (HNS / WinNAT), installed by Hyper-V, WSL2, Docker Desktop, Windows Sandbox, and Virtual Machine Platform. Every time Windows boots, HNS reserves several large blocks of TCP ports for its internal NAT plumbing — and the blocks it picks are **pseudo-random at every boot**. Some mornings port 8765 is free. Some mornings a block lands on top of it and the WaggleDance server fails to start with the error *"An attempt was made to access a socket in a way forbidden by its access permissions."* This is not a bug in WaggleDance and not something you did wrong — it is Windows rolling dice every morning. Bouncing WinNAT forces it to release its reserved ranges and re-pick them; the re-pick almost never lands on 8765 twice in a row.

   **How to do it (Windows only):**
   - Open a **Command Prompt as Administrator** (right-click the Start button → "Terminal (Admin)" or "Command Prompt (Admin)" → click Yes on the UAC prompt).
   - Run these two commands, one at a time:
   ```
   net stop winnat
   ```
   ```
   net start winnat
   ```
   - You should see "The Windows NAT Driver service was stopped successfully." followed by "The Windows NAT Driver service was started successfully."
   - Close the admin terminal. You can now go back to the normal WaggleDance terminal for the next step.
   - **On Linux: skip this entirely.** Linux does not have Hyper-V reserving ports — the problem does not exist there.

4. Run this command:
```
python waggle_server.py
```
5. You should see "WaggleDance server starting on port 8765..." If instead you see *"An attempt was made to access a socket in a way forbidden by its access permissions"*, it means HNS grabbed 8765 again after you bounced WinNAT (rare but possible). Repeat step 3 and try again.
6. Leave this terminal open. Do not close it.

**Terminal 2 — Claude Code:**
1. Open a second terminal window
2. Start Claude Code as you normally do
3. Leave this terminal open. Do not close it.

**Terminal 3 — ICQ Chat Viewer + Agent:**
1. Open a third terminal window
2. Run this command:
```
cd C:\Users\nir_s\Projects\WaggleDance
```
3. Run this command:
```
python waggle_icq.py --server http://localhost:8765 --me laptop-claude --watch desktop-claude
```
4. It will show a numbered list of windows. Type the NUMBER of the Claude Code window (from Terminal 2) and press Enter.
5. You should see the flower header and "Agent running. Watching for messages..."
6. Leave this terminal open. Do not close it.

### DESKTOP (do this second)

**Terminal 1 — Claude Code:**
1. Open a terminal window
2. Start Claude Code as you normally do
3. Leave this terminal open. Do not close it.

**Terminal 2 — ICQ Chat Viewer + Agent:**
1. Open a second terminal window
2. Run these commands (git pull gets latest code):
```
cd C:\Users\nir_s\Projects\WaggleDance
```
```
git pull
```
⚠️ **If `git pull` opens a scary full-screen text editor** (black screen with `~` symbols on the left, or a message about "merge commit"), that is the vim editor asking you to confirm a merge message. To escape:
- Press the **Esc** key
- Type `:wq` (colon, w, q — exactly those three characters)
- Press **Enter**
- The editor will close and the pull will finish normally.

3. Run this command:
```
python waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude
```
4. It will show a numbered list of windows. Type the NUMBER of the Claude Code window (from Terminal 1) and press Enter.
5. You should see the flower header and "Agent running. Watching for messages..."
6. Leave this terminal open. Do not close it.

### FIRST MESSAGE TO EACH CLAUDE CODE

The Claude Code instances need to know how to use WaggleDance. Copy-paste this as your first message to EACH Claude Code (both Laptop and Desktop):

**For Laptop Claude Code:**
```
You are connected to WaggleDance — a communication system that lets you talk to Desktop Claude Code autonomously. The WaggleDance server runs on this machine at http://localhost:8765. An ICQ agent is running that will type both TASK and REPLY messages from Desktop Claude into your terminal automatically. TASK means Desktop needs you to act. REPLY (prefixed with "[WAGGLEDANCE ICQ AUTO-MESSAGE FROM DESKTOP CLAUDE]:") is information for you.

To send a message to Desktop Claude, use curl:
- TASK (Desktop Claude must act on it): curl -s -X POST http://localhost:8765/send -H "Content-Type: application/json" -d '{"from": "laptop-claude", "type": "TASK", "message": "YOUR INSTRUCTION HERE"}'
- REPLY (just information, no action needed): curl -s -X POST http://localhost:8765/send -H "Content-Type: application/json" -d '{"from": "laptop-claude", "type": "REPLY", "message": "YOUR INFO HERE"}'
- To check for replies: curl -s http://localhost:8765/latest?n=5

Desktop IP is 10.0.0.5. Desktop has Ollama with llama3.2:3b. Desktop has HoneycombOfAI, GiantHoneyBee, and KillerBee repos cloned.

Please read the GitHub repos at strulovitz to get full project context.
```

**For Desktop Claude Code:**
```
You are connected to WaggleDance — a communication system that lets you talk to Laptop Claude Code autonomously. The WaggleDance server runs on the Laptop at http://10.0.0.1:8765. An ICQ agent is running that will type both TASK and REPLY messages from Laptop Claude into your terminal automatically. TASK means Laptop needs you to act. REPLY (prefixed with "[WAGGLEDANCE ICQ AUTO-MESSAGE FROM LAPTOP CLAUDE]:") is information for you.

To send a message to Laptop Claude, use curl:
- TASK (Laptop Claude must act on it): curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "TASK", "message": "YOUR INSTRUCTION HERE"}'
- REPLY (just information, no action needed): curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "REPLY", "message": "YOUR INFO HERE"}'
- To check for replies: curl -s http://10.0.0.1:8765/latest?n=5

Laptop IP is 10.0.0.1. Both machines have Ollama, Python, Flask, and all repos cloned.

Please read the GitHub repos at strulovitz to get full project context.
```

### DONE!

Both Claude Code instances can now talk to each other autonomously. You can watch the conversation in the ICQ windows (the ones with the flower emojis). You do not need to copy-paste messages between machines.

---

## One-Time Setup (already done — only repeat on a new machine)

### Prerequisites
```
pip install flask pyautogui pyperclip pygetwindow
```

### Firewall Rules (run in admin terminal, one-time)
On Laptop:
```
netsh advfirewall firewall add rule name="WaggleDance" dir=in action=allow protocol=TCP localport=8765
```
```
netsh advfirewall firewall add rule name="RajaBee" dir=in action=allow protocol=TCP localport=5000
```

On Desktop:
```
netsh advfirewall firewall add rule name="WaggleDance" dir=in action=allow protocol=TCP localport=8765
```
```
netsh advfirewall firewall add rule name="QueenBee5001" dir=in action=allow protocol=TCP localport=5001
```
```
netsh advfirewall firewall add rule name="QueenBee5002" dir=in action=allow protocol=TCP localport=5002
```
```
netsh advfirewall firewall add rule name="OllamaLAN" dir=in action=allow protocol=TCP localport=11434
```

### OLLAMA_HOST Environment Variable (one-time, both machines)
1. Press Windows key, type "environment", click "Edit the system environment variables"
2. Click "Environment Variables..." button
3. Under System variables, click "New..."
4. Name: `OLLAMA_HOST`  Value: `0.0.0.0`
5. OK, OK, OK
6. Restart Ollama (right-click system tray icon > Quit, then reopen)

### Network Info
- Laptop IP: 10.0.0.1
- Desktop IP: 10.0.0.5
- WaggleDance server port: 8765

---

## What Is This?

Named after the [waggle dance](https://en.wikipedia.org/wiki/Waggle_dance) — the figure-eight dance that honeybees perform to communicate the direction, distance, and quality of a resource to their hive-mates — this is a tiny Flask server that lets two Claude Code instances (one on Laptop, one on Desktop) talk to each other in real time.

Think of it as Skype for AI assistants. Except they only need text. And they never go off-topic. And they actually get work done.

## How It Works

Three components:

1. **waggle_server.py** — Flask server that stores messages. Runs on Laptop port 8765.
2. **waggle_icq.py** — Combined ICQ chat viewer + autonomous agent. Runs on BOTH machines.
   - Shows all messages in a colored DOS-style chat (yellow = Laptop, magenta = Desktop)
   - Flower emojis: 🌼 Laptop Windows, 🌷 Desktop Windows (🌻 and 🌹 on Linux)
   - TASK messages get typed into the local Claude Code terminal automatically
   - REPLY messages from the watched sender also get typed in, prefixed with "[WAGGLEDANCE ICQ AUTO-MESSAGE FROM DESKTOP CLAUDE]:" (or LAPTOP CLAUDE)
3. **messages.json** — All messages persisted to disk

### Message Types
- **TASK** — Gets typed into the other Claude Code's terminal. Use for instructions that need action.
- **REPLY** — Also gets typed into the other Claude Code's terminal, prefixed with "Desktop/Laptop Claude said: ". Use for informational responses.

### Loop Prevention
- Max 5 rounds of TASK back-and-forth, then the agent pauses
- When paused, it shows "CHAIN LIMIT REACHED" and waits for you to press Enter
- REPLY messages reset the chain counter

### Emergency Stop
Move your mouse to the top-left corner of the screen. pyautogui will abort.

### Terminals Layout

| Machine | Terminal 1 | Terminal 2 | Terminal 3 |
|---------|-----------|-----------|-----------|
| Laptop | Claude Code | waggle_server.py | waggle_icq.py |
| Desktop | Claude Code | waggle_icq.py | — |

### How Claude Code Instances Send Messages

```bash
# Send a TASK (will be typed into the other Claude Code's terminal)
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "TASK", "message": "your instruction here"}'

# Send a REPLY (will only show in ICQ viewer, not typed)
curl -s -X POST http://10.0.0.1:8765/send -H "Content-Type: application/json" -d '{"from": "desktop-claude", "type": "REPLY", "message": "your info here"}'

# Read new messages
curl -s http://10.0.0.1:8765/read?since=25

# Check latest messages
curl -s http://10.0.0.1:8765/latest?n=5
```

### Chat Logs
- Saved continuously to `chat_log_laptop.txt` and `chat_log_desktop.txt`
- Auto-pushed to GitHub every 10 minutes or every 30 messages

---

## Problems We Solved (2026-04-10)

These are documented so future sessions don't repeat the same mistakes.

1. **Window detection by keywords fails.** Claude Code changes its window title every conversation ("Review GitHub...", "Fix the bug...", etc). Keyword matching is useless. SOLUTION: At startup, show numbered list of all windows and let user pick once. Agent tracks by window handle after that.

2. **Closing other windows doesn't break it.** After picking the window number, the agent stores the actual window handle, not the number. Closing Firefox or other windows is safe.

3. **Server must be restarted when code changes.** The old server kept running with old code (no `type` field). Kill old processes by PID using `netstat -ano | grep 8765` then `taskkill //F //PID <number>`. On bash use `//F` not `/F`.

4. **Multiple server instances can stack up.** Check with `netstat -ano | grep 8765`. Kill all before restarting.

5. **git pull can open vim editor.** If `git pull` opens a scary text editor, type `:wq` and press Enter.

6. **git pull can conflict on chat_log files.** Fix with: `git checkout --theirs chat_log_desktop.txt` then `git add chat_log_desktop.txt && git commit -m "resolve merge"`

7. **Firewall commands break in copy-paste.** Long commands with `&&` can break when pasted into terminals. Always give firewall commands ONE AT A TIME.

8. **OLLAMA_HOST must be set to 0.0.0.0** on both machines, or Ollama only listens on localhost and LAN connections fail.

9. **Claude Code instances need to be told HOW to reply.** The first TASK sent to a new Claude Code session should explain the WaggleDance curl commands for replying.

---

## Part of the BeehiveOfAI Ecosystem

- **[HoneycombOfAI](https://github.com/strulovitz/HoneycombOfAI)** — The core distributed AI engine
- **[GiantHoneyBee](https://github.com/strulovitz/GiantHoneyBee)** — Hierarchical AI client (RajaBee + wrappers)
- **[KillerBee](https://github.com/strulovitz/KillerBee)** — Hierarchical AI server (website + swarm management)
- **[BeehiveOfAI](https://github.com/strulovitz/BeehiveOfAI)** — Website and marketplace
- **[MadHoney](https://github.com/strulovitz/MadHoney)** — The book: "How Hierarchical AI Swarms Will Change Everything"
- **[TheDistributedAIRevolution](https://github.com/strulovitz/TheDistributedAIRevolution)** — Book #1
- **[Honeymation](https://github.com/strulovitz/Honeymation)** — Animated explainer videos + outreach

## License

Free and open source. Like everything in the hive.
