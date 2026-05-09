---
ralph_type: experiment
memory_layer: experiment
created: 2026-05-09
status: active
summary: "Per-skill A/B history scorecard."
---

# Workflow Scorecard

Same shape as `prompt-scorecard.md` but for skills (procedural memory).
The skills-optimizer cron writes here.

## Per-skill rolling success-rate

| Skill              | Invocations (30d) | Success rate (30d) | Mean tokens | Last validated |
| ------------------ | ----------------- | ------------------ | ----------- | -------------- |
| `recall`           | 0                 | —                  | —           | 2026-05-09     |
| `pr-from-branch`   | 0                 | —                  | —           | 2026-05-09     |

(Empty until first invocation.)

## Auto-evolve thresholds

Per `07-autoevolve.md`:

- `success_rate < 0.6` over 14d AND ≥ 5 invocations → propose deprecation.
- `last_validated > 14d` AND no invocation since → propose canonical
  experiment re-run.
- Three consecutive A/B losses → rewrite-from-scratch population spawn.

## Skill A/B verdict trail

```dataview
TABLE
  skill,
  arm,
  rubric,
  tokens
FROM "90-Meta"
WHERE file.name = "metrics" AND axis = "skills"
SORT started DESC
LIMIT 20
```

## Cross-references

- `04_Harnesses/prompt-scorecard.md` — sibling, for prompts.
- `00_System/Skill Registry.md` — full skill registry.
- `02-skills-optimizer.md` — daily skill amend pass.
- `07-autoevolve.md` — weekly fitness pass.
