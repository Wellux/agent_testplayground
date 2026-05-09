#!/usr/bin/env bash
# install.sh — single-entry dispatcher for the three Ralph install targets.
#
#     prompts/ralph-meta-chain/install/install.sh --target <target> [flags]
#
# Targets (one or more, comma-separated; or `all`):
#
#   cron          schedule the chain (cron on Linux; launchd on macOS)
#   claude-code   wire the interactive surface into Claude Code
#                   (~/.claude/, slash commands + agents + skills + hooks + MCP)
#   codex         wire the interactive surface into OpenAI Codex CLI
#                   (~/.codex/ + ~/.agents/skills/, MCP via TOML, AGENTS.md)
#   all           shorthand for "cron,claude-code,codex"
#
# Common flags propagated to every per-target installer:
#
#   --dry-run     preview; touch nothing
#   --uninstall   call the matching uninstaller for each target
#   --scope X     pass `--scope X` to interactive installers (claude-code, codex);
#                 ignored by `cron` (which has no scope)
#   --            everything after `--` is forwarded verbatim to each
#                 per-target installer (e.g. --without-mcp, --without-prompts)
#
# Examples:
#
#   install.sh --target all                  # everything, default scopes
#   install.sh --target claude-code,codex    # both interactive surfaces
#   install.sh --target codex --dry-run      # preview Codex install
#   install.sh --target all --uninstall      # tear everything down
#   install.sh --target codex -- --without-mcp --without-prompts
#
# Exit codes:
#   0   all selected installers completed successfully
#   64  usage error
#   65+ first non-zero exit code from a child installer (forwarded)

set -euo pipefail

_find_repo_root() {
  local p
  p="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$p" != "/" && -n "$p" ]]; do
    if [[ -d "$p/.git" ]]; then printf '%s' "$p"; return 0; fi
    p="$(dirname "$p")"
  done
  return 1
}

REPO="$(_find_repo_root)" || { echo "[install] no .git ancestor" >&2; exit 70; }
RALPH="$REPO/prompts/ralph-meta-chain"
INSTALL_DIR="$RALPH/install"

TARGETS=""
DRY_RUN=0
DO_UNINSTALL=0
SCOPE=""
PASS_ARGS=()

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)        TARGETS="${2:-}"; shift 2 ;;
    --target=*)      TARGETS="${1#*=}"; shift ;;
    --dry-run)       DRY_RUN=1; PASS_ARGS+=("--dry-run"); shift ;;
    --uninstall)     DO_UNINSTALL=1; shift ;;
    --scope)         SCOPE="${2:-}"; shift 2 ;;
    --scope=*)       SCOPE="${1#*=}"; shift ;;
    -h|--help)       usage; exit 0 ;;
    --)              shift; while [[ $# -gt 0 ]]; do PASS_ARGS+=("$1"); shift; done ;;
    *) echo "[install] unknown flag: $1 (use \`--\` to forward installer-specific flags)" >&2; usage; exit 64 ;;
  esac
done

if [[ -z "$TARGETS" ]]; then
  echo "[install] error: --target is required (one of: cron, claude-code, codex, all)" >&2
  usage
  exit 64
fi

# Expand `all` and split on commas / whitespace.
if [[ "$TARGETS" == "all" ]]; then
  TARGETS="cron,claude-code,codex"
fi
IFS=',' read -ra TARGET_LIST <<<"$TARGETS"

# Per-target script lookup.
script_for() {
  local target="$1"
  local action="$2"   # install | uninstall
  case "$target:$action" in
    cron:install)         printf '%s' "$INSTALL_DIR/install_cron.sh" ;;
    cron:uninstall)       printf '%s' "$INSTALL_DIR/uninstall_cron.sh" ;;
    claude-code:install)  printf '%s' "$INSTALL_DIR/install_claude_code.sh" ;;
    claude-code:uninstall) printf '%s' "$INSTALL_DIR/uninstall_claude_code.sh" ;;
    codex:install)        printf '%s' "$INSTALL_DIR/install_codex.sh" ;;
    codex:uninstall)      printf '%s' "$INSTALL_DIR/uninstall_codex.sh" ;;
    *) echo "[install] unknown target/action: $target/$action" >&2; return 1 ;;
  esac
}

action="install"
[[ $DO_UNINSTALL -eq 1 ]] && action="uninstall"

OVERALL_RC=0

for target in "${TARGET_LIST[@]}"; do
  target="$(echo "$target" | tr -d '[:space:]')"
  [[ -z "$target" ]] && continue

  script="$(script_for "$target" "$action")" || { OVERALL_RC=64; continue; }
  if [[ ! -x "$script" ]]; then
    echo "[install] error: $script not found or not executable" >&2
    OVERALL_RC=70
    continue
  fi

  echo
  echo "═══ [install] target=$target action=$action ═══"

  # Build per-target args.
  args=("${PASS_ARGS[@]}")
  case "$target" in
    claude-code|codex)
      [[ -n "$SCOPE" ]] && args+=("--scope" "$SCOPE")
      [[ $DO_UNINSTALL -eq 1 ]] && args+=()  # uninstaller handles --scope itself
      ;;
    cron)
      # install_cron.sh accepts --dry-run + --uninstall; no --scope.
      :
      ;;
  esac

  if [[ $DO_UNINSTALL -eq 1 && "$target" != "cron" ]]; then
    # Interactive installers route their own --uninstall to the matching script.
    # We invoke the uninstaller directly to skip the round-trip + always pass
    # --scope through.
    [[ -n "$SCOPE" ]] && args=("--scope" "$SCOPE" "${PASS_ARGS[@]}")
    if "$script" "${args[@]}"; then
      echo "[install] $target uninstall ✓"
    else
      rc=$?
      echo "[install] $target uninstall failed (rc=$rc)" >&2
      [[ $OVERALL_RC -eq 0 ]] && OVERALL_RC=$rc
    fi
  else
    if "$script" "${args[@]}"; then
      echo "[install] $target $action ✓"
    else
      rc=$?
      echo "[install] $target $action failed (rc=$rc)" >&2
      [[ $OVERALL_RC -eq 0 ]] && OVERALL_RC=$rc
    fi
  fi
done

echo
if [[ $OVERALL_RC -eq 0 ]]; then
  echo "[install] all targets completed."
else
  echo "[install] one or more targets failed (overall rc=$OVERALL_RC)" >&2
fi
exit $OVERALL_RC
