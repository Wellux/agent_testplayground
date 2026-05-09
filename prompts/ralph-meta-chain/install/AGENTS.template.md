<!-- RALPH-managed AGENTS.md briefing -->
# Ralph meta-chain — Codex briefing

This file is auto-loaded by Codex CLI when it walks up from cwd.
It tells Codex what the Ralph meta-chain is, where the artefacts
live, and which skills + slash commands are available.

## What this is

A "Ralph" loop runs the **same prompt repeatedly** until the work is
done. The Ralph **meta-chain** points that loop at the agent itself:
each pass mines yesterday's traces, distills lessons into the
Obsidian vault, and rewrites the prompts/skills/playbooks the next
run will execute.

The chain has **8 axes** — each is one numbered prompt
(`0[1-8]-*.md`) under `prompts/ralph-meta-chain/`. Eight cron entries
fire the prompts on a schedule (see `crontab.example`); when you're
working interactively you invoke them via skills or slash commands
(below).

## Skills available (`.agents/skills/`)

Codex auto-discovers these by walking up. Two groups:

### 8 axis specialists (one per chain axis)

Use when you want Codex to act AS that axis:

| Skill              | When to invoke (description triggers)                        |
| ------------------ | ------------------------------------------------------------ |
| `ralph-research`   | "fetch trending repos for topic X", "ingest research"        |
| `ralph-memory`     | "promote inbox", "MOC pass", "atomicize this note"            |
| `ralph-skills`     | "synthesize a skill from N notes", "Voyager step"             |
| `ralph-interaction`| "A/B this prompt", "rewrite the system prompt"                |
| `ralph-compress`   | "compress this note", "weekly rollup"                         |
| `ralph-autoheal`   | "self-test", "fix the red check", "triage failure"            |
| `ralph-evolve`     | "score fitness", "propose mutation", "weekly evolve"          |
| `ralph-update`     | "scan releases", "draft a bump", "weekly digest"              |

### 8 specialist topic skills (cross-cutting concerns)

Use when reasoning about a *concern*, not an axis:

| Skill                          | Concern                                                     |
| ------------------------------ | ----------------------------------------------------------- |
| `memory-architect`             | shape the vault taxonomy (memory types, layers, frontmatter) |
| `prompt-evaluator`             | judge prompt quality with a rubric                           |
| `obsidian-vault-engineer`      | vault-layout migrations, MOC structure                       |
| `shell-safety-engineer`         | review bash for `set -euo pipefail`, deny-list patterns      |
| `business-ops-analyst`          | business-entity ledger schema review                         |
| `repo-migration-engineer`       | safe `git mv` migrations with audit trails                   |
| `provider-adapter-designer`     | new provider conformance (13-field interface)                |
| `context-compression-engineer`  | summarize-without-loss; preserve wikilinks + code blocks     |

## Slash commands available (`~/.codex/prompts/`)

Each is a read-only dashboard view:

```
/ralph-cron               master dashboard of all 8 axes
/ralph-memory             today's promotions
/ralph-skill              propose a skill from current note
/ralph-experiment         spawn an A/B fixture
/ralph-research           what arrived from upstream
/ralph-compress           what got compressed; what's bloated
/ralph-evolve             weekly fitness + open proposals
/ralph-autoheal           run validators + summarize
/ralph-autoupdate         weekly Monday digest
/ralph-business-review    pending approvals
/ralph-migration-plan     preview next migration
```

Note: Codex's custom prompts are deprecated upstream. The skills
above are the future-proof path.

## MCP server (`ralph`)

Registered in `~/.codex/config.toml` as `[mcp_servers.ralph]`. Four
read-only tools:

| Tool                       | Use                                                       |
| -------------------------- | --------------------------------------------------------- |
| `ralph_query`              | semantic search the vault (Markdown bullets + wikilinks)  |
| `ralph_axis_status`        | last log line for one or all 8 axes                        |
| `ralph_self_test`          | run the local CI mirror (frontmatter, links, privacy, …)  |
| `ralph_migration_dry_run`  | preview vault migration proposals                          |

## Operating rules

- **Append-only** inside `$VAULT/`. Edits add `## Ralph YYYY-MM-DD`
  blocks at the bottom; never delete.
- **Privacy**: never write real user identifiers (email, full name,
  account IDs) into any tracked file. Local secrets live in
  `*.local.yml` / `.env*` (gitignored).
- **Local-first embeddings** via Ollama (`nomic-embed-text` by
  default; sqlite-vec backend). No external embedding endpoints.
- **Bounded passes**: each axis honours a budget cap from
  `config.yml: budgets.<axis>.*`. Re-running a maxed-out axis is a
  no-op.
- **Exit contract**: each axis emits `<promise>COMPLETE</promise>`
  on stdout when the loop predicate trips (budget hit, zero work,
  or `90-Meta/STOP` exists).

## Where to learn more

- `prompts/ralph-meta-chain/README.md` — top-level intro.
- `prompts/ralph-meta-chain/docs/ROADMAP.md` — round-by-round shipping log.
- `prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md` — daily/weekly playbook.
- `prompts/ralph-meta-chain/install/CODEX_INSTALL.md` — this install's surface map.
- `prompts/ralph-meta-chain/install/CLAUDE_CODE_INSTALL.md` — sister install for Claude Code.

To uninstall this briefing (and everything else this surface placed):

```bash
prompts/ralph-meta-chain/install/uninstall_codex.sh --scope user
```
