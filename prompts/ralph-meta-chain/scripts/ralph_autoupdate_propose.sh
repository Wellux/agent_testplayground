#!/usr/bin/env bash
# ralph_autoupdate_propose.sh — wraps prompts/ralph-meta-chain/08-autoupdate.md.
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
  ralph_help_header "ralph_autoupdate_propose.sh" "Run the weekly autoupdate scout."
  cat <<EOF
WHAT
  Reads prompts/ralph-meta-chain/08-autoupdate.md and pipes it to \`claude -p\`.

USAGE
  ralph_autoupdate_propose.sh                          # one-shot run
  ralph_autoupdate_propose.sh --help

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prompt="$repo/prompts/ralph-meta-chain/08-autoupdate.md"
[[ -f "$prompt" ]] || { ralph_error "missing $prompt"; exit 66; }
command -v claude >/dev/null || { ralph_error "claude not on PATH"; exit 67; }

ralph_log "running autoupdate_propose pass: $prompt"
claude -p "$(cat "$prompt")"
