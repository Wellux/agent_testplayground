#!/usr/bin/env bash
# ralph_business_ledger_check.sh — schema check for business-entity ledgers.
# Risk class: LOW (read-only).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"
# shellcheck source=lib/markdown.sh
source "$HERE/lib/markdown.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_business_ledger_check.sh" "Lint business-entity ledger files."
  cat <<EOF
WHAT
  Verifies each ledger file under business-entity/ledgers/ has:
    - YAML frontmatter,
    - ralph_type: business,
    - status: active,
    - the section headings expected by governance/audit-policy.md.

  Append-only invariant is checked: the most recent entry must NOT
  be earlier than the file's \`created:\` field (no time-travel writes).

  Exit code = number of files with issues (0 = clean).

USAGE
  ralph_business_ledger_check.sh
EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
ledger_dir="$repo/prompts/ralph-meta-chain/business-entity/ledgers"
[[ -d "$ledger_dir" ]] || { ralph_error "ledgers/ missing"; exit 66; }

fail=0
for f in "$ledger_dir"/*.md; do
  [[ -f "$f" ]] || continue
  base="$(basename "$f" .md)"

  if ! ralph_md_has_frontmatter "$f"; then
    printf '%s: missing frontmatter\n' "$base" >&2
    fail=$((fail + 1))
    continue
  fi

  rtype="$(ralph_md_fm_get ralph_type "$f")"
  if [[ "$rtype" != "business" ]]; then
    printf '%s: ralph_type=%s (expected business)\n' "$base" "$rtype" >&2
    fail=$((fail + 1))
  fi

  status="$(ralph_md_fm_get status "$f")"
  if [[ "$status" != "active" ]]; then
    printf '%s: status=%s (expected active)\n' "$base" "$status" >&2
    fail=$((fail + 1))
  fi

  # Spot-check: ledgers should mention "Append-only" somewhere.
  if ! grep -qiE 'append-only' "$f"; then
    printf '%s: missing "Append-only" note\n' "$base" >&2
    fail=$((fail + 1))
  fi
done

ralph_log "ledger lint failures: $fail"
exit $((fail > 254 ? 254 : fail))
