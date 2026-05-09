# Quick start — Claude Code

Get the Ralph meta-chain running interactively inside Claude Code in **under
10 minutes** from a fresh `git clone`. This guide assumes nothing about
your machine beyond `git`, Python 3.11+, and a Claude Code install.

> Sister guide for OpenAI Codex CLI: [`QUICKSTART_CODEX.md`](QUICKSTART_CODEX.md).

---

## Prerequisites (~3 min)

| Required | Version | Install |
| --- | --- | --- |
| `claude` (Claude Code CLI) | latest | https://docs.anthropic.com/en/docs/claude-code/quickstart |
| `python3` | ≥ 3.11 | system / `brew install python@3.11` / `apt install python3.11` |
| `git` | any modern | system / `brew install git` |
| `bats` (optional, for tests) | ≥ 1.5 | `brew install bats-core` / `apt install bats` |

Optional but recommended:

| Optional | Why |
| --- | --- |
| `ollama` running locally | semantic search via `nomic-embed-text` (else queries degrade to FTS5 only) |
| `jq` | nicer hook output |
| an Obsidian vault you control | the chain's substrate — start with the bundled `vault-template/` if you don't have one |

Verify:

```bash
claude --version          # Claude Code installed
python3 --version          # 3.11 or higher
git --version
```

---

## 1. Clone + position (1 min)

```bash
git clone https://github.com/Wellux/agent_testplayground.git
cd agent_testplayground
```

The chain lives entirely under `prompts/ralph-meta-chain/`. Nothing
outside that folder is required — you can copy just that subtree into
your own monorepo if you prefer.

---

## 2. Install — 1 line (1 min)

The unified dispatcher wires Claude Code in one shot. Default scope is
`user` (writes to `~/.claude/`); use `--scope project` to confine it
to this repo's `.claude/` so collaborators inherit the same surface
via git.

```bash
# Preview first (touches nothing):
prompts/ralph-meta-chain/install/install.sh --target claude-code --dry-run

# Then install:
prompts/ralph-meta-chain/install/install.sh --target claude-code
```

What landed (32 artefacts, all tracked in
`~/.claude/.ralph-installed.json`):

| Surface | Path | Count |
| --- | --- | --- |
| Slash commands | `~/.claude/commands/ralph-*.md` | 11 |
| Subagents | `~/.claude/agents/ralph-*.md` | 8 |
| Specialist skills | `~/.claude/skills/<slug>/SKILL.md` | 8 |
| Lifecycle hooks | `~/.claude/hooks/*.sh` | 5 |
| Permissions | merged into `~/.claude/settings.json` | allow + deny |
| MCP server | `ralph` entry in `~/.claude/.mcp.json` | 4 read-only tools |

---

## 3. Verify (1 min)

```bash
# Files are where they should be
ls ~/.claude/commands ~/.claude/agents ~/.claude/skills ~/.claude/hooks

# Manifest tracks every symlink
cat ~/.claude/.ralph-installed.json | python3 -m json.tool | head

# Settings.json picked up the permissions + hooks
python3 -c "
import json
s = json.load(open('$HOME/.claude/settings.json'))
print('hooks:', sorted(s.get('hooks', {}).keys()))
print('allow patterns:', len(s['permissions']['allow']))
print('deny patterns:', len(s['permissions']['deny']))
"

# MCP server smoke test
python3 -c "
import json, subprocess, os, sys
env = dict(os.environ); env['PYTHONPATH'] = '$PWD/prompts/ralph-meta-chain/mcp-server'
env['RALPH_REPO'] = '$PWD'
inp = json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/list'}) + '\n'
cp = subprocess.run([sys.executable,'-m','ralph_mcp_server'],
    input=inp, capture_output=True, text=True, timeout=10, env=env)
tools = json.loads(cp.stdout.splitlines()[0])['result']['tools']
print('MCP tools:', [t['name'] for t in tools])
"
```

Expected:
- `commands/`, `agents/`, `skills/`, `hooks/` directories all populated
- 5 hook events: `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, `Notification`
- 9 allow patterns + 6 deny patterns
- 4 MCP tools: `ralph_query`, `ralph_axis_status`, `ralph_self_test`, `ralph_migration_dry_run`

---

## 4. First commands (2 min)

Open a new Claude Code session in any directory:

```bash
claude
```

Try the master dashboard:

```
/ralph-cron
```

You should see a table of all 8 axes with their last-run state. On a
fresh install most rows will say `(no entries yet)` — that's expected.

Try a per-axis dashboard:

```
/ralph-memory
```

Or describe a task in natural language and let Claude route via skill
or subagent:

> "Promote the inbox notes from yesterday into atomic notes."
>
> Claude routes to → `Agent(subagent_type='ralph-memory', ...)`

Or call an MCP tool from inside Claude's reasoning:

> "What's the last research-ingest pass say?"
>
> Claude calls → `ralph_axis_status(axis='research')`

---

## 5. Connect to a vault (1 min)

The chain needs a vault to work against. You have three options:

### Option A — start from the bundled template

```bash
# Create a vault from the template (cp -n; never overwrites)
cp -rn prompts/ralph-meta-chain/vault-template ~/Obsidian/SecondBrain
export VAULT="$HOME/Obsidian/SecondBrain"
```

### Option B — point at an existing Obsidian vault

```bash
export VAULT="$HOME/Documents/MyExistingVault"
# Add the required 90-Meta/ if missing — chain expects it
mkdir -p "$VAULT/90-Meta"
```

### Option C — let the chain run without a vault (dashboards only)

Slash commands like `/ralph-cron` work read-only with empty output if
no vault is configured. Useful for inspection from any cwd.

Persist `VAULT` in your shell rc:

```bash
echo 'export VAULT="$HOME/Obsidian/SecondBrain"' >> ~/.zshrc
```

---

## 6. (Optional) Schedule the cron (1 min)

Steps 1-5 give you the **interactive** surface. To also enable the
**scheduled** axes (research at 01:00 UTC, memory at 02:00, etc.), run
the cron installer:

```bash
# Copy the example config and edit vault_path
cp prompts/ralph-meta-chain/config.example.yml prompts/ralph-meta-chain/config.yml
$EDITOR prompts/ralph-meta-chain/config.yml

# Preview the cron entries:
prompts/ralph-meta-chain/install/install.sh --target cron --dry-run

# Install (Linux: crontab; macOS: launchd):
prompts/ralph-meta-chain/install/install.sh --target cron
```

Or install all three targets at once:

```bash
prompts/ralph-meta-chain/install/install.sh --target all
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/ralph-cron` not visible in Claude Code | wrong scope | If you used `--scope project`, `cd` into the repo. If `--scope user`, any cwd should work. |
| Slash command prompts for permission every time | tool not in allowlist | Check `~/.claude/settings.json` `permissions.allow` includes the patterns from `prompts/ralph-meta-chain/install/settings.template.json` |
| MCP server not loading | absolute path issue | `cat ~/.claude/.mcp.json` and verify `PYTHONPATH` + `RALPH_REPO` are absolute |
| `ralph_query` returns "harness query failed" | Ollama not running | `ollama serve` in another terminal; `ollama pull nomic-embed-text` |
| `installer refuses: ~/.claude/commands/ralph-memory.md exists and is not a symlink` | pre-existing user file | Move it aside (`mv ralph-memory.md ralph-memory.md.bak`), re-run installer |
| SessionStart hook produces no output | `$VAULT` not set or doesn't exist | `export VAULT=/path/to/vault` and re-launch Claude Code |

---

## Uninstall

```bash
prompts/ralph-meta-chain/install/install.sh --target claude-code --uninstall
```

Removes only what the manifest tracks. User-owned files (e.g. a
manually-edited `~/.claude/settings.json` permission you added) are
preserved byte-for-byte.

---

## What you've installed (deeper read)

- [`install/CLAUDE_CODE_INSTALL.md`](../install/CLAUDE_CODE_INSTALL.md) — full surface map
- [`commands/README.md`](../commands/README.md) — slash-command catalog
- [`agents/README.md`](../agents/README.md) — subagent catalog
- [`mcp-server/README.md`](../mcp-server/README.md) — MCP protocol details
- [`docs/CRON_JOBS.md`](CRON_JOBS.md) — scheduled axis details
- [`docs/PRD.md`](PRD.md) — product requirements
- [`docs/HANDOFF.md`](HANDOFF.md) — for the next maintainer
