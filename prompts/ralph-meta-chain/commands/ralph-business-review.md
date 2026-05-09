---
description: |
  Triggers: "ralph business review", "open pending approvals", "what needs my approval"
allowed-tools:
  - "Read"
  - "Bash(grep:*,find:*)"
---

# /ralph-business-review

Open the business-entity pending-approvals queue + this week's
ledger activity. Read-only; LOW risk. Approving an entry remains a
manual user action per `docs/APPROVAL_GATES.md`.

## Inputs

`$ARGUMENTS` — optional. `pending` (default) | `decisions` |
`commitments` | `external-communications` | `audit`.

## Process

1. Read the matching ledger from
   `$VAULT/business-entity/ledgers/<ledger>.md` (or
   `$VAULT/07_Business/<ledger>.md` mirror).
2. Filter to entries with `status: pending` or `status: drafted`.
3. Sort by created date DESC.
4. Read the linked workflow / proposal note for each entry to add
   context.

## Output

Render a Markdown report:

- **Open approvals (count)** — table with ID, risk, subject, age.
- **Recently committed decisions** — last 5 from `decisions.md`.
- **Stale commitments** — anything in `commitments.md` with
  `due_date` < today and `status` not `fulfilled` / `withdrawn`.
- **Recommended next action** — at most one sentence per HIGH/CRITICAL
  open approval, with a `[[wikilink]]` to the ledger entry.

## Safety

LOW risk: read-only. Per `docs/APPROVAL_GATES.md`:
- Approving an entry = editing its frontmatter `status: approved`
  manually.
- External-send / financial / legal actions are CRITICAL and never
  triggered by this command.

## Cross-references

- `business-entity/README.md`.
- `business-entity/ledgers/pending-approvals.md`.
- `docs/BUSINESS_ENTITY_SCOPE.md`.
- `docs/APPROVAL_GATES.md`.
