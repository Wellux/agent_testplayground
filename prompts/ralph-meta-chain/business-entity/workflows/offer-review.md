---
ralph_type: business
memory_layer: business
risk_class_default: LOW
created: 2026-05-09
status: scaffold
summary: "Internal review pass on an offer (incoming) before any decision."
---

# Offer Review

The user receives an incoming offer (a vendor pitch, a contract from a
counterparty, a job offer, a partnership proposal). Ralph helps think
through it before any commitment.

## Purpose

Score an incoming offer along multiple dimensions, surface trade-offs
and missing data, and produce a decision-ready summary. Pure
internal — Ralph never responds to the offer-sender directly.

## Inputs

- the offer document (in `01_Inbox/Daily Capture.md`, a captured PDF
  pasted as text, or a voice transcript of the conversation)
- the user's goals + constraints (from
  `vault-template/00_System/Interaction Preferences.md` + project
  context)
- optional: prior offers for style consistency

## Process

1. Parse offer content; extract: offerer, scope, price/value,
   timeline, exclusivity, IP terms, termination clauses.
2. Score the offer on dimensions: alignment with goals, financial
   value, risk, reversibility, opportunity cost.
3. Identify missing-but-needed data ("what would the user need to
   know before deciding?").
4. Identify red flags: non-standard clauses, vague terms, ambiguous
   scope.
5. Render decision-ready summary at
   `30-Notes/<id>-offer-review-<topic>.md`.
6. Append to `ledgers/decisions.md` (status: pending) — the actual
   decision (accept / decline / negotiate) is the user's, recorded
   later as a separate decisions.md entry.

## Outputs

- offer-review Markdown.
- `ledgers/decisions.md` (append, status: pending).

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-5  | LOW      | always allowed (internal note)                     |
| 6    | LOW      | append-only ledger                                  |
| —    | CRITICAL | "Sign contract" / "Make legal claim" — NEVER autonomous |

## Risk notes

- **Legal advice**: Ralph is NOT a lawyer. The review surfaces
  questions; it doesn't answer them. Any legal-clause analysis is
  flagged "consult counsel".
- **Optimism bias**: a flashy offer can feel high-value; Ralph
  scores along risk + reversibility too to balance.
- **Missing context**: the offer summary depends on Ralph having all
  the relevant pages. Missing pages flagged ERROR severity.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| review drafted                            | `ledgers/decisions.md` (status pending)  |
| user accepts                              | `ledgers/decisions.md` (new entry: accepted) AND possibly `ledgers/legal-actions.md` (CRITICAL, manual) |
| user declines                             | `ledgers/decisions.md` (new entry: declined) |
| user negotiates (counter-offer)           | `workflows/proposal-drafting.md` upstream |

## Example output (excerpt)

```markdown
# Offer Review — vendor X partnership · 2026-05-09

## Scoring
| Dimension          | Score (1-5) | Note                                |
| ------------------ | ----------- | ----------------------------------- |
| Goal alignment     | 4           | matches Q3 expansion priority        |
| Financial value    | 3           | revenue split needs negotiation       |
| Risk               | 2 (lower=better) | exclusivity clause is unusual    |
| Reversibility      | 2 (lower=better) | 12-month commitment              |
| Opportunity cost   | 4 (higher=better) | replaces current vendor          |

## Missing data
- exact revenue-share waterfall above $X tier
- termination penalties for early exit

## Red flags
- "exclusive partnership in <region>" — broad; needs scope tightening
- "auto-renews unless 90-day notice" — flag for legal review

## Recommendation framing
> If revenue-share above the $X tier is symmetric and exclusivity is
> scoped to <region/sector>, this is worth pursuing. Otherwise, propose
> a 6-month pilot via proposal-drafting.

## Caveats
- Not legal advice. Consult counsel on the exclusivity + auto-renewal
  clauses before signing.
```

## Cross-references

- `workflows/proposal-drafting.md` — counter-offer path.
- `governance/risk-register.md` — recurring red-flag patterns.
- `ledgers/decisions.md`, `ledgers/legal-actions.md`.

## Next actions

- Read the missing-data list; gather what's needed before deciding.
- For any legal-flag item: consult counsel. Ralph stops there.
