---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Index of every prompt in 50-Prompts/ + their A/B history."
---

# Prompt Registry

Active prompts the `interaction-optimizer` cron may A/B-test, plus their
MAP-Elites bin and accumulated Reflexion lessons.

## Active prompts

| Name              | Last rewritten | Bin             | Validated against              | A/B wins / losses | Reflections |
| ----------------- | -------------- | --------------- | ------------------------------ | ----------------- | ----------- |
| `code-review`     | 2026-05-09     | terse-strict    | `harness/fixtures/code-review.yml` | 0 / 0           | 0           |
| `daily-summary`   | 2026-05-09     | terse-strict    | `harness/fixtures/daily-summary.yml` | 0 / 0          | 0           |

(Day-1 seeds. The interaction cron writes to this table after each A/B.)

## MAP-Elites grid

GEPA's diversity heuristic. Each candidate carries `bin: "<axis>"` in
frontmatter. Default geometry: `(token-cost) × (format-strictness)`,
nine cells.

|              | loose | medium | strict |
| ------------ | ----- | ------ | ------ |
| **terse**    |       |        | × code-review, daily-summary |
| **medium**   |       |        |        |
| **verbose**  |       |        |        |

Cells with `×` have at least one survivor. Empty cells are open
territory for autoevolve to spawn into.

## Schema reminder

```yaml
---
name: <slug>
last_rewritten: <YYYY-MM-DD>
validated_against: ["harness/fixtures/<name>.yml"]
bin: <token-cost>-<format-strictness>
reflections:
  - "[YYYY-MM-DD] <one-line lesson, ≤ 80 chars>"
---
```

## Population (per-prompt survivors)

`50-Prompts/_population/<name>/<bin>.md` holds the per-bin best so
autoevolve can recombine them later.

## Rejected prompts

`50-Prompts/_rejected/<name>-<date>.md` — losing candidates archived
for forensic review. Never deleted (per Operating Principles rule 2).

## Cross-references

- `50-Prompts/` — actual prompt files.
- `seed/50-Prompts/` — day-1 seeds.
- `docs/AB_HARNESS.md` — fixture format + scoring + verdict rule.
- `03-interaction-optimizer.md` — A/B daily.
- `07-autoevolve.md` — population spawn + rewrite proposals.
- `harness reflect --candidate <path>` — Reflexion lesson loop.
