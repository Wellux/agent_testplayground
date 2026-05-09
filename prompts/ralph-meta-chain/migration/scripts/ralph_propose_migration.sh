#!/usr/bin/env bash
# ralph_propose_migration.sh — convert file-classification.md into a moves
# proposal + a rollback plan. Risk class: MEDIUM (writes proposal Markdown
# but does not move any file).

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_print_help_header "ralph_propose_migration.sh" "Generate proposed-moves + rollback-plan."
  cat <<EOF
WHAT IT DOES
  - Reads file-classification.md (runs classify first if missing).
  - For each non-no-op classification, generates a proposed `git mv`.
  - Detects conflicts (destination exists / outside repo / etc.).
  - Writes proposed-moves.md AND rollback-plan.md (both mandatory before
    any apply per docs/REPO_MIGRATION.md).
  - Refuses if conflicts exist (emits exit code 65).

RISK CLASS
  MEDIUM (writes Markdown proposals; never moves files).

OUTPUTS
  prompts/ralph-meta-chain/migration/proposed-moves.md
  prompts/ralph-meta-chain/migration/rollback-plan.md
  prompts/ralph-meta-chain/migration/conflicts.md (if any conflicts)
EOF
  exit 0
fi

ralph_require_repo

repo="$(ralph_repo_root)"
mig="$(ralph_migration_dir)"
cls_file="$mig/file-classification.md"
out_moves="$mig/proposed-moves.md"
out_rollback="$mig/rollback-plan.md"
out_conflicts="$mig/conflicts.md"

if [[ ! -f "$cls_file" ]]; then
  ralph_log "classification missing; running ralph_classify_repo_files.sh first"
  "$HERE/ralph_classify_repo_files.sh" >/dev/null
fi

# Extract source → target pairs from the classification table.
# Format of input rows: | <path> | <class> | <target> |
# (with optional " (no-op)" suffix on target)

tmp_moves="$(mktemp)"
tmp_rollback="$(mktemp)"
tmp_conflicts="$(mktemp)"
trap 'rm -f "$tmp_moves" "$tmp_rollback" "$tmp_conflicts"' EXIT

awk -F'|' '
  /^\|[^|]+\|[^|]+\|[^|]+\|$/ {
    src = $2; cls = $3; tgt = $4
    gsub(/^[ \t]+|[ \t]+$/, "", src)
    gsub(/^[ \t]+|[ \t]+$/, "", cls)
    gsub(/^[ \t]+|[ \t]+$/, "", tgt)
    if (src == "Path" || src ~ /^-+$/) next
    if (tgt ~ /\(no-op\)/) next                  # already at target path
    sub(/ \(no-op\)$/, "", tgt)
    print src "\t" tgt
  }
' "$cls_file" > "$tmp_moves"

total_moves=$(wc -l < "$tmp_moves" | tr -d ' ')

# Detect conflicts: destination exists, source missing, target outside repo.
> "$tmp_conflicts"
while IFS=$'\t' read -r src tgt; do
  if [[ -e "$repo/$tgt" ]]; then
    echo "destination exists: $tgt (cannot overwrite)" >> "$tmp_conflicts"
  fi
  if [[ ! -e "$repo/$src" ]]; then
    echo "source missing: $src" >> "$tmp_conflicts"
  fi
  case "$tgt" in
    /*|../*|*../*) echo "target escapes repo: $tgt" >> "$tmp_conflicts" ;;
  esac
done < "$tmp_moves"

conflicts=$(wc -l < "$tmp_conflicts" | tr -d ' ')

# Render proposed-moves.md.
{
  echo "---"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "generator: ralph_propose_migration.sh"
  echo "based_on: migration/file-classification.md"
  echo "total_moves: $total_moves"
  echo "conflicts: $conflicts"
  echo "target_root: prompts/ralph-meta-chain"
  echo "risk_class: CRITICAL"
  echo "---"
  echo
  echo "# Proposed Moves"
  echo
  if [[ $conflicts -gt 0 ]]; then
    echo '> **CONFLICTS PRESENT** ('"$conflicts"' issue(s)).'
    echo '> See `migration/conflicts.md`. Apply will refuse until resolved.'
    echo
  fi
  echo "## Moves ($total_moves)"
  echo
  echo "| Source path | Target path | Operation |"
  echo "|-------------|-------------|-----------|"
  while IFS=$'\t' read -r src tgt; do
    echo "| $src | $tgt | git mv |"
  done < "$tmp_moves"
  echo
  echo "## Apply gate"
  echo
  echo "CRITICAL per docs/APPROVAL_GATES.md § Repo migration. Required:"
  echo
  echo "1. inventory-report.md present + reviewed"
  echo "2. file-classification.md present + reviewed"
  echo "3. proposed-moves.md present (this file)"
  echo "4. rollback-plan.md present"
  echo "5. audit-log entry created BEFORE apply"
  echo "6. \`--apply --confirmed\` invocation"
  echo "7. \`harness self-test\` green AFTER apply"
} > "$out_moves.tmp"

# Render rollback-plan.md.
{
  echo "---"
  echo "generated_for_apply_at: <pending>"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "generator: ralph_propose_migration.sh"
  echo "estimated_rollback_seconds: $((total_moves * 2 + 10))"
  echo "---"
  echo
  echo "# Rollback Plan"
  echo
  echo "Reverses every move in proposed-moves.md. Run via"
  echo "\`ralph_rollback_migration.sh --apply --confirmed\`."
  echo
  echo "## Inverse moves"
  echo
  echo "| Forward path | Original path | Operation |"
  echo "|--------------|---------------|-----------|"
  while IFS=$'\t' read -r src tgt; do
    echo "| $tgt | $src | git mv |"
  done < "$tmp_moves"
  echo
  echo "## Restore CI workflow"
  echo
  echo '```bash'
  echo "cp migration/ci-backup-<ts>.yml .github/workflows/ci.yml"
  echo "git add .github/workflows/ci.yml"
  echo 'git commit -m "rollback: restore CI workflow"'
  echo '```'
  echo
  echo "## Restart cron"
  echo
  echo "After rollback, the install paths revert too. The user must:"
  echo
  echo '```bash'
  echo "./scripts/uninstall.sh   # at restored path"
  echo "./scripts/install.sh"
  echo '```'
  echo
  echo "## Verify"
  echo
  echo '```bash'
  echo "harness self-test"
  echo '```'
  echo
  echo "If self-test green AND log.md shows expected last-runs, rollback"
  echo "is complete."
} > "$out_rollback.tmp"

# Render conflicts.md.
{
  echo "---"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "generator: ralph_propose_migration.sh"
  echo "total_conflicts: $conflicts"
  echo "---"
  echo
  echo "# Conflicts"
  echo
  if [[ $conflicts -eq 0 ]]; then
    echo "(none)"
  else
    echo "Apply will refuse until each conflict is resolved."
    echo
    echo "## Issues"
    echo
    while IFS= read -r line; do
      echo "- $line"
    done < "$tmp_conflicts"
  fi
} > "$out_conflicts.tmp"

mv "$out_moves.tmp" "$out_moves"
mv "$out_rollback.tmp" "$out_rollback"
mv "$out_conflicts.tmp" "$out_conflicts"

ralph_log "wrote $out_moves ($total_moves move(s); $conflicts conflict(s))"
ralph_log "wrote $out_rollback"
ralph_log "wrote $out_conflicts"
ralph_migration_log_append propose "moves=$total_moves conflicts=$conflicts"

if [[ $conflicts -gt 0 ]]; then
  ralph_warn "$conflicts conflict(s); see $out_conflicts. Apply will refuse."
  exit 65
fi

echo "$out_moves"
