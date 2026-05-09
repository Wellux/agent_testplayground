# skills/ — Specialist roles per master spec

Eight SKILL.md files, one per specialist role the master spec
identified. Each is a Claude Code skill (charlie947 schema) that the
agent invokes when the user's ask matches its trigger phrases.

These are **specialist roles** — high-level personas Ralph can assume
to tackle specific kinds of work. The day-1 skills under
`vault-template/03_Skills/skill-template.md` and `seed/40-Skills/` are
narrower (per-action). The two complement each other.

## Roles

| Slug                            | When to invoke                                                       |
| ------------------------------- | -------------------------------------------------------------------- |
| `memory-architect`              | shaping the vault's typed-memory taxonomy / lifecycle rules          |
| `prompt-evaluator`              | scoring and rewriting prompts against the rubric                     |
| `obsidian-vault-engineer`       | vault structure, plugin integration, frontmatter migration           |
| `shell-safety-engineer`         | reviewing / hardening Bash scripts (allowlist, dry-run, locks)        |
| `business-ops-analyst`          | drafting workflows, ledger schemas, approval gates                   |
| `repo-migration-engineer`       | inventory / classify / propose migrations                            |
| `provider-adapter-designer`     | populating / activating provider adapter specs                       |
| `context-compression-engineer`  | designing compression strategies that preserve provenance            |

## Install

Per-project (Claude Code reads `.claude/skills/<name>.md` from cwd-up):

```bash
mkdir -p .claude/skills
ln -sfn "$REPO/prompts/ralph-meta-chain/skills"/*/SKILL.md .claude/skills/
```

Per-user:

```bash
mkdir -p ~/.claude/skills
for d in $REPO/prompts/ralph-meta-chain/skills/*/; do
  ln -sfn "$d/SKILL.md" "~/.claude/skills/$(basename "$d").md"
done
```

## File shape (each skill follows charlie947 / vault-template)

```yaml
---
name: <slug>
description: |
  Triggers: "<phrase 1>", "<phrase 2>"
when_to_use: |
  ...
inputs: [...]
steps: [...]
tools: [...]
failure_modes: [...]
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [...]
is_prerequisite_of: [...]
links: [...]
tags: [skill, specialist]
---

# <Title>

<role description; canonical experiment>
```

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Skills.
- `vault-template/03_Skills/skill-template.md` — generic template.
- `seed/40-Skills/recall.md`, `pr-from-branch.md` — day-1 narrow skills.
- `02-skills-optimizer.md` — how new skills get amended weekly.
