# GitHub watchlist

## Purpose

Categorized list of repos the autoupdate cron (`08-autoupdate.md`) scans
for releases / news. The list is intentionally curated — every entry is
present in `RESEARCH_NOTES.md` with a confidence/stability score.

## Usage

`harness ingest --topics releases:<repo>,...` resolves each entry to its
GitHub releases feed and writes the per-week digest to
`$VAULT/00-Inbox/futuretools-YYYY-Www.md`.

The list is intentionally additive. Removing an entry is a HIGH-risk
operation (the chain may have come to depend on it). Add freely; remove
only via `07-autoevolve.md` proposal.

## Categories

### Claude Code core

- anthropics/claude-code
- anthropics/anthropic-sdk-python
- anthropics/anthropic-cookbook

### Ralph-loop family

- anthropics/claude-code/plugins/ralph-wiggum (subdir)
- ghuntley/how-to-ralph-wiggum
- snarktank/ralph
- frankbria/ralph-claude-code
- Th0rgal/open-ralph-wiggum
- harrymunro/ralph-wiggum
- snwfdhmp/awesome-ralph

### Karpathy + auto-research

- karpathy/autoresearch
- karpathy/build-nanogpt (context only)

### Hermes / self-evolving

- NousResearch/hermes-agent
- NousResearch/hermes-agent-self-evolution
- 0xNyk/awesome-hermes-agent
- gepa-ai/gepa
- EvoAgentX/Awesome-Self-Evolving-Agents
- XMUDeepLIT/Awesome-Self-Evolving-Agents

### Memory layer

- obra/knowledge-graph
- cognee-ai/cognee
- letta-ai/letta
- mem0ai/mem0
- getzep/zep

### Obsidian

- brianpetro/obsidian-smart-connections
- GoBeromsu/open-connections
- NicholasSpisak/second-brain
- charlie947/ai-second-brain

### Coding-CLI landscape (Claude Code stays primary)

- openai/codex
- paul-gauthier/aider
- cline/cline
- RooCodeInc/Roo-Code
- continuedev/continue
- block/goose

### OpenClaw / ClaudeClaw / Codex orchestration

- moazbuilds/claudeclaw
- swarmclawai/swarmclaw
- Enderfga/openclaw-claude-code (claw-orchestrator)
- alizarion/openclaw-claude-code-plugin
- simple10/openclaw-stack

### Storage + UX

- asg017/sqlite-vec
- ollama/ollama
- promptfoo/promptfoo

### DSPy / programmatic prompting

- stanfordnlp/dspy

### n8n (Nate Herk parity context)

- n8n-io/n8n

## Safety notes

- All entries are public OSS. No private repos, no licensed/proprietary
  code.
- Network calls are gated: 08-autoupdate runs only with `--apply` (not
  in dry-run); the harness honors the spec's "no network research without
  approval" rule.
- Watchlist additions/removals do NOT autonomously install dependencies.
  Bumps are *proposed* in `30-Notes/<id>-bump-<package>-<version>.md`,
  applied only with explicit user merge.

## Cross-references

- `RESEARCH_NOTES.md` — every entry above has a corresponding entry there
  with confidence/stability scores.
- `RESEARCH_SYNTHESIS.md` — patterns adopted from these projects.
- `docs/AUTOUPDATE.md` — how the cron consumes this list.
- `prompts/ralph-meta-chain/08-autoupdate.md` — current implementation.

## Next actions

If you want to add a repo: append below the appropriate category, then
add a corresponding `RESEARCH_NOTES.md` entry scoring it against
`source-quality-rubric.md`. Re-run `harness ingest --creators` /
`--topics releases:<repo>` to confirm the resolver works.
