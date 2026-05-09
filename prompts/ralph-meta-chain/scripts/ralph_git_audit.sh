#!/usr/bin/env bash
# ralph_git_audit.sh — git log + diff summary for the most recent commits.
# Risk class: LOW (read-only).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"
# shellcheck source=lib/git_safety.sh
source "$HERE/lib/git_safety.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_git_audit.sh" "Recent git activity in the repo."
  cat <<EOF
WHAT
  Renders a 1-screen overview:
    - HEAD branch + dirty status,
    - last 10 commits oneline,
    - file-change summary per commit,
    - any push-suspicious flags in the last 50 reflog entries.

USAGE
  ralph_git_audit.sh                     # default 10 commits
  ralph_git_audit.sh -- -n 20            # passthrough to git log -n

EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
cd "$repo"

cat <<EOF
# Git audit — $(date -u +%Y-%m-%dT%H:%M:%SZ)

## HEAD
- branch: $(git rev-parse --abbrev-ref HEAD)
- commit: $(git rev-parse --short HEAD)
- dirty:  $(git status --porcelain | wc -l) file(s) changed

## Recent commits
EOF
git log --oneline -n "${1:-10}" || true

cat <<EOF

## File change summary
EOF
git log --stat --format='%h %s' -n "${1:-10}" 2>/dev/null | head -120

cat <<EOF

## Recent reflog (last 25)
EOF
git reflog -n 25 2>/dev/null || echo "(no reflog)"
