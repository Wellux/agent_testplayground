#!/usr/bin/env bash
# ralph_provider_validate.sh — verify each providers/<vendor>/adapter-spec.md
# fills the 13 fields per provider-interface.schema.json.
# Risk class: LOW (read-only).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_provider_validate.sh" "Spec-conformance check for adapter specs."
  cat <<EOF
WHAT
  For each providers/<vendor>/adapter-spec.md, verify the 13 fields
  from providers/provider-interface.md are mentioned by name (not
  necessarily populated — that's a separate readiness check).

  Active provider (claude-code) must have all 13 populated.
  Deferred providers must mention all 13 (template form is OK).

  Exit code = total missing (0 = all conformant).

USAGE
  ralph_provider_validate.sh
EOF
  exit 0
fi

repo="$(ralph_repo_root .)" || { ralph_error "not in a git repo"; exit 1; }
prov_dir="$repo/prompts/ralph-meta-chain/providers"
[[ -d "$prov_dir" ]] || { ralph_error "providers/ missing"; exit 66; }

required_fields=(
  prompt_input_format
  context_package_format
  memory_retrieval_package_format
  tool_permission_model
  file_read_write_model
  shell_execution_model
  approval_gate_model
  output_report_format
  error_format
  evaluation_format
  logging_format
  rollback_expectation
  provider_metadata
)

fail=0
for vendor_dir in "$prov_dir"/*/; do
  vendor="$(basename "$vendor_dir")"
  spec="$vendor_dir/adapter-spec.md"
  case "$vendor" in
    claude-code) spec="$vendor_dir/runtime-notes.md" ;;
  esac
  if [[ ! -f "$spec" ]]; then
    ralph_warn "$vendor: no adapter-spec.md"
    fail=$((fail + 1))
    continue
  fi
  for f in "${required_fields[@]}"; do
    if ! grep -qE "^[#]+[[:space:]]+[0-9]+\.[[:space:]]+\`?${f}\`?\b|^${f}:" "$spec"; then
      printf '%s → missing field: %s\n' "$vendor" "$f" >&2
      fail=$((fail + 1))
    fi
  done
done

ralph_log "field-conformance failures: $fail"
exit $((fail > 254 ? 254 : fail))
