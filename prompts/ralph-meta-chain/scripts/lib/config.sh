#!/usr/bin/env bash
# scripts/lib/config.sh — read prompts/ralph-meta-chain/config.yml.
# Tiny YAML reader; we only need top-level scalar keys.

# Echo the value for a top-level YAML key. Empty if missing.
#   ralph_config_get <key>          # uses default config path
#   ralph_config_get <key> <path>
ralph_config_get() {
  local key="$1"
  local path="${2:-}"
  if [[ -z "$path" ]]; then
    local repo
    repo="$(git -C "${BASH_SOURCE%/*}" rev-parse --show-toplevel 2>/dev/null \
              || git -C . rev-parse --show-toplevel 2>/dev/null)"
    path="$repo/prompts/ralph-meta-chain/config.yml"
    [[ -f "$path" ]] || path="$repo/prompts/ralph-meta-chain/config.example.yml"
  fi
  [[ -f "$path" ]] || return 1
  awk -v k="$key" 'BEGIN{FS=":"} $1==k {sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'\'']|["'\'']$)/,""); print; exit}' "$path"
}

# Resolve $VAULT: env var > config.yml's vault_path > error.
ralph_vault_path() {
  if [[ -n "${VAULT:-}" ]]; then
    echo "$VAULT"
    return 0
  fi
  local v
  v="$(ralph_config_get vault_path)"
  if [[ -z "$v" ]]; then
    return 1
  fi
  # Expand a leading "~/" to "$HOME/". `${v#~/}` would tilde-EXPAND
  # (replacing $HOME-prefix), not literal-strip a `~/` prefix — sed
  # is robust.
  echo "$v" | sed "s|^~/|${HOME}/|"
}

# Echo absolute path to repo root via git.
ralph_repo_root() {
  git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null
}
