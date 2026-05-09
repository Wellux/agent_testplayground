---
description: |
  Triggers: "ralph skill", "make this a skill", "propose a skill from this note",
  "generate skill"
allowed-tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Bash(grep:*,find:*)"
---

# /ralph-skill

Propose a new Claude Code skill from the currently-open note (or from
`$ARGUMENTS` if a path is supplied). MEDIUM risk: writes a draft to
`$VAULT/40-Skills/<slug>.candidate.md`; does NOT promote to incumbent.

## Inputs

`$ARGUMENTS` — optional. If a path is provided, read that note.
Otherwise read the active editor file via the Read tool.

## Process

1. Read the source note (frontmatter + body).
2. Identify the recurring action it describes:
   - `When` does this skill fire?
   - `Inputs` — what data does it need?
   - `Steps` — concrete sequence?
   - `Tools` — which Claude Code tools or shims?
   - `Failure modes` — what could go wrong?
3. Choose a slug: snake-case verb-object (e.g. `pr-from-branch`).
4. Map prerequisites (Voyager curriculum):
   - Which existing skills must run first? Add to `prerequisites:`.
   - Which future skills will build on this? Add to `is_prerequisite_of:`.
5. Render `$VAULT/40-Skills/<slug>.candidate.md` per
   `vault-template/03_Skills/skill-template.md`.
6. Append a one-line entry to `$VAULT/06_Reports/daily-skills-report.md`.

## Output

Print a one-paragraph summary of the proposed skill + the path to
the new candidate file. Do NOT auto-apply; promotion to incumbent
goes through `02-skills-optimizer.md`'s weekly population A/B.

## Safety

- MEDIUM risk: writes a draft. The user reviews before any
  `last_validated:` flip.
- Refuse if the source note has no clear "Steps" structure (ambiguous
  delegation) — emit a Notice asking the user to add a Steps section
  first.

## Cross-references

- `vault-template/03_Skills/skill-template.md`
- `prompts/ralph-meta-chain/02-skills-optimizer.md` § Step 4½ —
  Voyager curriculum.
- `vault-template/00_System/Skill Registry.md`
