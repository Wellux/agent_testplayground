---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for the daily memory pass output."
---

# Memory Quality Scorecard

Grades the output of `01-memory-optimizer.md` (atomic-note promotions,
MOC updates, orphan tagging, hypothesis drafts).

## Scored axes (1-5 each; rubric = mean)

### atomicity (1-5)

How well does each promoted note conform to the Zettelkasten "one idea
per note" rule?

| Score | Criterion                                                     |
| ----- | ------------------------------------------------------------- |
| 5     | Single durable claim, no embedded TODOs, no thread-of-thought |
| 4     | Mostly atomic; one minor digression                            |
| 3     | Multiple ideas glommed; recoverable                            |
| 2     | Inbox-style scratchpad masquerading as atomic                  |
| 1     | Multi-page transcript dumped under an atomic frontmatter       |

### linkage (1-5)

Does the memory pass touch 10–15 related wiki pages per ingest
(Karpathy LLM-Wiki rule)?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | 10-15 backlinks added; every backlink is meaningful       |
| 4     | 8-12 backlinks; mostly meaningful                         |
| 3     | 5-9 backlinks; some are noise                             |
| 2     | < 5 backlinks; isolated note                              |
| 1     | 0 backlinks; orphan from day 1                            |

### frontmatter conformance (1-5)

Does the frontmatter pass `memory-frontmatter.schema.json`?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | All 5 required fields + appropriate optional fields       |
| 4     | All required; missing 1-2 useful optional fields          |
| 3     | All required; tags/links missing                          |
| 2     | 1 required field missing                                  |
| 1     | ≥ 2 required fields missing                              |

### contradiction-detection (1-5)

When the pass surfaces contradictions in the wiki, are they real?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | All contradictions flagged are genuine; precision = 1.0   |
| 3     | Half are genuine; half are paraphrase artifacts            |
| 1     | Most flagged "contradictions" are paraphrase                |

### MOC promotion timing (1-5)

When ≥ 3 atomic notes share a tag, is the MOC created?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | MOC created on the next pass after the third note          |
| 3     | MOC created within a week                                  |
| 1     | MOC never created despite ≥ 3 notes (broken)                |

## Pass threshold

- **rubric ≥ 3.5** required for the memory pass to claim
  `state.memory.status: COMPLETE`.
- **atomicity = 1** is a BLOCKER: the pass refuses to promote and
  emits an escalation.
- **frontmatter conformance < 3** triggers `ralph_validate_frontmatter.sh`
  in the next heal cycle.

## Cross-references

- `docs/MEMORY_MODEL.md`.
- `prompts/ralph-meta-chain/01-memory-optimizer.md` § Step 4 (Ingest).
- `vault-template/04_Harnesses/eval-rubric.md`.
- `config/memory-frontmatter.schema.json`.
