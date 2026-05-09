---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "User-style preferences distilled from feedback signals — read by every prompt."
---

# Interaction Preferences

Hot-loaded by every prompt firing. The `interaction-optimizer` cron
maintains this from `60-Interactions/feedback-log.md`.

> This is the operational copy. The append-only source of truth is
> `60-Interactions/user-profile.md` — every Ralph pass adds a
> `## Ralph YYYY-MM-DD` section there. This file is the **most-recent
> snapshot**, kept thin so prompts don't drag history into context.

## Tone

- Prefer terse over verbose.
- No preambles ("Great question", "Certainly", "I'd be happy to", "As an AI").
- Cite evidence inline; don't summarize the prompt back at the user.

## Format

- Code blocks for any output ≥ 2 lines of code.
- Bulleted lists where structure helps; prose where it doesn't.
- File paths as `path/to/file:line` so the user can click to navigate.

## Dislikes

- Editorializing about the user's project.
- "Let me break this down" / "Let's explore".
- Restating what was just asked.

## Recurring asks

- "summarize this PR"
- "explain trade-offs"
- "what changed since last week"
- "draft a follow-up"
- "review this diff"

## How this gets updated

`03-interaction-optimizer.md` reads the trailing 7 days of
`feedback-log.md`, appends distilled signals to `user-profile.md`,
then **rewrites this file** as a thin operational snapshot. The
operational copy never accumulates history; the SOT does.

## Cross-references

- `60-Interactions/user-profile.md` — full append-only history.
- `60-Interactions/feedback-log.md` — raw signals.
- `03-interaction-optimizer.md` — the maintainer.
- `docs/AB_HARNESS.md` — how preferences become rubric weights.
