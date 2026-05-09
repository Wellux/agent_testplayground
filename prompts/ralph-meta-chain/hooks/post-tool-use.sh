#!/usr/bin/env bash
# post-tool-use.sh — Claude Code PostToolUse hook.
# Appends a Karpathy-format log line. Never blocks.

set -uo pipefail

input="$(cat)"

tool_name="$(printf '%s' "$input" | grep -oE '"tool_name":[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
[[ -z "$tool_name" ]] && tool_name="?"

duration="$(printf '%s' "$input" | grep -oE '"duration_ms":[[:space:]]*[0-9]+' | head -1 | sed -E 's/[^0-9]+//')"
[[ -z "$duration" ]] && duration="0"

vault="${VAULT:-$HOME/Obsidian/SecondBrain}"
log_file="$vault/90-Meta/log.md"
[[ -d "$(dirname "$log_file")" ]] || log_file="/tmp/ralph-post-tool-use.log"
mkdir -p "$(dirname "$log_file")" 2>/dev/null || true

printf '## [%s] post-tool-use | tool=%s ms=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$tool_name" "$duration" \
  >> "$log_file" 2>/dev/null || true

exit 0
