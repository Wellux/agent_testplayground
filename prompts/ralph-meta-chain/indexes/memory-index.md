---
ralph_type: system
memory_layer: system
created: 2026-05-09
status: template
generated_by: prompts/ralph-meta-chain/01-memory-optimizer.md
summary: "Memory-specific subset of vault-index.md, grouped by typed-memory layer."
---

# Memory Index — TEMPLATE

Same data as `vault-index.md`'s "Atomic notes" + "MOCs" sections, but
sliced by `memory_layer` for navigation.

## raw

| Note                          | Created    | Source              |
| ----------------------------- | ---------- | ------------------- |
| `[[00-Inbox/<file>]]`          | YYYY-MM-DD | manual / voice / cron |

## episodic (daily notes)

| Daily                          | Status        |
| ------------------------------ | ------------- |
| `[[10-Daily/<date>]]`           | active / rolled |

## semantic (atomic notes)

| Note                              | Tags              | Inbound links |
| --------------------------------- | ----------------- | ------------- |
| `[[30-Notes/<id>-<slug>]]`         | `#<tag>`           | N             |

## procedural (skills)

See `indexes/skill-index.md`.

## preference

| File                                  | Last touch  |
| ------------------------------------- | ----------- |
| `[[60-Interactions/user-profile]]`     | YYYY-MM-DD  |

## interaction

| File                                  | Last entry   |
| ------------------------------------- | ------------ |
| `[[60-Interactions/feedback-log]]`     | YYYY-MM-DD   |

## entity / project / decision (tagged)

(`#entity`, `#project`, `#decision` rows from `30-Notes/`)

## business

See `indexes/business-index.md` (and the `business-entity/ledgers/`
folder).

## research / experiment

| Date       | Source / fixture            | Notes generated |
| ---------- | --------------------------- | --------------- |
| YYYY-MM-DD | trending / fixture-name     | N               |

## system / canonical

| File                                  | Stability   |
| ------------------------------------- | ----------- |
| `[[CLAUDE.md]]`                        | canonical   |
| `[[00_System/Memory Taxonomy]]`         | canonical   |

## Cross-references

- `docs/MEMORY_MODEL.md` — type taxonomy.
- `vault-template/02_Memory/` — typed buckets.
- `indexes/vault-index.md` — composite view.
