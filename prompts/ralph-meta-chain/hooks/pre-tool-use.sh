#!/usr/bin/env bash
# pre-tool-use.sh — Claude Code PreToolUse hook.
# Guards against forbidden Bash patterns. Always logs; only blocks
# when a pattern in the deny-list appears.
#
# Fail-safe contract: this script's own errors must NEVER block Claude
# Code. We always emit a JSON decision; we exit 0 unless catastrophic.

set -uo pipefail

# Read tool input JSON from stdin.
input="$(cat)"

# Best-effort field extraction without jq dependency. Defensive.
tool_name="$(printf '%s' "$input" | grep -oE '"tool_name":[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
[[ -z "$tool_name" ]] && tool_name="?"

# Find $VAULT for logging.
vault="${VAULT:-}"
if [[ -z "$vault" ]]; then
  # Try a common default; never error if not set.
  vault="$HOME/Obsidian/SecondBrain"
fi
log_file="$vault/90-Meta/log.md"
[[ -d "$(dirname "$log_file")" ]] || log_file="/tmp/ralph-pre-tool-use.log"
mkdir -p "$(dirname "$log_file")" 2>/dev/null || true

# Always log.
printf '## [%s] pre-tool-use | tool=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$tool_name" \
  >> "$log_file" 2>/dev/null || true

# Deny-list: refuse Bash invocations matching these patterns.
# (Mirrors config.example.yml's permissions.deny.)
if [[ "$tool_name" == "Bash" ]]; then
  cmd="$(printf '%s' "$input" | grep -oE '"command":[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
  for pattern in 'rm -rf' 'sudo ' 'curl ' 'wget ' 'git push --force' 'git push -f' '--no-verify'; do
    if [[ "$cmd" == *"$pattern"* ]]; then
      printf '{"decision":"block","reason":"forbidden Bash pattern: %s"}\n' "$pattern"
      exit 0
    fi
  done
fi

# Default allow. Empty body == allow.
exit 0
