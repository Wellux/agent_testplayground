#!/usr/bin/env bash
# ralph_research_digest.sh — wraps prompts/ralph-meta-chain/04-research-ingest.md.
#
# Risk class: LOW. One-shot ad-hoc invocation; does NOT install cron.

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_research_digest.sh" "Run the daily research-ingest pass."
  cat <<EOF
WHAT
  Reads prompts/ralph-meta-chain/04-research-ingest.md and pipes it to \`claude -p\`.

USAGE
  ralph_research_digest.sh                          # one-shot run
  ralph_research_digest.sh --help

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prompt="$repo/prompts/ralph-meta-chain/04-research-ingest.md"
[[ -f "$prompt" ]] || { ralph_error "missing $prompt"; exit 66; }
command -v claude >/dev/null || { ralph_error "claude not on PATH"; exit 67; }

ralph_log "running research_digest pass: $prompt"
claude -p "$(cat "$prompt")"
