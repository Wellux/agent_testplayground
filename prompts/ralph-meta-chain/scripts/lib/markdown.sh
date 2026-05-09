#!/usr/bin/env bash
# scripts/lib/markdown.sh — small Markdown helpers.

# Print the body (everything after closing ---) of a Markdown file.
ralph_md_body() {
  awk '
    BEGIN { in_fm=0; n=0 }
    NR==1 && /^---/ { in_fm=1; next }
    in_fm && /^---/ { in_fm=0; next }
    in_fm { next }
    { print }
  ' "$1"
}

# Print just the YAML frontmatter (between leading ---/---).
ralph_md_frontmatter() {
  awk '
    NR==1 && /^---/ { in_fm=1; next }
    in_fm && /^---/ { in_fm=0; exit }
    in_fm { print }
  ' "$1"
}

# True (exit 0) if file has YAML frontmatter.
ralph_md_has_frontmatter() {
  head -1 "$1" 2>/dev/null | grep -qE '^---[[:space:]]*$'
}

# Extract a single scalar key from frontmatter ("" if missing).
ralph_md_fm_get() {
  local key="$1"; local file="$2"
  ralph_md_frontmatter "$file" |
    awk -v k="$key" 'BEGIN{FS=":"} $1==k {sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'\'']|["'\'']$)/,""); print; exit}'
}

# List all `[[wikilinks]]` in a file (one per line).
ralph_md_wikilinks() {
  grep -oE '\[\[[^]]+\]\]' "$1" 2>/dev/null | sed 's/^\[\[//; s/\]\]$//'
}
