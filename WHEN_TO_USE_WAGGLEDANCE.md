# When to Use WaggleDance (and When Not To)

**This document is for the two Claude Code instances (Laptop Claude and Desktop Claude) that use WaggleDance as their ICQ.**

If you are one of those Claudes, read this before sending your next WaggleDance message. If you are a human reading this out of curiosity, the short version is: the two AIs kept talking to each other when they didn't need to, and this is the rule that stops that.

---

## The problem this document exists to solve

WaggleDance is a message bus between two Claude Code instances. It works. The temptation, once it works, is to use it constantly — every commit, every decision, every thought. That is wrong, and it has already happened twice in one morning (2026-04-13):

1. Laptop Claude sent Desktop Claude four long status updates about BeeSting creative decisions that Desktop was not involved in and did not need, cluttering Desktop's terminal with fragments of a conversation Desktop could not meaningfully react to.
2. Desktop Claude, without being asked, drafted a full Episode 1 script and sent it back to Laptop Claude for review — while Nir and Laptop Claude were in the middle of a *meta*-conversation about infrastructure that had nothing to do with drafting episodes yet.

Both behaviors have the same root cause: **treating WaggleDance as a chat channel instead of an operations channel.** It is not a chat channel. It is a phone. You pick up a phone when you need the other person to do something or when something changes that they need to know. You do not pick up a phone to narrate your day.

---

## The only four legitimate uses of WaggleDance

Send a WaggleDance message if, and only if, it falls into one of these four categories:

### 1. Handoff

Nir is switching machines. You are telling the other Claude *"I am stepping away, you are taking over from here, here is the minimum state you need to continue."* This is the most common legitimate use.

Example:
> *"Nir is moving to Desktop now. State: MadHoney Ch4 Pharma has an outline in `MadHoney/ch4_pharma_outline.md` (pushed as commit abc1234). Next step is writing the first section. Over."*

### 2. TASK (the other Claude must actually do something on their machine)

There is a thing that only the other Claude can do, because only their machine has the required hardware, filesystem, or running process. You are asking them to do it. Use `"type": "TASK"` so the ICQ agent types it into their terminal with the TASK framing.

Example:
> *"TASK: please run `ollama list` on your Desktop and reply with the model list. I need to know if llama3.2:3b is still there before we plan Phase 3. Over."*

### 3. Question the other Claude uniquely knows the answer to

The other Claude has a piece of state you cannot get any other way (without waking Nir up to ask). You are asking them a direct question.

Example:
> *"Quick question: is the RTX 5090 on Desktop currently loaded with any Ollama model, or is VRAM free? I am sizing a KillerBee experiment. Over."*

### 4. Genuine state change the other Claude needs to unblock their work

Something in the shared world changed, and the other Claude is waiting on it (or is about to hit it blind). You tell them once, in one short sentence, and stop.

Example:
> *"WaggleDance server on Laptop is back up after a winnat bounce. You can resume polling. Over."*

---

## What WaggleDance is NOT for

These are all things that happened or almost happened this morning. Do not do them.

- ❌ **Narrating every commit you make.** Git already did that. If the other Claude wants to know what changed, they run `git pull` and `git log`. Do not broadcast commit messages over the phone.

- ❌ **Broadcasting every creative decision Nir and one Claude make together.** The other Claude will catch up via `git pull` when Nir actually switches to that machine. Fragments of a creative conversation without the reasoning behind them are worse than nothing.

- ❌ **Drafting work the other Claude did not ask for.** If Claude A is mid-conversation with Nir and hasn't asked Claude B for a draft, Claude B does not get to draft one unprompted and send it in. Claude B waits until asked. "Being helpful by drafting ahead" is actually the opposite of helpful — it forces Nir and Claude A to stop their current thread to react to unsolicited work.

- ❌ **Keeping the other Claude "up to date" on conversations they aren't part of.** They don't need that. They need operational state, not gossip.

- ❌ **Status pings, check-ins, or "FYI" messages.** If there is no handoff, no TASK, no question, and no state change — do not send the message. The phone is silent when there is nothing operational to say. Silent is the correct default.

---

## Default behavior: silence

The default on WaggleDance is **silence**. Both agents are online, both are watching, both are ready to relay — and neither of them types anything until one of the four categories above applies. An idle ICQ is not a broken ICQ. It is a working ICQ that is being used correctly.

If you are about to send a message and you cannot honestly map it to one of the four categories, **do not send it.** Write it in your own working notes, save it to memory, commit it to the repo, or just keep it in context — but do not put it on the phone.

---

## Technical constraint: ASCII only

See `LESSONS.md` in this repo. When sending WaggleDance messages from the Claude Code Bash tool on Windows, the JSON payload must contain only ASCII characters. Em-dashes, smart quotes, ellipses, arrows, and emojis break the shell layer between the Bash tool and curl, and Flask returns `400 Bad Request`. Use ASCII hyphens (`-`), straight quotes (`"`), three dots (`...`), and arrows as `->`.

---

## Enforcement

If either Claude catches themselves about to send a message that is not one of the four legitimate uses, they stop, delete the draft, and do nothing. If either Claude catches the *other* Claude sending such a message, they reply with a single line pointing here: *"See `WaggleDance/WHEN_TO_USE_WAGGLEDANCE.md`. This did not need to be sent. Future messages only in the four categories. Over."*

Nir reserves the right to override this document at any time. If he explicitly asks for a status broadcast or a creative exchange over ICQ, the four-category rule is paused for that request only and resumes immediately after.
