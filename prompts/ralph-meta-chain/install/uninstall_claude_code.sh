#!/usr/bin/env bash
# uninstall_claude_code.sh — remove every artefact written by install_claude_code.sh.
#
# Reads <target>/.claude/.ralph-installed.json (the manifest) and:
#   1. Removes each tracked symlink (only if it still points at a path inside RALPH).
#   2. Strips the matching hook entries from settings.json.
#   3. Strips ralph-tagged permissions from settings.json (only those we added; never user-added).
#   4. Removes the ralph entry from .mcp.json.
#   5. Removes the manifest itself.
#
# Honours the same scope flag as install_claude_code.sh.
#
#   --scope user      → ~/.claude/                (default)
#   --scope project   → <repo>/.claude/
#   --scope vault     → <vault>/.claude/
#   --dry-run         Print what would change; touch nothing.

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

REPO="$(_find_repo_root)" || { echo "[uninstall-cc] no .git ancestor" >&2; exit 70; }
RALPH="$REPO/prompts/ralph-meta-chain"

SCOPE="user"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)        SCOPE="${2:-}"; shift 2 ;;
    --scope=*)      SCOPE="${1#*=}"; shift ;;
    --dry-run)      DRY_RUN=1; shift ;;
    -h|--help)
      cat <<USAGE
uninstall_claude_code.sh — remove the Claude Code surface installed by
install_claude_code.sh. Honours --scope user|project|vault and --dry-run.
USAGE
      exit 0 ;;
    *) echo "[uninstall-cc] unknown arg: $1" >&2; exit 64 ;;
  esac
done

resolve_target() {
  case "$SCOPE" in
    user)    printf '%s/.claude' "$HOME" ;;
    project) printf '%s/.claude' "$REPO" ;;
    vault)
      local cfg vault_raw vault
      cfg="$RALPH/config.yml"
      [[ -f "$cfg" ]] || cfg="$RALPH/config.example.yml"
      vault_raw="$(awk -F: '$1=="vault_path"{sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'"'"']|["'"'"']$)/,""); print; exit}' "$cfg")"
      vault="${vault_raw/#\~/$HOME}"
      [[ -n "$vault" ]] || { echo "[uninstall-cc] vault_path missing" >&2; exit 65; }
      printf '%s/.claude' "$vault" ;;
    *) echo "[uninstall-cc] bad --scope: $SCOPE" >&2; exit 64 ;;
  esac
}

TARGET="$(resolve_target)"
MANIFEST="$TARGET/.ralph-installed.json"

echo "[uninstall-cc] target:    $TARGET"
echo "[uninstall-cc] manifest:  $MANIFEST"
echo "[uninstall-cc] dry-run:   $DRY_RUN"

if [[ ! -f "$MANIFEST" ]]; then
  echo "[uninstall-cc] no manifest at $MANIFEST — nothing to undo." >&2
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[uninstall-cc] error: python3 required" >&2; exit 66
fi

# ── Remove tracked symlinks ─────────────────────────────────────────────────

remove_links() {
  local link target
  while IFS= read -r link; do
    if [[ -z "$link" ]]; then continue; fi
    if [[ ! -L "$link" ]]; then
      echo "[uninstall-cc] skip   $link (no longer a symlink)"
      continue
    fi
    target="$(readlink "$link")"
    case "$target" in
      "$RALPH"/*)
        if [[ $DRY_RUN -eq 1 ]]; then
          echo "── DRY: rm $link"
        else
          rm "$link"; echo "[uninstall-cc] rm     $link"
        fi
        ;;
      *)
        echo "[uninstall-cc] keep   $link (points outside RALPH: $target)"
        ;;
    esac
  done < <(python3 -c '
import json,sys
m=json.load(open(sys.argv[1]))
for s in m.get("symlinks",[]): print(s)
' "$MANIFEST")
}

remove_links

# ── Strip hooks + ralph-tagged permissions from settings.json ───────────────

strip_settings() {
  local s="$TARGET/settings.json"
  [[ -f "$s" ]] || return 0
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: strip ralph hooks + permissions from $s"
    return
  fi
  python3 - "$s" "$TARGET/hooks" "$RALPH/config.example.yml" <<'PY'
import json, os, re, sys
path, hooks_dir, cfg = sys.argv[1:]
with open(path) as f:
    s = json.load(f)
hooks = s.get("hooks", {})
marker = hooks_dir + os.sep
for event in list(hooks):
    pruned = []
    for block in hooks[event]:
        cmds = [h.get("command","") for h in block.get("hooks",[]) if h.get("type")=="command"]
        if cmds and all(c.startswith(marker) for c in cmds):
            continue
        pruned.append(block)
    if pruned: hooks[event] = pruned
    else: del hooks[event]
if not hooks and "hooks" in s:
    del s["hooks"]
# Strip ralph-managed permissions (those listed in config.example.yml).
allow=set(); deny=set()
in_p=False; mode=None
for line in open(cfg):
    st=line.lstrip()
    if line.startswith("permissions:"): in_p=True; continue
    if in_p and not line.startswith((" ","\t")) and st and not st.startswith("#"):
        in_p=False; mode=None
    if not in_p: continue
    if st.startswith("allow:"): mode="allow"; continue
    if st.startswith("deny:"):  mode="deny"; continue
    m=re.match(r'^\s*-\s*"(.+)"\s*$', line)
    if m and mode=="allow": allow.add(m.group(1))
    if m and mode=="deny":  deny.add(m.group(1))
perms = s.get("permissions", {})
for k, drop in (("allow", allow), ("deny", deny)):
    if k in perms:
        perms[k] = [x for x in perms[k] if x not in drop]
        if not perms[k]: del perms[k]
if "permissions" in s and not perms: del s["permissions"]
if not s:
    os.remove(path)
    print(f"[uninstall-cc] removed empty {path}")
else:
    tmp = path + ".tmp"
    with open(tmp,"w") as f: json.dump(s,f,indent=2); f.write("\n")
    os.replace(tmp, path)
    print(f"[uninstall-cc] cleaned {path}")
PY
}

strip_settings

# ── Strip ralph from .mcp.json ──────────────────────────────────────────────

strip_mcp() {
  local m="$TARGET/.mcp.json"
  [[ -f "$m" ]] || return 0
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: drop ralph from $m"
    return
  fi
  python3 - "$m" <<'PY'
import json, os, sys
p = sys.argv[1]
with open(p) as f: data = json.load(f)
servers = data.get("mcpServers", {})
if "ralph" in servers:
    del servers["ralph"]
    if not servers: del data["mcpServers"]
    if not data:
        os.remove(p); print(f"[uninstall-cc] removed empty {p}")
    else:
        with open(p,"w") as f: json.dump(data,f,indent=2); f.write("\n")
        print(f"[uninstall-cc] dropped ralph from {p}")
PY
}

strip_mcp

# ── Manifest ────────────────────────────────────────────────────────────────

if [[ $DRY_RUN -eq 1 ]]; then
  echo "── DRY: rm $MANIFEST"
else
  rm -f "$MANIFEST"
  echo "[uninstall-cc] removed manifest"
fi

# Best-effort: remove now-empty subdirs.
for d in commands skills agents hooks; do
  [[ -d "$TARGET/$d" ]] || continue
  if [[ -z "$(ls -A "$TARGET/$d" 2>/dev/null)" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "── DRY: rmdir $TARGET/$d"
    else
      rmdir "$TARGET/$d"
      echo "[uninstall-cc] rmdir  $TARGET/$d"
    fi
  fi
done

# And the .claude/ root if it's now empty.
if [[ -d "$TARGET" ]] && [[ -z "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: rmdir $TARGET"
  else
    rmdir "$TARGET"
    echo "[uninstall-cc] rmdir  $TARGET"
  fi
fi

echo "[uninstall-cc] done."
