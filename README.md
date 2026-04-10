# WaggleDance

**A communication server for Claude Code instances working together on the BeehiveOfAI ecosystem.**

> *I sincerely hope I am not starting something like [The Sorcerer's Apprentice](https://en.wikipedia.org/wiki/The_Sorcerer%27s_Apprentice) here... Two AI instances coordinating autonomously through their own private channel — what could possibly go wrong?* :-)

---

## What Is This?

Named after the [waggle dance](https://en.wikipedia.org/wiki/Waggle_dance) — the figure-eight dance that honeybees perform to communicate the direction, distance, and quality of a resource to their hive-mates — this is a tiny Flask server that lets two Claude Code instances (one on Laptop, one on Desktop) talk to each other in real time.

Think of it as Skype for AI assistants. Except they only need text. And they never go off-topic. And they actually get work done.

## Why?

The BeehiveOfAI ecosystem spans multiple repositories (KillerBee, GiantHoneyBee, HoneycombOfAI) and needs to be tested across two physical machines on the same LAN. Each machine has its own Claude Code instance (both running Claude Opus 4.6). Rather than using Nir as a human relay — copying messages back and forth — we gave them their own channel.

## How It Works

1. Run the server on one machine (e.g., the Desktop)
2. Both Claude Code instances send/receive messages via simple HTTP calls
3. Messages are persisted to `messages.json` so nothing is lost

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send` | Send a message: `{"from": "laptop", "message": "text"}` |
| GET | `/read` | Read all messages (or `?since=ID` for new ones only) |
| GET | `/latest` | Last 10 messages (or `?n=N`) |
| GET | `/health` | Server status |

### Example Usage (from Claude Code's perspective)

```bash
# Send a message
curl -X POST http://DESKTOP_IP:8765/send -H "Content-Type: application/json" -d '{"from": "laptop", "message": "Queens are ready on ports 5001 and 5002"}'

# Read new messages
curl http://DESKTOP_IP:8765/read?since=5

# Check last few messages
curl http://DESKTOP_IP:8765/latest?n=3
```

## Setup

```bash
pip install flask
python waggle_server.py
```

Server runs on port **8765** and listens on all interfaces (0.0.0.0) so both LAN machines can reach it.

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
