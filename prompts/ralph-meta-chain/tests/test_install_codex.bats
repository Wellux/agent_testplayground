#!/usr/bin/env bats
# install_codex.sh + uninstall_codex.sh round-trip tests.
# Run via: bats prompts/ralph-meta-chain/tests/test_install_codex.bats

REPO="$(git rev-parse --show-toplevel)"
INSTALLER="$REPO/prompts/ralph-meta-chain/install/install_codex.sh"
UNINSTALLER="$REPO/prompts/ralph-meta-chain/install/uninstall_codex.sh"

setup() {
  : "${BATS_TEST_TMPDIR:?missing BATS_TEST_TMPDIR}"
  export HOME="$BATS_TEST_TMPDIR/home"
  export CODEX_HOME="$HOME/.codex"
  mkdir -p "$HOME"
}

@test "installer + uninstaller exist and are executable" {
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
  [[ "$output" == *"--without-mcp"* ]]
  [[ "$output" == *"--without-prompts"* ]]
}

@test "dry-run emits 'DRY:' lines and writes nothing" {
  run "$INSTALLER" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"DRY:"* ]]
  [ ! -d "$HOME/.codex" ]
  [ ! -d "$HOME/.agents" ]
}

@test "wet user install creates expected structure (skills + prompts + TOML)" {
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  # Specialist skills (8) — symlinks to skill directories.
  [ -L "$HOME/.agents/skills/memory-architect" ]
  [ -L "$HOME/.agents/skills/prompt-evaluator" ]
  # Axis subagents wrapped as skill directories with SKILL.md inside.
  [ -d "$HOME/.agents/skills/ralph-memory" ]
  [ -L "$HOME/.agents/skills/ralph-memory/SKILL.md" ]
  [ -L "$HOME/.agents/skills/ralph-research/SKILL.md" ]
  [ -L "$HOME/.agents/skills/ralph-update/SKILL.md" ]
  # Custom prompts (11).
  [ -L "$CODEX_HOME/prompts/ralph-cron.md" ]
  [ -L "$CODEX_HOME/prompts/ralph-memory.md" ]
  [ -L "$CODEX_HOME/prompts/ralph-research.md" ]
  # MCP TOML registration.
  [ -f "$CODEX_HOME/config.toml" ]
  # AGENTS.md briefing.
  [ -f "$CODEX_HOME/AGENTS.md" ]
  # Manifest.
  [ -f "$CODEX_HOME/.ralph-installed.json" ]
}

@test "config.toml parses as valid TOML and exposes ralph MCP server" {
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  run python3 -c "
import tomllib
with open('$CODEX_HOME/config.toml','rb') as f:
    d = tomllib.load(f)
ralph = d['mcp_servers']['ralph']
assert ralph['command'] == 'python3', ralph
assert ralph['args'] == ['-m', 'ralph_mcp_server'], ralph
assert 'cwd' in ralph and ralph['cwd'].endswith('mcp-server'), ralph
env = ralph.get('env', {})
assert env.get('PYTHONPATH','').endswith('mcp-server'), env
assert env.get('RALPH_REPO','').endswith('agent_testplayground'), env
print('OK')
"
  [ "$status" -eq 0 ]
}

@test "second install is idempotent (no duplicate ralph block; same TOML)" {
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  hash1="$(sha256sum "$CODEX_HOME/config.toml" | cut -d' ' -f1)"
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  hash2="$(sha256sum "$CODEX_HOME/config.toml" | cut -d' ' -f1)"
  [ "$hash1" = "$hash2" ]
  # And only one [mcp_servers.ralph] section in the TOML.
  count="$(grep -c '^\[mcp_servers\.ralph\]$' "$CODEX_HOME/config.toml")"
  [ "$count" = "1" ]
}

@test "TOML merge preserves pre-existing user content" {
  mkdir -p "$CODEX_HOME"
  cat > "$CODEX_HOME/config.toml" <<'EOF'
# my preserved comment
model = "gpt-5"
disable_response_storage = true

[mcp_servers.fileSystem]
command = "node"
args = ["/usr/local/bin/fs-server"]
EOF
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  # User keys still present.
  run python3 -c "
import tomllib
d = tomllib.load(open('$CODEX_HOME/config.toml','rb'))
assert d['model'] == 'gpt-5'
assert d['disable_response_storage'] is True
assert 'fileSystem' in d['mcp_servers']
assert 'ralph' in d['mcp_servers']
"
  [ "$status" -eq 0 ]
  # User comment line still present.
  grep -q '^# my preserved comment' "$CODEX_HOME/config.toml"
}

@test "AGENTS.md briefing has the RALPH-managed marker" {
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  head -1 "$CODEX_HOME/AGENTS.md" | grep -q '^<!-- RALPH-managed AGENTS.md briefing -->'
}

@test "second install keeps user-edited AGENTS.md untouched" {
  "$INSTALLER" >/dev/null
  # Strip the marker (simulate user editing).
  tail -n +2 "$CODEX_HOME/AGENTS.md" > "$CODEX_HOME/AGENTS.md.tmp"
  mv "$CODEX_HOME/AGENTS.md.tmp" "$CODEX_HOME/AGENTS.md"
  echo "USER OVERRIDE LINE" >> "$CODEX_HOME/AGENTS.md"
  # Re-install.
  run "$INSTALLER"
  [ "$status" -eq 0 ]
  # User edit preserved; marker is gone.
  grep -q '^USER OVERRIDE LINE$' "$CODEX_HOME/AGENTS.md"
  ! grep -q '^<!-- RALPH-managed' "$CODEX_HOME/AGENTS.md"
}

@test "installer refuses to clobber a non-symlink skill file" {
  mkdir -p "$HOME/.agents/skills"
  echo 'real file' > "$HOME/.agents/skills/memory-architect"
  run "$INSTALLER"
  [ "$status" -eq 67 ]
  [ "$(cat "$HOME/.agents/skills/memory-architect")" = "real file" ]
}

@test "uninstall removes everything tracked + leaves user files alone" {
  "$INSTALLER" >/dev/null
  echo 'user keep me' > "$HOME/.agents/skills/my-personal-skill.md" 2>/dev/null || true
  echo 'user toml' > "$CODEX_HOME/scratch.toml"
  run "$UNINSTALLER"
  [ "$status" -eq 0 ]
  [ ! -L "$HOME/.agents/skills/memory-architect" ]
  [ ! -d "$HOME/.agents/skills/ralph-memory" ]
  [ ! -L "$CODEX_HOME/prompts/ralph-memory.md" ]
  # User files preserved.
  [ -f "$HOME/.agents/skills/my-personal-skill.md" ]
  [ -f "$CODEX_HOME/scratch.toml" ]
}

@test "uninstall preserves pre-existing user TOML content" {
  mkdir -p "$CODEX_HOME"
  cat > "$CODEX_HOME/config.toml" <<'EOF'
model = "gpt-5"

[mcp_servers.fileSystem]
command = "node"
EOF
  "$INSTALLER" >/dev/null
  run "$UNINSTALLER"
  [ "$status" -eq 0 ]
  [ -f "$CODEX_HOME/config.toml" ]
  run python3 -c "
import tomllib
d = tomllib.load(open('$CODEX_HOME/config.toml','rb'))
assert d['model'] == 'gpt-5'
assert 'fileSystem' in d['mcp_servers']
assert 'ralph' not in d.get('mcp_servers', {}), 'ralph block should be gone'
"
  [ "$status" -eq 0 ]
}

@test "uninstall removes empty config.toml" {
  "$INSTALLER" >/dev/null
  run "$UNINSTALLER"
  [ "$status" -eq 0 ]
  [ ! -f "$CODEX_HOME/config.toml" ]
}

@test "uninstall is no-op when nothing installed" {
  run "$UNINSTALLER"
  [ "$status" -eq 0 ]
  [[ "$output" == *"nothing to undo"* ]]
}

@test "--without-prompts skips ~/.codex/prompts/" {
  run "$INSTALLER" --without-prompts
  [ "$status" -eq 0 ]
  [ -d "$HOME/.agents/skills" ]
  [ ! -d "$CODEX_HOME/prompts" ]
}

@test "--without-mcp skips MCP TOML registration" {
  run "$INSTALLER" --without-mcp
  [ "$status" -eq 0 ]
  [ ! -f "$CODEX_HOME/config.toml" ]
  [ -d "$HOME/.agents/skills" ]
}

@test "project scope writes skills to repo .agents/skills/ (not HOME)" {
  pushd "$BATS_TEST_TMPDIR" >/dev/null
  cp -r "$REPO" testrepo
  cd testrepo
  run "./prompts/ralph-meta-chain/install/install_codex.sh" --scope project --without-mcp
  [ "$status" -eq 0 ]
  [ -d "./.agents/skills" ]
  # User home should still be empty for skills (project scope).
  [ ! -d "$HOME/.agents/skills" ] || [ -z "$(ls -A "$HOME/.agents/skills" 2>/dev/null)" ]
  popd >/dev/null
}
