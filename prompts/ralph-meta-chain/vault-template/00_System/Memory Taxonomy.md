---
ralph_type: system
memory_layer: system
memory_temperature: hot
stability: canonical
created: 2026-05-09
summary: "Vault-side mirror of the memory-type / temperature / stability schema."
---

# Memory Taxonomy

Authoritative source: `docs/MEMORY_MODEL.md`. Lives here so the cron
prompts can `Read` it without grepping the repo.

## Types

| Type           | Where it lives                            |
| -------------- | ----------------------------------------- |
| raw            | `00-Inbox/` (Phase 1-6 path) / `01_Inbox/` |
| episodic       | `10-Daily/`                                |
| semantic       | `30-Notes/` / `02_Memory/semantic/`         |
| procedural     | `40-Skills/` / `02_Memory/procedural/`       |
| preference     | `60-Interactions/user-profile.md`          |
| interaction    | `60-Interactions/feedback-log.md`          |
| entity         | `30-Notes/` w/ `tag: #entity`              |
| project        | `30-Notes/` w/ `tag: #project`             |
| decision       | `30-Notes/` w/ `tag: #decision`            |
| business       | `business-entity/ledgers/` (Round 3+)      |
| research       | `00-Inbox/`-then-`30-Notes/`                |
| experiment     | `harness/fixtures/`, `90-Meta/metrics.ndjson` |
| system         | `90-Meta/`, this folder                     |
| canonical      | `30-Notes/` flagged stable                  |

## Temperatures

`hot` (active) → `warm` (useful, not always loaded) → `cold` (archived
but searchable) → `frozen` (provenance only).

Demotion windows in `config.yml`:
- hot: ≤ 7 days since last touch
- warm: ≤ 90 days
- cold: > 90 days
- frozen: explicit demotion only

## Stability

`volatile` → `provisional` → `stable` → `canonical` (source of truth) /
`deprecated` (don't use unless specifically needed).

`07-autoevolve` proposes deprecation when a skill's `success_rate < 0.6`
over 14d AND ≥ 5 invocations. Deprecation is HIGH-risk: never automatic.

## Frontmatter contract

Every Ralph-managed Markdown file uses (subset per type):

```yaml
ralph_type:        memory | skill | experiment | report | research | ...
memory_layer:      raw | episodic | semantic | procedural | ...
memory_temperature: hot | warm | cold | frozen
stability:         volatile | provisional | stable | canonical | deprecated
privacy:           private | work | client | public
provider:          claude-code | provider-neutral | ...-deferred
approval_required: true | false
status:            draft | proposed | approved | active | archived | deprecated
```

## Cross-references

- `docs/MEMORY_MODEL.md` — full schema + per-type extensions.
- `00_System/Memory Lifecycle.md` — pipeline (capture → archive).
- `00_System/Skill Registry.md` / `Prompt Registry.md` — typed indexes.
