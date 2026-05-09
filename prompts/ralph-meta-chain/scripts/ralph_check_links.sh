#!/usr/bin/env bash
# ralph_check_links.sh — scan $VAULT for broken [[wikilinks]].
# Risk class: LOW (read-only).

set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$HERE/lib/common.sh"
# shellcheck source=lib/config.sh
source "$HERE/lib/config.sh"
# shellcheck source=lib/markdown.sh
source "$HERE/lib/markdown.sh"

ralph_parse_flags "$@"
if [[ ${RALPH_HELP:-0} -eq 1 ]]; then
  ralph_help_header "ralph_check_links.sh" "Scan the vault for broken [[wikilinks]]."
  cat <<EOF
WHAT
  Walks every .md in \$VAULT, extracts \`[[wikilinks]]\`, and reports
  any that do not resolve to either a file (matching basename) or an
  archived note (\`_archive/<id>-original.md\`).

  Exit code = number of broken links (0 = clean).

USAGE
  ralph_check_links.sh
EOF
  exit 0
fi

target="${RALPH_PASSTHROUGH[0]:-}"
if [[ -z "$target" ]]; then
  target="$(ralph_vault_path 2>/dev/null || true)"
fi
[[ -d "$target" ]] || { ralph_error "no vault dir: ${target:-<unset>}"; exit 1; }

ralph_log "scanning $target"

# Build name-set of every .md basename (without extension) and every id.
namelist=$(mktemp)
trap 'rm -f "$namelist"' EXIT
find "$target" -type f -name '*.md' \
  -not -path '*/node_modules/*' \
  -not -path '*/.venv/*' 2>/dev/null \
  | while IFS= read -r f; do
      base="$(basename "$f" .md)"
      echo "$base"
      # Also accept any id frontmatter value as a link target.
      ralph_md_fm_get id "$f" 2>/dev/null
    done | sort -u > "$namelist"

fail=0
while IFS= read -r f; do
  while IFS= read -r link; do
    [[ -z "$link" ]] && continue
    # Strip subpath / anchor fragments (e.g. "[[foo|bar]]" → "foo").
    target_name="${link%%|*}"
    target_name="${target_name%%#*}"
    target_name="${target_name##*/}"   # basename only
    if ! grep -qxF "$target_name" "$namelist"; then
      printf '%s → broken link [[%s]]\n' "${f#"$target/"}" "$link" >&2
      fail=$((fail + 1))
    fi
  done < <(ralph_md_wikilinks "$f")
done < <(find "$target" -type f -name '*.md' \
            -not -path '*/_archive/*' \
            -not -path '*/_processed/*' \
            -not -path '*/_rejected/*' \
            -not -path '*/node_modules/*' \
            -not -path '*/.venv/*' 2>/dev/null)

ralph_log "broken links: $fail"
exit $((fail > 254 ? 254 : fail))
