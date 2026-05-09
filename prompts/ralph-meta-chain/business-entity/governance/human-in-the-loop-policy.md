---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: scaffold
summary: "When Ralph stops and asks. The asymmetry between drafting and committing."
---

# Human-in-the-Loop Policy

Ralph operates with **fully autonomous internal drafting** and
**always-human external committing**. This policy makes the asymmetry
explicit so the cron prompts and the operator share the same mental
model.

## The asymmetry

```
   internal              boundary             external
   ─────────             ───────              ────────
   draft / classify      ●                    send / sign / pay
   organize / link       │                    accept / commit
   summarize / score      │                    bind legally
                         │
   Ralph is autonomous   │   Ralph is gated
   per APPROVAL_GATES    │   per APPROVAL_GATES
```

The line is drawn at: **does the action create or signal a binding
relationship to a non-Ralph party?** If yes, human approval. If no,
Ralph proceeds within its budget.

## The two questions Ralph asks before any non-LOW action

Before any MEDIUM+ action the cron prompts answer two questions:

1. **Is the artifact externally visible?**
   - Yes → at least HIGH; CRITICAL if the action is also irreversible.
   - No → MEDIUM is allowed.

2. **Is the action irreversible (within ~24 hours)?**
   - Yes → CRITICAL; rollback plan mandatory.
   - No → class held at HIGH or below.

If either answer is uncertain, the chain treats it as one class higher
("when in doubt, choose the higher class" — `docs/GOVERNANCE.md`).

## The three artifacts Ralph never autonomously produces

Even with all approval gates open:

1. **External communications** (emails, posts, DMs, calls). Drafts only.
2. **Financial actions** (any movement of money). Always human.
3. **Legal actions** (signatures, filings, claims). Always human.

The reason is institutional, not technical: legal and financial
agency requires durable identity + authorization records + (in many
jurisdictions) explicit registration. Ralph doesn't provide those
infrastructure pieces.

## When Ralph stops mid-workflow

Each workflow file in `business-entity/workflows/` has explicit
"Approval gates" steps. When the cron prompt hits one:

1. It writes the artifact to `business-entity/templates/...md` or
   `30-Notes/<id>-<workflow>-<topic>.md`.
2. It appends an entry to `ledgers/pending-approvals.md`.
3. It exits the iteration with `<promise>COMPLETE</promise>` (so the
   outer Ralph loop stops re-feeding this workflow until the
   pending-approval is resolved).
4. The next firing checks if the approval landed; if yes, it applies;
   if no, it skips this workflow and moves to others.

## When the human stops Ralph

User-side emergency stops, in order:

1. `touch $VAULT/90-Meta/STOP` — pauses every cron.
2. Edit a proposal's frontmatter to `status: rejected` — refuses that
   specific apply.
3. `./scripts/uninstall.sh` — removes `# RALPH-managed:` cron entries.

The chain treats user-set `STOP` as authoritative; it never
auto-removes the file.

## Multi-user

Single-user mode (current default): operator IS owner IS auditor IS
approver.

Multi-user mode (deferred): roles separate per
`governance/delegated-authority-matrix.md`. The user → Owner mapping
becomes explicit, and proposals route to the role that can approve them.

## Cross-references

- `governance/operating-model.md` — what the entity does.
- `governance/approval-gates.md` — concrete matrix.
- `governance/delegated-authority-matrix.md` — role mapping.
- `docs/APPROVAL_GATES.md` § Override mechanism.
- `docs/GOVERNANCE.md` § Roles.

## Next actions

- Read this once. The asymmetry is the whole policy.
- The "two questions" framing is what cron prompts use during
  diagnose → propose; revisit it if you see Ralph proposing
  HIGH-risk apply for clearly internal work, or MEDIUM-risk apply
  for clearly external commitments.
