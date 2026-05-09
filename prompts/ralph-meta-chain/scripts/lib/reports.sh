#!/usr/bin/env bash
# scripts/lib/reports.sh — Markdown report rendering helpers.

# Render a leading frontmatter block (writes to stdout).
#   ralph_report_frontmatter <ralph_type> <generator> <summary> [<extra-yaml>]
ralph_report_frontmatter() {
  local rtype="$1" generator="$2" summary="$3" extra="${4:-}"
  cat <<EOF
---
ralph_type: $rtype
generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
generator: $generator
status: active
summary: "$summary"
$extra
---

EOF
}

# Render a key/value table (Markdown).
#   ralph_report_kv_table <header-key> <header-value>
#   then echo "$k|$v" lines on stdin.
ralph_report_kv_table() {
  local hk="$1" hv="$2"
  echo "| $hk | $hv |"
  echo "|------|------|"
  while IFS='|' read -r k v; do
    [[ -z "$k" ]] && continue
    echo "| $k | $v |"
  done
}

# Atomic file write: write to .tmp.PID then rename.
#   ralph_report_write <path> < input
ralph_report_write() {
  local path="$1"
  mkdir -p "$(dirname "$path")"
  local tmp="${path}.tmp.$$"
  cat > "$tmp"
  mv "$tmp" "$path"
}
