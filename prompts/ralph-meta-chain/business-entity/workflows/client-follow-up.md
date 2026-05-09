---
ralph_type: business
memory_layer: business
risk_class_default: MEDIUM
created: 2026-05-09
status: scaffold
summary: "Draft client follow-up messages. Send is CRITICAL and never autonomous."
---

# Client Follow-up

Drafts a follow-up message for a stalled engagement. Never sends.

## Purpose

When a commitment in `ledgers/commitments.md` has `due_date` past or
approaching with no movement, draft a one-paragraph follow-up the user
can finalize and send.

## Inputs

- `ledgers/commitments.md` (filtered by `audience: external` and
  `due_date <= today + 7d`)
- `business-entity/clients/<slug>/brief.md` (tone + relationship)
- `vault-template/00_System/Interaction Preferences.md`
- optional: prior follow-ups in `ledgers/external-communications.md`

## Process

1. Identify stale external commitments (due_date past or near).
2. Per commitment: draft 1-3 sentences acknowledging timeline + a
   single concrete next step.
3. Save draft to
   `business-entity/clients/<slug>/follow-ups/<YYYY-MM-DD>-<topic>.md`.
4. Append HIGH approval to `ledgers/pending-approvals.md`.
5. Refuse to send.

## Outputs

- follow-up draft Markdown.
- pending-approval entry.

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-3  | MEDIUM    | proposal-first                                     |
| 4    | HIGH      | explicit user approval                              |
| 5    | CRITICAL  | external send NEVER autonomous                     |

## Risk notes

- **Tone overshoots**: a "gentle nudge" can read as pressure. Mitigation:
  Ralph never writes anxious / pressuring language; the rubric scores
  follow-up drafts on (politeness × clarity × brevity).
- **Wrong recipient**: counterparty pulled from the brief; if the brief
  is stale, the follow-up may target an outdated contact. Mitigation:
  Ralph cross-checks against the most-recent
  `ledgers/external-communications.md` entry per counterparty.
- **Missed acknowledgment**: a commitment marked stale might already be
  fulfilled in a thread Ralph hasn't seen. Mitigation: the draft says
  "I haven't heard back since X — please confirm" rather than asserting
  no progress.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| follow-up drafted                         | (no ledger; the draft is its own artifact) |
| approval requested                        | `ledgers/pending-approvals.md`           |
| approval granted                          | `ledgers/decisions.md`                    |
| external send happens                    | `ledgers/external-communications.md` AND `ledgers/audit-log.md` |

## Example output (draft)

```markdown
# Follow-up — Acme Corp · 2026-05-09 · "doc sprint timeline"

Hi <name>,

Following up on our doc sprint timeline (last touched 2026-04-25).
The proposed start was 2026-05-15; could you confirm whether that
still works on your side?

Happy to adjust if priorities shifted.

Best,
<user>
```

## Cross-references

- `workflows/proposal-drafting.md` — typical upstream.
- `workflows/meeting-summary.md` — adjacent.
- `ledgers/commitments.md` — what triggers follow-ups.
- `ledgers/external-communications.md` — outbound trail.

## Next actions

- Review draft tone. The user's preferences live in Interaction
  Preferences and update daily — make sure the draft sounds like you.
- After approval: copy-paste into your email tool. Ralph never has
  email access.
