---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for business-entity workflow output (drafts only)."
---

# Business Action Quality Scorecard

Grades the OUTPUT of business-entity workflows. **Send/sign/pay
actions are CRITICAL and never autonomous** per
`docs/BUSINESS_ENTITY_SCOPE.md`; this scorecard rates the DRAFTS
those workflows produce.

## Scored axes (1-5 each)

### scope fidelity (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every claim traces to a sentence in the source brief OR offer-template |
| 4     | mostly traceable; 1-2 unsourced minor claims               |
| 3     | half traceable                                             |
| 2     | most claims unsourced                                       |
| 1     | hallucinated commitments                                    |

### approval-gate respect (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | drafts only; pending-approvals.md updated; no send       |
| 3     | drafts only but missed a ledger update                    |
| 1     | attempted to send / sign / pay (BLOCKER — never reachable in valid execution) |

### tone (per Interaction Preferences) (1-5)

Same axis as `interaction-quality.md` § tone match. External-bound
artifacts (proposals, follow-ups) require ≥ 4.

### privacy frontmatter (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | client-class data tagged `privacy: client`; subject_id pseudonymized |
| 4     | minor lapse on a single field                              |
| 3     | inconsistent privacy tagging                                |
| 2     | client name in plaintext where pseudonym expected           |
| 1     | PII leaked into a privacy: work or privacy: public file     |

### reversibility documentation (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every commitment row has explicit reversibility notes     |
| 3     | reversibility implicit                                     |
| 1     | irreversible commitment drafted without flagging            |

## Composite

`rubric_business = mean(scope_fidelity, approval_gate, tone,
privacy_frontmatter, reversibility)`.

## Pass thresholds

- **internal-only artifacts** (lead briefs, vendor comparisons,
  meeting summaries): rubric ≥ 3.5.
- **proposed-external-send artifacts** (proposals, invoices,
  follow-ups, offer responses): rubric ≥ 4.0 AND every individual
  axis ≥ 3.0. The user's approval is still required regardless.
- **rubric < 3.0 on any axis** → `07-autoevolve` flags the
  workflow's draft template for review.

## Refusal conditions (BLOCKER)

The chain refuses to ship a business-class draft if ANY of:

1. `approval-gate respect < 3` — drafts attempting to send.
2. `privacy frontmatter < 3` — PII leakage risk.
3. Source brief missing `privacy: client` while subject is identifiable.

## Cross-references

- `docs/BUSINESS_ENTITY_SCOPE.md`.
- `docs/APPROVAL_GATES.md` § Business entity.
- `business-entity/governance/{operating-model,human-in-the-loop-policy,approval-gates,gdpr-data-map}.md`.
- `business-entity/workflows/*.md`.
- `business-entity/templates/*.md`.
