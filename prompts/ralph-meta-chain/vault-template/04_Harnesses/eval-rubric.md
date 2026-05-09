---
ralph_type: experiment
memory_layer: experiment
stability: stable
created: 2026-05-09
status: active
summary: "Per-output rubric used by the LLM judge in `harness ab`."
---

# Eval Rubric

Authoritative source: `harness/harness/judge.py` (`RUBRIC_PROMPT`). This
file is the human-readable spec.

## Scored axes

The judge returns JSON only:

```json
{"helpfulness": 1-5, "brevity": 1-5, "format": 1-5}
```

Each axis is 1.0–5.0. The composite `rubric` score is the arithmetic
mean.

### Helpfulness (1-5)

| Score | Criterion                                                     |
| ----- | ------------------------------------------------------------- |
| 5     | answers the task fully, would unblock the user                 |
| 4     | answers the task with minor gaps                                |
| 3     | partial answer; user would need to ask follow-up                |
| 2     | tangential; misses the core ask                                  |
| 1     | wrong / contradicts the task                                     |

### Brevity (1-5)

| Score | Criterion                                                     |
| ----- | ------------------------------------------------------------- |
| 5     | no preambles, no padding; every line carries content           |
| 4     | mostly tight; one or two filler phrases                         |
| 3     | average; some restating, some padding                           |
| 2     | clearly verbose                                                  |
| 1     | mostly preamble / restating the prompt                           |

### Format (1-5)

| Score | Criterion                                                     |
| ----- | ------------------------------------------------------------- |
| 5     | matches every explicit format requirement (max-tokens, headers, code blocks) |
| 4     | matches most requirements                                       |
| 3     | partial format compliance                                        |
| 2     | format ignored in places                                         |
| 1     | format requirements ignored                                      |

## Banned-phrase counter

Independent of the rubric — counts how many times the output uses
forbidden phrases:

```
"Great question"
"I'd be happy to"
"Certainly!"
"As an AI"
```

Plus failed asserts (max-tokens / not-contains / contains).

## Verdict rule

Per `docs/AB_HARNESS.md`:

```
keep candidate iff
  rubric_candidate ≥ rubric_incumbent
  AND
  ( tokens_candidate ≤ tokens_incumbent
    OR
    banned_candidate < banned_incumbent )
```

## Cross-references

- `harness/harness/judge.py` — implementation.
- `docs/AB_HARNESS.md` — full evaluation surface.
- `04_Harnesses/prompt-scorecard.md` — per-prompt history.
- `00_System/Interaction Preferences.md` — what "helpful" means for THIS user.
