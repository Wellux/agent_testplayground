#!/usr/bin/env bash
# scripts/lib/frontmatter.sh — frontmatter validation against
# memory-frontmatter.schema.json (best-effort; uses jq if available).

# Validate a single Markdown file's frontmatter. Returns 0 if valid,
# 1 if missing frontmatter, 2 if invalid.
#   ralph_fm_validate <file>
ralph_fm_validate() {
  local file="$1"
  if ! head -1 "$file" 2>/dev/null | grep -qE '^---[[:space:]]*$'; then
    echo "missing frontmatter: $file" >&2
    return 1
  fi

  # Required fields per memory-frontmatter.schema.json.
  local required=(ralph_type created)
  local fm
  fm="$(awk '
    NR==1 && /^---/ { in_fm=1; next }
    in_fm && /^---/ { exit }
    in_fm { print }
  ' "$file")"

  local missing=()
  for k in "${required[@]}"; do
    grep -qE "^${k}:" <<<"$fm" || missing+=("$k")
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "invalid frontmatter ($file) — missing: ${missing[*]}" >&2
    return 2
  fi

  return 0
}

# Validate every .md under a directory; print failures to stderr.
# Returns count of failures via stdout (0 = all valid).
ralph_fm_validate_tree() {
  local dir="$1"
  local fail=0
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    case "$f" in
      */_archive/*|*/_processed/*|*/_rejected/*) continue ;;
      */_population/*) continue ;;
      */node_modules/*|*/.venv/*) continue ;;
    esac
    if ! ralph_fm_validate "$f" 2>/dev/null; then
      fail=$((fail + 1))
    fi
  done < <(find "$dir" -name '*.md' -type f 2>/dev/null)
  echo "$fail"
}
