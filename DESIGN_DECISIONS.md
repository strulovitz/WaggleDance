# WaggleDance Design Decisions

## Nir's Instructions (2026-04-10)

### ICQ-Style Chat Viewer
- READ ONLY for Nir — he cannot type into it on any machine
- Shows full conversation from BOTH sides on BOTH machines (symmetrical)
- Each user has a name, color, and emoji
- Saved to a log file continuously on each machine
- Periodically pushed to GitHub (every 10 minutes or every 30 messages)
- Separate from the Claude Code terminal window

### User Identity

| Machine | Name | Windows Emoji | Linux Emoji | Color |
|---------|------|---------------|-------------|-------|
| Laptop | Laptop Windows | 🌼 | 🌻 | Yellow |
| Desktop | Desktop Windows | 🌷 | 🌹 | Magenta/Pink |

Timestamps in gray.

### Loop Prevention: Option D (TASK/REPLY + Max Chain)
- Messages are tagged as TASK (type into Claude Code) or REPLY (show in ICQ only)
- Max chain length: 5 rounds (10 messages). After that, agent stops and waits for Nir to press Enter.
- Two layers of protection: tags handle normal case, chain limit is emergency brake.

### Architecture (terminals per machine)
- **Laptop:** Claude Code + WaggleDance server + Agent/ICQ = 3 terminals
- **Desktop:** Claude Code + Agent/ICQ = 2 terminals

### Naming from ICQ
- ICQ logo was a flower — we use flower emojis
- Connects to WaggleDance (bees report where flowers are)
