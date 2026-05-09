#!/usr/bin/env bats
# Migration-pipeline dry-run tests. The apply path is gated; we never
# call --apply --confirmed in CI. Run via:
#   bats prompts/ralph-meta-chain/tests/test_migration_dry_run.bats

REPO="$(git rev-parse --show-toplevel)"
MIG="$REPO/prompts/ralph-meta-chain/migration"
SCRIPTS="$MIG/scripts"

@test "every migration script supports --help (5 scripts)" {
  count=0
  for f in "$SCRIPTS"/ralph_*.sh; do
    out="$("$f" --help 2>&1 || true)"
    [[ "$out" == *USAGE* ]] || { echo "no USAGE in $f --help"; return 1; }
    count=$((count + 1))
  done
  [[ $count -eq 5 ]] || { echo "expected 5 migration scripts, got $count"; return 1; }
}

@test "ralph_repo_inventory writes inventory-report.md" {
  run "$SCRIPTS/ralph_repo_inventory.sh"
  [ "$status" -eq 0 ]
  [ -f "$MIG/inventory-report.md" ]
  grep -q "Inventory Report" "$MIG/inventory-report.md"
}

@test "ralph_classify_repo_files writes file-classification.md" {
  run "$SCRIPTS/ralph_classify_repo_files.sh"
  [ "$status" -eq 0 ]
  [ -f "$MIG/file-classification.md" ]
  grep -q "File Classification" "$MIG/file-classification.md"
}

@test "ralph_propose_migration writes proposed-moves + rollback + conflicts" {
  run "$SCRIPTS/ralph_propose_migration.sh"
  # 0 = success; 65 = conflicts present (also acceptable, exit-of-class).
  [[ "$status" -eq 0 || "$status" -eq 65 ]]
  [ -f "$MIG/proposed-moves.md" ]
  [ -f "$MIG/rollback-plan.md" ]
  [ -f "$MIG/conflicts.md" ]
}

@test "ralph_apply_migration default invocation refuses to apply" {
  "$SCRIPTS/ralph_propose_migration.sh" >/dev/null 2>&1 || true
  run "$SCRIPTS/ralph_apply_migration.sh"
  # Must NOT be 0. Allowed exit codes: 64 (default dry-run), 65 (conflicts).
  [ "$status" -ne 0 ]
  [[ "$status" -eq 64 || "$status" -eq 65 ]]
}

@test "ralph_apply_migration with --apply --confirmed but no token refuses" {
  "$SCRIPTS/ralph_propose_migration.sh" >/dev/null 2>&1 || true
  run "$SCRIPTS/ralph_apply_migration.sh" --apply --confirmed
  [ "$status" -ne 0 ]
  # Acceptable: 65 (conflicts), 67 (token mismatch), 68 (dirty tree).
  [[ "$status" -eq 65 || "$status" -eq 67 || "$status" -eq 68 ]]
}

@test "ralph_rollback_migration default invocation dry-runs" {
  run "$SCRIPTS/ralph_rollback_migration.sh"
  # 64 = dry-run; 66 = no rollback-plan present (also fine).
  [[ "$status" -eq 64 || "$status" -eq 66 ]]
}
