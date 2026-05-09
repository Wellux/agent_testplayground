#!/usr/bin/env bash
# ralph_memory_optimize.sh — wraps the daily memory pass.
#   claude -p "$(cat 01-memory-optimizer.md)"
#
# Risk class: LOW (read-only ad-hoc; does NOT install cron; uses
# Phase 1-6 prompt unchanged).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_memory_optimize.sh" "Run the memory pass once via claude -p."
  cat <<EOF
WHAT
  Reads prompts/ralph-meta-chain/01-memory-optimizer.md and pipes it
  to \`claude -p\`. The prompt itself honors all the budgets,
  invariants, and \`<promise>COMPLETE</promise>\` exit contract
  documented in \`docs/CRON_JOBS.md\`.

USAGE
  ralph_memory_optimize.sh                    # one-shot run
  ralph_memory_optimize.sh --help

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prompt="$repo/prompts/ralph-meta-chain/01-memory-optimizer.md"
[[ -f "$prompt" ]] || { ralph_error "missing $prompt"; exit 66; }
command -v claude >/dev/null || { ralph_error "claude not on PATH"; exit 67; }

ralph_log "running memory pass: $prompt"
claude -p "$(cat "$prompt")"
