---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Index of every skill in 40-Skills/ with metric snapshots."
---

# Skill Registry

The single page that summarizes every skill in `40-Skills/`. The
`02-skills-optimizer` cron updates this index after each pass.

## Active skills

| Slug                   | Last validated | Invocations | Success rate | Status   | Tags                |
| ---------------------- | -------------- | ----------- | ------------ | -------- | ------------------- |
| `recall`               | 2026-05-09     | 0           | —            | active   | retrieval, voyager  |
| `pr-from-branch`       | 2026-05-09     | 0           | —            | active   | github, pr          |

(Day-1 seeds. The skills cron writes to this table.)

## Voyager prerequisite chain

```
recall  ──prerequisite_of──►  pr-from-branch
```

When proposing new skills, sort by prerequisite depth (simple → complex)
and add `prerequisites:` / `is_prerequisite_of:` frontmatter explicitly.
This makes the chain a curriculum rather than a flat bag of tricks.

## Deprecated skills

(none yet)

## Schema reminder

```yaml
---
name: <slug>
description: |
  Triggers: "...", "..."
when_to_use: ...
inputs: [...]
steps: [...]
tools: ["Bash(...)", ...]
failure_modes: [...]
last_validated: <YYYY-MM-DD>
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []
is_prerequisite_of: []
links: []
tags: [skill]
---
```

## Cross-references

- `40-Skills/` — actual skill files.
- `seed/40-Skills/` — day-1 seeds.
- `docs/CLAUDE_CODE_INTEGRATION.md` § Skills — schema rationale.
- `02-skills-optimizer.md` — how skills get amended weekly.
- `07-autoevolve.md` — when skills get deprecation proposals.
