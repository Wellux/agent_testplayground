#!/usr/bin/env bash
# install_codex.sh — wire the Ralph meta-chain into the OpenAI Codex CLI.
#
# Codex's surface is leaner than Claude Code's (no lifecycle hooks, no
# named subagents). We deploy the four artefact classes Codex DOES
# support:
#
#   1. Skills (the future-proof path)        → <skills_root>/.agents/skills/<slug>/SKILL.md
#       - 8 specialist skills (memory-architect, prompt-evaluator, ...)
#       - 8 axis "subagents" wrapped as skills (ralph-memory, ralph-research, ...)
#   2. Custom prompts (deprecated, still works) → $CODEX_HOME/prompts/<axis>.md
#       - 11 slash commands (/ralph-cron + 10 axis dashboards)
#   3. MCP server                              → $CODEX_HOME/config.toml
#       - The same `ralph` MCP server we expose to Claude Code; works
#         unchanged because MCP is the protocol layer.
#   4. AGENTS.md briefing                      → <briefing_target>/AGENTS.md
#       - Codex auto-loads AGENTS.md from cwd up. Optional but recommended.
#
# Scope:
#   --scope user      → ~/.codex/, ~/.agents/skills/      (DEFAULT)
#   --scope project   → <repo>/.agents/skills/, <repo>/.codex/prompts/  (skills only — Codex
#                       config.toml is user-scoped only)
#   --scope vault     → <vault>/.agents/skills/ + AGENTS.md inside the vault
#                       (skills + AGENTS only; Codex run from inside the
#                       vault discovers them by walking up)
#
# Other flags:
#   --dry-run         Print intended writes; touch nothing.
#   --uninstall       Hand off to uninstall_codex.sh.
#   --with-mcp        Force MCP registration even if --scope project (writes ~/.codex/).
#   --without-mcp     Skip MCP registration.
#   --without-prompts Skip ~/.codex/prompts/ symlinks (skills-only mode).
#   -h, --help        Show this help.

set -euo pipefail

# ── Helpers ─────────────────────────────────────────────────────────────────

_find_repo_root() {
  local p
  p="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  while [[ "$p" != "/" && -n "$p" ]]; do
    if [[ -d "$p/.git" ]]; then printf '%s' "$p"; return 0; fi
    p="$(dirname "$p")"
  done
  return 1
}

REPO="$(_find_repo_root)" || {
  echo "[install-codex] error: no .git ancestor found" >&2
  exit 70
}
RALPH="$REPO/prompts/ralph-meta-chain"
CONFIG="$RALPH/config.yml"
CONFIG_EXAMPLE="$RALPH/config.example.yml"

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SCOPE="user"
DRY_RUN=0
WITH_MCP="auto"
WITH_PROMPTS=1
DO_UNINSTALL=0

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)            SCOPE="${2:-}"; shift 2 ;;
    --scope=*)          SCOPE="${1#*=}"; shift ;;
    --dry-run)          DRY_RUN=1; shift ;;
    --uninstall)        DO_UNINSTALL=1; shift ;;
    --with-mcp)         WITH_MCP="yes"; shift ;;
    --without-mcp)      WITH_MCP="no"; shift ;;
    --without-prompts)  WITH_PROMPTS=0; shift ;;
    -h|--help)          usage; exit 0 ;;
    *) echo "[install-codex] unknown arg: $1" >&2; usage; exit 64 ;;
  esac
done

case "$SCOPE" in
  user|project|vault) ;;
  *) echo "[install-codex] --scope must be user|project|vault (got: $SCOPE)" >&2; exit 64 ;;
esac

if [[ $DO_UNINSTALL -eq 1 ]]; then
  exec "$RALPH/install/uninstall_codex.sh" --scope "$SCOPE" \
    $([[ $DRY_RUN -eq 1 ]] && echo --dry-run)
fi

# ── Resolve targets ─────────────────────────────────────────────────────────
# Skills + briefing live at scope. MCP + prompts live at user-scope only
# (Codex config.toml is user-scoped).

resolve_skills_root() {
  case "$SCOPE" in
    user)    printf '%s/.agents/skills' "$HOME" ;;
    project) printf '%s/.agents/skills' "$REPO" ;;
    vault)
      local cfg vault_raw vault
      cfg="$CONFIG"; [[ -f "$cfg" ]] || cfg="$CONFIG_EXAMPLE"
      vault_raw="$(awk -F: '$1=="vault_path"{sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'"'"']|["'"'"']$)/,""); print; exit}' "$cfg")"
      vault="${vault_raw/#\~/$HOME}"
      [[ -n "$vault" ]] || { echo "[install-codex] vault_path missing in $cfg" >&2; exit 65; }
      printf '%s/.agents/skills' "$vault"
      ;;
  esac
}

resolve_briefing_dir() {
  case "$SCOPE" in
    user)    printf '%s' "$CODEX_HOME" ;;
    project) printf '%s' "$REPO" ;;
    vault)
      local cfg vault_raw vault
      cfg="$CONFIG"; [[ -f "$cfg" ]] || cfg="$CONFIG_EXAMPLE"
      vault_raw="$(awk -F: '$1=="vault_path"{sub(/^[^:]+:[ \t]*/,""); gsub(/(^["'"'"']|["'"'"']$)/,""); print; exit}' "$cfg")"
      vault="${vault_raw/#\~/$HOME}"
      printf '%s' "$vault"
      ;;
  esac
}

SKILLS_ROOT="$(resolve_skills_root)"
SKILLS_PARENT="$(dirname "$SKILLS_ROOT")"
BRIEFING_DIR="$(resolve_briefing_dir)"
PROMPTS_DIR="$CODEX_HOME/prompts"
TOML_FILE="$CODEX_HOME/config.toml"
MANIFEST_DIR="$CODEX_HOME"
[[ "$SCOPE" == "project" ]] && MANIFEST_DIR="$REPO/.codex"
[[ "$SCOPE" == "vault" ]]   && MANIFEST_DIR="$BRIEFING_DIR/.codex"
MANIFEST="$MANIFEST_DIR/.ralph-installed.json"

# Check parent dirs exist (don't auto-create the user's HOME etc.)
if [[ ! -d "$HOME" ]]; then
  echo "[install-codex] error: HOME does not exist: $HOME" >&2
  exit 65
fi

# Decide MCP install eligibility.
if [[ "$WITH_MCP" == "auto" ]]; then
  if [[ "$SCOPE" == "user" ]]; then
    WITH_MCP="yes"
  else
    WITH_MCP="no"   # project/vault scope skips MCP by default (it's user-scoped)
  fi
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[install-codex] error: python3 required (used for safe TOML/JSON merge)" >&2
  exit 66
fi

echo "[install-codex] repo:           $REPO"
echo "[install-codex] scope:          $SCOPE"
echo "[install-codex] skills root:    $SKILLS_ROOT"
echo "[install-codex] briefing dir:   $BRIEFING_DIR"
echo "[install-codex] CODEX_HOME:     $CODEX_HOME"
echo "[install-codex] dry-run:        $DRY_RUN"
echo "[install-codex] with-mcp:       $WITH_MCP"
echo "[install-codex] with-prompts:   $WITH_PROMPTS"

# ── Ensure target subdirs ───────────────────────────────────────────────────

ensure_dir() {
  local d="$1"
  if [[ -e "$d" && ! -d "$d" ]]; then
    echo "[install-codex] refuses: $d exists but is not a directory" >&2
    exit 67
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    [[ -d "$d" ]] || echo "── DRY: mkdir -p $d"
    return
  fi
  mkdir -p "$d"
}

ensure_dir "$SKILLS_ROOT"
ensure_dir "$MANIFEST_DIR"
[[ "$WITH_PROMPTS" -eq 1 ]] && ensure_dir "$PROMPTS_DIR"
[[ "$WITH_MCP" == "yes" ]] && ensure_dir "$CODEX_HOME"

# ── Symlinker (idempotent; refuses to clobber non-symlink files) ────────────

INSTALLED_LINKS=()

link_one() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    local cur; cur="$(readlink "$dst")"
    if [[ "$cur" == "$src" ]]; then
      echo "[install-codex] keep   $dst → $src"
      INSTALLED_LINKS+=("$dst")
      return
    fi
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "── DRY: relink $dst   (was → $cur)   → $src"
    else
      ln -sfn "$src" "$dst"
      echo "[install-codex] relink $dst → $src"
    fi
    INSTALLED_LINKS+=("$dst")
    return
  fi
  if [[ -e "$dst" ]]; then
    echo "[install-codex] refuses: $dst exists and is not a symlink" >&2
    exit 67
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: ln -s $src $dst"
  else
    ln -s "$src" "$dst"
    echo "[install-codex] link   $dst → $src"
  fi
  INSTALLED_LINKS+=("$dst")
}

# 1. Skills — specialists + axis subagents wrapped as skills.
#
# 8 specialist skills are already in directory form:
#    repo/skills/<slug>/SKILL.md
# We can symlink the whole directory.
#
# 8 axis subagents are flat .md files in repo/agents/. Wrap each as
# its own skill directory: <skill>/SKILL.md → ../../../agents/ralph-<axis>.md

# Specialists (whole directory)
shopt -s nullglob
for skill_dir in "$RALPH/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  link_one "${skill_dir%/}" "$SKILLS_ROOT/$skill_name"
done

# Axis subagents (wrap each in a skill dir)
for agent_md in "$RALPH/agents"/ralph-*.md; do
  axis_name="$(basename "$agent_md" .md)"
  skill_dir="$SKILLS_ROOT/$axis_name"
  if [[ ! -d "$skill_dir" && ! -L "$skill_dir" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "── DRY: mkdir $skill_dir"
    else
      mkdir -p "$skill_dir"
    fi
  fi
  link_one "$agent_md" "$skill_dir/SKILL.md"
done
shopt -u nullglob

# 2. Custom prompts — symlink slash commands as plain markdown files.
if [[ "$WITH_PROMPTS" -eq 1 ]]; then
  shopt -s nullglob
  for cmd in "$RALPH/commands"/ralph-*.md; do
    base="$(basename "$cmd")"
    link_one "$cmd" "$PROMPTS_DIR/$base"
  done
  shopt -u nullglob
fi

# 3. MCP server registration in ~/.codex/config.toml
register_mcp() {
  if [[ "$WITH_MCP" != "yes" ]]; then
    echo "[install-codex] skip   MCP (--without-mcp or non-user scope)"
    return
  fi
  local server_dir="$RALPH/mcp-server"
  if [[ ! -d "$server_dir" ]]; then
    echo "[install-codex] skip   MCP — $server_dir not present"
    return
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: register [mcp_servers.ralph] in $TOML_FILE"
    return
  fi
  python3 - "$TOML_FILE" "$server_dir" "$REPO" <<'PY'
"""Idempotently merge a [mcp_servers.ralph] block into ~/.codex/config.toml.

Strategy: text-based, preserves user formatting elsewhere. We only
touch the ralph block. We do NOT use tomli-w to avoid an external dep.

The block we write is canonical:

    [mcp_servers.ralph]
    command = "python3"
    args = ["-m", "ralph_mcp_server"]
    cwd = "<server_dir>"
    [mcp_servers.ralph.env]
    PYTHONPATH = "<server_dir>"
    RALPH_REPO = "<repo_root>"
"""
import os, re, sys
toml_path, server_dir, repo_root = sys.argv[1:4]

block = (
    "# RALPH-managed: ralph MCP server\n"
    "[mcp_servers.ralph]\n"
    'command = "python3"\n'
    'args = ["-m", "ralph_mcp_server"]\n'
    f'cwd = "{server_dir}"\n'
    "[mcp_servers.ralph.env]\n"
    f'PYTHONPATH = "{server_dir}"\n'
    f'RALPH_REPO = "{repo_root}"\n'
)

existing = ""
if os.path.exists(toml_path):
    with open(toml_path) as f:
        existing = f.read()

# Strip any prior ralph block (between our marker comment and the
# next top-level [section] or EOF).
stripped_lines = []
in_ralph = False
for line in existing.splitlines(keepends=True):
    s = line.strip()
    if s == "# RALPH-managed: ralph MCP server":
        in_ralph = True
        continue
    if in_ralph:
        # End the ralph block when we hit a new top-level table that
        # is NOT a sub-table of mcp_servers.ralph.
        if s.startswith("[") and not s.startswith("[mcp_servers.ralph"):
            in_ralph = False
            stripped_lines.append(line)
            continue
        # Skip lines inside the ralph block.
        continue
    stripped_lines.append(line)

cleaned = "".join(stripped_lines).rstrip()
out = (cleaned + ("\n\n" if cleaned else "") + block).lstrip("\n")

# Atomic write.
tmp = toml_path + ".tmp"
with open(tmp, "w") as f:
    f.write(out)
os.replace(tmp, toml_path)
print(f"[install-codex] wrote [mcp_servers.ralph] → {toml_path}")
PY
}

register_mcp

# 4. AGENTS.md — only if not present (don't clobber user briefing).
write_briefing() {
  local target="$BRIEFING_DIR/AGENTS.md"
  local source="$RALPH/install/AGENTS.template.md"
  if [[ ! -d "$BRIEFING_DIR" ]]; then
    echo "[install-codex] skip   AGENTS.md ($BRIEFING_DIR doesn't exist)"
    return
  fi
  if [[ -e "$target" ]]; then
    # If we previously wrote it (marker present), still track in manifest
    # so re-install → uninstall remains a clean round-trip.
    if grep -q '^<!-- RALPH-managed AGENTS.md briefing -->' "$target" 2>/dev/null; then
      echo "[install-codex] keep   $target (RALPH-managed; tracked in manifest)"
      INSTALLED_LINKS+=("$target")
    else
      echo "[install-codex] keep   $target (user-owned; not clobbered)"
    fi
    return
  fi
  if [[ ! -f "$source" ]]; then
    echo "[install-codex] skip   AGENTS.md (template not at $source)"
    return
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: cp $source $target"
    return
  fi
  cp "$source" "$target"
  echo "[install-codex] wrote  $target (Ralph briefing for Codex)"
  INSTALLED_LINKS+=("$target")
}

write_briefing

# ── Manifest ────────────────────────────────────────────────────────────────

write_manifest() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "── DRY: write manifest $MANIFEST (${#INSTALLED_LINKS[@]} artefacts tracked)"
    return
  fi
  python3 - "$MANIFEST" "$REPO" "$RALPH" "$WITH_MCP" "$WITH_PROMPTS" "$TOML_FILE" "${INSTALLED_LINKS[@]}" <<'PY'
import json, os, sys, time
manifest_path, repo, ralph, with_mcp, with_prompts, toml_file, *links = sys.argv[1:]
data = {
    "ralph_managed": True,
    "schema_version": 1,
    "target": "codex",
    "installed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "repo": repo,
    "ralph_root": ralph,
    "with_mcp": with_mcp == "yes",
    "with_prompts": with_prompts == "1",
    "toml_file": toml_file if with_mcp == "yes" else None,
    "artefacts": sorted(set(links)),
}
tmp = manifest_path + ".tmp"
os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
with open(tmp, "w") as f:
    json.dump(data, f, indent=2); f.write("\n")
os.replace(tmp, manifest_path)
print(f"[install-codex] wrote manifest → {manifest_path} ({len(data['artefacts'])} artefacts)")
PY
}

write_manifest

echo
echo "[install-codex] done."
if [[ $DRY_RUN -eq 1 ]]; then
  echo "                (dry-run; nothing was written)"
else
  echo "                try \`codex\` then type \`/ralph-cron\` for the master command,"
  echo "                or just describe an axis task — Codex will match a skill."
  echo "                uninstall: $RALPH/install/uninstall_codex.sh --scope $SCOPE"
fi
