# business-entity/

The deeper Markdown scaffold for Ralph's business-operations layer. The
master spec calls this the *autonomous business entity* layer; the
working name is more honest: a **drafting and ledger surface** with
explicit human-in-the-loop gates for everything externally visible.

> **Critical rule, mirrored from `docs/BUSINESS_ENTITY_SCOPE.md`:**
> Ralph **drafts and organizes**. It **never autonomously commits** to
> anything that creates legal, financial, or contractual obligations.

The vault-side daily surfaces live in
`vault-template/00_System/Business Entity Control Panel.md` and
`vault-template/07_Business/`. This `business-entity/` directory is the
**policy + workflow + ledger + template** authoring source — heavier
governance documents that the cron prompts read but a non-technical
operator may not need to open daily.

## Layout

```
business-entity/
├── README.md                        ← you are here
├── governance/      (7 files)       policies + risk + GDPR + audit
├── workflows/       (9 files)       per-workflow process specs
├── ledgers/         (7 files)       append-only SOTs
└── templates/       (6 files)       ready-to-use Markdown forms
```

## Reading order for new operators

1. `governance/operating-model.md` — what this entity does.
2. `governance/human-in-the-loop-policy.md` — where Ralph stops and asks.
3. `governance/approval-gates.md` — risk-class matrix.
4. `governance/delegated-authority-matrix.md` — who can approve what.
5. `governance/risk-register.md` — known risk surfaces.
6. `governance/gdpr-data-map.md` — what client data is held + retention.
7. `governance/audit-policy.md` — auditability invariants.

Then sample a workflow:

8. `workflows/lead-intake.md` — narrowest, simplest example.

Then look at the ledgers:

9. `ledgers/decisions.md` and `ledgers/commitments.md` — what gets logged.

## Activation status

| Capability                     | Status                                                |
| ------------------------------ | ----------------------------------------------------- |
| Markdown drafting              | active (Ralph can write under any of these folders)    |
| Internal workflow execution    | active                                                  |
| Ledger append (decisions, etc.)| active                                                  |
| **External communication**     | **GATED — CRITICAL approval per workflow**             |
| **Financial action**           | **NEVER autonomous — human-only**                      |
| **Legal action**               | **NEVER autonomous — human-only**                      |
| **Account access (CRM, banking, etc.)** | **NEVER autonomous — human-only**             |

The "NEVER autonomous" rows are the spec's `CRITICAL: NEVER autonomous`
class. They stay gated even with `approvalMode: auto-medium`.

## Cross-references

- `docs/BUSINESS_ENTITY_SCOPE.md` — full scope contract (master).
- `docs/APPROVAL_GATES.md` § Business entity — concrete gate matrix.
- `docs/GOVERNANCE.md` — risk-class policy.
- `vault-template/00_System/Business Entity Control Panel.md` — daily UI.
- `vault-template/07_Business/` — daily-use ledger surfaces.
- `docs/ROADMAP.md` § Round 3 — this round's plan.

## Next actions

- Skim `governance/operating-model.md`, then any single workflow file to
  see the shape.
- Round 4 wires migration tooling under `migration/` so the chain can
  later reconcile the dual paths (`business-entity/` and `vault-template/07_Business/`).
- Round 5+ adds Bash shims (`scripts/ralph_business_ledger_check.sh`)
  that validate ledger entries against the schemas defined in this round.
