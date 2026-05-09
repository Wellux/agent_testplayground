#!/usr/bin/env bash
# scripts/lib/logging.sh — Karpathy-format log line helpers.

# Append a single Karpathy-format line to a target log file.
#   ralph_log_kv <file> <axis> <key>=<value> [<key>=<value> ...]
ralph_log_kv() {
  local target="$1"; shift
  local axis="$1"; shift
  local kvs="$*"
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  mkdir -p "$(dirname "$target")"
  printf '## [%s] %s | %s\n' "$ts" "$axis" "$kvs" >> "$target"
}

# Tail the last N lines from a file, with a header.
#   ralph_log_tail <file> <n>
ralph_log_tail() {
  local file="$1"; local n="${2:-50}"
  if [[ ! -f "$file" ]]; then
    echo "(no log at $file)"
    return 1
  fi
  echo "── tail -$n $file ──"
  tail -n "$n" "$file"
}
