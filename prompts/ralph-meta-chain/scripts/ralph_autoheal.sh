#!/usr/bin/env bash
# ralph_autoheal.sh — wraps prompts/ralph-meta-chain/06-autoheal.md.
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
  ralph_help_header "ralph_autoheal.sh" "Run the autoheal supervisor + harness self-test."
  cat <<EOF
WHAT
  Reads prompts/ralph-meta-chain/06-autoheal.md and pipes it to \`claude -p\`.

USAGE
  ralph_autoheal.sh                          # one-shot run
  ralph_autoheal.sh --help

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prompt="$repo/prompts/ralph-meta-chain/06-autoheal.md"
[[ -f "$prompt" ]] || { ralph_error "missing $prompt"; exit 66; }
command -v claude >/dev/null || { ralph_error "claude not on PATH"; exit 67; }

ralph_log "running autoheal pass: $prompt"
claude -p "$(cat "$prompt")"
