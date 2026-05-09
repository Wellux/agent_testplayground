#!/usr/bin/env bash
# Idempotent installer for the Ralph meta-chain.
#   - Linux: writes managed crontab entries tagged "# RALPH-managed: <axis>"
#   - macOS: writes launchd plists at ~/Library/LaunchAgents/ai.ralph.<axis>.plist
#
# Reads vault path & paths from prompts/ralph-meta-chain/config.yml.
# Backs up your existing crontab before any write.
# Refuses to clobber non-Ralph entries.
#
# Usage:
#   scripts/install.sh              # install (or update)
#   scripts/install.sh --dry-run    # print intended changes; touch nothing
#   scripts/install.sh --uninstall  # alias for scripts/uninstall.sh

set -euo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RALPH="$REPO/prompts/ralph-meta-chain"
CONFIG="$RALPH/config.yml"
DRY_RUN=0
TAG_PREFIX="# RALPH-managed:"

usage() {
  cat <<USAGE
install.sh — register the Ralph meta-chain on this machine.

Options:
  --dry-run     Print intended cron/launchd writes; do not modify the system.
  --uninstall   Hand off to scripts/uninstall.sh.
  -h, --help    Show this help.

Reads $CONFIG to resolve vault path; aborts if the file is missing.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN=1 ;;
    --uninstall)  exec "$REPO/scripts/uninstall.sh" ;;
    -h|--help)    usage; exit 0 ;;
    *)            echo "Unknown arg: $arg" >&2; usage; exit 64 ;;
  esac
done

if [[ ! -f "$CONFIG" ]]; then
  echo "[install] $CONFIG not found." >&2
  echo "          cp $RALPH/config.example.yml $CONFIG  and edit vault_path." >&2
  exit 66
fi

# Tiny YAML reader — we only need vault_path (single-line, no anchors).
read_yaml() {
  awk -v key="$1" 'BEGIN{FS=":"} $1==key {sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'\'']|["'\'']$)/,""); print; exit}' "$CONFIG"
}

VAULT_RAW="$(read_yaml vault_path || true)"
VAULT="${VAULT_RAW/#\~/$HOME}"
if [[ -z "$VAULT" ]]; then
  echo "[install] vault_path missing from $CONFIG" >&2; exit 65
fi
if [[ ! -d "$VAULT" ]]; then
  echo "[install] vault directory does not exist: $VAULT" >&2
  echo "          create it (e.g. mkdir -p \"$VAULT\") and rerun." >&2
  exit 66
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "[install] 'claude' (Claude Code CLI) not on PATH" >&2; exit 67
fi

# ── Seed first-day vault content ────────────────────────────────────────────
# Sources, in order. Each is `cp -n` (never overwrites; later sources fill
# gaps the earlier sources didn't cover):
#   1. seed/             — Phase 1-6 starter (CLAUDE.md, day-1 skills, fixtures)
#   2. vault-template/   — Round 2 master-spec layout (00_System/ … 99_Archive/)
seed_one() {
  local label="$1"; local src="$2"
  if [[ ! -d "$src" ]]; then
    echo "[install] no $label/ directory; skipping"
    return
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY RUN — would seed (cp -n) from $src into $VAULT ──"
    (cd "$src" && find . -type f | sed "s|^\\./|  $VAULT/|")
    return
  fi
  # cp -n = never overwrite. Honors existing user content + earlier seeds.
  (cd "$src" && find . -type f -exec sh -c '
    src_file="$1"; rel="${src_file#./}"; dst="'"$VAULT"'/$rel"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ]; then
      echo "[install] keep existing $dst"
    else
      cp "$src_file" "$dst" && echo "[install] seeded ('"$label"') $dst"
    fi
  ' _ {} \;)
}

seed_one seed             "$RALPH/seed"
seed_one vault-template   "$RALPH/vault-template"

OS="$(uname -s)"
LOG="${RALPH_LOG:-$HOME/.ralph.log}"
TS_BAK="$(date -u +%Y%m%dT%H%M%SZ)"

# ── Cron entries (Linux + manual macOS users) ───────────────────────────────
linux_cron_lines() {
  cat <<EOF
SHELL=/bin/bash
PATH=$PATH
RALPH=$RALPH
$TAG_PREFIX research
0 1 * * * timeout 25m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/04-research-ingest.md)"      || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX memory
0 2 * * * timeout 25m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/01-memory-optimizer.md)"     || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX skills
0 3 * * * timeout 25m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/02-skills-optimizer.md)"     || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX interaction
0 4 * * * timeout 25m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/03-interaction-optimizer.md)" || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX compress
30 * * * * timeout 10m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/05-compress.md)"            || [ \$((i+=1)) -ge 4 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX heal
15 */6 * * * timeout 10m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/06-autoheal.md)"          || [ \$((i+=1)) -ge 4 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX evolve
0 5 * * 0 timeout 30m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/07-autoevolve.md)"           || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
$TAG_PREFIX update
0 6 * * 1 timeout 25m bash -c 'i=0; until ! claude -p "\$(cat \$RALPH/08-autoupdate.md)"           || [ \$((i+=1)) -ge 8 ]; do :; done' >> $LOG 2>&1
EOF
}

install_linux() {
  local existing managed merged
  existing="$(crontab -l 2>/dev/null || true)"
  if [[ -n "$existing" ]]; then
    if [[ $DRY_RUN -eq 0 ]]; then
      printf '%s\n' "$existing" > "$HOME/.ralph-crontab.bak.$TS_BAK"
      echo "[install] backed up existing crontab → $HOME/.ralph-crontab.bak.$TS_BAK"
    fi
  fi

  # Strip any prior Ralph-managed lines.
  managed="$(printf '%s\n' "$existing" | awk -v tag="$TAG_PREFIX" '
    BEGIN { skip=0 }
    {
      if (index($0, tag) == 1) { skip=1; next }
      if (skip == 1 && /^[0-9*]/) { skip=0; next }
      if (skip == 1) { skip=0 }
      print
    }')"

  merged="$(printf '%s\n%s\n' "$managed" "$(linux_cron_lines)")"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY RUN — would install crontab ──"
    printf '%s\n' "$merged"
    return
  fi

  printf '%s\n' "$merged" | crontab -
  echo "[install] crontab installed (5 entries: research, memory, skills, interaction, compress)"
}

# ── launchd plists (macOS) ──────────────────────────────────────────────────
install_macos() {
  local LA="$HOME/Library/LaunchAgents"
  local TMPL="$REPO/scripts/launchd/ai.ralph.axis.plist.tmpl"
  if [[ ! -f "$TMPL" ]]; then
    echo "[install] template missing: $TMPL" >&2; exit 70
  fi
  mkdir -p "$LA"

  local axes=(research memory skills interaction compress heal evolve update)
  local hours=(1 2 3 4 -1 -6 5 6)     # -1 = hourly; -6 = every 6h (Hour omitted, StartCalendarInterval Hour=6 unused)
  local minutes=(0 0 0 0 30 15 0 0)
  local prompts=(04-research-ingest.md 01-memory-optimizer.md 02-skills-optimizer.md 03-interaction-optimizer.md 05-compress.md 06-autoheal.md 07-autoevolve.md 08-autoupdate.md)
  local timeouts=(1500 1500 1500 1500 600 600 1800 1500)
  local maxiters=(8 8 8 8 4 4 8 8)
  local weekdays=("" "" "" "" "" "" "0" "1")  # 0=Sun, 1=Mon; empty = daily/hourly

  for i in "${!axes[@]}"; do
    local axis="${axes[$i]}"
    local plist="$LA/ai.ralph.$axis.plist"
    local body
    body="$(sed \
      -e "s|@@AXIS@@|$axis|g" \
      -e "s|@@HOUR@@|${hours[$i]}|g" \
      -e "s|@@MINUTE@@|${minutes[$i]}|g" \
      -e "s|@@PROMPT@@|${prompts[$i]}|g" \
      -e "s|@@TIMEOUT@@|${timeouts[$i]}|g" \
      -e "s|@@MAXITERS@@|${maxiters[$i]}|g" \
      -e "s|@@WEEKDAY@@|${weekdays[$i]:-}|g" \
      -e "s|@@RALPH@@|$RALPH|g" \
      -e "s|@@LOG@@|$LOG|g" \
      "$TMPL")"

    # Post-process the rendered plist for non-daily schedules.
    case "${hours[$i]}" in
      -1)
        # Hourly: drop the Hour key+integer pair so it fires every hour at @@MINUTE@@.
        body="$(printf '%s\n' "$body" | awk '
          /<key>Hour<\/key>/      { skip=2; next }
          skip>0                  { skip--; next }
          { print }')"
        ;;
      -6)
        # Every 6h: replace StartCalendarInterval with StartInterval=21600s.
        body="$(printf '%s\n' "$body" | awk '
          /<key>StartCalendarInterval<\/key>/ { in_block=1; print "  <key>StartInterval</key>"; print "  <integer>21600</integer>"; next }
          /<\/dict>/ && in_block==1 { in_block=0; next }
          in_block==1 { next }
          { print }')"
        ;;
    esac

    # If weekly, inject <key>Weekday</key><integer>N</integer> after Minute.
    if [[ -n "${weekdays[$i]}" ]]; then
      local wd="${weekdays[$i]}"
      body="$(printf '%s\n' "$body" | awk -v wd="$wd" '
        /<key>Minute<\/key>/ { print; in_min=1; next }
        in_min==1 && /<integer>/ {
          print
          print "    <key>Weekday</key>"
          print "    <integer>" wd "</integer>"
          in_min=0
          next
        }
        { print }')"
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
      echo "── DRY RUN — would write $plist ──"
      printf '%s\n' "$body"
      continue
    fi

    printf '%s\n' "$body" > "$plist"
    launchctl unload "$plist" 2>/dev/null || true
    launchctl load   "$plist"
    echo "[install] loaded $plist"
  done
}

case "$OS" in
  Linux)  install_linux ;;
  Darwin) install_macos ;;
  *) echo "[install] unsupported OS: $OS" >&2; exit 71 ;;
esac

echo "[install] done. Tail logs: tail -f $LOG"
