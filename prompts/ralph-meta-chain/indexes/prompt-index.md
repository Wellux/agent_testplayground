---
ralph_type: system
memory_layer: system
created: 2026-05-09
status: template
generated_by: prompts/ralph-meta-chain/03-interaction-optimizer.md
target: $VAULT/00_System/Prompt Registry.md
summary: "Prompt registry index — A/B history + MAP-Elites grid + Reflexion lessons."
---

# Prompt Index — TEMPLATE

The interaction-optimizer cron writes the live registry at
`$VAULT/00_System/Prompt Registry.md`. This file is the schema authority.

## Active prompts

| Name              | Last rewritten | Bin             | Validated against              | A/B wins / losses (30d) | Reflections |
| ----------------- | -------------- | --------------- | ------------------------------ | ----------------------- | ----------- |
| `[[50-Prompts/<name>]]` | YYYY-MM-DD | terse-strict    | `harness/fixtures/<name>.yml`  | W / L                   | N           |

## MAP-Elites grid

|                | loose                                  | medium                                  | strict                                  |
| -------------- | -------------------------------------- | --------------------------------------- | --------------------------------------- |
| **terse**      | `[[<name>@terse-loose]]` ?              | ...                                     | × current incumbent                     |
| **medium**     | ...                                    | ...                                     | ...                                     |
| **verbose**    | ...                                    | ...                                     | ...                                     |

Cells with `×` have at least one survivor. Per `docs/AB_HARNESS.md` §
MAP-Elites. Empty cells are open territory for `07-autoevolve` to spawn into.

## Population (per-prompt survivors)

`50-Prompts/_population/<name>/<bin>.md` holds the per-bin best so
autoevolve can recombine them later.

## Recent A/B verdicts

| Date       | Prompt           | Fixture              | Verdict           |
| ---------- | ---------------- | -------------------- | ----------------- |
| YYYY-MM-DD | `<name>`          | `<fixture>.yml`       | candidate-wins / tie / incumbent-wins |

## Reflexion lessons (last 14 days)

| Prompt           | Lesson                                              |
| ---------------- | --------------------------------------------------- |
| `<name>`          | "[YYYY-MM-DD] preamble killed terse rubric (-0.4)" |

(Aggregated from `50-Prompts/<name>.candidate-N.md` frontmatter
`reflections:` lists.)

## Rejected prompts (`50-Prompts/_rejected/`)

| File                                | Lost on    | Reason                       |
| ----------------------------------- | ---------- | ---------------------------- |
| `<name>-<date>.md`                   | YYYY-MM-DD | A/B loss × 3 / tie × 5       |

## Cross-references

- `vault-template/00_System/Prompt Registry.md` — vault-side mirror.
- `prompts/ralph-meta-chain/03-interaction-optimizer.md` — daily A/B + writer.
- `prompts/ralph-meta-chain/07-autoevolve.md` — weekly population spawn.
- `harness/harness/{ab,reflect,traces}.py`.
- `harness/fixtures/code-review.yml`, `daily-summary.yml`.
- `benchmarks/prompt-quality.md` — rubric + thresholds.
