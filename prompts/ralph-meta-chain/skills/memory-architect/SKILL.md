---
name: memory-architect
description: |
  Triggers: "memory architect", "design memory", "shape the taxonomy",
  "what type is this", "where does this note belong", "memory lifecycle".
when_to_use: |
  When the user is shaping how the vault organizes notes — adding a
  new memory type, adjusting demotion windows, defining canonical
  fields in frontmatter, or reasoning about hot/warm/cold/frozen
  thresholds.
inputs:
  - vault_path: existing vault to inspect (optional)
  - proposed_change: free-text description of the taxonomy shift
  - constraints: privacy / size / retention requirements
steps:
  - "Read docs/MEMORY_MODEL.md and 00_System/Memory Taxonomy.md."
  - "Inspect the vault: count notes per memory_layer / memory_temperature."
  - "Identify what the proposed change breaks — Voyager curriculum, A/B fixtures, ledger schemas."
  - "Sketch a migration path that's append-only (no delete; no silent rewrite)."
  - "Score the proposal: clarity (1-5) × stability (1-5) × tooling-cost (1-5)."
  - "Output a proposal note in 30-Notes/ with status: open."
tools:
  - "Read"
  - "Bash(grep:*,find:*,wc:*,jq:*)"
  - "Agent(Explore)"
failure_modes:
  - proposed change deletes memory → refuse; suggest archive-not-delete
  - proposed change conflicts with append-only invariant → refuse; cite docs/GOVERNANCE.md
  - missing privacy frontmatter on the affected notes → flag as ERROR before any change
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [recall]
is_prerequisite_of: [obsidian-vault-engineer, context-compression-engineer]
links:
  - "[[docs/MEMORY_MODEL.md]]"
  - "[[00_System/Memory Taxonomy.md]]"
tags: [skill, specialist, memory]
---

# Memory Architect

The role you assume when the question is "how should we MODEL this in
memory?" rather than "what should we DO with this note?". Slow,
deliberate; favors the canonical schema over per-case ad-hoc.

## Canonical experiment

Given a fixture taxonomy proposal in `04_Harnesses/fixtures/memory-arch-001/`
that adds a new `memory_layer: provisional`, the skill must:

1. Identify every existing layer that conflicts.
2. Sketch the migration path (no deletes).
3. Score the proposal using the rubric in `04_Harnesses/eval-rubric.md`.
4. Output a proposal note matching `30-Notes/<id>-memory-arch-*.md`
   shape.

The fixture (Round 7+) ships expected output to compare against.
