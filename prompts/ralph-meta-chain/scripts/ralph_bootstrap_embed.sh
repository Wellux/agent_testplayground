#!/usr/bin/env bash
# ralph_bootstrap_embed.sh — opt-in: pull Ollama embedding model and run a
# full vault index. Designed for first-install on the user's real host.
#
# Default: --dry-run (prints what it would do). Pass --apply to execute.
# Refuses if Ollama isn't on PATH and prints the install command.
#
# Usage:
#   ./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh           # dry-run
#   ./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh --apply   # for real

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh" 2>/dev/null || true

DRY_RUN=1
EMBED_MODEL="${RALPH_EMBED_MODEL:-nomic-embed-text}"

usage() {
  cat <<EOF
ralph_bootstrap_embed.sh — bootstrap the local vault embedding index.

USAGE: $0 [--apply] [--model <name>]

OPTIONS:
  --apply            Actually run (default is dry-run).
  --model <name>     Ollama model to pull (default: nomic-embed-text).
  -h, --help         Show this help.

ENVIRONMENT:
  RALPH_EMBED_MODEL  Override default embedding model.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) DRY_RUN=0; shift ;;
    --model) EMBED_MODEL="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[bootstrap-embed] unknown arg: $1" >&2; usage; exit 64 ;;
  esac
done

# Locate repo root (walk up to .git).
find_repo_root() {
  local p="$SCRIPT_DIR"
  while [[ "$p" != "/" ]]; do
    if [[ -d "$p/.git" ]]; then echo "$p"; return; fi
    p="$(dirname "$p")"
  done
  echo "[bootstrap-embed] no .git ancestor found from $SCRIPT_DIR" >&2
  exit 1
}
REPO_ROOT="$(find_repo_root)"
HARNESS_DIR="$REPO_ROOT/prompts/ralph-meta-chain/scripts/harness"

echo "[bootstrap-embed] repo root: $REPO_ROOT"
echo "[bootstrap-embed] harness dir: $HARNESS_DIR"
echo "[bootstrap-embed] embedding model: $EMBED_MODEL"
[[ $DRY_RUN -eq 1 ]] && echo "[bootstrap-embed] mode: DRY-RUN (pass --apply to execute)"

# Gate 1: Ollama on PATH.
if ! command -v ollama >/dev/null 2>&1; then
  cat >&2 <<EOF
[bootstrap-embed] FAIL: 'ollama' is not on PATH.

Install Ollama first:
  macOS:   brew install ollama && ollama serve &
  Linux:   curl -fsSL https://ollama.com/install.sh | sh
  Other:   see https://ollama.com/download

After install, run this script again.
EOF
  exit 65
fi
echo "[bootstrap-embed] ollama found: $(command -v ollama)"

# Gate 2: harness directory exists.
if [[ ! -d "$HARNESS_DIR" ]]; then
  echo "[bootstrap-embed] FAIL: harness not found at $HARNESS_DIR" >&2
  exit 66
fi

# Gate 3: vault path resolved (via config.yml or $VAULT).
RESOLVED_VAULT="${VAULT:-}"
if [[ -z "$RESOLVED_VAULT" ]]; then
  CONFIG_YML="$REPO_ROOT/prompts/ralph-meta-chain/config.yml"
  if [[ -f "$CONFIG_YML" ]]; then
    RESOLVED_VAULT="$(grep -E '^vault_path:' "$CONFIG_YML" | head -1 \
      | sed -E 's/^vault_path:[[:space:]]*//; s/^"//; s/"$//; s/^'"'"'//; s/'"'"'$//' \
      | sed "s|^~/|${HOME}/|")"
  fi
fi
if [[ -z "$RESOLVED_VAULT" ]]; then
  echo "[bootstrap-embed] FAIL: vault path not set. Either:" >&2
  echo "  - export VAULT=/path/to/your/vault, or" >&2
  echo "  - cp $REPO_ROOT/prompts/ralph-meta-chain/config.example.yml \\" >&2
  echo "       $REPO_ROOT/prompts/ralph-meta-chain/config.yml and edit vault_path." >&2
  exit 67
fi
echo "[bootstrap-embed] vault: $RESOLVED_VAULT"

if [[ ! -d "$RESOLVED_VAULT" ]]; then
  echo "[bootstrap-embed] FAIL: vault directory does not exist: $RESOLVED_VAULT" >&2
  exit 68
fi

# Step 1: pull the embedding model.
echo "[bootstrap-embed] step 1: pull '$EMBED_MODEL' via ollama"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "  would run: ollama pull $EMBED_MODEL"
else
  ollama pull "$EMBED_MODEL"
fi

# Step 2: run a full vault index via harness.
echo "[bootstrap-embed] step 2: full vault index"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "  would run: (cd $HARNESS_DIR && uv run python -m harness embed --vault $RESOLVED_VAULT --vault-full)"
else
  ( cd "$HARNESS_DIR" && uv run python -m harness embed --vault "$RESOLVED_VAULT" --vault-full )
fi

echo
if [[ $DRY_RUN -eq 1 ]]; then
  echo "[bootstrap-embed] DRY-RUN complete. Re-run with --apply to execute."
else
  echo "[bootstrap-embed] DONE."
  echo "  Verify: ls -lh $RESOLVED_VAULT/90-Meta/embeddings.db"
  echo "  Query : (cd $HARNESS_DIR && uv run python -m harness query --vault $RESOLVED_VAULT 'your search')"
fi
