#!/usr/bin/env bash
# ralph_rollback_migration.sh — undo the moves done by ralph_apply_migration.sh.
#
# Risk class: HIGH (mutates filesystem). Refuses unless --apply --confirmed.

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_print_help_header "ralph_rollback_migration.sh" "Reverse a prior migration apply."
  cat <<EOF
WHAT IT DOES
  - Reads migration/rollback-plan.md.
  - Reverses every "Inverse moves" row.
  - Refuses unless --apply --confirmed.

RISK CLASS
  HIGH (mutates filesystem; reverses prior apply).

EXIT CODES
  0   rollback succeeded (or dry-run completed)
  64  default-dry-run; --apply --confirmed missing
  66  rollback-plan missing
EOF
  exit 0
fi

ralph_require_repo

repo="$(ralph_repo_root)"
mig="$(ralph_migration_dir)"
rollback="$mig/rollback-plan.md"

if [[ ! -f "$rollback" ]]; then
  ralph_error "missing $rollback — nothing to roll back"
  exit 66
fi

# Parse "Inverse moves" table.
tmp_moves="$(mktemp)"
trap 'rm -f "$tmp_moves"' EXIT
awk -F'|' '
  /^\| / && NF == 5 {
    fwd=$2; orig=$3
    gsub(/^[ \t]+|[ \t]+$/, "", fwd)
    gsub(/^[ \t]+|[ \t]+$/, "", orig)
    if (fwd == "Forward path" || fwd ~ /^-+$/) next
    print fwd "\t" orig
  }
' "$rollback" > "$tmp_moves"

total=$(wc -l < "$tmp_moves" | tr -d ' ')

if [[ ${RALPH_APPLY:-0} -ne 1 || ${RALPH_CONFIRMED:-0} -ne 1 ]]; then
  ralph_log "DRY RUN. Would reverse $total move(s):"
  while IFS=$'\t' read -r fwd orig; do
    echo "  git mv \"$fwd\" \"$orig\""
  done < "$tmp_moves"
  ralph_log "Use --apply --confirmed to actually roll back."
  exit 64
fi

cd "$repo"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo
  echo "## [$ts] migration | op=rollback moves=$total"
} >> "$mig/migration-log.md"

# Execute reverse moves.
fail=0
while IFS=$'\t' read -r fwd orig; do
  if [[ ! -e "$fwd" ]]; then
    ralph_warn "skip (forward path missing): $fwd"
    continue
  fi
  if [[ -e "$orig" ]]; then
    ralph_error "original path exists: $orig — refusing rollback"
    fail=1
    break
  fi
  mkdir -p "$(dirname "$orig")"
  if ! git mv "$fwd" "$orig" 2>/dev/null; then
    mv "$fwd" "$orig"
  fi
  ralph_log "rolled: $fwd → $orig"
done < "$tmp_moves"

if [[ $fail -ne 0 ]]; then
  ralph_error "rollback aborted mid-flight; manual reconciliation needed"
  exit 1
fi

{
  echo "## [$ts] migration | op=rollback-complete moves=$total status=success"
} >> "$mig/migration-log.md"

ralph_log "rollback complete. $total move(s) reversed."
echo "$total"
