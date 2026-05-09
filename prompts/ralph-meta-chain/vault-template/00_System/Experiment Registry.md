---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Index of fixtures, A/B runs, and metric trends."
---

# Experiment Registry

The single page summarizing every A/B fixture, its history, and current
verdicts.

## Fixtures

| Fixture                                | Cases | Last run    | Current incumbent              | Survivors per bin |
| -------------------------------------- | ----- | ----------- | ------------------------------ | ----------------- |
| `harness/fixtures/code-review.yml`     | 2     | not yet     | `50-Prompts/code-review.md`    | 1 (terse-strict)  |
| `harness/fixtures/daily-summary.yml`   | 2     | not yet     | `50-Prompts/daily-summary.md`  | 1 (terse-strict)  |

## Recent A/B verdicts

(empty — populated by `03-interaction-optimizer.md` after the first run)

## Open hypotheses

(populated by `02-skills-optimizer.md` and `07-autoevolve.md`)

## Metric trends (last 60 days)

The Obsidian plugin's metrics view renders SVG sparklines from
`90-Meta/metrics.ndjson`. CLI equivalent: `harness traces --tail 200`.

## Schema reminder

```yaml
# Fixture file (promptfoo-shaped)
description: <fixture name>
prompts:
  - file://<path-to-incumbent.md>
tests:
  - description: <case>
    vars:
      <var>: |
        <input>
    assert:
      - { type: max-tokens, value: 600 }
      - { type: not-contains, value: "Great question" }
      - { type: contains, value: "<expected>" }
```

```json
// metrics.ndjson row
{"axis":"interaction","fixture":"code-review","started":"<ISO>",
 "incumbent_path":"...","candidate_path":"...","model":"claude-sonnet-4-6",
 "judge_model":"...","arm":"incumbent|candidate","tokens":420,
 "rubric":4.2,"banned":0,"latency":3.1}
```

## Cross-references

- `docs/AB_HARNESS.md` — fixture format + scoring + verdict rule + MAP-Elites.
- `harness/fixtures/` — fixture files.
- `90-Meta/metrics.ndjson` — raw experiment log.
- `harness traces` — CLI summary.
- `00_System/Prompt Registry.md` — bin grid.
