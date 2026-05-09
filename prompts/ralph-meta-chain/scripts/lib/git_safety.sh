#!/usr/bin/env bash
# scripts/lib/git_safety.sh — guards against unsafe git ops.

# Refuse if working tree is dirty (apart from caller-allowed paths).
#   ralph_git_require_clean [<allow-prefix>]
ralph_git_require_clean() {
  local allow="${1:-}"
  local repo
  repo="$(git rev-parse --show-toplevel 2>/dev/null)" || return 1
  local dirty
  if [[ -n "$allow" ]]; then
    dirty="$(git -C "$repo" status --porcelain | awk -v a="$allow" '$2 !~ a {print $2}')"
  else
    dirty="$(git -C "$repo" status --porcelain | awk '{print $2}')"
  fi
  if [[ -n "$dirty" ]]; then
    echo "git tree dirty:" >&2
    echo "$dirty" | head -10 >&2
    return 1
  fi
}

# Refuse force-push, force-with-lease, --no-verify on any push args.
#   ralph_git_check_push_args "$@"
ralph_git_check_push_args() {
  for arg in "$@"; do
    case "$arg" in
      -f|--force|--force-with-lease|--no-verify)
        echo "git_safety: refusing dangerous flag: $arg" >&2
        return 1
        ;;
    esac
  done
  return 0
}

# Append a line to migration-log.md (or another append-only audit log).
#   ralph_git_audit_append <log-path> <message>
ralph_git_audit_append() {
  local log="$1"; shift
  local msg="$*"
  mkdir -p "$(dirname "$log")"
  printf '## [%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" >> "$log"
}
