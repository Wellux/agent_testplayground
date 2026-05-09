---
ralph_type: experiment
memory_layer: experiment
created: 2026-05-09
status: active
summary: "Per-prompt A/B history scorecard."
---

# Prompt Scorecard

The interaction-optimizer cron updates this from
`90-Meta/metrics.ndjson`. Read this when you want a quick "is my
`code-review` prompt getting better over time?" answer.

## Per-prompt rolling rubric

| Prompt              | 7-day mean rubric | 30-day mean | Wins / Losses (30d) | Reflections (cumulative) |
| ------------------- | ----------------- | ----------- | ------------------- | ------------------------ |
| `code-review`       | —                 | —           | 0 / 0               | 0                        |
| `daily-summary`     | —                 | —           | 0 / 0               | 0                        |

(Empty until first A/B firing.)

## How to interpret

- **Rubric trending up** = candidates have been winning. Good.
- **Wins / Losses** ratio < 0.5 over 30 days = the incumbent is too
  strong; consider an autoevolve "rewrite-from-scratch" proposal.
- **Reflections accumulating without rubric improvement** = the
  reflection loop is identifying issues but the rewrites aren't
  improving. Manual review needed.

## A/B verdict trail

```dataview
TABLE
  fixture,
  arm,
  rubric,
  tokens,
  banned
FROM "90-Meta"
WHERE file.name = "metrics" AND axis = "interaction"
SORT started DESC
LIMIT 20
```

(Dataview query illustrative; raw data lives in
`90-Meta/metrics.ndjson`. Use `harness traces --tail 20 --axis
interaction` for the same view.)

## Cross-references

- `04_Harnesses/eval-rubric.md` — what the scores mean.
- `04_Harnesses/workflow-scorecard.md` — for skills (procedural memory).
- `00_System/Prompt Registry.md` — full registry.
- `harness/harness/ab.py`, `harness/harness/reflect.py`, `harness/harness/traces.py`.
