#!/usr/bin/env bash
# ralph_ab_harness.sh — passthrough to `python -m harness ab`.
# Risk class: LOW (writes 2 metrics rows; deterministic).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_ab_harness.sh" "A/B two prompts on a fixture."
  cat <<EOF
WHAT
  Wraps \`python -m harness ab\`. Runs incumbent + candidate prompts,
  scores each via the LLM judge, writes two rows to
  90-Meta/metrics.ndjson, returns 0 (candidate wins), 1 (incumbent
  wins), or 2 (tie).

REQUIRES
  - ANTHROPIC_API_KEY in harness/.env

USAGE
  ralph_ab_harness.sh \\
    --incumbent  50-Prompts/code-review.md \\
    --candidate  50-Prompts/code-review.candidate-1.md \\
    --fixture    harness/fixtures/code-review.yml

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
cd "$repo/harness"
exec python3 -m harness ab "${RALPH_PASSTHROUGH[@]}"
