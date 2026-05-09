#!/usr/bin/env bash
# ralph_validate_frontmatter.sh — walk $VAULT and check every .md has
# valid frontmatter per memory-frontmatter.schema.json.
# Risk class: LOW (read-only).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"
# shellcheck source=lib/markdown.sh
source "$HERE/lib/markdown.sh"
# shellcheck source=lib/frontmatter.sh
source "$HERE/lib/frontmatter.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_validate_frontmatter.sh" "Check every .md in the vault."
  cat <<EOF
WHAT
  For each .md under \$VAULT (excluding _archive/ / _processed/ /
  _rejected/ / _population/), verify:
    - has YAML frontmatter,
    - has \`ralph_type\` and \`created\` fields.

  Files failing print to stderr; exit code is the count of failures
  (0 = all valid).

USAGE
  ralph_validate_frontmatter.sh                    # default: \$VAULT
  ralph_validate_frontmatter.sh -- /path/to/dir    # passthrough

EOF
  exit 0
fi

target="${RALPH_PASSTHROUGH[0]:-}"
if [[ -z "$target" ]]; then
  target="$(ralph_vault_path 2>/dev/null || true)"
fi
[[ -d "$target" ]] || { ralph_error "no vault dir: ${target:-<unset>}"; exit 1; }

ralph_log "scanning $target"
fail="$(ralph_fm_validate_tree "$target")"
ralph_log "validation failures: $fail"
[[ "$fail" =~ ^[0-9]+$ ]] || fail=1
exit $((fail > 254 ? 254 : fail))
