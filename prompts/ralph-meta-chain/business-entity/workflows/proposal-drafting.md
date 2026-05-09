---
ralph_type: business
memory_layer: business
risk_class_default: MEDIUM
created: 2026-05-09
status: scaffold
summary: "Draft a proposal from a lead brief; never sends externally."
---

# Proposal Drafting

Drafts a proposal from a lead brief + offer template. The DRAFT is
MEDIUM (internal); SENDING is CRITICAL (always human).

## Purpose

Take a `clients/<slug>/brief.md`, plus
`business-entity/templates/offer-template.md`, plus the user's tone
preferences (`vault-template/00_System/Interaction Preferences.md`),
and produce a draft proposal document for human review.

## Inputs

- `business-entity/clients/<slug>/brief.md` (from lead-intake)
- `business-entity/templates/offer-template.md`
- `vault-template/00_System/Interaction Preferences.md` (tone)
- optional: prior proposals to cite for style consistency

## Process

1. Read the brief; extract: scope, ask, constraints, urgency.
2. Read offer-template.md; identify variable slots.
3. Fill slots with proposal-specific content. Cite any reused phrasing
   from prior proposals in `30-Notes/_archive/proposal-*.md`.
4. Write the draft to
   `business-entity/clients/<slug>/proposal.md`.
5. Append to `ledgers/commitments.md` with `status: drafted` and
   `audience: external` (visibility flag).
6. Append a HIGH-risk approval request to `ledgers/pending-approvals.md`
   with subject "Send proposal to <counterparty>". The user reviews
   the draft AND the pending-approval before sending.
7. Refuse to send. Send is CRITICAL and never autonomous.

## Outputs

- `business-entity/clients/<slug>/proposal.md` (new file, draft)
- `ledgers/commitments.md` (append, status: drafted)
- `ledgers/pending-approvals.md` (append, HIGH approval gate)

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-4  | MEDIUM    | proposal-first (the file IS the proposal)         |
| 5    | MEDIUM    | ledger append                                      |
| 6    | HIGH      | explicit user approval required to mark "approved" |
| 7    | CRITICAL  | external send is NEVER autonomous                  |

The send (step 7) requires:
1. proposal.md status approved by user,
2. audit-log entry written before send,
3. user manually triggers the send (e.g. `mail`, copy-paste, or — in
   future Round 7+ — `harness send --proposal <id>` after a strong
   gate).

## Risk notes

- **Hallucination**: Ralph might draft commitments not in the brief.
  Mitigation: every claim in the draft must trace back to a sentence in
  the brief or offer-template; the cron prompt enforces this and flags
  uncited claims as `#unsourced`.
- **Tone misalignment**: the operator's preferences may evolve faster
  than the cron's snapshot. Mitigation: the
  `interaction-optimizer` cron updates Interaction Preferences daily,
  and proposal-drafting reads it at run time.
- **Commitment overreach**: the draft might propose timelines or
  scopes the user didn't authorize. Mitigation: every commitment row
  in the draft is cross-listed in `ledgers/commitments.md` with
  `status: drafted` so the user can spot it.

## Ledger update requirements

| Trigger                                                     | Append to                              |
| ----------------------------------------------------------- | -------------------------------------- |
| proposal drafted                                            | `ledgers/commitments.md` (drafted)     |
| approval requested                                          | `ledgers/pending-approvals.md`         |
| approval granted                                            | `ledgers/decisions.md`                 |
| external send happens                                       | `ledgers/external-communications.md` AND `ledgers/audit-log.md` |
| approval rejected                                           | append to source proposal (rejected)   |

## Example output (excerpt of `proposal.md`)

```markdown
# Proposal — Acme Corp · Internal Docs Engagement

## Engagement summary
We propose <scope> over <timeline>, with <deliverables>.

## Scope (from brief)
- ...

## Timeline (proposed; not yet committed)
- ...

## Pricing (proposed)
- ...

## Open questions
- (uncited) — needs counterparty review
```

## Cross-references

- `templates/offer-template.md` — the source.
- `workflows/lead-intake.md` — upstream.
- `workflows/client-follow-up.md` — downstream after send.
- `governance/approval-gates.md` § Sends.

## Next actions

- After Ralph drafts: open the proposal.md in Obsidian, review every
  uncited claim, edit, then mark frontmatter `status: approved` to
  unblock send.
