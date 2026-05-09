#!/usr/bin/env bash
# scripts/lib/common.sh — shared base for ralph_*.sh shims.
#
# Conventions:
#   - log/warn/error → stderr (stdout stays clean for piping).
#   - all scripts source this file via:
#       source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
#   - flags: --dry-run / --apply / --confirmed / -h --help.

# Don't `set -euo pipefail` here — leave that to each caller. Some shims
# need pipelines that tolerate sub-failures.

ralph_log()   { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
ralph_warn()  { ralph_log "WARN: $*"; }
ralph_error() { ralph_log "ERROR: $*"; }

# Parse common flags. Sets RALPH_DRY_RUN / RALPH_APPLY / RALPH_CONFIRMED /
# RALPH_HELP in caller scope. Forwards anything else to RALPH_PASSTHROUGH
# (an array).
ralph_parse_flags() {
  RALPH_DRY_RUN=1
  RALPH_APPLY=0
  RALPH_CONFIRMED=0
  RALPH_HELP=0
  RALPH_PASSTHROUGH=()
  for arg in "$@"; do
    case "$arg" in
      --dry-run) RALPH_DRY_RUN=1; RALPH_APPLY=0 ;;
      --apply)   RALPH_DRY_RUN=0; RALPH_APPLY=1 ;;
      --confirmed) RALPH_CONFIRMED=1 ;;
      -h|--help) RALPH_HELP=1 ;;
      *) RALPH_PASSTHROUGH+=("$arg") ;;
    esac
  done
}

# Standard help blurb header — each shim adds its own body.
ralph_help_header() {
  local script="$1"; local synopsis="$2"
  cat <<EOF
$script — $synopsis

USAGE
  $script [--dry-run] [--apply] [--help] [<extra args>]

DEFAULT MODE
  Dry-run for any script that mutates files. Use --apply to act.

EOF
}
