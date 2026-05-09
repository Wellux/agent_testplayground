---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: scaffold
summary: "Repo inventory — populated by `harness migration inventory` (Round 4+)."
---

# Inventory Report

> **Round 4+ scaffold.** Until then, this file is empty. Run
> `harness migration inventory` (Round 4+) to populate it.

## Generated header

```yaml
---
generated: <ISO_TS>
total_files: <N>
classes:
  ralph-core: <N>
  prompts: <N>
  scripts: <N>
  docs: <N>
  research: <N>
  experiments: <N>
  memory: <N>
  skills: <N>
  provider-adapters: <N>
  business-entity: <N>
  migration: <N>
  archive: <N>
  unrelated: <N>
  unknown: <N>
---
```

## Classes (per `docs/REPO_MIGRATION.md`)

- `ralph-core` — prompts, harness, voice-server, plugin, scripts.
- `prompts` — anything matching `*ralph*` or under `prompts/`.
- `scripts` — `scripts/`, `*.sh`.
- `docs` — `*.md` outside the above.
- `research` — `RESEARCH_*`, `research/`.
- `experiments` — `experiments/`, `harness/fixtures/`.
- `memory` — Markdown with `ralph_type: memory` frontmatter.
- `skills` — Markdown with `ralph_type: skill`.
- `provider-adapters` — `providers/`.
- `business-entity` — `business-entity/`.
- `migration` — `migration/`.
- `archive` — `_archive/`, `_processed/`, `_rejected/`.
- `unrelated` — clearly outside Ralph scope.
- `unknown` — couldn't classify; manual review required.

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `00_System/Repo Migration Control Panel.md` — dashboard.
- `09_Migration/proposed-moves.md` — next step after inventory.
