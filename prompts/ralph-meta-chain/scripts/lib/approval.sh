#!/usr/bin/env bash
# scripts/lib/approval.sh — approval-ledger helpers.

# Append a pending-approval entry to the vault's
# 60-Interactions/escalations.md (or business ledger if Round 3 active).
#   ralph_approval_request <severity> <axis> <one-line-symptom>
ralph_approval_request() {
  local severity="$1"; local axis="$2"; local subject="$3"
  local vault
  vault="$(VAULT="${VAULT:-}" bash -c 'echo "$VAULT"')"
  [[ -z "$vault" ]] && return 1
  local target="$vault/60-Interactions/escalations.md"
  mkdir -p "$(dirname "$target")"
  cat <<EOF >> "$target"

## [$(date -u +%Y-%m-%dT%H:%M:%SZ)] $severity — $axis — $subject
**Diagnosis:** (auto-generated stub; fill in)
**Suggested fix:** (auto-generated stub; fill in)
**Will retry in:** next-heal-window
EOF
}

# Test if a proposal note's frontmatter `status:` is approved.
#   ralph_approval_check <note-path>
ralph_approval_check() {
  local note="$1"
  [[ -f "$note" ]] || return 1
  local status
  status="$(awk '
    NR==1 && /^---/ { in_fm=1; next }
    in_fm && /^---/ { exit }
    in_fm && $1=="status:" { gsub(/^[^:]+:[ \t]*/,""); print; exit }
  ' "$note")"
  [[ "$status" == "approved" ]]
}
