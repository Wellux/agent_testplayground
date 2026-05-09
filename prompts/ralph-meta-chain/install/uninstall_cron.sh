#!/usr/bin/env bash
# Symmetric uninstaller for the Ralph meta-chain. Removes only managed
# entries; user's other cron / launchd entries are left alone.

set -euo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TAG_PREFIX="# RALPH-managed:"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      cat <<USAGE
uninstall.sh — remove Ralph cron / launchd entries.

Options:
  --dry-run   Print intended removals; do not modify the system.
USAGE
      exit 0 ;;
    *) echo "Unknown arg: $arg" >&2; exit 64 ;;
  esac
done

OS="$(uname -s)"
TS_BAK="$(date -u +%Y%m%dT%H%M%SZ)"

uninstall_linux() {
  local existing managed
  existing="$(crontab -l 2>/dev/null || true)"
  if [[ -z "$existing" ]]; then
    echo "[uninstall] no crontab present"; return
  fi

  managed="$(printf '%s\n' "$existing" | awk -v tag="$TAG_PREFIX" '
    BEGIN { skip=0 }
    {
      if (index($0, tag) == 1) { skip=1; next }
      if (skip == 1 && /^[0-9*]/) { skip=0; next }
      if (skip == 1) { skip=0 }
      print
    }')"

  if [[ "$existing" == "$managed" ]]; then
    echo "[uninstall] no Ralph entries found in crontab"; return
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY RUN — would replace crontab with: ──"
    printf '%s\n' "$managed"
    return
  fi

  printf '%s\n' "$existing" > "$HOME/.ralph-crontab.bak.$TS_BAK"
  printf '%s\n' "$managed" | crontab -
  echo "[uninstall] backed up to $HOME/.ralph-crontab.bak.$TS_BAK; Ralph entries removed."
}

uninstall_macos() {
  local LA="$HOME/Library/LaunchAgents"
  local axes=(research memory skills interaction compress heal evolve update)
  local found=0
  for axis in "${axes[@]}"; do
    local plist="$LA/ai.ralph.$axis.plist"
    if [[ -f "$plist" ]]; then
      found=1
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "── DRY RUN — would unload + remove $plist ──"
        continue
      fi
      launchctl unload "$plist" 2>/dev/null || true
      mv "$plist" "$plist.removed.$TS_BAK"
      echo "[uninstall] $plist → $plist.removed.$TS_BAK"
    fi
  done
  [[ $found -eq 0 ]] && echo "[uninstall] no Ralph launchd plists found"
}

case "$OS" in
  Linux)  uninstall_linux ;;
  Darwin) uninstall_macos ;;
  *) echo "[uninstall] unsupported OS: $OS" >&2; exit 71 ;;
esac
