#!/usr/bin/env bash
# notification.sh — Claude Code Notification hook.
# Routes important events to a desktop notification (macOS) or a log
# file (Linux). Stub: by default, log only; user enables osascript
# routing manually.

set -uo pipefail

input="$(cat)"

vault="${VAULT:-$HOME/Obsidian/SecondBrain}"
log_file="$vault/90-Meta/log.md"
[[ -d "$(dirname "$log_file")" ]] || log_file="/tmp/ralph-notification.log"
mkdir -p "$(dirname "$log_file")" 2>/dev/null || true

# Best-effort field extraction.
title="$(printf '%s' "$input" | grep -oE '"title":[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
body="$(printf '%s' "$input" | grep -oE '"message":[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
[[ -z "$title" ]] && title="Ralph"
[[ -z "$body" ]] && body="(notification)"

printf '## [%s] notification | title=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$title" \
  >> "$log_file" 2>/dev/null || true

# macOS: opt-in by uncommenting. Privacy-aware: notifications appear
# on screen; only enable on a personal trusted device.
#
# if command -v osascript >/dev/null 2>&1; then
#   osascript -e "display notification \"$body\" with title \"$title\""
# fi

# Linux: opt-in by uncommenting. Requires libnotify-bin.
#
# if command -v notify-send >/dev/null 2>&1; then
#   notify-send "$title" "$body"
# fi

exit 0
