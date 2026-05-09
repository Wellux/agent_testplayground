#!/usr/bin/env bash
# ralph_classify_repo_files.sh — classify each repo file by migration class.
#
# Risk class: LOW (read-only). Always allowed.
#
# Reads inventory-report.md (runs inventory if missing).
# Writes file-classification.md with one row per file + class.

set -euo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_print_help_header "ralph_classify_repo_files.sh" "Classify each file by migration class."
  cat <<EOF
WHAT IT DOES
  - Reads migration/inventory-report.md (or runs inventory first if missing).
  - Classifies each file into one of the 14 classes per docs/REPO_MIGRATION.md:
      ralph-core | prompts | scripts | docs | research | experiments
      memory | skills | provider-adapters | business-entity | migration
      archive | unrelated | unknown

RISK CLASS
  LOW (read-only).

OUTPUT
  prompts/ralph-meta-chain/migration/file-classification.md
EOF
  exit 0
fi

ralph_require_repo

repo="$(ralph_repo_root)"
mig="$(ralph_migration_dir)"
inv="$mig/inventory-report.md"
out="$mig/file-classification.md"

if [[ ! -f "$inv" ]]; then
  ralph_log "inventory missing; running ralph_repo_inventory.sh first"
  "$HERE/ralph_repo_inventory.sh" >/dev/null
fi

# Map a relative path to a class. Order matters: most-specific first.
classify() {
  local p="$1"
  case "$p" in
    */_archive/*|*/_processed/*|*/_rejected/*) echo archive ;;
    prompts/ralph-meta-chain/migration/*)      echo migration ;;
    prompts/ralph-meta-chain/business-entity/*) echo business-entity ;;
    prompts/ralph-meta-chain/providers/*)      echo provider-adapters ;;
    prompts/ralph-meta-chain/research/*)       echo research ;;
    prompts/ralph-meta-chain/docs/*)           echo docs ;;
    prompts/ralph-meta-chain/seed/40-Skills/*) echo skills ;;
    prompts/ralph-meta-chain/vault-template/*) echo prompts ;;
    prompts/ralph-meta-chain/seed/*)           echo prompts ;;
    prompts/ralph-meta-chain/0[1-9]-*.md)      echo prompts ;;
    prompts/ralph-meta-chain/*.md)             echo prompts ;;
    prompts/ralph-meta-chain/*.yml|*.yaml)     echo prompts ;;
    prompts/*)                                 echo prompts ;;
    harness/fixtures/*)                        echo experiments ;;
    harness/*.py|harness/**/*.py)              echo ralph-core ;;
    harness/*)                                 echo ralph-core ;;
    voice-server/*)                            echo ralph-core ;;
    obsidian-ralph/*)                          echo ralph-core ;;
    scripts/*.sh|scripts/launchd/*)            echo scripts ;;
    scripts/*)                                 echo scripts ;;
    docs/*)                                    echo docs ;;
    .github/workflows/*)                       echo ralph-core ;;
    .gitignore|README.md|CHANGELOG.md|LICENSE) echo unrelated ;;
    *)                                         echo unknown ;;
  esac
}

# Target path under master-spec layout (per docs/REPO_MIGRATION.md).
target_path() {
  local p="$1"
  case "$p" in
    harness/*)
      echo "prompts/ralph-meta-chain/scripts/${p}"
      ;;
    voice-server/*)
      echo "prompts/ralph-meta-chain/voice-server/${p#voice-server/}"
      ;;
    obsidian-ralph/*)
      echo "prompts/ralph-meta-chain/obsidian-plugin/${p#obsidian-ralph/}"
      ;;
    scripts/install.sh)
      echo "prompts/ralph-meta-chain/install/install_cron.sh"
      ;;
    scripts/uninstall.sh)
      echo "prompts/ralph-meta-chain/install/uninstall_cron.sh"
      ;;
    scripts/launchd/*)
      echo "prompts/ralph-meta-chain/install/launchd/${p#scripts/launchd/}"
      ;;
    docs/voice-multidevice-design.md)
      # Already migrated to docs/ inside ralph-meta-chain in Round 1.
      echo "prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md"
      ;;
    CHANGELOG.md)
      echo "prompts/ralph-meta-chain/CHANGELOG.md"
      ;;
    *)
      echo "$p"  # already in target tree or unrelated; no move
      ;;
  esac
}

# Counts per class.
declare -A counts
for c in ralph-core prompts scripts docs research experiments memory skills \
         provider-adapters business-entity migration archive unrelated unknown; do
  counts[$c]=0
done

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

{
  echo "---"
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "generator: ralph_classify_repo_files.sh"
  echo "based_on: migration/inventory-report.md"
  echo "---"
  echo
  echo "# File Classification"
  echo
  echo "Each file in the repo classified per docs/REPO_MIGRATION.md."
  echo
  echo "## Files"
  echo
  echo "| Path | Class | Target path |"
  echo "|------|-------|-------------|"

  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    rel="${f#"$repo/"}"
    case "$rel" in
      .git/*|node_modules/*|__pycache__/*|*/.venv/*|*/dist/*) continue ;;
    esac
    cls="$(classify "$rel")"
    tgt="$(target_path "$rel")"
    same=""
    [[ "$tgt" == "$rel" ]] && same=" (no-op)"
    echo "| $rel | $cls | $tgt$same |"
    counts[$cls]=$((counts[$cls] + 1))
  done < <(find "$repo" \
              -name .git -prune -o \
              -name node_modules -prune -o \
              -name __pycache__ -prune -o \
              -name .venv -prune -o \
              -name .uv -prune -o \
              -name dist -prune -o \
              -name .pytest_cache -prune -o \
              -name .idea -prune -o \
              -name .vscode -prune -o \
              -type f -print | sort)

  echo
  echo "## Counts"
  echo
  echo "| Class | Count |"
  echo "|-------|-------|"
  for c in ralph-core prompts scripts docs research experiments memory skills \
           provider-adapters business-entity migration archive unrelated unknown; do
    echo "| $c | ${counts[$c]} |"
  done

  echo
  echo "## Next steps"
  echo
  echo "Run \`ralph_propose_migration.sh\` to convert this classification"
  echo "into a proposed-moves report."
} > "$tmp"

mkdir -p "$mig"
mv "$tmp" "$out"
trap - EXIT

ralph_log "wrote $out"
ralph_migration_log_append classify "classes=$(awk -F'|' '/^\|/ && NR>2 {print $3}' "$out" | sort -u | wc -l)"

echo "$out"
