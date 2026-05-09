#!/usr/bin/env bash
# uninstall_codex.sh — remove the Codex install written by install_codex.sh.
#
# Reads the manifest at .codex/.ralph-installed.json (or
# ~/.codex/.ralph-installed.json) and removes:
#   1. Each tracked symlink/file (only if it still points inside RALPH or
#      is an AGENTS.md we wrote).
#   2. Any wrapper skill directories that become empty after symlink removal.
#   3. The [mcp_servers.ralph] block from ~/.codex/config.toml (and any
#      child sub-tables tagged with the # RALPH-managed marker).
#   4. The manifest itself.
#
# Honours the same scope flag as install_codex.sh.

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

REPO="$(_find_repo_root)" || { echo "[uninstall-codex] no .git ancestor" >&2; exit 70; }
RALPH="$REPO/prompts/ralph-meta-chain"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

SCOPE="user"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)        SCOPE="${2:-}"; shift 2 ;;
    --scope=*)      SCOPE="${1#*=}"; shift ;;
    --dry-run)      DRY_RUN=1; shift ;;
    -h|--help)
      echo "uninstall_codex.sh — undo install_codex.sh"; exit 0 ;;
    *) echo "[uninstall-codex] unknown arg: $1" >&2; exit 64 ;;
  esac
done

resolve_briefing_dir() {
  case "$SCOPE" in
    user)    printf '%s' "$CODEX_HOME" ;;
    project) printf '%s' "$REPO" ;;
    vault)
      local cfg vault_raw vault
      cfg="$RALPH/config.yml"; [[ -f "$cfg" ]] || cfg="$RALPH/config.example.yml"
      vault_raw="$(awk -F: '$1=="vault_path"{sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'"'"']|["'"'"']$)/,""); print; exit}' "$cfg")"
      vault="${vault_raw/#\~/$HOME}"
      printf '%s' "$vault"
      ;;
    *) echo "[uninstall-codex] bad --scope: $SCOPE" >&2; exit 64 ;;
  esac
}

BRIEFING_DIR="$(resolve_briefing_dir)"
MANIFEST_DIR="$CODEX_HOME"
[[ "$SCOPE" == "project" ]] && MANIFEST_DIR="$REPO/.codex"
[[ "$SCOPE" == "vault" ]]   && MANIFEST_DIR="$BRIEFING_DIR/.codex"
MANIFEST="$MANIFEST_DIR/.ralph-installed.json"
TOML_FILE="$CODEX_HOME/config.toml"

echo "[uninstall-codex] manifest:  $MANIFEST"
echo "[uninstall-codex] dry-run:   $DRY_RUN"

if [[ ! -f "$MANIFEST" ]]; then
  echo "[uninstall-codex] no manifest at $MANIFEST — nothing to undo." >&2
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[uninstall-codex] python3 required" >&2; exit 66
fi

# ── Remove tracked artefacts ────────────────────────────────────────────────

remove_artefacts() {
  local item
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    if [[ -L "$item" ]]; then
      local target; target="$(readlink "$item")"
      case "$target" in
        "$RALPH"/*)
          if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rm $item"
          else rm "$item"; echo "[uninstall-codex] rm     $item"
          fi
          ;;
        *)
          echo "[uninstall-codex] keep   $item (points outside RALPH)"
          ;;
      esac
    elif [[ -f "$item" && "$(basename "$item")" == "AGENTS.md" ]]; then
      # AGENTS.md: only remove if it still has the marker we put there.
      if grep -q '^<!-- RALPH-managed AGENTS.md briefing -->' "$item" 2>/dev/null; then
        if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rm $item"
        else rm "$item"; echo "[uninstall-codex] rm     $item (RALPH-managed)"
        fi
      else
        echo "[uninstall-codex] keep   $item (no RALPH marker; user-edited)"
      fi
    else
      echo "[uninstall-codex] skip   $item (not a tracked artefact)"
    fi
  done < <(python3 -c '
import json,sys
m=json.load(open(sys.argv[1]))
for s in m.get("artefacts",[]): print(s)
' "$MANIFEST")
}

remove_artefacts

# ── Remove empty wrapper skill directories ──────────────────────────────────
# When we wrap an axis subagent as <skills_root>/ralph-<axis>/SKILL.md,
# the dir becomes orphaned after we strip the symlink.

cleanup_empty_dirs() {
  local skills_root
  skills_root="$(python3 -c '
import json,sys,os
m=json.load(open(sys.argv[1]))
arts=m.get("artefacts",[])
roots=set()
for a in arts:
    if "/.agents/skills/" in a:
        idx=a.index("/.agents/skills/")
        roots.add(a[:idx+len("/.agents/skills/")].rstrip("/"))
for r in roots: print(r)
' "$MANIFEST" | head -1)"
  [[ -n "$skills_root" && -d "$skills_root" ]] || return 0
  shopt -s nullglob
  for d in "$skills_root"/ralph-*; do
    if [[ -d "$d" && -z "$(ls -A "$d" 2>/dev/null)" ]]; then
      if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rmdir $d"
      else rmdir "$d"; echo "[uninstall-codex] rmdir  $d"
      fi
    fi
  done
  shopt -u nullglob
  # And the .agents/skills/ root if empty.
  if [[ -d "$skills_root" ]] && [[ -z "$(ls -A "$skills_root" 2>/dev/null)" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rmdir $skills_root"
    else rmdir "$skills_root"; echo "[uninstall-codex] rmdir  $skills_root"
    fi
  fi
  # And .agents/ if empty.
  local agents_root; agents_root="$(dirname "$skills_root")"
  if [[ -d "$agents_root" ]] && [[ -z "$(ls -A "$agents_root" 2>/dev/null)" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rmdir $agents_root"
    else rmdir "$agents_root"; echo "[uninstall-codex] rmdir  $agents_root"
    fi
  fi
}

cleanup_empty_dirs

# ── Strip [mcp_servers.ralph] from config.toml ──────────────────────────────

strip_mcp() {
  if [[ ! -f "$TOML_FILE" ]]; then return 0; fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: strip [mcp_servers.ralph] from $TOML_FILE"
    return
  fi
  python3 - "$TOML_FILE" <<'PY'
import os, sys
p = sys.argv[1]
with open(p) as f:
    text = f.read()
out_lines = []
in_ralph = False
for line in text.splitlines(keepends=True):
    s = line.strip()
    if s == "# RALPH-managed: ralph MCP server":
        in_ralph = True
        continue
    if in_ralph:
        if s.startswith("[") and not s.startswith("[mcp_servers.ralph"):
            in_ralph = False
            out_lines.append(line)
            continue
        continue
    out_lines.append(line)
new = "".join(out_lines).rstrip()
if not new:
    os.remove(p)
    print(f"[uninstall-codex] removed empty {p}")
else:
    tmp = p + ".tmp"
    with open(tmp, "w") as f: f.write(new + "\n")
    os.replace(tmp, p)
    print(f"[uninstall-codex] cleaned {p}")
PY
}

strip_mcp

# ── Manifest + empty Codex dirs ─────────────────────────────────────────────

if [[ $DRY_RUN -eq 1 ]]; then
  echo "── DRY: rm $MANIFEST"
else
  rm -f "$MANIFEST"
  echo "[uninstall-codex] removed manifest"
fi

# Best-effort: rmdir empty .codex/prompts and .codex/ if we left them empty.
for d in "$CODEX_HOME/prompts" "$MANIFEST_DIR" "$CODEX_HOME"; do
  [[ -d "$d" ]] || continue
  if [[ -z "$(ls -A "$d" 2>/dev/null)" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then echo "── DRY: rmdir $d"
    else rmdir "$d" 2>/dev/null && echo "[uninstall-codex] rmdir  $d" || true
    fi
  fi
done

echo "[uninstall-codex] done."
