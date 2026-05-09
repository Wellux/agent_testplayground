---
ralph_type: business
memory_layer: business
risk_class_default: MEDIUM
created: 2026-05-09
status: scaffold
summary: "Package and check deliverables for a client engagement."
---

# Knowledge Work Delivery

Wraps the act of "we're ready to ship the deliverable to the client".
Packages files, runs internal checks, and produces a delivery checklist.

## Purpose

When a piece of contracted work is ready, produce:
- a delivery checklist (markdown),
- a manifest of files (paths, sizes, timestamps),
- an internal QA pass (broken-link / spelling / tone-rubric scan),
- a draft cover note for sending alongside the deliverable.

The actual sending is CRITICAL and never autonomous.

## Inputs

- `business-entity/clients/<slug>/deliverables/`
- `business-entity/clients/<slug>/proposal.md` (scope reference)
- `ledgers/commitments.md` (what was committed)

## Process

1. Build manifest: list every file in `deliverables/` with size + mtime.
2. Cross-check manifest against `commitments.md`: every committed
   deliverable present? flag missing as ERROR.
3. QA pass:
   - broken `[[wikilinks]]`?
   - spelling (best-effort; uses `aspell` if installed; skipped otherwise)
   - tone rubric per `04_Harnesses/eval-rubric.md` against the deliverable
4. Draft cover note (1-2 paragraphs) using
   `templates/client-brief-template.md` shape inverted.
5. Render delivery checklist at
   `business-entity/clients/<slug>/delivery-<YYYY-MM-DD>.md`.
6. Append HIGH approval to `ledgers/pending-approvals.md`.
7. Refuse to send.

## Outputs

- delivery-<YYYY-MM-DD>.md (manifest + QA + checklist + cover draft).
- pending-approval entry.

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-5  | MEDIUM    | proposal-first                                     |
| 6    | HIGH      | explicit user approval                              |
| 7    | CRITICAL  | external send NEVER autonomous                     |

## Risk notes

- **Scope mismatch**: a missed deliverable is worse than an extra one.
  ERROR severity if any committed deliverable absent.
- **Quality below bar**: QA pass is best-effort, not authoritative. The
  user should still spot-read every deliverable.
- **Wrong version sent**: deliverables live in git or a versioned
  filesystem. The manifest captures sha256 of every file so the user
  can verify what got packaged.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| delivery packaged                         | `ledgers/decisions.md`                    |
| approval requested                        | `ledgers/pending-approvals.md`           |
| external send happens                    | `ledgers/external-communications.md` + `ledgers/audit-log.md` |
| commitment fulfilled                      | `ledgers/commitments.md` (status: fulfilled) |

## Example output (delivery checklist excerpt)

```markdown
# Delivery — Acme Corp · 2026-05-09

## Manifest
- deliverables/sprint-1-doc.md     (4392 bytes, 2026-05-08, sha256:abc...)
- deliverables/sprint-2-doc.md     (5210 bytes, 2026-05-09, sha256:def...)

## QA
- broken wikilinks: 0
- spelling: 0 errors (aspell present)
- tone rubric: 4.5 / 5 (terse, format-strict)

## Checklist before send
- [ ] User has read both files end-to-end
- [ ] Pricing reconciles to proposal
- [ ] Cover note approved
- [ ] Sent via accounting/email tool
- [ ] commitments.md updated to fulfilled

## Cover note (draft)
Hi <name>,

Sprints 1 and 2 are attached. Anything you'd like adjusted before we
move to sprint 3?

Best,
<user>
```

## Cross-references

- `workflows/proposal-drafting.md` — what was promised.
- `workflows/invoice-preparation.md` — typical follow-up.
- `04_Harnesses/eval-rubric.md` — QA pass scoring.
- `ledgers/commitments.md` — fulfillment tracking.

## Next actions

- After Ralph drafts the delivery checklist: spot-read every
  deliverable. The QA pass is a sanity net, not a substitute for
  review.
