# BUSINESS_ENTITY_SCOPE.md

## Purpose

The scope and boundary of business-entity scaffolding in Ralph Meta Chain.
The chain may **draft and organize** business workflows; it **never
autonomously commits** to anything that creates legal, financial, or
contractual obligations. This doc defines the line.

The full scaffold (`business-entity/governance/`, `workflows/`, `ledgers/`,
`templates/`) lands in Round 3+. This doc is the policy.

## What Ralph MAY do (proposal-only)

- draft proposals (internal),
- summarize client needs from notes,
- classify leads by stage / priority,
- prepare checklists,
- prepare invoice **drafts** in `business-entity/templates/`,
- prepare follow-up message **drafts**,
- compare vendors based on captured notes,
- structure offers,
- prepare meeting summaries from transcripts,
- draft internal SOPs,
- maintain the pending-approval ledger,
- maintain decision logs,
- flag legal / financial risks,
- maintain the GDPR data map (where client data lives, how long),
- maintain the audit log,
- maintain the delegated authority matrix.

All of the above writes to `business-entity/` Markdown files; nothing
leaves the host.

## What Ralph MAY NOT do autonomously (CRITICAL gates)

- sign contracts,
- send offers externally,
- send invoices externally,
- make payments,
- accept payments,
- bind the user legally,
- bind a company legally,
- make tax filings,
- access bank accounts,
- access accounting / payroll systems,
- access CRM / email / calendar without explicit consent + scope,
- communicate with clients without explicit approval per message,
- purchase software or services,
- hire or fire people,
- make regulated professional claims (legal advice, medical, financial
  advice).

These are NEVER autonomous (per `APPROVAL_GATES.md`). Even with
`approvalMode: auto-medium`, these stay gated.

## Why this distinction matters

Two reasons:

1. **Legal/financial agency** is the formal doctrine that an agent's
   acts bind a principal. AI agents legitimately operating with such
   agency requires durable identity, authorization records, audit
   trails, and (depending on jurisdiction) explicit registration. Ralph
   does not provide those infrastructure pieces; therefore it cannot
   responsibly hold agency.
2. **Reversibility.** Internal drafts are 100% reversible (delete the
   file). External communications and financial actions are not
   (recipient already saw it; bank already cleared the wire). The risk
   classes mirror the reversibility profile.

## Ledger pattern

Every business action — even drafts — produces a ledger entry. Ledgers
under `business-entity/ledgers/`:

| Ledger                                                  | Purpose                                            |
| ------------------------------------------------------- | -------------------------------------------------- |
| `decisions.md`                                           | every decision made (by user or proposed by chain)  |
| `commitments.md`                                         | every commitment made or proposed                  |
| `pending-approvals.md`                                   | open approval requests                              |
| `audit-log.md`                                           | append-only timestamped record of every action     |
| `external-communications.md`                             | every outbound message + approval reference        |
| `financial-actions.md`                                   | every financial-class action (always human)         |
| `legal-actions.md`                                       | every legal-class action (always human)             |

Ledger entries have a fixed shape:

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: decisions | commitments | pending-approvals | audit-log | ...
created: ISO_TS
proposer: ralph-cron-<axis> | ralph-plugin | user
status: proposed | approved | rejected | applied | rolled-back
risk_class: LOW | MEDIUM | HIGH | CRITICAL
related: ["[[<other-ledger-id>]]", "[[<note-id>]]"]
summary: "One-line"
---

# <Title>

## What
...

## Why
...

## Approval reference
- approved by: <user>
- approved at: <ISO_TS>
- approval method: explicit | proposal-default

## Audit
- action_taken: <description>
- action_at: <ISO_TS>

## Rollback (CRITICAL only)
<plan>
```

## Workflow files

Each business workflow file at `business-entity/workflows/<name>.md`
(Round 3+) follows this schema:

```yaml
---
ralph_type: business
status: active
risk_class_default: MEDIUM
---

# <Workflow Name>

## Purpose
...

## Inputs
- ...

## Process
1. ...
2. ...

## Outputs
- ...

## Approval gates
- step <N>: <class> — <why>

## Risk notes
...

## Ledger updates required
- on draft: append to commitments.md
- on approval: append to decisions.md + audit-log.md
- on external send: append to external-communications.md

## Example
<inline Markdown>
```

## Initial workflow set (Round 3+)

- `lead-intake.md` — capture lead from inbox; classify; queue.
- `proposal-drafting.md` — draft from template; route to approval.
- `invoice-preparation.md` — draft only; never send.
- `client-follow-up.md` — draft only; never send.
- `knowledge-work-delivery.md` — package + checklist.
- `vendor-comparison.md` — score + rank from notes.
- `meeting-summary.md` — from transcript.
- `offer-review.md` — internal review only.
- `task-delegation.md` — internal only; assignment ledger.

## GDPR data map

`business-entity/governance/gdpr-data-map.md` (Round 3+) tracks:

- per data subject: what data is held, where (which `30-Notes/` notes
  with `privacy: client`).
- retention: hot/warm/cold/frozen per subject.
- right to erasure: process for CRITICAL erase operation.
- consent: explicit consent record per subject + scope.

## Roles + delegated authority

`business-entity/governance/delegated-authority-matrix.md` (Round 3+):

| Role              | What they can approve                              |
| ----------------- | -------------------------------------------------- |
| Owner (default)   | every class up to CRITICAL                          |
| Operator           | LOW + MEDIUM autonomously; HIGH with co-sign        |
| Auditor            | read-only; can challenge any approved entry        |
| External advisor   | proposes only                                       |

In single-user mode, the user holds all roles. Multi-user mode (deferred)
separates them.

## Safety notes

- The line between "draft" and "send" is the line between MEDIUM and
  CRITICAL risk. Cross it explicitly.
- Even apparently safe actions (drafting an invoice) demand careful
  data handling: the invoice text references the client's name + amount.
- The chain never accepts CRM credentials. If the user wants Ralph to
  read calendar / email, they do that integration themselves with
  scoped tokens; Ralph reads the resulting Markdown captures.
- Ledger files are append-only. Editing a ledger entry's `status` is
  HIGH risk; deleting one is CRITICAL.

## Cross-references

- `GOVERNANCE.md` — risk classes referenced here.
- `APPROVAL_GATES.md` — concrete gate matrix; CRITICAL "NEVER autonomous"
  category.
- `SECURITY_PRIVACY.md` — client-data handling rules.
- `MEMORY_MODEL.md` — `privacy: client` frontmatter field.
- Round 3+ scaffold target: `business-entity/`.

## Next actions

If you don't run a business out of this vault: skip Round 3 entirely;
nothing in `business-entity/` activates without explicit user adoption.
If you do: read this doc end-to-end; populate `governance/operating-model.md`
when Round 3 lands; never enable any "send externally" path without
re-reading `APPROVAL_GATES.md`.
