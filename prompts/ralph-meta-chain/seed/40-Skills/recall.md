---
name: recall
description: |
  Surface relevant atomic notes, MOCs, and skills before doing new work.
  Triggers: "what do we know about", "search the vault for", "have I
  thought about", "is there a note on".
when_to_use: |
  At the start of any axis pass, and before drafting a new hypothesis,
  skill, or prompt. The idea is "look before you write" — Voyager
  curriculum baseline.
inputs:
  - query: free-text question or keyword
  - k:     int, default 10
steps:
  - Bash: `harness query --semantic "<query>" --k <k>`
  - Read returned wikilinks; cite the most relevant 2-3 in any new note.
tools: ["Bash(harness:*)"]
failure_modes:
  - Ollama down → harness query returns "(no results)"; proceed without recall
    but tag any new note with `#unrecalled`.
  - sqlite-vec extension missing → query degrades to FTS5 only.
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []
is_prerequisite_of: ["pr-from-branch"]
links: []
tags: [skill, retrieval, voyager-baseline]
---

# recall

Hybrid (vector × FTS5 reciprocal-rank-fusion) retrieval over the user's
Obsidian vault. Calls the local `harness query` CLI; no network egress.

## Canonical experiment
Replay the last `harness query` invocation against a frozen vault snapshot
(`$VAULT/90-Meta/_test-fixtures/recall-001/`); assert the top result's id
matches the expected wikilink. Time-cap: `ralph.experiment_minutes`.
