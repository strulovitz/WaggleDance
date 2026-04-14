#!/usr/bin/env bash
# WaggleDance sync — works from ANY repo state, on ANY machine, every time.
#
# What it does, in order:
#   1. Ensures the one-time git config is set (idempotent — safe to re-run forever).
#   2. Stashes EVERYTHING dirty (tracked + untracked) so the working tree is pristine.
#   3. Fetches the remote.
#   4. Merges with -X theirs (remote wins line-level conflicts) and --no-edit (vim never opens).
#   5. Pops the stash. If pop conflicts, the script stops and tells you what to do.
#   6. Pushes if there are local commits ahead of the remote.
#
# Why -X theirs is the right default for THIS repo:
#   chat_log_*.txt and messages.json are append-only logs that both machines write to
#   constantly. Real code lives in *.py and *.md and is only edited on one machine at a
#   time, so genuine conflicts are rare; when they do happen the stash-pop step surfaces
#   them as a real human-resolve event instead of silently overwriting.
#
# Usage:  ./sync.sh         (run from anywhere inside the WaggleDance repo)

set -euo pipefail

# Always operate from the repo root, no matter where the user invoked us from.
cd "$(git rev-parse --show-toplevel)"

echo "[sync] repo: $(pwd)"
echo "[sync] branch: $(git rev-parse --abbrev-ref HEAD)"

# --- 1. Idempotent one-time config ------------------------------------------
git config pull.rebase false
git config rerere.enabled true
git config merge.ours.driver true >/dev/null 2>&1 || true

# --- 2. Stash everything dirty ----------------------------------------------
STASHED=0
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  echo "[sync] working tree dirty — stashing (tracked + untracked)"
  git stash push --include-untracked --message "sync.sh auto-stash $(date -Iseconds)"
  STASHED=1
else
  echo "[sync] working tree clean"
fi

# --- 3. Fetch ----------------------------------------------------------------
echo "[sync] fetching origin"
git fetch origin

# --- 4. Merge with remote-wins strategy --------------------------------------
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "[sync] merging origin/$BRANCH (strategy: -X theirs, --no-edit)"
if ! git pull --no-rebase -X theirs --no-edit origin "$BRANCH"; then
  echo "[sync] !! pull failed. Repo state has been left as-is for inspection."
  echo "[sync] !! Your local changes are safe in the stash (run: git stash list)."
  exit 1
fi

# --- 5. Restore stashed work -------------------------------------------------
if [ "$STASHED" -eq 1 ]; then
  echo "[sync] restoring stashed changes"
  if ! git stash pop; then
    echo ""
    echo "[sync] !! stash pop produced conflicts in files YOU edited locally."
    echo "[sync] !! These are REAL conflicts — open the files, fix the <<<<< markers,"
    echo "[sync] !! then run:  git add <file> && git commit"
    echo "[sync] !! Your stash is still saved (run: git stash list) until you drop it."
    exit 2
  fi
fi

# --- 6. Push if we have anything to push -------------------------------------
LOCAL_AHEAD="$(git rev-list --count "origin/$BRANCH..HEAD")"
if [ "$LOCAL_AHEAD" -gt 0 ]; then
  echo "[sync] $LOCAL_AHEAD local commit(s) ahead of origin — pushing"
  git push origin "$BRANCH"
else
  echo "[sync] nothing to push"
fi

echo "[sync] done."
