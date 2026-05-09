---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for tone / format conformance to user preferences."
---

# Interaction Quality Scorecard

Grades how well outputs match `60-Interactions/user-profile.md`. The
`03-interaction-optimizer.md` cron writes proposals based on this
scorecard.

## Scored axes (1-5 each)

### tone match (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | matches user-profile tone exactly (terseness, register)   |
| 4     | minor drift; one over-formal phrase                       |
| 3     | average                                                    |
| 2     | clearly off-tone (verbose when user wants terse, e.g.)     |
| 1     | opposite tone of profile                                    |

### format match (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | matches user-profile format prefs (code blocks vs prose, list density) |
| 4     | minor drift                                                |
| 3     | average                                                    |
| 2     | clearly off-format                                          |
| 1     | format the user explicitly disliked                         |

### dislike avoidance (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | no banned phrases; no items from the profile's "Dislikes" |
| 4     | one minor brush                                             |
| 3     | one banned-phrase hit                                       |
| 2     | two banned-phrase hits                                      |
| 1     | three+ hits OR a hard-banned item from "Dislikes"            |

### recurring-ask coverage (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | output anticipates the user's known recurring asks         |
| 3     | meets the literal request without anticipating               |
| 1     | misses the recurring ask the user has voiced ≥ 3× recently   |

## Composite rubric

`rubric_interaction = mean(tone, format, dislike, recurring)`.

## Pass thresholds

- `rubric_interaction ≥ 3.5` for any output the chain emits to the
  user (status bar messages, daily report headers, escalation
  summaries).
- Three consecutive `rubric_interaction < 3.0` → `07-autoevolve`
  flags the operational `Interaction Preferences.md` snapshot as
  stale and proposes refresh.

## Profile drift detection

The `03-interaction-optimizer.md` pass mines
`60-Interactions/feedback-log.md` for signals that contradict the
current operational snapshot. When ≥ 3 same-direction signals appear:

- Append a `## Ralph YYYY-MM-DD` block to
  `60-Interactions/user-profile.md`.
- Rewrite `00_System/Interaction Preferences.md` to reflect the new
  snapshot.
- The vault status bar shows "interaction-prefs updated".

## Cross-references

- `docs/AB_HARNESS.md` § Banned-phrase counter.
- `vault-template/00_System/Interaction Preferences.md`.
- `60-Interactions/{user-profile,feedback-log}.md`.
- `prompts/ralph-meta-chain/03-interaction-optimizer.md`.
