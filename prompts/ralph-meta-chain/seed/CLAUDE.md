# Vault Schema (Karpathy LLM-Wiki + Obsidian) — seed copy

You are the maintainer of this vault. Same prompt, mutating workspace.

## Layers
- raw     → 00-Inbox/                 (immutable captures)
- wiki    → 20-MOCs/, 30-Notes/       (LLM-curated markdown)
- schema  → this file + 90-Meta/      (rules + audit trail)

## Atomic note frontmatter (30-Notes/)
id, created, aliases, tags, links, source, type

## MOC frontmatter (20-MOCs/)
id, created, tag, child_count

## Skill frontmatter (40-Skills/) — see charlie947/ai-second-brain
name, description, when_to_use, inputs, steps, tools, failure_modes,
last_validated, metrics, prerequisites, is_prerequisite_of

## Prompt frontmatter (50-Prompts/)
name, last_rewritten, validated_against, bin (MAP-Elites bin),
reflections (Reflexion lesson loop)

## Mandatory files (Karpathy LLM-Wiki)
- 90-Meta/index.md         categorized catalog, 1-line summaries
- 90-Meta/log.md           append-only "## [YYYY-MM-DD] axis | k=v ..."
- 90-Meta/ralph-state.json last-run pointers, hashes, open promises
- 90-Meta/metrics.ndjson   one JSON line per experiment
- 90-Meta/embeddings.db    sqlite-vec + FTS5 (or backend of choice)

## Hard rules
- Append-only. Never delete notes or sections.
- Backlinks: every promotion touches 10–15 related pages.
- Promotions ≥ 3 same-tag → MOC.
- Orphans (>7d, 0 inbound) → #orphan, never deleted.
- Voyager curriculum: new skills carry prerequisite chains.
- MAP-Elites: keep per-bin survivor, not just global best.
- Reflexion: candidate prompts accumulate `reflections:` over weeks.
