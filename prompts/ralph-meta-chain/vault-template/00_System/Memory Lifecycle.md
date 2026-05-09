---
ralph_type: system
memory_layer: system
memory_temperature: hot
stability: canonical
created: 2026-05-09
summary: "Sixteen-step pipeline from raw capture to canonical memory."
---

# Memory Lifecycle

Authoritative source: `docs/MEMORY_MODEL.md` § Memory pipeline. Lives
here so prompts can `Read` it at runtime.

## Pipeline

1. Capture raw note (`01_Inbox/` / `00-Inbox/`).
2. Add frontmatter (auto-attempted on inbox files; manual fallback).
3. Classify memory type.
4. Score usefulness (current project / recurrence / leverage / actionability).
5. Score stability (volatile / provisional / stable / canonical).
6. Score privacy sensitivity.
7. Score retrieval relevance.
8. Detect duplicates.
9. Link related notes (`[[wikilinks]]`).
10. Extract durable facts.
11. Generate compression proposal (if oversize).
12. Archive raw content before any rewrite.
13. Promote distilled knowledge to canonical memory.
14. Update indexes (`90-Meta/index.md`, `00_System/Skill Registry.md`, etc.).
15. Generate daily memory report (`06_Reports/daily-memory-report.md`).
16. Emit recommendations for future retrieval.

## Where each step is implemented

| Step  | Implementation                                              |
| ----- | ----------------------------------------------------------- |
| 1     | iOS Shortcut, voice-server, manual edit                     |
| 2     | manual frontmatter; future `harness ingest --autotag`        |
| 3-5   | `prompts/ralph-meta-chain/01-memory-optimizer.md` (memory pass) |
| 6-8   | same                                                         |
| 9-10  | same; touches 10-15 wiki pages per ingest (Karpathy rule)   |
| 11    | `prompts/ralph-meta-chain/05-compress.md`                    |
| 12    | `harness compress` archives original to `_archive/`          |
| 13    | `01-memory-optimizer.md` step 4                              |
| 14    | every prompt's "Index + Log + State" step                    |
| 15    | `06_Reports/daily-memory-report.md` (daily)                   |
| 16    | autoevolve weekly (`07-autoevolve.md`)                        |

## Compression rules

Per `docs/MEMORY_MODEL.md` § Compression rules. Summary:

**MUST:**
- preserve raw input in `_archive/` before any rewrite,
- summary ≤ 40% of original word count,
- retain every `[[wikilink]]`,
- retain every claim flagged `stability: canonical`,
- mark uncertain claims as `provisional`.

**MUST NOT:**
- delete the original,
- collapse contradictory notes silently,
- silently rewrite preferences,
- silently alter business ledgers,
- silently change approval gates.

## Cross-references

- `docs/MEMORY_MODEL.md`, `docs/CONTEXT_LIFECYCLE.md`.
- `00_System/Memory Taxonomy.md`.
- `06_Reports/daily-memory-report.md`.
