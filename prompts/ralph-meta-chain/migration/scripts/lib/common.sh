#!/usr/bin/env bash
# migration/scripts/lib/common.sh — shared helpers for migration scripts.
# Sourced via: source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

set -euo pipefail

# Repo root via git. Robust to call chains: BASH_SOURCE indexing is fragile
# when functions call each other across sourced files. Falls back to walking
# up from $PWD looking for a .git directory if git itself is unavailable.
ralph_repo_root() {
  local start="${1:-$PWD}"
  if command -v git >/dev/null 2>&1; then
    local r
    r="$(git -C "$start" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "$r" ]]; then
      echo "$r"
      return 0
    fi
  fi
  local d
  d="$(cd -- "$start" && pwd)"
  while [[ "$d" != "/" && -n "$d" ]]; do
    [[ -d "$d/.git" ]] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}

# Migration directory under prompts/ralph-meta-chain/.
ralph_migration_dir() {
  echo "$(ralph_repo_root)/prompts/ralph-meta-chain/migration"
}

# Logging — to stderr so stdout stays clean for piping.
ralph_log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
ralph_warn() { ralph_log "WARN: $*"; }
ralph_error() { ralph_log "ERROR: $*"; }

# Standard help blurb.
ralph_print_help_header() {
  local script="$1"; local synopsis="$2"
  cat <<EOF
$script — $synopsis

USAGE
  $script [--dry-run] [--apply] [--help]

DEFAULT MODE
  Dry-run for any script that mutates files. Use --apply to act.

INVARIANTS (per docs/REPO_MIGRATION.md)
  - Default dry-run.
  - Inventory-first, proposal-second, apply-last.
  - Never move files outside the repo.
  - Never overwrite existing files.
  - git mv preserves history; cp+rm is forbidden.
  - Rollback plan must exist before apply.

EOF
}

# Parse common --dry-run / --apply / --help flags. Sets RALPH_APPLY=0|1
# and RALPH_HELP=0|1 in the caller's scope.
ralph_parse_flags() {
  RALPH_APPLY=0
  RALPH_HELP=0
  RALPH_CONFIRMED=0
  for arg in "$@"; do
    case "$arg" in
      --dry-run) RALPH_APPLY=0 ;;
      --apply)   RALPH_APPLY=1 ;;
      --confirmed) RALPH_CONFIRMED=1 ;;
      -h|--help) RALPH_HELP=1 ;;
      --) ;;
      *) ralph_warn "unknown arg: $arg" ;;
    esac
  done
}

# Refuse if invocation is unsafe. Hardens scripts against accidental --apply.
ralph_require_repo() {
  local repo
  repo="$(ralph_repo_root)"
  if [[ ! -d "$repo/.git" ]]; then
    ralph_error "not in a git repo (looking from $repo)"
    return 1
  fi
  if [[ ! -d "$repo/prompts/ralph-meta-chain" ]]; then
    ralph_error "$repo/prompts/ralph-meta-chain missing — wrong tree?"
    return 1
  fi
}

# Append a Karpathy-format line to migration-log.md.
# Truncates the head when the file exceeds RALPH_MIGRATION_LOG_MAX_LINES
# (default 500); the tail is what's audit-relevant. Truncation message
# is itself appended so the file stays self-describing.
ralph_migration_log_append() {
  local op="$1"; shift
  local kvs="$*"
  local mig
  mig="$(ralph_migration_dir)"
  local log="$mig/migration-log.md"
  local cap="${RALPH_MIGRATION_LOG_MAX_LINES:-500}"
  mkdir -p "$mig"

  # Rotate if we're about to exceed the cap.
  if [[ -f "$log" ]]; then
    local lines
    lines="$(wc -l < "$log" | tr -d ' ')"
    if [[ "$lines" -gt "$cap" ]]; then
      local keep=$((cap / 2))
      local tmp="${log}.tmp.$$"
      {
        printf '## [%s] migration | op=log-rotate kept=%d dropped=%d\n' \
          "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$keep" "$((lines - keep))"
        tail -n "$keep" "$log"
      } > "$tmp"
      mv "$tmp" "$log"
    fi
  fi

  printf '## [%s] migration | op=%s %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$op" "$kvs" \
    >> "$log"
}

# Atomic file write: write to .tmp then rename.
ralph_atomic_write() {
  local path="$1"; local content="$2"
  local tmp="${path}.tmp.$$"
  mkdir -p "$(dirname "$path")"
  printf '%s' "$content" > "$tmp"
  mv "$tmp" "$path"
}
