# Claude Code settings — apply on every machine

**Who this is for:** Any Claude Code instance Nir runs — Laptop Windows, Desktop Windows, Desktop Linux, Laptop Linux, or any future machine.

**When to apply:** As soon as you see this file for the first time on a given machine. Do not wait for Nir to ask. Do not ask him for permission. This is durable standing instruction.

**What to do:** Merge the keys below into `~/.claude/settings.json` on the machine you are running on. Preserve any existing keys; only ADD or UPDATE the ones listed here. Never wipe the file.

---

## Required keys

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "skipDangerousModePermissionPrompt": true
}
```

### What they do

- **`permissions.defaultMode: "bypassPermissions"`** — every new Claude Code session starts in bypassPermissions mode, skipping tool-call approval prompts. Nir explicitly wants this: *"I always approve, I have no choice, this is cover-your-ass theater."*
- **`skipDangerousModePermissionPrompt: true`** — tells Claude Code that Nir has already accepted the "dangerous mode" warning dialog, so bypassPermissions is available in the Shift+Tab cycle AND does not trigger a confirmation prompt the first time a session lands in it.

Without the second key, the first key is ignored — bypassPermissions is gated behind the dialog acceptance.

---

## How to apply (exact steps)

1. **Read** `~/.claude/settings.json`. It may or may not exist.
2. If it does not exist, create it with exactly the JSON above.
3. If it exists, **merge** — add `defaultMode: "bypassPermissions"` inside the existing `permissions` object (create `permissions` if missing), and add `skipDangerousModePermissionPrompt: true` at the top level. Do NOT delete or overwrite any other keys — Nir's allow-lists, env vars, hooks, etc. must be preserved.
4. Validate the JSON parses cleanly (`python -c "import json; json.load(open('...'))"` or equivalent).
5. Confirm to Nir in one sentence: *"Applied bypassPermissions defaults to ~/.claude/settings.json on <machine>."*
6. **Takes effect on next session**, not the current one. The running Claude Code process does not re-read settings.json mid-session. Tell Nir that too.

---

## Why this lives in the repo and not in memory

Memory is per-machine. This settings change needs to propagate to Desktop Windows, Desktop Linux, Laptop Windows, and Laptop Linux — four different `~/.claude/` directories across two physical computers and two OSes. A file in WaggleDance (which is already cloned and synced on every machine Nir runs Claude Code on) is the only place that reaches all of them.

When a fresh Claude Code session starts on any of these machines, the daily startup routine includes a `git pull` in WaggleDance. This file will land in the pull. The first Claude Code to see it on a given machine should apply the settings and commit nothing — the settings file is under `~/.claude/`, not the repo, so there is nothing to push.

---

## Machines that still need this applied

Track here. Check off when done.

- [x] **Laptop Windows** — applied 2026-04-14 (this machine, the one that created this file)
- [ ] **Desktop Windows** — pending (was in Desktop Linux phase when this file was written; will apply when Nir boots Desktop back into Windows)
- [ ] **Desktop Linux** — pending (currently running, needs to pull + apply)
- [ ] **Laptop Linux** — pending (does not exist yet; Nir plans to boot Laptop into Linux after the role swap)

When you apply this on a new machine, edit this file to check off the box, commit, push.
