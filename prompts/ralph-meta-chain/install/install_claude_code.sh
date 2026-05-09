#!/usr/bin/env bash
# install_claude_code.sh — wire the Ralph meta-chain into a Claude Code surface.
#
# What it does (idempotent; safe to re-run):
#   1. Symlinks commands/*.md            → <target>/.claude/commands/
#   2. Symlinks skills/<slug>/           → <target>/.claude/skills/<slug>/
#   3. Symlinks agents/*.md              → <target>/.claude/agents/
#   4. Symlinks hooks/*.sh               → <target>/.claude/hooks/
#   5. Merges hook bindings + permissions into <target>/.claude/settings.json
#   6. Registers MCP server in <target>/.claude/.mcp.json (when --with-mcp)
#   7. Writes a manifest at <target>/.claude/.ralph-installed.json so that
#      uninstall_claude_code.sh can remove exactly what we put there.
#
# Scope:
#   --scope user      → ~/.claude/                (DEFAULT — global to user)
#   --scope project   → <repo>/.claude/           (per-repo)
#   --scope vault     → <vault>/.claude/          (vault_path from config.yml)
#
# Other flags:
#   --dry-run         Print what would change; touch nothing.
#   --uninstall       Hand off to uninstall_claude_code.sh with same scope.
#   --with-mcp        Also register the ralph-mcp-server in .mcp.json.
#   --without-mcp     Skip MCP registration (default if mcp-server/ absent).
#   -h, --help        Show help.
#
# Exit codes:
#   0  success / no-op (already installed and current)
#   64 usage error
#   65 config error (missing config.yml, bad vault path)
#   66 prerequisite missing (e.g. python3 for settings merge)
#   67 target busy (a non-symlink file would be overwritten — refuses)

set -euo pipefail

# ── Helpers ─────────────────────────────────────────────────────────────────

_find_repo_root() {
  local p
  p="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$p" != "/" && -n "$p" ]]; do
    if [[ -d "$p/.git" ]]; then
      printf '%s' "$p"
      return 0
    fi
    p="$(dirname "$p")"
  done
  return 1
}

REPO="$(_find_repo_root)" || {
  echo "[install-cc] error: no .git ancestor found" >&2
  exit 70
}
RALPH="$REPO/prompts/ralph-meta-chain"
CONFIG="$RALPH/config.yml"
CONFIG_EXAMPLE="$RALPH/config.example.yml"

SCOPE="user"
DRY_RUN=0
WITH_MCP="auto"
DO_UNINSTALL=0

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)        SCOPE="${2:-}"; shift 2 ;;
    --scope=*)      SCOPE="${1#*=}"; shift ;;
    --dry-run)      DRY_RUN=1; shift ;;
    --uninstall)    DO_UNINSTALL=1; shift ;;
    --with-mcp)     WITH_MCP="yes"; shift ;;
    --without-mcp)  WITH_MCP="no"; shift ;;
    -h|--help)      usage; exit 0 ;;
    *)              echo "[install-cc] unknown arg: $1" >&2; usage; exit 64 ;;
  esac
done

case "$SCOPE" in
  user|project|vault) ;;
  *) echo "[install-cc] --scope must be user|project|vault (got: $SCOPE)" >&2; exit 64 ;;
esac

if [[ $DO_UNINSTALL -eq 1 ]]; then
  exec "$RALPH/install/uninstall_claude_code.sh" --scope "$SCOPE" \
    $([[ $DRY_RUN -eq 1 ]] && echo --dry-run)
fi

# ── Resolve target directory ────────────────────────────────────────────────

resolve_target() {
  case "$SCOPE" in
    user)    printf '%s/.claude' "$HOME" ;;
    project) printf '%s/.claude' "$REPO" ;;
    vault)
      local cfg vault_raw vault
      cfg="$CONFIG"
      [[ -f "$cfg" ]] || cfg="$CONFIG_EXAMPLE"
      vault_raw="$(awk -F: '$1=="vault_path"{sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'"'"']|["'"'"']$)/,""); print; exit}' "$cfg")"
      vault="${vault_raw/#\~/$HOME}"
      [[ -n "$vault" ]] || { echo "[install-cc] vault_path missing in $cfg" >&2; exit 65; }
      printf '%s/.claude' "$vault"
      ;;
  esac
}

TARGET="$(resolve_target)"
TARGET_PARENT="$(dirname "$TARGET")"
MANIFEST="$TARGET/.ralph-installed.json"

if [[ ! -d "$TARGET_PARENT" ]]; then
  echo "[install-cc] error: target parent does not exist: $TARGET_PARENT" >&2
  echo "             create it (e.g. mkdir -p \"$TARGET_PARENT\") and rerun." >&2
  exit 65
fi

# Decide MCP install eligibility.
if [[ "$WITH_MCP" == "auto" ]]; then
  if [[ -d "$RALPH/mcp-server" ]]; then
    WITH_MCP="yes"
  else
    WITH_MCP="no"
  fi
fi

# Sanity: python3 for JSON merge (we deliberately don't depend on jq).
if ! command -v python3 >/dev/null 2>&1; then
  echo "[install-cc] error: python3 required (used for safe settings.json merge)" >&2
  exit 66
fi

echo "[install-cc] repo:       $REPO"
echo "[install-cc] target:     $TARGET"
echo "[install-cc] scope:      $SCOPE"
echo "[install-cc] dry-run:    $DRY_RUN"
echo "[install-cc] with-mcp:   $WITH_MCP"

# ── Ensure target subdirs ───────────────────────────────────────────────────

ensure_dir() {
  local d="$1"
  if [[ -e "$d" && ! -d "$d" ]]; then
    echo "[install-cc] refuses: $d exists but is not a directory" >&2
    exit 67
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    [[ -d "$d" ]] || echo "── DRY: mkdir -p $d"
    return
  fi
  mkdir -p "$d"
}

ensure_dir "$TARGET"
ensure_dir "$TARGET/commands"
ensure_dir "$TARGET/skills"
ensure_dir "$TARGET/agents"
ensure_dir "$TARGET/hooks"

# ── Symlinker (idempotent; refuses to clobber non-symlink files) ────────────

INSTALLED_LINKS=()

link_one() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    local cur; cur="$(readlink "$dst")"
    if [[ "$cur" == "$src" ]]; then
      echo "[install-cc] keep   $dst → $src"
      INSTALLED_LINKS+=("$dst")
      return
    fi
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "── DRY: relink $dst   (was → $cur)   → $src"
    else
      ln -sfn "$src" "$dst"
      echo "[install-cc] relink $dst → $src"
    fi
    INSTALLED_LINKS+=("$dst")
    return
  fi
  if [[ -e "$dst" ]]; then
    echo "[install-cc] refuses: $dst exists and is not a symlink (won't clobber)" >&2
    exit 67
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: ln -s $src $dst"
  else
    ln -s "$src" "$dst"
    echo "[install-cc] link   $dst → $src"
  fi
  INSTALLED_LINKS+=("$dst")
}

link_glob() {
  local src_dir="$1" dst_dir="$2" pattern="$3"
  if [[ ! -d "$src_dir" ]]; then
    echo "[install-cc] skip   $src_dir (not present)"
    return
  fi
  shopt -s nullglob
  local f base
  for f in "$src_dir"/$pattern; do
    base="$(basename "$f")"
    link_one "$f" "$dst_dir/$base"
  done
  shopt -u nullglob
}

# 1. Slash commands
link_glob "$RALPH/commands"  "$TARGET/commands"  "ralph-*.md"

# 2. Skills (each is a directory with SKILL.md inside)
if [[ -d "$RALPH/skills" ]]; then
  shopt -s nullglob
  for skill_dir in "$RALPH/skills"/*/; do
    skill_name="$(basename "$skill_dir")"
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    link_one "${skill_dir%/}" "$TARGET/skills/$skill_name"
  done
  shopt -u nullglob
fi

# 3. Subagents (only if agents/ dir exists in repo)
link_glob "$RALPH/agents"    "$TARGET/agents"    "ralph-*.md"

# 4. Hooks
link_glob "$RALPH/hooks"     "$TARGET/hooks"     "*.sh"

# ── Merge settings.json ─────────────────────────────────────────────────────
#
# Strategy: a Python helper that
#   - loads existing settings.json (or starts from {} if absent)
#   - reads hooks.example.json from the repo as the canonical hook map
#   - rewrites hook command paths to point at $TARGET/hooks/<name>.sh
#   - merges hooks (replacing prior Ralph entries identified by command path)
#   - merges permissions.allow + permissions.deny (set-union; never deletes)
#   - writes back atomically
#
# We embed the script here to avoid an extra file dependency.

settings_file="$TARGET/settings.json"
hooks_template="$RALPH/hooks/hooks.example.json"

merge_settings() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: merge $hooks_template + permissions into $settings_file"
    return
  fi
  python3 - "$settings_file" "$hooks_template" "$TARGET/hooks" "$RALPH/config.example.yml" <<'PY'
import json, os, re, sys, pathlib

settings_path, hooks_tmpl_path, hooks_dir, config_yml = sys.argv[1:5]

def load_json(p, default):
    if not os.path.exists(p):
        return default
    with open(p, "r") as f:
        txt = f.read().strip()
    if not txt:
        return default
    return json.loads(txt)

settings = load_json(settings_path, {})
template = load_json(hooks_tmpl_path, {})
template_hooks = template.get("hooks", {})

# Rewrite all command paths in the template to live under $TARGET/hooks/.
for event, blocks in template_hooks.items():
    for block in blocks:
        for h in block.get("hooks", []):
            if h.get("type") == "command" and "command" in h:
                base = os.path.basename(h["command"])
                h["command"] = os.path.join(hooks_dir, base)

# Merge: replace any existing block whose hooks all live under $TARGET/hooks
# (idempotent re-install). Append new ones. Leave non-Ralph blocks alone.
existing = settings.setdefault("hooks", {})
ralph_marker = hooks_dir + os.sep
for event, blocks in template_hooks.items():
    cur = existing.setdefault(event, [])
    cur = [b for b in cur
           if not all(h.get("command", "").startswith(ralph_marker)
                      for h in b.get("hooks", []) if h.get("type") == "command")]
    cur.extend(blocks)
    existing[event] = cur

# Permissions: parse the YAML allow/deny lists from config.example.yml.
allow, deny = [], []
in_perm = False
in_allow = False
in_deny = False
with open(config_yml) as f:
    for raw in f:
        line = raw.rstrip("\n")
        stripped = line.lstrip()
        if line.startswith("permissions:"):
            in_perm = True
            continue
        if in_perm and not line.startswith((" ", "\t")) and stripped and not stripped.startswith("#"):
            in_perm = False
            in_allow = in_deny = False
        if not in_perm:
            continue
        if stripped.startswith("allow:"):
            in_allow, in_deny = True, False
            continue
        if stripped.startswith("deny:"):
            in_allow, in_deny = False, True
            continue
        m = re.match(r'^\s*-\s*"(.+)"\s*$', line)
        if m:
            (allow if in_allow else deny if in_deny else []).append(m.group(1))

perms = settings.setdefault("permissions", {})
def union(key, items):
    cur = perms.setdefault(key, [])
    seen = set(cur)
    for it in items:
        if it not in seen:
            cur.append(it)
            seen.add(it)
allow and union("allow", allow)
deny  and union("deny",  deny)

# Atomic write.
tmp = settings_path + ".tmp"
with open(tmp, "w") as f:
    json.dump(settings, f, indent=2, sort_keys=False)
    f.write("\n")
os.replace(tmp, settings_path)
print(f"[install-cc] merged settings → {settings_path}")
PY
}

merge_settings

# ── MCP registration ────────────────────────────────────────────────────────

register_mcp() {
  local mcp_file="$TARGET/.mcp.json"
  local server_dir="$RALPH/mcp-server"
  if [[ "$WITH_MCP" != "yes" ]]; then
    echo "[install-cc] skip   MCP registration (--without-mcp or mcp-server/ absent)"
    return
  fi
  if [[ ! -d "$server_dir" ]]; then
    echo "[install-cc] skip   MCP — $server_dir not present"
    return
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: register ralph-mcp-server in $mcp_file"
    return
  fi
  python3 - "$mcp_file" "$server_dir" "$REPO" <<'PY'
import json, os, sys
mcp_path, server_dir, repo_root = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(mcp_path):
    with open(mcp_path) as f:
        txt = f.read().strip()
    if txt:
        data = json.loads(txt)
servers = data.setdefault("mcpServers", {})
servers["ralph"] = {
    "command": "python3",
    "args": ["-m", "ralph_mcp_server"],
    "env": {
        "PYTHONPATH": server_dir,
        "RALPH_REPO": repo_root,
    },
}
tmp = mcp_path + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
os.replace(tmp, mcp_path)
print(f"[install-cc] registered ralph MCP server → {mcp_path}")
PY
}

register_mcp

# ── Manifest ────────────────────────────────────────────────────────────────

write_manifest() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: write manifest $MANIFEST (${#INSTALLED_LINKS[@]} symlinks tracked)"
    return
  fi
  python3 - "$MANIFEST" "$REPO" "$RALPH" "$WITH_MCP" "${INSTALLED_LINKS[@]}" <<'PY'
import json, os, sys, time
manifest_path, repo, ralph, with_mcp, *links = sys.argv[1:]
data = {
    "ralph_managed": True,
    "schema_version": 1,
    "installed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "repo": repo,
    "ralph_root": ralph,
    "with_mcp": with_mcp == "yes",
    "symlinks": sorted(set(links)),
}
tmp = manifest_path + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
os.replace(tmp, manifest_path)
print(f"[install-cc] wrote manifest → {manifest_path} ({len(data['symlinks'])} symlinks)")
PY
}

write_manifest

echo
echo "[install-cc] done."
if [[ $DRY_RUN -eq 1 ]]; then
  echo "             (dry-run; nothing was written)"
else
  echo "             try \`claude\` then type \`/ralph-cron\` for the master command."
  echo "             uninstall:  $RALPH/install/uninstall_claude_code.sh --scope $SCOPE"
fi
