#!/usr/bin/env bash
# scripts/lib/locks.sh — mutual-exclusion locks for cron-fired scripts.

# Acquire an exclusive lock for the given name (single-writer).
# Releases automatically when the script exits.
#   ralph_lock_acquire <lock-name>
ralph_lock_acquire() {
  local name="$1"
  local dir="${RALPH_LOCK_DIR:-${HOME}/.ralph/locks}"
  mkdir -p "$dir"
  local lockfile="$dir/$name.lock"

  # `flock` is the canonical mechanism. Fall back to mkdir-based lock
  # if flock isn't on PATH (rare; some BSD installations).
  if command -v flock >/dev/null 2>&1; then
    exec 9> "$lockfile"
    if ! flock -n 9; then
      echo "lock held: $lockfile" >&2
      return 1
    fi
  else
    if ! mkdir "$lockfile.dir" 2>/dev/null; then
      echo "lock held: $lockfile.dir" >&2
      return 1
    fi
    trap 'rmdir "'"$lockfile.dir"'" 2>/dev/null || true' EXIT
  fi
  return 0
}
