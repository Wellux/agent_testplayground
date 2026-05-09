#!/usr/bin/env bash
# session-start.sh — Claude Code SessionStart hook.
#
# Fires when a Claude Code session begins. Surfaces a one-screen
# briefing about the chain's current state to stdout (Claude Code
# injects this into the model's context). The user sees the same
# briefing in their terminal.
#
# Fail-safe contract (mandatory for every Ralph hook):
#   1. Never block Claude Code (always exit 0; emit "" on any error).
#   2. Hard 10s budget (orchestrated by the hook timeout, not us).
#   3. No network. Reads only.
#   4. Append diagnostics to heal-checks.ndjson if anything weird.

set -uo pipefail

vault="${VAULT:-$HOME/Obsidian/SecondBrain}"
log="$vault/90-Meta/log.md"

emit() { printf '%s\n' "$*"; }

# Bail early if no vault (e.g. CI invocation; cron container with no vault yet).
if [[ ! -d "$vault" ]]; then
  emit "_(Ralph: no vault at \`$vault\`; SessionStart briefing skipped.)_"
  exit 0
fi

# ── Header ─────────────────────────────────────────────────────────────────

emit "## Ralph briefing — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
emit ""
emit "Vault: \`$vault\`"

# ── Last 8 axis log entries (one per axis if available) ────────────────────

if [[ -f "$log" ]]; then
  emit ""
  emit "### Last per-axis log lines"
  emit ""
  emit '```'
  for axis in research memory skills interaction compress heal evolve update; do
    line="$(grep -E "^## \[[0-9-]+T[0-9:]+Z\] $axis \|" "$log" 2>/dev/null | tail -1 || true)"
    if [[ -n "$line" ]]; then
      printf '%s\n' "$line"
    else
      printf '## [—] %s | (no entries yet)\n' "$axis"
    fi
  done
  emit '```'
fi

# ── STOP / STOP-* sentinels ────────────────────────────────────────────────

stops=()
[[ -f "$vault/90-Meta/STOP" ]] && stops+=("STOP")
shopt -s nullglob
for f in "$vault/90-Meta"/STOP-*; do
  stops+=("$(basename "$f")")
done
shopt -u nullglob

if [[ ${#stops[@]} -gt 0 ]]; then
  emit ""
  emit "### ⚠️  Active stop sentinels"
  emit ""
  for s in "${stops[@]}"; do
    emit "- \`90-Meta/$s\`"
  done
  emit ""
  emit "_(Ralph axes will skip on next firing while these exist.)_"
fi

# ── Inbox depth (hot signal) ───────────────────────────────────────────────

if [[ -d "$vault/00_Inbox" ]]; then
  count="$(find "$vault/00_Inbox" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  emit ""
  emit "### Inbox depth"
  emit ""
  emit "- \`00_Inbox/\` has **$count** markdown files awaiting the next memory pass."
fi

# ── Open escalations (non-blocking) ────────────────────────────────────────

esc="$vault/60-Interactions/escalations.md"
if [[ -f "$esc" ]]; then
  open_count="$(grep -cE '^- \[ \]' "$esc" 2>/dev/null || echo 0)"
  if [[ "$open_count" -gt 0 ]]; then
    emit ""
    emit "### Open escalations"
    emit ""
    emit "- $open_count item(s) in \`60-Interactions/escalations.md\` awaiting human action."
  fi
fi

# ── Hint at the master command ─────────────────────────────────────────────

emit ""
emit "_Type \`/ralph-cron\` for the full per-axis dashboard._"

exit 0
