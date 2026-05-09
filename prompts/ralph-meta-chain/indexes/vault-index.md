---
ralph_type: system
memory_layer: system
stability: canonical
created: 2026-05-09
status: template
generated_by: prompts/ralph-meta-chain/01-memory-optimizer.md
target: $VAULT/90-Meta/index.md
summary: "Karpathy LLM-Wiki index template. Categorized catalog with one-line summaries."
---

# Vault Index — TEMPLATE

This file is the **authoring source**. The cron memory pass at 02:00
UTC writes the live index at `$VAULT/90-Meta/index.md`. Both files
share this exact shape.

> Karpathy LLM-Wiki rule (mandatory): the index is a categorized
> catalog with **one-line summaries** per page. Updated on every ingest.

## Atomic notes

| Note                              | Tag(s)            | One-line summary                                |
| --------------------------------- | ----------------- | ----------------------------------------------- |
| `[[<id>-<slug>]]`                 | `#<tag>`          | (1 line)                                        |

## MOCs

| MOC                   | Tag         | Member count |
| --------------------- | ----------- | ------------ |
| `[[20-MOCs/<topic>]]` | `#<topic>`  | N            |

## Skills

| Skill                          | Status     | Last validated |
| ------------------------------ | ---------- | -------------- |
| `[[40-Skills/<slug>]]`          | active     | YYYY-MM-DD     |

## Prompts

| Prompt                          | Bin             | Last rewritten |
| ------------------------------- | --------------- | -------------- |
| `[[50-Prompts/<name>]]`          | terse-strict    | YYYY-MM-DD     |

## Hypotheses (open)

| Hypothesis                        | Axis     | Created    |
| --------------------------------- | -------- | ---------- |
| `[[<id>-hypothesis-<topic>]]`      | <axis>   | YYYY-MM-DD |

## Research dumps

| Date       | Source           | New / Total |
| ---------- | ---------------- | ----------- |
| YYYY-MM-DD | trending         | N / N       |
| YYYY-MM-DD | futuretools      | N / N       |
| YYYY-MM-DD | creators         | N / N       |

## Compressed (this week)

| Note                              | Tokens before → after | Ratio |
| --------------------------------- | --------------------- | ----- |
| `[[<id>]]`                         | N → N                 | x.xx  |

## Cron status (last successful run per axis)

| Axis        | Last run    | Status   |
| ----------- | ----------- | -------- |
| research    | YYYY-MM-DD  | COMPLETE |
| memory      | YYYY-MM-DD  | COMPLETE |
| skills      | YYYY-MM-DD  | COMPLETE |
| interaction | YYYY-MM-DD  | COMPLETE |
| compress    | YYYY-MM-DD HH | COMPLETE |
| heal        | YYYY-MM-DD HH | COMPLETE |
| evolve      | YYYY-MM-DD  | COMPLETE |
| update      | YYYY-MM-DD  | COMPLETE |

## Cross-references

- `docs/MEMORY_MODEL.md` § Memory pipeline.
- `00_System/Memory Lifecycle.md`.
- `90-Meta/log.md` — append-only audit trail (this index summarizes it).
