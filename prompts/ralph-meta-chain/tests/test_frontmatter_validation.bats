#!/usr/bin/env bats
# Frontmatter validator tests. Run via:
#   bats prompts/ralph-meta-chain/tests/test_frontmatter_validation.bats

REPO="$(git rev-parse --show-toplevel)"
SCRIPTS="$REPO/prompts/ralph-meta-chain/scripts"

setup() {
  : "${BATS_TEST_TMPDIR:?missing BATS_TEST_TMPDIR}"
  export VAULT="$BATS_TEST_TMPDIR/vault"
  mkdir -p "$VAULT/30-Notes" "$VAULT/40-Skills"
}

@test "valid frontmatter passes" {
  cat > "$VAULT/30-Notes/ok.md" <<EOF
---
ralph_type: memory
created: 2026-05-09
---
# ok
EOF
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 0 ]
}

@test "missing frontmatter fails (count = 1)" {
  echo "no frontmatter" > "$VAULT/30-Notes/bad.md"
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 1 ]
}

@test "missing required field fails (count = 1)" {
  cat > "$VAULT/30-Notes/missing-type.md" <<EOF
---
created: 2026-05-09
---
# missing ralph_type
EOF
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 1 ]
}

@test "multiple invalid files counted" {
  echo "no frontmatter 1" > "$VAULT/30-Notes/bad1.md"
  echo "no frontmatter 2" > "$VAULT/30-Notes/bad2.md"
  cat > "$VAULT/40-Skills/missing.md" <<EOF
---
created: 2026-05-09
---
# missing ralph_type
EOF
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 3 ]
}

@test "_archive subfolder is skipped" {
  mkdir -p "$VAULT/30-Notes/_archive"
  echo "no frontmatter" > "$VAULT/30-Notes/_archive/old.md"
  run "$SCRIPTS/ralph_validate_frontmatter.sh"
  [ "$status" -eq 0 ]
}
