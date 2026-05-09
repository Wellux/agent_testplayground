---
ralph_type: business
memory_layer: business
risk_class_default: LOW
created: 2026-05-09
status: scaffold
summary: "Draft a task delegation note. Internal-only; the user assigns."
---

# Task Delegation

Drafts a task delegation note when the user wants to hand off work to
a contractor / colleague / future-self. Internal only.

## Purpose

Standardize the way work gets handed off so it's traceable and
reviewable. Per the master spec, "hire or fire" is NEVER autonomous —
this workflow only drafts the task description, never assigns
contracts or approves payments.

## Inputs

- task description (free text from inbox)
- delegator (user)
- proposed delegate (name OR placeholder if hiring)
- timeline + acceptance criteria
- compensation context (link to existing engagement; never new
  payment authorization)

## Process

1. Read the task description.
2. Apply `templates/task-delegation-template.md` shape.
3. Fill: scope, acceptance criteria, deadline, dependencies, risks,
   handoff artifacts.
4. Save the draft to
   `business-entity/clients/<slug>/delegations/<YYYY-MM-DD>-<topic>.md`
   (or `30-Notes/<id>-delegation-<topic>.md` if not client-specific).
5. Append to `ledgers/commitments.md` (status: drafted) since
   delegating creates a downstream commitment.
6. If the delegate is external + paid, append HIGH approval to
   `ledgers/pending-approvals.md`.
7. Refuse to send the delegation externally.

## Outputs

- task delegation Markdown draft.
- `ledgers/commitments.md` (append, drafted).
- `ledgers/pending-approvals.md` (append IF external + paid).

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-5  | LOW      | internal note                                       |
| 5    | MEDIUM   | commitment-ledger append                            |
| 6    | HIGH     | external paid delegation needs approval             |
| 7    | CRITICAL | sending externally is NEVER autonomous              |
| —    | CRITICAL | "Hire or fire" is NEVER autonomous                   |

## Risk notes

- **Scope creep**: an under-specified delegation creates rework. The
  rubric scores delegation drafts on (specificity × testability ×
  brevity).
- **Confidentiality**: delegations may include client material
  (`privacy: client`). The draft frontmatter inherits the client's
  privacy class.
- **Compensation ambiguity**: Ralph never proposes new payment terms.
  The user provides compensation context; Ralph echoes it.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| delegation drafted                        | `ledgers/commitments.md` (drafted)        |
| approval requested (external + paid)      | `ledgers/pending-approvals.md`           |
| approval granted                          | `ledgers/decisions.md`                    |
| handoff happens (user sends externally)   | `ledgers/external-communications.md` AND `ledgers/audit-log.md` (user logs manually) |

## Example output (excerpt)

```markdown
# Delegation — review draft API docs · 2026-05-09

## Delegate
- Name: <future-self / contractor name>
- Compensation: existing engagement (no new authorization)

## Scope
Review `deliverables/sprint-1-doc.md` for technical accuracy + clarity.

## Acceptance criteria
1. Every endpoint description matches the implementation.
2. No spelling / grammar errors per `aspell`.
3. Tone consistent with the rest of the document set.

## Deadline
2026-05-15 EOD <user's TZ>

## Dependencies
- Access to internal API: <pointer to credentials note (NOT included
  in this draft)>

## Risks
- Unclear scope on edge-case endpoints (lines 84-101). Flag uncertainty
  in line comments.

## Handoff artifacts
- `deliverables/sprint-1-doc.md`
- API endpoint list: `[[<note-id>]]`

## Acknowledgment
The delegate confirms scope by replying to the handoff message with
"acknowledged".
```

## Cross-references

- `templates/task-delegation-template.md` — output shape.
- `workflows/knowledge-work-delivery.md` — adjacent.
- `ledgers/commitments.md` — the delegation IS a commitment.

## Next actions

- After Ralph drafts: review the acceptance criteria. Vague criteria
  = rework. Tighten before handoff.
- Ralph never sends the handoff. Use your existing comms tool.
