---
ralph_type: report
memory_layer: report
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Daily skills-pass output: new, amended, deprecated, A/B verdicts."
---

# Daily Skills Report

Updated every day by `02-skills-optimizer.md` at 03:00 UTC.

## Today's pass

| Metric              | Count |
| ------------------- | ----- |
| New skills          | —     |
| Amended skills      | —     |
| Validated           | —     |
| Refuted             | —     |
| Hypotheses opened   | —     |
| Population spawned  | —     |

## New skills

(`[[wikilinks]]` to `40-Skills/<slug>.md` for any skills created today)

## Amended skills

(`[[wikilinks]]` for any whose `last_validated` was bumped)

## Failing canonical experiments

(skills whose canonical experiment failed today; they get auto-flagged
for autoevolve next Sunday)

## Cross-references

- `02-skills-optimizer.md` — the source cron prompt.
- `00_System/Skill Registry.md` — the index.
- `04_Harnesses/workflow-scorecard.md` — rolling success rates.
- `90-Meta/log.md` — the line: `## [<YYYY-MM-DD>] skills | new=N ...`
