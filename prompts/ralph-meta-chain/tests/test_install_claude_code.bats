#!/usr/bin/env bats
# install_claude_code.sh + uninstall_claude_code.sh round-trip tests.
# Run via: bats prompts/ralph-meta-chain/tests/test_install_claude_code.bats

REPO="$(git rev-parse --show-toplevel)"
INSTALLER="$REPO/prompts/ralph-meta-chain/install/install_claude_code.sh"
UNINSTALLER="$REPO/prompts/ralph-meta-chain/install/uninstall_claude_code.sh"

setup() {
  : "${BATS_TEST_TMPDIR:?missing BATS_TEST_TMPDIR}"
  # Each test gets an isolated HOME so --scope user writes into the tmpdir.
  export HOME="$BATS_TEST_TMPDIR/home"
  mkdir -p "$HOME"
}

@test "installer exists and is executable" {
  [ -x "$INSTALLER" ]
  [ -x "$UNINSTALLER" ]
}

@test "installer rejects unknown --scope" {
  run "$INSTALLER" --scope bogus --dry-run
  [ "$status" -eq 64 ]
}

@test "installer --help prints usage" {
  run "$INSTALLER" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"--scope"* ]]
  [[ "$output" == *"--dry-run"* ]]
}

@test "dry-run emits 'DRY:' lines and writes nothing" {
  run "$INSTALLER" --scope user --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"DRY: mkdir -p"* ]]
  [[ "$output" == *"DRY: ln -s"* ]]
  # Nothing actually written.
  [ ! -d "$HOME/.claude" ]
}

@test "wet install creates expected structure" {
  run "$INSTALLER" --scope user
  [ "$status" -eq 0 ]
  # Subdirs populated.
  [ -d "$HOME/.claude/commands" ]
  [ -d "$HOME/.claude/agents" ]
  [ -d "$HOME/.claude/skills" ]
  [ -d "$HOME/.claude/hooks" ]
  # Symlinks for the master command + key axis commands.
  [ -L "$HOME/.claude/commands/ralph-cron.md" ]
  [ -L "$HOME/.claude/commands/ralph-memory.md" ]
  [ -L "$HOME/.claude/commands/ralph-research.md" ]
  [ -L "$HOME/.claude/commands/ralph-compress.md" ]
  [ -L "$HOME/.claude/commands/ralph-evolve.md" ]
  # Symlinks for axis subagents.
  [ -L "$HOME/.claude/agents/ralph-memory.md" ]
  [ -L "$HOME/.claude/agents/ralph-research.md" ]
  [ -L "$HOME/.claude/agents/ralph-update.md" ]
  # Hook scripts.
  [ -L "$HOME/.claude/hooks/session-start.sh" ]
  [ -L "$HOME/.claude/hooks/pre-tool-use.sh" ]
  # Manifest written.
  [ -f "$HOME/.claude/.ralph-installed.json" ]
  # Settings + MCP file written.
  [ -f "$HOME/.claude/settings.json" ]
  [ -f "$HOME/.claude/.mcp.json" ]
}

@test "settings.json has Ralph permissions and hook bindings" {
  run "$INSTALLER" --scope user
  [ "$status" -eq 0 ]
  run python3 -c "
import json
with open('$HOME/.claude/settings.json') as f:
    s = json.load(f)
assert 'permissions' in s, 'permissions missing'
assert 'allow' in s['permissions'], 'allow missing'
assert 'Read(**)' in s['permissions']['allow'], 'Read(**) missing'
assert 'Bash(rm:*)' in s['permissions'].get('deny', []), 'rm deny missing'
assert 'hooks' in s, 'hooks missing'
for ev in ('SessionStart', 'PreToolUse', 'PostToolUse', 'Stop', 'Notification'):
    assert ev in s['hooks'], f'hook event {ev} missing'
print('OK')
"
  [ "$status" -eq 0 ]
}

@test ".mcp.json registers ralph server with absolute paths" {
  run "$INSTALLER" --scope user
  [ "$status" -eq 0 ]
  run python3 -c "
import json
with open('$HOME/.claude/.mcp.json') as f:
    m = json.load(f)
ralph = m['mcpServers']['ralph']
assert ralph['command'] == 'python3'
assert ralph['args'] == ['-m', 'ralph_mcp_server']
assert ralph['env']['PYTHONPATH'].endswith('mcp-server'), ralph['env']
assert ralph['env']['RALPH_REPO'].endswith('agent_testplayground'), ralph['env']
print('OK')
"
  [ "$status" -eq 0 ]
}

@test "second install is idempotent (no errors; no duplicate symlinks)" {
  run "$INSTALLER" --scope user
  [ "$status" -eq 0 ]
  run "$INSTALLER" --scope user
  [ "$status" -eq 0 ]
  # Settings still has exactly one SessionStart entry (not duplicated).
  count="$(python3 -c "import json; print(len(json.load(open('$HOME/.claude/settings.json'))['hooks']['SessionStart']))")"
  [ "$count" = "1" ]
}

@test "installer refuses to clobber a non-symlink file" {
  mkdir -p "$HOME/.claude/commands"
  echo 'real file' > "$HOME/.claude/commands/ralph-memory.md"
  run "$INSTALLER" --scope user
  [ "$status" -eq 67 ]
  # Original file untouched.
  [ "$(cat "$HOME/.claude/commands/ralph-memory.md")" = "real file" ]
}

@test "uninstall removes everything tracked + leaves user files alone" {
  echo '{"my":"settings"}' > /tmp/preserve-settings-marker.json
  "$INSTALLER" --scope user >/dev/null
  # Add a user-owned file inside .claude/ that we should NOT touch.
  echo 'user-only' > "$HOME/.claude/my-other-file.txt"
  run "$UNINSTALLER" --scope user
  [ "$status" -eq 0 ]
  # Tracked symlinks gone.
  [ ! -e "$HOME/.claude/commands/ralph-memory.md" ]
  [ ! -e "$HOME/.claude/hooks/session-start.sh" ]
  [ ! -f "$HOME/.claude/.ralph-installed.json" ]
  # User file preserved.
  [ -f "$HOME/.claude/my-other-file.txt" ]
  [ "$(cat "$HOME/.claude/my-other-file.txt")" = "user-only" ]
}

@test "uninstall is no-op when nothing installed" {
  run "$UNINSTALLER" --scope user
  [ "$status" -eq 0 ]
  [[ "$output" == *"nothing to undo"* ]]
}

@test "--without-mcp skips MCP registration" {
  run "$INSTALLER" --scope user --without-mcp
  [ "$status" -eq 0 ]
  [ ! -f "$HOME/.claude/.mcp.json" ]
}

@test "project scope writes to repo .claude/ (not HOME)" {
  pushd "$BATS_TEST_TMPDIR" >/dev/null
  cp -r "$REPO" testrepo
  cd testrepo
  run "./prompts/ralph-meta-chain/install/install_claude_code.sh" --scope project --without-mcp
  [ "$status" -eq 0 ]
  [ -d "./.claude/commands" ]
  [ ! -d "$HOME/.claude/commands" ]
  popd >/dev/null
}
