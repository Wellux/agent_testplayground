---
ralph_type: system
memory_layer: system
created: 2026-05-09
status: template
generated_by: prompts/ralph-meta-chain/02-skills-optimizer.md
target: $VAULT/00_System/Skill Registry.md
summary: "Skills index template — Voyager curriculum + per-skill metrics."
---

# Skill Index — TEMPLATE

The cron skills pass writes the live registry at
`$VAULT/00_System/Skill Registry.md`. This file is the schema authority.

## Active skills

| Slug                    | Last validated | Invocations | Success rate | Status   | Tags          |
| ----------------------- | -------------- | ----------- | ------------ | -------- | ------------- |
| `[[40-Skills/<slug>]]`  | YYYY-MM-DD     | N           | 0.0–1.0      | active   | `#<tag>`      |

## Voyager curriculum (prerequisite chain)

```
recall  ──prerequisite_of──►  pr-from-branch
                              │
                              └──prerequisite_of──►  ...
```

(Render as a flat list when there's no DAG visualization available.)

## MAP-Elites bins (per skill amend cycle)

| Bin               | Skill            | Survivor file                                  |
| ----------------- | ---------------- | ---------------------------------------------- |
| terse-strict      | `<slug>`          | `[[40-Skills/_population/<slug>/terse-strict]]` |
| medium-loose      | `<slug>`          | ...                                            |

(One row per (skill × bin). Per `02-skills-optimizer.md` step 4 §
MAP-Elites.)

## Recently amended (last 7 days)

| Slug              | Date amended | Outcome                |
| ----------------- | ------------ | ---------------------- |
| `<slug>`          | YYYY-MM-DD   | candidate-wins / tie / refuted |

## Deprecated (never deleted)

| Slug              | Deprecated on | Reason                 |
| ----------------- | ------------- | ---------------------- |
| `<slug>`          | YYYY-MM-DD    | success_rate < 0.6 (14d, 5+ inv) |

## Open hypotheses (axis: skills)

| Hypothesis                      | Created    | Cheap to test? |
| ------------------------------- | ---------- | -------------- |
| `[[<id>-hypothesis-<topic>]]`    | YYYY-MM-DD | yes / no       |

## Cross-references

- `vault-template/00_System/Skill Registry.md` — vault-side mirror.
- `prompts/ralph-meta-chain/02-skills-optimizer.md` — daily writer.
- `prompts/ralph-meta-chain/07-autoevolve.md` — weekly fitness pass.
- `seed/40-Skills/recall.md`, `pr-from-branch.md` — day-1 seeds.
- `skills/` (Round 6) — 8 specialist roles.
