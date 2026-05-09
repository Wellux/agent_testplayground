---
name: context-compression-engineer
description: |
  Triggers: "compress this", "context bloat", "weekly rollup", "compression strategy",
  "summary preserving wikilinks".
when_to_use: |
  When notes exceed the compression threshold OR daily-note rollups
  are due. Discipline: archive-before-rewrite; preserve every wikilink
  and every canonical claim.
inputs:
  - target: a single note path | "older-than 7d" | "weekly --iso-week YYYY-Www"
steps:
  - "Read the source note(s) + 00_System/Memory Lifecycle.md (compression rules)."
  - "Identify canonical claims, all wikilinks, and any privacy: client tags."
  - "If the note has stability: canonical → REFUSE; HIGH-risk to compress."
  - "Generate a summary ≤ 40% of the original word count."
  - "Verify: every wikilink appears in the summary."
  - "Verify: every canonical claim appears verbatim in the summary."
  - "If verification fails, regenerate (up to 3 attempts) before refusing."
  - "Move the original to _archive/<id>-original.md (NEVER rm)."
  - "Write the summary back in place with frontmatter compressed_from: [[<id>-original]]."
  - "Re-embed both the compressed summary and the archived original."
  - "Append a metrics row to 90-Meta/metrics.ndjson."
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Bash(harness compress:*,harness embed:*,mv:*,find:*)"
failure_modes:
  - canonical note targeted → REFUSE; HIGH-risk
  - verification (every wikilink preserved) fails after 3 attempts → REFUSE; surface to user
  - rm requested → REFUSE; archive-only
  - privacy: client note compressed without privacy frontmatter retained → REFUSE
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [memory-architect, recall]
is_prerequisite_of: []
links:
  - "[[docs/MEMORY_MODEL.md]]"
  - "[[00_System/Memory Lifecycle.md]]"
  - "[[prompts/ralph-meta-chain/05-compress.md]]"
  - "[[harness/harness/compress.py]]"
tags: [skill, specialist, compression]
---

# Context Compression Engineer

The role you assume when the bloated-note threshold fires or when
weekly rollups are due. Discipline: append-only invariant is sacred;
verify wikilink + canonical-claim preservation before mv-to-archive.

## Canonical experiment

Given a 4500-word note in `30-Notes/test-bloat.md` with:
- 8 wikilinks (`[[A]]`, `[[B]]`, ..., `[[H]]`),
- 2 canonical claims (`stability: stable` somewhere; the body
  contains "**Decision: X**" and "**Decision: Y**"),

the skill must:

1. Refuse if `stability: canonical`.
2. Generate a ≤ 1800-word summary preserving all 8 wikilinks + both
   "**Decision: ...**" lines verbatim.
3. mv original to `_archive/<id>-original.md`.
4. Write summary to `30-Notes/test-bloat.md` with
   `compressed_from: [[<id>-original]]`.
5. Re-embed both via `harness embed`.
6. Append metrics row with `tokens_before / tokens_after / ratio`.

Verification: ratio < 0.4 AND all 8 wikilinks present AND both
decision lines present.
