---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for prompt outputs (mirrors the AB harness)."
---

# Prompt Quality Scorecard

Authoritative source: `docs/AB_HARNESS.md` § Scoring rubric. This file
restates the same rubric in scorecard form so it can be referenced
from `01-memory-optimizer.md` / `02-skills-optimizer.md` /
`03-interaction-optimizer.md` / `07-autoevolve.md` without each having
to re-derive.

## Scored axes (the rubric judge returns JSON ONLY)

```json
{"helpfulness": 1-5, "brevity": 1-5, "format": 1-5}
```

Composite `rubric` = arithmetic mean of the three axes.

### helpfulness (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | answers the task fully; would unblock the user             |
| 4     | answers with minor gaps                                    |
| 3     | partial answer; user must follow up                        |
| 2     | tangential                                                  |
| 1     | wrong / contradicts the task                                |

### brevity (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | no preambles, no padding                                  |
| 4     | mostly tight; 1-2 filler phrases                          |
| 3     | average                                                   |
| 2     | clearly verbose                                           |
| 1     | mostly preamble                                           |

### format (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | matches every explicit format requirement                  |
| 4     | matches most                                              |
| 3     | partial                                                    |
| 2     | format ignored in places                                   |
| 1     | format requirements ignored                                |

## Banned-phrase counter (independent of rubric)

Counts forbidden phrases:
- "Great question"
- "I'd be happy to"
- "Certainly!"
- "As an AI"

Plus failed promptfoo asserts (`max-tokens`, `not-contains`,
`contains`).

## Verdict rule (per A/B run)

```
keep candidate iff
  rubric_candidate ≥ rubric_incumbent
  AND
  ( tokens_candidate ≤ tokens_incumbent
    OR
    banned_candidate < banned_incumbent )
```

## Pass thresholds per axis

- **incumbent prompts**: rubric ≥ 3.5 OR they're flagged for rewrite.
- **candidate prompts**: must beat the incumbent OR be archived to
  `_rejected/`.
- **3 consecutive A/B losses** → `07-autoevolve` proposes
  rewrite-from-scratch with a 3-candidate population.

## Round 6 reflexion lessons

After each A/B, `harness reflect` appends a one-line ≤ 80 char
takeaway to the candidate's `reflections:` frontmatter:

```yaml
reflections:
  - "[2026-05-09] preamble killed terse rubric (-0.4)"
```

3 same-flavor lessons → free rewrite next pass.

## Cross-references

- `docs/AB_HARNESS.md`.
- `harness/harness/judge.py`.
- `harness/harness/reflect.py`.
- `vault-template/04_Harnesses/{eval-rubric,prompt-scorecard}.md`.
- `seed/50-Prompts/{code-review,daily-summary}.md`.
