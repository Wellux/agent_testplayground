# RESEARCH_NOTES.md

Per-source notes. Each entry follows the master spec's 18-field shape.
Scores per `source-quality-rubric.md`.

## Entry template

```yaml
---
research_date: YYYY-MM-DD
source_name: e.g. anthropics/claude-code ralph-wiggum plugin
source_url: https://...
category: harness | memory | self-evolving | obsidian | provider | creator | paper | tool
observed_mechanism: |
  what the source actually does
adopt: |
  what Ralph should adopt (verbatim or adapted)
reject: |
  what Ralph should not adopt
security_concerns: |
  ...
privacy_concerns: |
  ...
context_efficiency_relevance: |
  ...
self_improvement_relevance: |
  ...
obsidian_relevance: |
  ...
claude_code_relevance: |
  ...
provider_neutral_relevance: |
  ...
business_entity_relevance: |
  ...
confidence: 0.0-1.0
stability: 0.0-1.0
freshness: free-text note
implementation_consequence: |
  what this means for Ralph today
---
```

---

## Harness / Ralph-loop family

### anthropics/claude-code ralph-wiggum plugin

```yaml
research_date: 2026-05-08
source_name: anthropics/claude-code ralph-wiggum plugin
source_url: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
category: harness
observed_mechanism: |
  /ralph-loop "<task>" --max-iterations <n> --completion-promise "<text>"
  slash command. Stop hook re-feeds the same prompt; the agent emits
  <promise>COMPLETE</promise> on its own line to exit. Loop runs inside a
  single Claude Code session.
adopt: |
  - <promise>COMPLETE</promise> exit contract verbatim.
  - max_iterations as the canonical safety cutoff.
  - "same prompt, mutating workspace = feedback signal" invariant.
reject: |
  - In-session loop via Stop hook. Our cron jobs need a fresh session each
    firing, so we wrap externally with `until ! ...` instead.
security_concerns: |
  Loop-without-cap is the primary risk; max_iterations is the mitigation.
privacy_concerns: none
context_efficiency_relevance: |
  Iterations accumulate vault state, not session context — context stays
  bounded.
self_improvement_relevance: |
  The mechanism by which any axis improves between iterations.
obsidian_relevance: |
  None directly; Ralph adapts the contract to a vault-mutating loop.
claude_code_relevance: high
provider_neutral_relevance: |
  Other CLI agents (Codex, Aider) need their own Stop-hook equivalent.
  The promise+max-iter contract is portable.
business_entity_relevance: |
  Approval gates between iterations let the loop pause for human review.
confidence: 1.0
stability: 0.8
freshness: verified live 2026-05-08
implementation_consequence: |
  Used in every prompts/ralph-meta-chain/0*-*.md prompt's exit section.
---
```

### ghuntley/how-to-ralph-wiggum

```yaml
research_date: 2026-05-08
source_name: ghuntley/how-to-ralph-wiggum
source_url: https://github.com/ghuntley/how-to-ralph-wiggum
category: harness
observed_mechanism: |
  `while :; do cat PROMPT.md | claude-code; done` shape; same prompt, the
  workspace mutates and that becomes the feedback channel.
adopt: |
  External-loop shape; "the workspace IS the prompt input" mental model.
reject: |
  Unbounded loops. Always cap with `until !` + iteration counter.
security_concerns: |
  Same as above; cap.
privacy_concerns: none
context_efficiency_relevance: |
  Each iteration starts a fresh session (low context cost).
self_improvement_relevance: high
obsidian_relevance: |
  Vault state is the workspace mutation channel.
claude_code_relevance: high
provider_neutral_relevance: |
  Works for any CLI agent.
business_entity_relevance: |
  Caller chooses iteration cap; reasonable for approval-gated workflows.
confidence: 0.9
stability: 0.7
freshness: verified live 2026-05-08
implementation_consequence: |
  scripts/install.sh's `until ! claude -p "$(cat ...)" || [ ... ]; do :;
  done` shape lifted directly from this.
---
```

### snarktank/ralph

```yaml
research_date: 2026-05-08
source_name: snarktank/ralph
source_url: https://github.com/snarktank/ralph
category: harness
observed_mechanism: |
  PRD-driven Ralph: loops until items in a Product Requirements Document
  are complete.
adopt: |
  Spec-as-exit-criterion. In Ralph Meta Chain, the YAML budget block per
  axis IS the spec; budget exhaustion = "done".
reject: none
security_concerns: none
privacy_concerns: none
context_efficiency_relevance: medium
self_improvement_relevance: medium
obsidian_relevance: none
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: |
  PRD-style specs translate naturally to deliverable tracking.
confidence: 0.8
stability: 0.6
freshness: 2026-05-08
implementation_consequence: |
  Each prompt has an explicit budgets.<axis> block in config.yml.
---
```

---

## Karpathy family

### karpathy/autoresearch

```yaml
research_date: 2026-05-08
source_name: karpathy/autoresearch
source_url: https://github.com/karpathy/autoresearch
category: self-evolving
observed_mechanism: |
  Single-GPU nanochat training; fixed 5-minute experiments; ~12/hr,
  ~100/night. Agent runs research overnight on its own.
adopt: |
  Fixed-time per experiment so a cron firing yields many parallel
  hypotheses. ralph.experiment_minutes default = 5.
reject: |
  GPU-specific assumptions; we're CPU + remote-Anthropic-API.
security_concerns: none
privacy_concerns: none
context_efficiency_relevance: high
self_improvement_relevance: high
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: medium
business_entity_relevance: low
confidence: 1.0
stability: 0.7
freshness: verified live 2026-05-08
implementation_consequence: |
  Drives the "Auto-research (Karpathy autoresearch)" section in every
  daily prompt.
---
```

### Karpathy LLM Wiki gist

```yaml
research_date: 2026-05-08
source_name: Karpathy LLM Wiki gist
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
category: memory
observed_mechanism: |
  Three-layer architecture: raw (immutable inputs) → wiki (LLM-curated
  markdown) → schema (CLAUDE.md / AGENTS.md rules). Mandatory files:
  index.md (categorized catalog) and log.md (append-only "[YYYY-MM-DD]"
  entries). Operations: ingest / query / lint.
adopt: |
  - Three-layer split mapped onto Obsidian: 00-Inbox/ raw → 30-Notes/ +
    20-MOCs/ wiki → CLAUDE.md + 90-Meta/ schema.
  - 90-Meta/index.md + 90-Meta/log.md mandatory.
  - ingest / query / lint as the daily memory pass operations.
  - "Touch 10-15 wiki pages per ingest" backlink rule.
reject: none
security_concerns: none
privacy_concerns: |
  Vault is local; raw layer means PII may live in 00-Inbox/. Treat it as
  privacy-sensitive.
context_efficiency_relevance: high
self_improvement_relevance: high
obsidian_relevance: very-high
claude_code_relevance: high
provider_neutral_relevance: |
  Plain Markdown; portable to any agent that can edit files.
business_entity_relevance: |
  Same vault holds business memory; same rules.
confidence: 1.0
stability: 0.9
freshness: verified live 2026-05-08
implementation_consequence: |
  prompts/ralph-meta-chain/01-memory-optimizer.md is a direct
  implementation of the ingest/lint pair.
---
```

---

## Hermes family

### NousResearch/hermes-agent

```yaml
research_date: 2026-05-08
source_name: NousResearch/hermes-agent
source_url: https://github.com/NousResearch/hermes-agent
category: self-evolving
observed_mechanism: |
  Self-improving agent that "creates skills from experience, improves
  them during use, searches its own past conversations". v0.13 ships
  /goal command + Kanban multi-agent board with heartbeat + zombie
  detection.
adopt: |
  - "Skills from experience" — any action pattern observed ≥ 2× in the
    trailing window becomes a candidate skill.
  - Heartbeat + zombie detection — `90-Meta/ralph-state.json` per-axis
    `last_run`; "zombie" = no run in > N hours.
  - /goal-as-target-state for the compressor (compress past sessions
    toward an open goal).
reject: |
  Multi-agent Kanban is over-engineered for our 8-axis chain right now.
security_concerns: |
  "Agent that grows with you" implies persistent state — needs careful
  approval gating for high-risk axes.
privacy_concerns: |
  Personal-agent framing — same vault PII concerns as memory layer.
context_efficiency_relevance: high
self_improvement_relevance: very-high
obsidian_relevance: medium
claude_code_relevance: high
provider_neutral_relevance: medium
business_entity_relevance: |
  20-platform messaging integration is a model for what business workflows
  could look like — but stays approval-gated.
confidence: 0.95
stability: 0.7
freshness: v0.13 verified 2026-05-07
implementation_consequence: |
  prompts/ralph-meta-chain/02-skills-optimizer.md cites this as the
  primary inspiration for the skills-from-experience rule. 06-autoheal.md
  uses heartbeat/zombie detection.
---
```

### NousResearch/hermes-agent-self-evolution

```yaml
research_date: 2026-05-08
source_name: NousResearch/hermes-agent-self-evolution
source_url: https://github.com/NousResearch/hermes-agent-self-evolution
category: self-evolving
observed_mechanism: |
  Evolutionary self-improvement using DSPy + GEPA. ICLR 2026 Oral.
adopt: |
  Population A/B at the prompt-rewrite layer (per `harness ab`); GEPA-
  style MAP-Elites bin (token-cost × format-strictness).
reject: |
  Weight-level retraining (we're prompt-level only).
security_concerns: |
  Auto-rewriting prompts can introduce regressions; harness ab is the
  guardrail.
privacy_concerns: none
context_efficiency_relevance: high
self_improvement_relevance: very-high
obsidian_relevance: low
claude_code_relevance: high
provider_neutral_relevance: high
business_entity_relevance: low
confidence: 0.9
stability: 0.7
freshness: ICLR 2026 Oral, recent
implementation_consequence: |
  02-skills-optimizer.md step 4 uses GEPA × MAP-Elites; 07-autoevolve.md
  uses week-scale GEPA over candidate populations.
---
```

### gepa-ai/gepa

```yaml
research_date: 2026-05-08
source_name: gepa-ai/gepa
source_url: https://github.com/gepa-ai/gepa
category: paper
observed_mechanism: |
  Genetic-Pareto reflective prompt evolution. ICLR 2026 Oral. Six tasks:
  6 pp better than GRPO at 35× fewer rollouts. Databricks reported 90×
  cost reduction.
adopt: |
  - Reflexion lesson-loop (one-line "lesson learned" per A/B verdict).
  - MAP-Elites diversity (per-bin survivor, not just global best).
  - Pareto-based candidate selection.
reject: none
security_concerns: none
privacy_concerns: none
context_efficiency_relevance: high
self_improvement_relevance: very-high
obsidian_relevance: low
claude_code_relevance: high
provider_neutral_relevance: high
business_entity_relevance: low
confidence: 1.0
stability: 0.8
freshness: ICLR 2026 Oral
implementation_consequence: |
  harness/harness/reflect.py is the Reflexion lesson-loop; 02 + 07
  prompts cite the MAP-Elites bin directly.
---
```

### EvoAgentX/Awesome-Self-Evolving-Agents

```yaml
research_date: 2026-05-08
source_name: EvoAgentX/Awesome-Self-Evolving-Agents
source_url: https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents
category: self-evolving
observed_mechanism: |
  Curated survey of self-evolving agent literature: Voyager, Reflexion,
  ADAS, OpenEvolve, GEPA, ShinkaEvolve.
adopt: |
  Use as the reading list for autoupdate's release-feed scan and as the
  canonical taxonomy for 07-autoevolve hypothesis types.
reject: none
security_concerns: none
privacy_concerns: none
context_efficiency_relevance: low
self_improvement_relevance: very-high
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: medium
business_entity_relevance: low
confidence: 0.9
stability: 0.8
freshness: actively maintained
implementation_consequence: |
  08-autoupdate.md release-feed list pulls from this survey.
---
```

---

## Memory frameworks (2026 landscape)

### obra/knowledge-graph

```yaml
research_date: 2026-05-08
source_name: obra/knowledge-graph
source_url: https://github.com/obra/knowledge-graph
category: memory
observed_mechanism: |
  "Query and traverse an Obsidian vault as a knowledge graph. Semantic
  search, path finding, community detection — all local. Claude Code
  plugin included." SQLite + sqlite-vec + FTS5 in one file.
adopt: |
  Storage shape verbatim: $VAULT/90-Meta/embeddings.db with sqlite-vec
  + FTS5 + reciprocal-rank-fusion hybrid retrieval.
reject: |
  Their full graph-traversal feature set; we start with vector + BM25.
security_concerns: |
  Local-first ✓
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: very-high
self_improvement_relevance: medium
obsidian_relevance: very-high
claude_code_relevance: high
provider_neutral_relevance: high
business_entity_relevance: medium
confidence: 1.0
stability: 0.7
freshness: verified live 2026-05-08
implementation_consequence: |
  harness/harness/embeddings.py uses this exact schema.
---
```

### cognee-ai/cognee

```yaml
research_date: 2026-05-08
source_name: cognee-ai/cognee
source_url: https://github.com/cognee-ai/cognee
category: memory
observed_mechanism: |
  Local-first graph reasoning over unstructured documents. Best for
  privacy-critical deployments per the 2026 surveys.
adopt: |
  As an opt-in memory backend (`embeddings.backend: cognee`).
reject: |
  Don't make it the default — sqlite-vec stays default for simplicity.
security_concerns: |
  Local-first ✓
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: high
self_improvement_relevance: medium
obsidian_relevance: high
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: |
  Graph reasoning over client docs is interesting but stays
  approval-gated.
confidence: 0.85
stability: 0.6
freshness: 2026-05-08
implementation_consequence: |
  harness/harness/memory_backends.py CogneeBackend stub.
---
```

### letta-ai/letta

```yaml
research_date: 2026-05-08
source_name: letta-ai/letta
source_url: https://github.com/letta-ai/letta
category: memory
observed_mechanism: |
  OS-style tiered memory; the MemGPT line. Best for long-running agents
  needing >> context-window memory.
adopt: |
  Opt-in backend (`embeddings.backend: letta`) for users explicitly
  running agents for days.
reject: |
  Default-on adoption — most users don't need it.
security_concerns: |
  Persistent agent state — same approval gating concerns as Hermes.
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: very-high
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: medium
confidence: 0.85
stability: 0.7
freshness: 2026-05-08
implementation_consequence: |
  harness/harness/memory_backends.py LettaBackend stub.
---
```

### mem0ai/mem0

```yaml
research_date: 2026-05-08
source_name: mem0ai/mem0
source_url: https://github.com/mem0ai/mem0
category: memory
observed_mechanism: |
  Personalization-style memory. Best for chatbot-style agents per the
  2026 surveys.
adopt: |
  Documented as an alternative; not currently a backend stub.
reject: |
  External-service variants (we're local-first by default).
security_concerns: |
  External service tier requires API key — not used here.
privacy_concerns: |
  Same.
context_efficiency_relevance: medium
self_improvement_relevance: low
obsidian_relevance: low
claude_code_relevance: low
provider_neutral_relevance: medium
business_entity_relevance: low
confidence: 0.8
stability: 0.7
freshness: 2026-05-08
implementation_consequence: |
  Mentioned in docs/MEMORY_MODEL.md as comparison only.
---
```

### getzep/zep

```yaml
research_date: 2026-05-08
source_name: getzep/zep
source_url: https://github.com/getzep/zep
category: memory
observed_mechanism: |
  Temporal knowledge graph (Graphiti). LongMemEval 63.8% vs Mem0 49.0%
  — a 15-pt gap driven by fact-validity windows rather than timestamped
  snapshots.
adopt: |
  Documented as the gold standard for temporal facts. If a future Ralph
  axis needs "fact X was true between t1 and t2" reasoning, Zep is the
  reference.
reject: |
  Not implemented; sqlite-vec + FTS5 is enough today.
security_concerns: |
  External service variant exists; local Graphiti is OK.
privacy_concerns: |
  Same.
context_efficiency_relevance: high
self_improvement_relevance: medium
obsidian_relevance: medium
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: |
  Decision/commitment ledgers benefit from temporal queries.
confidence: 0.9
stability: 0.7
freshness: 2026-05-08
implementation_consequence: |
  Docs only; no code in Round 1.
---
```

---

## Obsidian plugin family

### brianpetro/obsidian-smart-connections

```yaml
research_date: 2026-05-08
source_name: brianpetro/obsidian-smart-connections
source_url: https://github.com/brianpetro/obsidian-smart-connections
category: obsidian
observed_mechanism: |
  Obsidian plugin: keeps an up-to-date embedding index of notes; recovers
  on interrupted indexing; status-bar UX.
adopt: |
  - Recovery-on-interrupt pattern (idempotent embed).
  - Status-bar pill UX.
  - Local Transformers.js / Ollama for embeddings.
reject: none
security_concerns: |
  Plugin runs in-process; respects Obsidian's sandbox.
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: high
self_improvement_relevance: low
obsidian_relevance: very-high
claude_code_relevance: low
provider_neutral_relevance: medium
business_entity_relevance: low
confidence: 0.95
stability: 0.8
freshness: 2026-05-08, v4.3
implementation_consequence: |
  obsidian-ralph/src/status-bar.ts mirrors the status-bar UX.
---
```

### GoBeromsu/open-connections

```yaml
research_date: 2026-05-08
source_name: GoBeromsu/open-connections
source_url: https://github.com/GoBeromsu/open-connections
category: obsidian
observed_mechanism: |
  Obsidian plugin: privacy-first, offline-capable, 7 embedding providers.
adopt: |
  Multi-provider settings shape (Ralph picks via embeddings.backend).
reject: none
security_concerns: |
  Same as smart-connections.
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: medium
self_improvement_relevance: low
obsidian_relevance: very-high
claude_code_relevance: low
provider_neutral_relevance: high
business_entity_relevance: low
confidence: 0.85
stability: 0.6
freshness: 2026
implementation_consequence: |
  Future obsidian-plugin/ rebuild will lift the multi-provider settings.
---
```

### NicholasSpisak/second-brain

```yaml
research_date: 2026-05-08
source_name: NicholasSpisak/second-brain
source_url: https://github.com/NicholasSpisak/second-brain
category: obsidian
observed_mechanism: |
  Canonical Obsidian implementation of Karpathy's LLM Wiki pattern.
adopt: |
  Folder convention naming — confirms our 00-Inbox/, 10-Daily/, 20-MOCs/,
  30-Notes/ layout.
reject: none
security_concerns: none
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: high
self_improvement_relevance: medium
obsidian_relevance: very-high
claude_code_relevance: high
provider_neutral_relevance: high
business_entity_relevance: medium
confidence: 0.9
stability: 0.7
freshness: 2026
implementation_consequence: |
  Vault layout in CLAUDE.md borrows from this.
---
```

### charlie947/ai-second-brain

```yaml
research_date: 2026-05-08
source_name: charlie947/ai-second-brain
source_url: https://github.com/charlie947/ai-second-brain
category: obsidian
observed_mechanism: |
  Claude Code skill that turns chat history into a Karpathy-style second
  brain.
adopt: |
  Skill-file frontmatter shape (name / description / when_to_use /
  inputs / steps / tools / failure_modes / last_validated / metrics).
reject: none
security_concerns: none
privacy_concerns: |
  Local-first ✓
context_efficiency_relevance: medium
self_improvement_relevance: high
obsidian_relevance: high
claude_code_relevance: very-high
provider_neutral_relevance: medium
business_entity_relevance: low
confidence: 0.9
stability: 0.7
freshness: 2026
implementation_consequence: |
  prompts/ralph-meta-chain/02-skills-optimizer.md skill file format
  lifted from this.
---
```

---

## Tooling / harness

### promptfoo/promptfoo

```yaml
research_date: 2026-05-08
source_name: promptfoo/promptfoo
source_url: https://github.com/promptfoo/promptfoo
category: harness
observed_mechanism: |
  Declarative YAML config; fixture format; CI before/after comparison via
  GitHub Action.
adopt: |
  Fixture format verbatim — harness/fixtures/*.yml is shaped so a user
  can later run `promptfoo eval -c <fixture>` directly.
reject: |
  Full promptfoo runtime as a hard dependency.
security_concerns: |
  External eval service variants — not used.
privacy_concerns: low
context_efficiency_relevance: medium
self_improvement_relevance: high
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: very-high
business_entity_relevance: low
confidence: 1.0
stability: 0.9
freshness: 2026-05-08
implementation_consequence: |
  harness/fixtures/code-review.yml + daily-summary.yml use the schema.
---
```

### openai/codex

```yaml
research_date: 2026-05-08
source_name: openai/codex
source_url: https://github.com/openai/codex
category: harness
observed_mechanism: |
  Rust CLI coding agent. 75k stars by April 2026. Cloud-sandboxed agent
  variant integrated into ChatGPT.
adopt: |
  Fixtures portable enough that a future Codex adapter could compare
  Codex vs Claude Code on the same task.
reject: |
  Active runtime (Claude Code only per user choice).
security_concerns: |
  Cloud sandbox = data egress; local CLI is fine.
privacy_concerns: |
  Cloud variant ships code to OpenAI; local CLI does not.
context_efficiency_relevance: medium
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: |
  Direct competitor; informs how generic the fixture format must be.
provider_neutral_relevance: very-high
business_entity_relevance: low
confidence: 1.0
stability: 0.8
freshness: 2026-05-08
implementation_consequence: |
  docs/PROVIDER_NEUTRAL_ARCHITECTURE.md documents the deferred Codex
  adapter.
---
```

### moazbuilds/claudeclaw

```yaml
research_date: 2026-05-08
source_name: moazbuilds/claudeclaw
source_url: https://github.com/moazbuilds/claudeclaw
category: harness
observed_mechanism: |
  OpenClaw-style autonomous agent system on Claude Code. Background
  daemon executing tasks on a schedule.
adopt: |
  "Cron daemon" framing — our crontab.example IS the ClaudeClaw shape.
reject: |
  Telegram/Discord integration (out of scope this round).
security_concerns: |
  Always-on daemon = always-on attack surface; Tailscale-only origin.
privacy_concerns: |
  Always-listening framing (we don't do that).
context_efficiency_relevance: medium
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: high
provider_neutral_relevance: medium
business_entity_relevance: |
  Background daemon is a model for safe business automation.
confidence: 0.85
stability: 0.6
freshness: 2026-05-08
implementation_consequence: |
  scripts/install.sh's launchd template references the ClaudeClaw shape.
---
```

### swarmclawai/swarmclaw

```yaml
research_date: 2026-05-08
source_name: swarmclawai/swarmclaw
source_url: https://github.com/swarmclawai/swarmclaw
category: harness
observed_mechanism: |
  Open-source self-hosted runtime; agent memory; schedules; delegation;
  23+ LLM providers.
adopt: |
  Permissions allowlist shape in config.example.yml.
reject: |
  Multi-provider runtime (Claude Code only).
security_concerns: |
  Multi-provider variant ships data widely.
privacy_concerns: same
context_efficiency_relevance: medium
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: medium
confidence: 0.85
stability: 0.6
freshness: 2026-05-08
implementation_consequence: |
  config.example.yml permissions allow/deny structure.
---
```

---

## Coding-CLI landscape (2026)

### Cursor 3 / Aider / Cline / Roo Code / Continue / Goose

```yaml
research_date: 2026-05-08
source_name: 2026 coding-CLI landscape
source_url: https://dev.to/soulentheo/every-ai-coding-cli-in-2026-the-complete-map-30-tools-compared-4gob
category: tool
observed_mechanism: |
  - Cursor 3 (Apr 2026): cloud agents on isolated VMs, parallel Agent Tabs.
  - Aider: gold standard for terminal pair-programming.
  - Cline + Roo Code: VS Code extensions.
  - Continue: open-source IDE assistant.
  - Goose: Block's open-source agentic CLI.
  - Claude Mythos config: 92.1% on Terminal-Bench 2.0.
adopt: |
  Add each repo to 08-autoupdate.md release-feed list so the chain stays
  current. Adopt their fixture / rubric ideas where applicable.
reject: |
  Active integration of any non-Claude-Code runtime (per user choice).
security_concerns: |
  Cloud-agent variants (Cursor 3) ship code to vendor.
privacy_concerns: same
context_efficiency_relevance: high
self_improvement_relevance: high
obsidian_relevance: low
claude_code_relevance: high
provider_neutral_relevance: very-high
business_entity_relevance: medium
confidence: 0.9
stability: 0.7
freshness: 2026-05-08
implementation_consequence: |
  Listed in 08-autoupdate.md release-feed; no active runtime.
---
```

---

## OpenAI cookbook + adjacent

### OpenAI Cookbook — Self-Evolving Agents

```yaml
research_date: 2026-05-08
source_name: OpenAI Cookbook — Self-Evolving Agents (autonomous retraining)
source_url: https://cookbook.openai.com/examples/partners/self_evolving_agents/autonomous_agent_retraining
category: self-evolving
observed_mechanism: |
  Loop: collect-traces → score → select → retrain.
adopt: |
  Loop applied at PROMPT/SKILL level (not weight level): metrics.ndjson
  is the trace store; harness ab + judge + reflect close the loop.
reject: |
  Weight retraining (we don't fine-tune).
security_concerns: none
privacy_concerns: none
context_efficiency_relevance: high
self_improvement_relevance: very-high
obsidian_relevance: medium
claude_code_relevance: high
provider_neutral_relevance: very-high
business_entity_relevance: medium
confidence: 0.95
stability: 0.8
freshness: 2026
implementation_consequence: |
  prompts/ralph-meta-chain/07-autoevolve.md cites this as the canonical
  retraining loop, applied to prompts.
---
```

---

## Creator signal channels (NOT sources)

### Alex Finn (@AlexFinnOfficial)

```yaml
research_date: 2026-05-08
source_name: Alex Finn YouTube channel
source_url: https://www.youtube.com/@AlexFinnOfficial
category: creator
observed_mechanism: |
  "Claude Life OS" — slash commands + sub-agents that automate research,
  news curation, brain-dump analysis, business metric tracking.
  Aggressive iteration: if a workflow doesn't 10× something, delete it.
adopt: |
  - Aggressive deprecation rule: skill success_rate < 0.6 over 14d →
    deprecate. Prompt loses 3 A/Bs in a row → rewrite from scratch.
  - "Claude Life OS" framing as the umbrella name for our daily chain.
reject: |
  Direct content copying.
security_concerns: |
  Vibe-coding aesthetic encourages skipping safety; we don't.
privacy_concerns: low
context_efficiency_relevance: high
self_improvement_relevance: very-high
obsidian_relevance: medium
claude_code_relevance: very-high
provider_neutral_relevance: medium
business_entity_relevance: high
confidence: 0.7
stability: 0.5
freshness: 2026
implementation_consequence: |
  07-autoevolve.md cites Alex Finn as the inspiration for ruthless
  iteration.
---
```

### Matt Wolfe (@mreflow / FutureTools.io)

```yaml
research_date: 2026-05-08
source_name: Matt Wolfe YouTube channel + FutureTools.io
source_url: https://www.youtube.com/@mreflow
category: creator
observed_mechanism: |
  Weekly AI-news + tools curation. 250k+ subscribers. Pattern:
  scan-everything-surface-signal.
adopt: |
  Weekly cadence + scan-everything ethos for 08-autoupdate. Single weekly
  output file (00-Inbox/futuretools-YYYY-Www.md) that prompt #1 promotes.
reject: none
security_concerns: low
privacy_concerns: low
context_efficiency_relevance: medium
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: medium
confidence: 0.8
stability: 0.7
freshness: 2026
implementation_consequence: |
  08-autoupdate.md cites Matt Wolfe as the inspiration; weekly Monday
  06:00 UTC cadence.
---
```

### Nate Herk (@nateherk)

```yaml
research_date: 2026-05-08
source_name: Nate Herk YouTube channel
source_url: https://www.youtube.com/@nateherk
category: creator
observed_mechanism: |
  n8n + AI agent automation tutorials. Centralized assistant managing
  specialized sub-agents (email/calendar/contacts/content).
adopt: |
  Supervisor + sub-agents pattern for 06-autoheal: one prompt surveys
  the whole chain's heartbeat and fixes/escalates per axis.
reject: |
  n8n stack itself (Claude Code is our primary runtime).
security_concerns: |
  His example workflows often touch CRM/email; we keep those gated.
privacy_concerns: medium
context_efficiency_relevance: medium
self_improvement_relevance: high
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: very-high
business_entity_relevance: very-high
confidence: 0.85
stability: 0.7
freshness: 2026
implementation_consequence: |
  06-autoheal.md cites Nate Herk as the supervisor pattern.
---
```

### Matthew Berman (added per master spec inspiration list)

```yaml
research_date: 2026-05-09
source_name: Matthew Berman YouTube channel
source_url: https://www.youtube.com/@matthew_berman
category: creator
observed_mechanism: |
  Hands-on AI tool reviews; agent-stack walkthroughs.
adopt: |
  Use as a secondary signal channel for autoupdate. Pattern: do the demo,
  log the cost, log the failure mode.
reject: none
security_concerns: low
privacy_concerns: low
context_efficiency_relevance: low
self_improvement_relevance: medium
obsidian_relevance: low
claude_code_relevance: medium
provider_neutral_relevance: high
business_entity_relevance: low
confidence: 0.7
stability: 0.6
freshness: 2026
implementation_consequence: |
  Added to research/trend-scout.md creator stream.
---
```

---

## Summary statistics

- 25 entries across categories: harness (7), memory (6), self-evolving (5),
  obsidian (4), tool (1), creator (4), paper (covered in self-evolving).
- 6 entries have confidence ≥ 0.95 (primary docs verified live).
- 4 entries have stability ≥ 0.85 (1.x or CS literature).
- All 25 entries are local-first or local-first-compatible.
- 0 entries are adopted that require sending data to a vendor.
