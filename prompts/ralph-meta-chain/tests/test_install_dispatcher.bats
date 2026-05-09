#!/usr/bin/env bats
# install.sh dispatcher smoke tests.
# Run via: bats prompts/ralph-meta-chain/tests/test_install_dispatcher.bats

REPO="$(git rev-parse --show-toplevel)"
DISPATCH="$REPO/prompts/ralph-meta-chain/install/install.sh"

setup() {
  : "${BATS_TEST_TMPDIR:?missing BATS_TEST_TMPDIR}"
  export HOME="$BATS_TEST_TMPDIR/home"
  export CODEX_HOME="$HOME/.codex"
  mkdir -p "$HOME"
}

@test "dispatcher exists and is executable" {
  [ -x "$DISPATCH" ]
}

@test "dispatcher errors on missing --target" {
  run "$DISPATCH"
  [ "$status" -eq 64 ]
  [[ "$output" == *"--target is required"* ]]
}

@test "dispatcher rejects unknown flag" {
  run "$DISPATCH" --target codex --bogus
  [ "$status" -eq 64 ]
}

@test "dispatcher --help prints all four targets" {
  run "$DISPATCH" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"cron"* ]]
  [[ "$output" == *"claude-code"* ]]
  [[ "$output" == *"codex"* ]]
  [[ "$output" == *"all"* ]]
}

@test "dispatcher --target codex --dry-run delegates to install_codex.sh" {
  run "$DISPATCH" --target codex --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"target=codex action=install"* ]]
  [[ "$output" == *"DRY:"* ]]
  [[ "$output" == *"codex install ✓"* ]]
  # Nothing written.
  [ ! -d "$HOME/.codex/prompts" ]
}

@test "dispatcher --target claude-code,codex --dry-run runs both" {
  run "$DISPATCH" --target claude-code,codex --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"target=claude-code action=install"* ]]
  [[ "$output" == *"target=codex action=install"* ]]
  [[ "$output" == *"all targets completed"* ]]
}

@test "dispatcher --target all --dry-run runs three targets" {
  run "$DISPATCH" --target all --dry-run
  # cron may exit non-zero in CI (no config.yml), but the dispatcher
  # forwards rc; we just check that all three were attempted.
  [[ "$output" == *"target=cron"* ]]
  [[ "$output" == *"target=claude-code"* ]]
  [[ "$output" == *"target=codex"* ]]
}

@test "dispatcher propagates --scope to interactive installers" {
  run "$DISPATCH" --target codex --scope project --dry-run
  [ "$status" -eq 0 ]
  # Codex installer log should show project scope.
  [[ "$output" == *"scope:          project"* ]]
}

@test "dispatcher forwards installer-specific flags after --" {
  run "$DISPATCH" --target codex --dry-run -- --without-mcp --without-prompts
  [ "$status" -eq 0 ]
  # The forwarded flags should affect the codex installer's announced state.
  [[ "$output" == *"with-mcp:       no"* ]]
  [[ "$output" == *"with-prompts:   0"* ]]
}

@test "dispatcher actually installs both surfaces (wet, MCP off)" {
  run "$DISPATCH" --target claude-code,codex -- --without-mcp
  [ "$status" -eq 0 ]
  [ -d "$HOME/.claude/commands" ]
  [ -d "$HOME/.agents/skills" ]
}

@test "dispatcher --uninstall reverses both installs" {
  "$DISPATCH" --target claude-code,codex -- --without-mcp >/dev/null 2>&1
  run "$DISPATCH" --target claude-code,codex --uninstall
  [ "$status" -eq 0 ]
  [ ! -d "$HOME/.claude/commands" ]
  [ ! -d "$HOME/.agents/skills" ]
}

@test "dispatcher rejects unknown bare flag (suggests using --)" {
  run "$DISPATCH" --target codex --without-mcp
  [ "$status" -eq 64 ]
  [[ "$output" == *"--"* ]]
}
