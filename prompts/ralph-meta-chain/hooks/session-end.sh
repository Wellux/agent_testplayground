#!/usr/bin/env bash
# session-end.sh — Claude Code Stop hook.
# Drops a session-capture stub into 00-Inbox/ for the morning memory
# pass. Never blocks; never sends data anywhere.

set -uo pipefail

# We don't actually parse stdin here; just generate a marker file.

vault="${VAULT:-$HOME/Obsidian/SecondBrain}"
inbox="$vault/00-Inbox"
[[ -d "$inbox" ]] || exit 0   # no vault → skip; fail-safe

ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="$inbox/session-${ts}.md"
[[ -e "$out" ]] && exit 0     # idempotent

cat > "$out" <<EOF
---
id: session-${ts}
type: session-capture
source: claude-code
created: $(date -u +%Y-%m-%d)
ralph_type: memory
memory_layer: raw
memory_temperature: hot
status: active
summary: "Session-end capture; the next memory pass distills."
---

# Session capture — ${ts}

> session-end hook — Claude Code session terminated. Ralph's memory
> pass at 02:00 UTC will look at this file and distill any notable
> signals into 30-Notes/.

## Notable signals (auto-collected; user adds context if desired)

- (no auto-extraction yet; future hook revs may include trace summary)

## User notes
EOF

exit 0
