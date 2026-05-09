---
ralph_type: business
memory_layer: business
memory_temperature: hot
created: 2026-05-09
status: scaffold
summary: "Live queue of pending approval requests."
---

# Pending Approvals

> The Obsidian status bar shows the count of items here. Open + approve
> as part of the weekly review.

## Open

| Id | Created | Risk | Subject | Action |
|----|---------|------|---------|--------|
| (empty) | | | | |

(Populated by Round 3+ — proposals from `07-autoevolve`,
`08-autoupdate`, business workflows, voice captures tagged for
approval.)

## How to approve

1. Open the linked proposal note in `30-Notes/` or `07_Business/`.
2. Read the test-plan + rollback-plan.
3. If approved: edit the note's frontmatter:
   ```yaml
   status: approved
   approver: <user>
   approved_at: <ISO_TS>
   ```
4. The next cron firing (or `harness apply --proposal <id>` in Round 5+)
   applies it.

## How to reject

Edit the proposal's frontmatter `status: rejected` and add a
`## Rejected on YYYY-MM-DD` block with a one-line rationale. The
proposal is archived, not deleted.

## Cross-references

- `07_Business/approval-ledger.md` — applied / archived approvals.
- `docs/APPROVAL_GATES.md` § Override mechanism.
- `business-entity/ledgers/pending-approvals.md` — Round 3 deeper version.
