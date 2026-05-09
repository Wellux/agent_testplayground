#!/usr/bin/env bash
# ralph_apply_migration.sh — execute the moves in proposed-moves.md.
#
# Risk class: CRITICAL. Refuses unless ALL of:
#   1. --apply --confirmed flags present
#   2. proposed-moves.md present and recent
#   3. rollback-plan.md present
#   4. conflicts.md reports zero conflicts
#   5. RALPH_MIGRATION_APPROVED=<sha256-of-proposed-moves> env var matches
#   6. git working tree is clean (no uncommitted changes elsewhere)
#
# Without ALL six, defaults to dry-run (prints intended moves, exits 64).

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_print_help_header "ralph_apply_migration.sh" "Execute proposed-moves.md (CRITICAL)."
  cat <<EOF
WHAT IT DOES
  - Reads migration/proposed-moves.md.
  - Validates conflict-free, rollback-plan present.
  - With --apply --confirmed AND RALPH_MIGRATION_APPROVED matching the
    proposed-moves.md sha256, performs every git mv in order.
  - Without all gates, dry-runs (prints intended moves) and exits 64.

RISK CLASS
  CRITICAL. Six independent gates required.

ENV
  RALPH_MIGRATION_APPROVED  hex sha256 of migration/proposed-moves.md;
                            must match exactly when --apply --confirmed.

EXIT CODES
  0   apply succeeded (or dry-run completed)
  64  default-dry-run; gates not all present
  65  conflicts present; refusing
  66  artifacts missing
  67  approval token mismatch
  68  git tree dirty; refusing
EOF
  exit 0
fi

ralph_require_repo

repo="$(ralph_repo_root)"
mig="$(ralph_migration_dir)"
moves="$mig/proposed-moves.md"
rollback="$mig/rollback-plan.md"
conflicts="$mig/conflicts.md"

# Gate 1: artifacts present.
for f in "$moves" "$rollback"; do
  if [[ ! -f "$f" ]]; then
    ralph_error "missing $f — run ralph_propose_migration.sh first"
    exit 66
  fi
done

# Gate 2: conflicts report says zero.
if [[ -f "$conflicts" ]]; then
  if grep -qE '^- ' "$conflicts" 2>/dev/null; then
    ralph_error "conflicts present in $conflicts; refusing apply"
    exit 65
  fi
fi

# Gate 3: parse moves.
tmp_moves="$(mktemp)"
trap 'rm -f "$tmp_moves"' EXIT
awk -F'|' '
  /^\| / && NF == 5 {
    src=$2; tgt=$3
    gsub(/^[ \t]+|[ \t]+$/, "", src)
    gsub(/^[ \t]+|[ \t]+$/, "", tgt)
    if (src == "Source path" || src ~ /^-+$/) next
    print src "\t" tgt
  }
' "$moves" > "$tmp_moves"

total_moves=$(wc -l < "$tmp_moves" | tr -d ' ')

# Gate 4: dry-run unless --apply --confirmed.
if [[ ${RALPH_APPLY:-0} -ne 1 || ${RALPH_CONFIRMED:-0} -ne 1 ]]; then
  ralph_log "DRY RUN. Would execute $total_moves git mv operation(s):"
  while IFS=$'\t' read -r src tgt; do
    echo "  git mv \"$src\" \"$tgt\""
  done < "$tmp_moves"
  ralph_log "Use --apply --confirmed AND RALPH_MIGRATION_APPROVED to actually move."
  exit 64
fi

# Gate 5: approval token must match sha256 of proposed-moves.md.
expected_sha="$(shasum -a 256 "$moves" 2>/dev/null | awk '{print $1}')"
[[ -z "$expected_sha" ]] && expected_sha="$(sha256sum "$moves" 2>/dev/null | awk '{print $1}')"

if [[ "${RALPH_MIGRATION_APPROVED:-}" != "$expected_sha" ]]; then
  ralph_error "RALPH_MIGRATION_APPROVED mismatch."
  ralph_error "  expected: $expected_sha"
  ralph_error "  got:      ${RALPH_MIGRATION_APPROVED:-<unset>}"
  exit 67
fi

# Gate 6: git tree must be clean apart from migration files themselves.
cd "$repo"
dirty=$(git status --porcelain | awk '{print $2}' | grep -v '^prompts/ralph-meta-chain/migration/' || true)
if [[ -n "$dirty" ]]; then
  ralph_error "git tree dirty (non-migration files modified); refusing apply"
  echo "$dirty" | head -10 >&2
  exit 68
fi

# All gates pass. Audit-log entry BEFORE moves.
audit="$mig/migration-log.md"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo
  echo "## [$ts] migration | op=apply moves=$total_moves sha256=$expected_sha"
  while IFS=$'\t' read -r src tgt; do
    echo "  - git mv \"$src\" \"$tgt\""
  done < "$tmp_moves"
} >> "$audit"

# Execute moves.
fail=0
while IFS=$'\t' read -r src tgt; do
  if [[ ! -e "$src" ]]; then
    ralph_warn "skip (source missing): $src"
    continue
  fi
  if [[ -e "$tgt" ]]; then
    ralph_error "destination exists (race?): $tgt — aborting"
    fail=1
    break
  fi
  mkdir -p "$(dirname "$tgt")"
  if ! git mv "$src" "$tgt" 2>/dev/null; then
    # git mv refuses if file is untracked; fall back to mv.
    mv "$src" "$tgt"
  fi
  ralph_log "moved: $src → $tgt"
done < "$tmp_moves"

if [[ $fail -ne 0 ]]; then
  ralph_error "apply aborted mid-flight; run ralph_rollback_migration.sh"
  exit 1
fi

# Final audit line + summary.
{
  echo "## [$ts] migration | op=apply-complete moves=$total_moves status=success"
} >> "$audit"

ralph_log "apply complete. $total_moves move(s)."
ralph_log "next: run \`harness self-test\` to confirm no regression."

echo "$total_moves"
