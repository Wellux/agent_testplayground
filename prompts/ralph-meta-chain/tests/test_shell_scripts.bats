#!/usr/bin/env bats
# Smoke tests for the Round 5 ralph_*.sh shims.
# Run with: bats prompts/ralph-meta-chain/tests/test_shell_scripts.bats
#
# CI does not currently install bats. Run locally via:
#   brew install bats-core
#   bats prompts/ralph-meta-chain/tests/

REPO="$(git rev-parse --show-toplevel)"
SCRIPTS="$REPO/prompts/ralph-meta-chain/scripts"

setup() {
  : "${BATS_TEST_TMPDIR:?missing BATS_TEST_TMPDIR}"
  export VAULT="$BATS_TEST_TMPDIR/vault"
  mkdir -p "$VAULT/30-Notes" "$VAULT/40-Skills" "$VAULT/90-Meta"
}

@test "every shim supports --help (15 scripts)" {
  count=0
  for f in "$SCRIPTS"/ralph_*.sh; do
    out="$("$f" --help 2>&1 || true)"
    [[ "$out" == *USAGE* ]] || { echo "no USAGE in $f --help"; return 1; }
    count=$((count + 1))
  done
  [[ $count -eq 15 ]] || { echo "expected 15 shims, got $count"; return 1; }
}

@test "bash -n on every shim" {
  for f in "$SCRIPTS"/ralph_*.sh "$SCRIPTS"/lib/*.sh; do
    bash -n "$f" || { echo "bash -n failed: $f"; return 1; }
  done
}

@test "ralph_business_ledger_check passes against shipped ledgers" {
  run "$SCRIPTS/ralph_business_ledger_check.sh"
  [ "$status" -eq 0 ]
}

@test "ralph_provider_validate passes against shipped specs" {
  run "$SCRIPTS/ralph_provider_validate.sh"
  [ "$status" -eq 0 ]
}

@test "ralph_validate_frontmatter passes on a clean scratch vault" {
  cat > "$VAULT/30-Notes/note-1.md" <<EOF
---
ralph_type: memory
created: 2026-05-09
---
# note 1
EOF
  cat > "$VAULT/40-Skills/skill-1.md" <<EOF
---
ralph_type: skill
created: 2026-05-09
---
# skill 1
EOF
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 0 ]
}

@test "ralph_validate_frontmatter flags a malformed file" {
  echo "no frontmatter here" > "$VAULT/30-Notes/bad.md"
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -gt 0 ]
}

@test "ralph_check_links flags a broken wikilink" {
  cat > "$VAULT/30-Notes/note-1.md" <<EOF
---
ralph_type: memory
created: 2026-05-09
---
[[orphan-target]]
EOF
  run "$SCRIPTS/ralph_check_links.sh"
  [ "$status" -gt 0 ]
}
