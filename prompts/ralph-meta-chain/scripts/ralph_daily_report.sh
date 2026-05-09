#!/usr/bin/env bash
# ralph_daily_report.sh — composite read of today's reports.
# Risk class: LOW (read-only; renders Markdown to stdout).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"
# shellcheck source=lib/logging.sh
source "$HERE/lib/logging.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_daily_report.sh" "Composite of today's vault reports."
  cat <<EOF
WHAT
  Pulls the most recent log line per axis from \$VAULT/90-Meta/log.md
  + a 50-line tail. Useful when you don't have Obsidian open.

USAGE
  ralph_daily_report.sh
  ralph_daily_report.sh --tail 200

EOF
  exit 0
fi

vault="$(ralph_vault_path)" || { ralph_error "vault path not set"; exit 1; }
log="$vault/90-Meta/log.md"

cat <<EOF
# Daily report — $(date -u +%Y-%m-%d)

Vault: $vault

## Most recent line per axis
EOF

for axis in research memory skills interaction compress heal evolve update; do
  line="$(grep -E "\] $axis \|" "$log" 2>/dev/null | tail -n 1 || true)"
  if [[ -n "$line" ]]; then
    echo "- $line"
  else
    echo "- $axis: (no log line yet)"
  fi
done

echo
echo "## log.md tail"
echo
ralph_log_tail "$log" "${RALPH_PASSTHROUGH[1]:-50}"
