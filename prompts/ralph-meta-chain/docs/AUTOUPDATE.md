# AUTOUPDATE.md

## Purpose

Specifies the update axis: a weekly Monday scout that scans release
feeds + creator RSS + curated AI-news, and **proposes** dependency
bumps + new-tool tryouts. Inspired by Matt Wolfe's FutureTools.io
weekly newsletter cadence ("scan everything, surface signal").

The update axis NEVER applies changes silently. Output is purely a
proposal stream.

## Cadence

Cron: `0 6 * * 1` (Monday 06:00 UTC). Hard cap 25 minutes; max 8
iterations.

## Inputs

- `research/github-watchlist.md` — categorized repo list.
- `research/trend-scout.md` — creator + paper streams.
- Release feeds via `harness ingest --topics releases:<repo>,...`
  (deferred future flag — Round 5+).
- Creator RSS via `harness ingest --creators @h1,@h2,...`.

## Outputs

- `00-Inbox/futuretools-YYYY-Www.md` — single weekly digest with
  release sections + news sections.
- `00-Inbox/creators-YYYY-MM-DD.md` — per-channel creator videos.
- `30-Notes/<id>-bump-<package>-<version>.md` — one bump-proposal per
  significantly-stale dependency.

The memory pass (#1) promotes the digest naturally on Tuesday.

## Bump-proposal schema

```yaml
---
id: <YYYYMMDDHHMM>
type: bump-proposal
package: anthropic
from: "0.40.0"
to: "0.51.2"
breaking_changes: false
test_plan: |
  cd harness && uv lock --upgrade-package anthropic
  python -m unittest discover -s tests
risk: low | medium | high
status: open
---

# Bump <package>: <from> → <to>

## Why
<one-line>

## How to apply
- ...

## Risk
<rationale>
```

Cap: ≤ 5 bump proposals per pass.

## Risk classification

| Type of update                                        | Risk class |
| ----------------------------------------------------- | ---------- |
| patch version of a vendor SDK (anthropic, openai)      | low        |
| minor version of a SDK                                 | medium     |
| major version of a SDK                                 | high       |
| new dev dependency (test framework, linter)            | low        |
| new runtime dependency                                 | medium     |
| new agent runtime variant (Codex, Cursor)              | high       |
| Claude Code CLI itself                                 | high       |
| sqlite-vec / Ollama / model swap                       | medium     |
| anything that adds network egress                      | high       |

LOW-risk patches MAY be auto-merged in future rounds via Dependabot/Renovate
once configured. Today, every bump is proposal-only.

## Source quality gate

A bump proposal is created **only if**:

1. Release notes are in `RESEARCH_NOTES.md` with confidence ≥ 0.8 OR
2. The package is on the watchlist AND we have ≥ 2 prior good-bump
   experiences with it.

This prevents 08-autoupdate from churning on no-op pre-releases.

## News digest sections

The weekly digest at `futuretools-YYYY-Www.md` has three sections:

1. **Releases** — per-tool one-liners with version + breaking-change
   flag. Sourced from GitHub releases feeds.
2. **News** — three-line summaries from FutureTools.io feed +
   Anthropic blog index. Each item tagged `#trending` so memory promotes.
3. **Proposed bumps** — `[[wikilinks]]` to the per-bump notes in
   `30-Notes/`.

## Source list (current)

Per `research/github-watchlist.md`:

- Claude Code: `anthropics/claude-code`, `anthropics/anthropic-sdk-python`.
- Coding CLIs: `openai/codex`, `paul-gauthier/aider`, `cline/cline`,
  `RooCodeInc/Roo-Code`, `continuedev/continue`, `block/goose`.
- Memory: `obra/knowledge-graph`, `cognee-ai/cognee`, `letta-ai/letta`,
  `mem0ai/mem0`, `getzep/zep`.
- Self-evolving: `gepa-ai/gepa`,
  `EvoAgentX/Awesome-Self-Evolving-Agents`, `NousResearch/hermes-agent`,
  `NousResearch/hermes-agent-self-evolution`.
- Storage: `asg017/sqlite-vec`, `ollama/ollama`.
- Eval: `promptfoo/promptfoo`.
- Programmatic prompting: `stanfordnlp/dspy`.
- For Nate Herk parity: `n8n-io/n8n`.

Adding a source is LOW risk; removing a source is HIGH risk (proposal
flow only).

## Network gating

Default mode: **no network calls**. The autoupdate pass runs with the
current `00-Inbox/_processed/` and any pre-cached release notes and
emits a digest based on what it knows.

Network mode: gated behind `RALPH_AUTOUPDATE_NETWORK=1`. Set this env
var in the cron entry only after explicit approval. With the env, the
harness fetches GitHub release pages + per-channel YouTube RSS.

## Safety notes

- **Proposal-only contract.** Update never edits `pyproject.toml`,
  `package.json`, or any code. The user (or `07-autoevolve` HIGH-risk
  proposal flow) does that.
- **Network gating.** No fetches by default. The `RALPH_AUTOUPDATE_NETWORK`
  env var is the explicit opt-in.
- **No autorun of new tools.** Discovery of a new agent runtime (e.g. a
  Cursor 4) generates a research note, not a runtime swap.
- **Hooks installation never auto.** If a watchlist repo ships a new
  Claude Code hook, the autoupdate proposal documents it; installation
  goes through `APPROVAL_GATES.md`.

## Cross-references

- `research/github-watchlist.md` — the input list.
- `research/trend-scout.md` — the creator + paper streams.
- `research/source-quality-rubric.md` — how confidence/stability score.
- `CONTEXT_LIFECYCLE.md` — update is observe + propose; apply happens
  separately.
- `APPROVAL_GATES.md` — bump-proposal apply requires explicit approval.
- Phase 1-6 reference: `prompts/ralph-meta-chain/08-autoupdate.md`,
  `harness/harness/ingest.py` (creators + topics).

## Next actions

To run a one-shot update with network on:
`RALPH_AUTOUPDATE_NETWORK=1 claude -p "$(cat 08-autoupdate.md)"`. The
output digest lands in `$VAULT/00-Inbox/futuretools-YYYY-Www.md`. Open
the file in Obsidian; promotion happens overnight via the memory pass.
