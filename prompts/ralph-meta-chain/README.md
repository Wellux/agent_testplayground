# Ralph Meta-Chain — Obsidian Second-Brain Cron Loop

A "Ralph" loop is the agentic pattern of running the *same* prompt repeatedly
until the work is done. A **meta-chain** points that loop at the agent itself:
each pass mines the day's traces, distills lessons into the Obsidian vault,
and rewrites the prompts/skills/playbooks the next run will execute.

Three drafts live in this folder. Run them once a day, in order, against the
same vault.

| Order | Cron (UTC)     | Prompt                          | Optimizes                                            |
| ----- | -------------- | ------------------------------- | ---------------------------------------------------- |
| 0     | `0 1 * * *`    | `04-research-ingest.md`         | GitHub-trending feeds → inbox                        |
| 1     | `0 2 * * *`    | `01-memory-optimizer.md`        | Long-term memory / notes / MOCs                      |
| 2     | `0 3 * * *`    | `02-skills-optimizer.md`        | Reusable skills, snippets, playbooks                 |
| 3     | `0 4 * * *`    | `03-interaction-optimizer.md`   | Tone, prompt patterns, user preferences              |
| ★     | `30 * * * *`   | `05-compress.md`                | Hourly context compression                           |
| 6     | `15 */6 * * *` | `06-autoheal.md`                | Supervisor heartbeat / fix-or-escalate (Nate Herk)   |
| 7     | `0 5 * * 0`    | `07-autoevolve.md`              | Weekly fitness function (Alex Finn)                  |
| 8     | `0 6 * * 1`    | `08-autoupdate.md`              | Weekly tool/news scan (Matt Wolfe FutureTools)       |

The order matters: research feeds memory; skills are derived from settled
memory; interaction heuristics are derived from skills + memory. The
compressor runs hourly to fight bloat regardless of axis. Run #4 → #1 → #2 → #3
once a day; run #5 every hour.

## Vault layout the prompts assume

```
$VAULT/
  00-Inbox/                  # raw captures (chat exports, journal, web clips)
  10-Daily/YYYY-MM-DD.md     # daily note (Ralph appends a session log here)
  20-MOCs/                   # Maps-of-Content per domain
  30-Notes/                  # atomic / evergreen notes
  40-Skills/                 # reusable skills + playbooks (one .md per skill)
  50-Prompts/                # prompt library, including this chain's outputs
  60-Interactions/           # per-thread distillations, user prefs, tone notes
  90-Meta/
    index.md                 # Karpathy LLM-Wiki: categorized catalog
    log.md                   # Karpathy LLM-Wiki: append-only chronological log
    ralph-state.json         # last-run pointers, hashes, open-promise per axis
    metrics.ndjson           # one JSON line per experiment
    embeddings.db            # sqlite-vec + FTS5 (Ollama nomic-embed-text)
    STOP                     # touch to halt the chain on next invocation
```

## Phase 2 surrounding system

This repo also ships:

- `scripts/install.sh` / `uninstall.sh` — idempotent cron (Linux) / launchd
  (macOS) installer.
- `obsidian-ralph/` — TypeScript Obsidian plugin: command palette, status
  bar, log + metrics side panes. Built with esbuild.
- `harness/` — Python CLI with subcommands `ab`, `embed`, `query`, `ingest`,
  `compress`, `reflect`, `traces`, `self-test`. Fixture format follows
  `promptfoo`. Storage uses `sqlite-vec` + FTS5 (à la `obra/knowledge-graph`).
  Embeddings via local Ollama.
- `docs/voice-multidevice-design.md` — Phase G architecture sketch (no code
  in this PR): Apple Shortcuts + Watch + AirPods + Mac mini server + Alexa.

## Round 1 — research-first greenfield design (canonical going forward)

Round 1 of the master spec lays the design foundation that future
greenfield rounds (Round 2-N) will implement against. The above
Phase 1-6 directories (`harness/`, `voice-server/`, `obsidian-ralph/`,
`scripts/`, `docs/voice-multidevice-design.md`) become the **Phase 1-6
reference implementation** — they inform but do not bind the rebuild.

Round 1 deliverables live under:

- `prompts/ralph-meta-chain/research/` — `RESEARCH_NOTES.md`,
  `RESEARCH_SYNTHESIS.md`, `github-watchlist.md`, `trend-scout.md`,
  `source-quality-rubric.md`.
- `prompts/ralph-meta-chain/docs/` — 18 design docs covering
  architecture, memory model, context lifecycle, cron jobs, Claude Code
  integration, Obsidian plugin, A/B harness, autoheal, autoupdate,
  provider-neutral architecture, business entity scope, voice/multi-device
  future scope, security/privacy, governance, approval gates, repo
  migration, roadmap, operations manual.

Start with `docs/ROADMAP.md` for what comes next.

If a folder is missing, the prompt creates it on first run.

## Wiring as cron

`crontab.example` shows a minimal setup using the Claude CLI. Each entry pipes
the prompt file into a non-interactive Claude run with the vault path exported
as `$VAULT`. Adjust the binary, model, and working directory for your setup.

The canonical installer (`install/install_cron.sh`) writes the schedule for
you on Linux (cron) or macOS (launchd) and seeds the vault from `seed/` +
`vault-template/`.

## Wiring as an interactive surface (Claude Code or Codex)

Cron is *background*. To make the chain available *interactively* from inside
your coding agent of choice, run the matching installer:

```bash
# Claude Code
prompts/ralph-meta-chain/install/install_claude_code.sh

# OpenAI Codex CLI
prompts/ralph-meta-chain/install/install_codex.sh
```

Both wire the same conceptual surface (slash commands, skills, MCP server,
auto-loaded briefing) into the conventions each agent expects:

| Surface             | Claude Code                         | Codex                                       |
| ------------------- | ----------------------------------- | ------------------------------------------- |
| Slash commands      | `~/.claude/commands/ralph-*.md`     | `~/.codex/prompts/ralph-*.md` (deprecated)  |
| Specialist skills   | `~/.claude/skills/<slug>/SKILL.md`  | `~/.agents/skills/<slug>/SKILL.md`          |
| Axis subagents      | `~/.claude/agents/ralph-*.md`       | `~/.agents/skills/ralph-*/SKILL.md` (folded into skills) |
| Lifecycle hooks     | `~/.claude/hooks/*.sh`              | _(none — Codex has no hook surface)_         |
| MCP server          | `~/.claude/.mcp.json` (JSON)        | `~/.codex/config.toml` (TOML)               |
| Auto-loaded briefing| `CLAUDE.md` (cwd-up)                | `AGENTS.md` (cwd-up)                        |

Both installers are **idempotent**, refuse to clobber non-symlink files,
honour `--scope user|project|vault`, and ship symmetric `--uninstall`.
The shared `mcp-server/` is the same Python module — Claude Code calls it
via JSON config, Codex via TOML config; both speak the same MCP protocol.

See `install/CLAUDE_CODE_INSTALL.md` and `install/CODEX_INSTALL.md` for
the full surface maps.

## Ralph guarantees baked into every prompt

1. **Idempotent.** Re-running the same day is a no-op (the prompt diffs against
   `90-Meta/ralph-state.json` before writing).
2. **Append-only by default.** Edits to existing notes preserve prior content
   and add a dated `## Ralph YYYY-MM-DD` section.
3. **Bounded.** Each pass writes ≤ N notes (configurable per prompt) so the
   vault doesn't drown.
4. **Auditable.** Every run appends a one-line summary to `90-Meta/ralph-log.md`.
5. **Self-healing.** If a prompt detects drift between vault and state, it
   reconciles before doing new work.
