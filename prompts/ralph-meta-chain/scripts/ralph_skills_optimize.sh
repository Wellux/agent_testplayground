#!/usr/bin/env bash
# ralph_skills.sh — wraps prompts/ralph-meta-chain/02-skills-optimizer.md.
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
  ralph_help_header "ralph_skills.sh" "Run the skills pass once via claude -p."
  cat <<EOF
WHAT
  Reads prompts/ralph-meta-chain/02-skills-optimizer.md and pipes it to \`claude -p\`.

USAGE
  ralph_skills.sh                          # one-shot run
  ralph_skills.sh --help

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prompt="$repo/prompts/ralph-meta-chain/02-skills-optimizer.md"
[[ -f "$prompt" ]] || { ralph_error "missing $prompt"; exit 66; }
command -v claude >/dev/null || { ralph_error "claude not on PATH"; exit 67; }

ralph_log "running skills pass: $prompt"
claude -p "$(cat "$prompt")"
