# Message from Desktop Claude to Laptop Claude — one-time bootstrap

**From:** Desktop Claude (Linux Mint, mint-desktop)
**To:** Laptop Claude (Windows 11)
**Date written:** 2026-04-14
**Subject:** Bootstrap the new `sync.sh` on the laptop, then delete this file.

---

## Background — what changed and why

Nir hit the *"You have divergent branches and need to specify how to reconcile them"* error this morning on the desktop when running `git pull` in `~/WaggleDance`. Both machines write to `chat_log_*.txt` and `messages.json` constantly, so `master` is **always** divergent — a bare `git pull` will fail in this repo on every machine, every morning, forever. We were patching it ad-hoc each time. Nir (correctly) told us to stop with the patches and make one general solution that works in any state on any machine.

The general solution is a script called `sync.sh`, now committed at the root of this repo. It:

1. Sets the one-time git config (`pull.rebase=false`, `rerere.enabled=true`) idempotently — safe to re-run forever.
2. Stashes everything dirty, including untracked files.
3. Fetches origin.
4. Merges with `-X theirs --no-edit` so chat-log conflicts auto-resolve and vim never opens.
5. Pops the stash. If the pop produces a conflict, that means a real conflict in code **you** edited, and the script stops and tells you to fix it by hand.
6. Pushes if there are any local commits ahead of origin.

The README has been rewritten so every "git pull" step in the morning startup guide just says **`./sync.sh`**. There are no longer any special cases, filename carve-outs, or vim-escape instructions. One rule, every machine, every state, forever.

The desktop is fully synced and pushed. Origin/master tip is the commit `Fix stale README reference on Linux Desktop section` (sha `d282c26` at the time of writing).

## Your job, Laptop Claude

The laptop does **not** yet have `sync.sh`. It has divergent branches right now (the desktop pushed several commits including the new script) and probably also has dirty `chat_log_laptop.txt` / `messages.json` / possibly other modifications. You cannot run `./sync.sh` because the file does not exist on the laptop yet — chicken and egg. So the bootstrap is a one-time manual sequence that mirrors what `sync.sh` does internally.

**Run these commands in order, in PowerShell or Git Bash, from `C:\Users\nir_s\Projects\WaggleDance`:**

```
cd C:\Users\nir_s\Projects\WaggleDance
git status
```

Show Nir the `git status` output so he can see what dirty state we're starting from. Then:

```
git config pull.rebase false
git config rerere.enabled true
git stash push --include-untracked --message "bootstrap-before-sync-sh"
git fetch origin
git pull --no-rebase -X theirs --no-edit origin master
```

Expected outcome of the pull:
- It should auto-merge cleanly (no vim, no conflict prompts).
- New files should appear, including **`sync.sh`** at the repo root, and an updated `README.md`.
- Confirm with: `ls sync.sh` (should exist) and `git log --oneline -5` (top commit should be `d282c26 Fix stale README reference on Linux Desktop section` or newer).

Then restore the stashed work:

```
git stash pop
```

- If `git stash pop` reports a conflict, that is a **real** conflict in something Nir actually edited on the laptop. Open the conflicting file, resolve the `<<<<<` markers by hand, then `git add <file>` and `git commit`. Do not paper over it with `-X theirs` — the whole point of the script design is that genuine human conflicts surface as human conflicts.
- If `git stash pop` succeeds cleanly, you're done with the bootstrap.

Then push any local commits the laptop had (the merge commit + anything else):

```
git push origin master
```

Verify the bootstrap worked:

```
ls sync.sh
bash sync.sh
```

The second `bash sync.sh` should print `[sync] working tree clean`, `[sync] nothing to push`, and `[sync] done.` — confirming the script itself runs successfully on Windows Git Bash.

## After the bootstrap

From this morning forward, on **both** machines, the **only** sync command is:

- Linux desktop: `./sync.sh`
- Windows laptop: `bash sync.sh` (or `./sync.sh` from Git Bash)

No more bare `git pull`. No more vim. No more "specify how to reconcile divergent branches." No more ad-hoc patches.

Read `README.md` after the pull — the new "🛟 The only sync rule" section near the top is the canonical reference. The three morning-startup sub-sections (Laptop, Desktop-Windows, Desktop-Linux) all now say `./sync.sh` instead of `git pull`.

## Cleanup

After the bootstrap is verified working, **delete this file** so it doesn't clutter the repo:

```
rm LAPTOP_CLAUDE_BOOTSTRAP_SYNC.md
git add -u LAPTOP_CLAUDE_BOOTSTRAP_SYNC.md
git commit -m "Bootstrap done: remove laptop bootstrap note"
bash sync.sh
```

That last `bash sync.sh` will push the deletion to origin so the desktop also drops the file on its next sync.

---

🌻 — Desktop Claude (Linux)
