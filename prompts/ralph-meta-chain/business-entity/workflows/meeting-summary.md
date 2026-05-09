---
ralph_type: business
memory_layer: business
risk_class_default: LOW
created: 2026-05-09
status: scaffold
summary: "Summarize a meeting transcript. Internal-only."
---

# Meeting Summary

Takes a transcript (text in inbox or a captured voice note) and
produces a structured summary: decisions, action items, open
questions.

## Purpose

Replace ad-hoc note-taking with a consistent template the user can
forward to participants if they choose (forwarding is CRITICAL —
never autonomous; the user copy-pastes from the resulting Markdown).

## Inputs

- transcript (text in `00-Inbox/voice-<UTC>.md` or `01_Inbox/Daily Capture.md`)
- optional: meeting context (project, counterparty, prior discussion
  pointers)

## Process

1. Read transcript.
2. Extract: decisions (≤ 5), action items (with owner + due date),
   open questions (≤ 5).
3. Identify any new commitments mentioned. Cross-list each in
   `ledgers/commitments.md` with `status: drafted` (the user confirms
   them later).
4. Write summary to
   `business-entity/clients/<slug>/meetings/<YYYY-MM-DD>-<topic>.md`
   (or `30-Notes/<id>-meeting-<topic>.md` if not client-specific).
5. Tag the original transcript `#meeting` so the memory pass promotes
   it correctly.

## Outputs

- meeting summary Markdown.
- `ledgers/commitments.md` (append per new commitment).

## Approval gates

| Step | Class | Gate                                      |
| ---- | ----- | ----------------------------------------- |
| 1-2  | LOW    | always allowed                              |
| 3    | MEDIUM | proposal-first per commitment               |
| 4-5  | LOW    | internal note                                |
| —    | CRITICAL | forwarding to participants is NEVER autonomous |

## Risk notes

- **Misattribution**: a quote attributed to the wrong speaker is
  reputational risk. Mitigation: Ralph cites the transcript line
  number + speaker label, and flags any quote where the speaker is
  ambiguous as `(uncertain attribution)`.
- **Hallucinated commitments**: LLMs sometimes invent specifics not
  said. Mitigation: every commitment in the summary cross-references
  the transcript line range.
- **Confidentiality**: meetings may include confidential material.
  Frontmatter `privacy: client` (or `private`) by default.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| summary drafted                           | (no ledger; summary IS the artifact)     |
| commitment identified                     | `ledgers/commitments.md` (drafted)       |
| user forwards to participants             | `ledgers/external-communications.md` AND `ledgers/audit-log.md` (the user logs this manually) |

## Example output (excerpt)

```markdown
# Meeting — Acme Corp · 2026-05-09 · "doc sprint kickoff"

## Decisions
1. Sprint 1 covers internal API docs (line 12-18; speaker: VP Eng).
2. Acceptance criteria: 80% endpoint coverage (line 24; speaker: Owner).

## Action items
- [ ] Owner: send acceptance-criteria checklist by 2026-05-15.
- [ ] VP Eng: provide API endpoint list by 2026-05-12.

## Open questions
- Tax handling for cross-border invoicing?
- Should we include OpenAPI spec generation?

## Commitments identified
- "Sprint 1 deliverable by 2026-05-22" → drafted in
  `ledgers/commitments.md` as `meeting-2026-05-09-acme-001`.

## Provenance
- Source transcript: `[[voice-20260509T140000Z]]`
- Lines cited: 12-18, 24, 41-44
```

## Cross-references

- `templates/meeting-summary-template.md` — output shape.
- `workflows/lead-intake.md` — when meeting introduces a new lead.
- `workflows/client-follow-up.md` — when a meeting commitment ages.
- `ledgers/commitments.md`.

## Next actions

- Read every cited transcript line range. Confirm attribution. Confirm
  no commitments were invented.
- Then either copy-paste relevant sections into your email tool to
  send to participants, or leave the summary as internal record.
