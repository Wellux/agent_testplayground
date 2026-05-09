#!/usr/bin/env bash
# ralph_index_vault.sh — full vault re-embed via the Phase 1-6 harness.
# Risk class: LOW (read-mostly; writes to 90-Meta/embeddings.db).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_index_vault.sh" "Re-embed the whole vault via Ollama."
  cat <<EOF
WHAT
  Wraps \`python -m harness embed --vault-full\`. Re-indexes every
  vault note into 90-Meta/embeddings.db (sqlite-vec + FTS5).

REQUIRES
  - python3 + harness package on PATH (cd \$REPO/harness; uv sync)
  - Ollama running locally (default http://localhost:11434)
  - nomic-embed-text model pulled (\`ollama pull nomic-embed-text\`)

USAGE
  ralph_index_vault.sh                       # default 5-min cap
  ralph_index_vault.sh --since 2h            # only re-embed recent changes

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
cd "$repo/harness"
exec python3 -m harness embed --vault-full "${RALPH_PASSTHROUGH[@]}"
