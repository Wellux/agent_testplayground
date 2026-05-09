---
ralph_type: provider
provider: claude-code
created: 2026-05-09
status: scaffold
summary: "Claude Code skills surface — schema + Voyager curriculum."
---

# Claude Code Skills

Skills are reusable procedural memories. The Phase 1-6 reference
implementation already ships day-1 seeds (`seed/40-Skills/recall.md`,
`pr-from-branch.md`); this file documents the canonical schema and
the Voyager curriculum constraints.

## File location

- **Vault-local skills**: `$VAULT/40-Skills/<slug>.md` (the chain
  reads/writes here daily).
- **Project-scoped skills** (per Anthropic spec):
  `.claude/skills/<slug>.md`.
- **Day-1 seeds** (shipped): `seed/40-Skills/<slug>.md` (`cp -n`'d on
  install).

## Frontmatter schema (charlie947 / ai-second-brain)

```yaml
---
name: <slug>
description: |
  Triggers: "<phrase 1>", "<phrase 2>", "<phrase 3>"
when_to_use: |
  Brief description of when this skill is appropriate.
inputs:
  - input_name: type / default / description
steps:
  - "1. ..."
  - "2. ..."
tools:
  - "Bash(cmd1:*,cmd2:*)"
  - "mcp__github__create_pull_request"
failure_modes:
  - condition → response
last_validated: <YYYY-MM-DD>
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []                 # Voyager: skills this skill depends on
is_prerequisite_of: []             # Voyager: skills that depend on this one
links: []
tags: [skill, ...]
---
```

## Voyager curriculum

When `02-skills-optimizer.md` proposes new skills, it sorts them by
prerequisite depth:

```
recall  ──prerequisite_of──►  pr-from-branch
                              │
                              └──prerequisite_of──►  release-notes (future)
```

A skill with `prerequisites: [other]` lands AFTER its prerequisite is
already in the registry. This produces a curriculum the agent can rely
on instead of re-deriving foundations every pass.

## MAP-Elites bin (per skill amend cycle)

When the skills-optimizer amends a stale skill, it spawns 3 candidates
along different evolutionary axes (token-cost / format-strictness /
trigger-coverage). Per `docs/AB_HARNESS.md` § MAP-Elites, the chain
keeps the best per-bin survivor in
`40-Skills/_population/<slug>/<bin>.md`.

## Reflexion lessons (per skill A/B)

After each `harness ab` run on a skill candidate, `harness reflect`
appends a one-line lesson to the candidate's `reflections:` frontmatter:

```yaml
reflections:
  - "[2026-05-09] preamble killed terse rubric (-0.4)"
  - "[2026-05-12] missing format header dropped score (-0.3)"
```

Three same-flavor lessons → free re-rewrite next pass.

## Day-1 shipped skills

| Slug              | Purpose                                                 | Voyager position          |
| ----------------- | ------------------------------------------------------- | ------------------------- |
| `recall`          | semantic retrieval via `harness query`                   | foundation (no prereqs)   |
| `pr-from-branch`  | open a draft GitHub PR from the current branch          | depends on `recall`       |

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Skills.
- `02-skills-optimizer.md` — daily skill amend pass.
- `seed/40-Skills/recall.md`, `seed/40-Skills/pr-from-branch.md`.
- `vault-template/00_System/Skill Registry.md` — index.
- `vault-template/03_Skills/skill-template.md` — blank template.

## Next actions

- Read `seed/40-Skills/recall.md` for a worked example.
- New skills should follow the Voyager curriculum: pick a prereq;
  document `is_prerequisite_of` if applicable.
