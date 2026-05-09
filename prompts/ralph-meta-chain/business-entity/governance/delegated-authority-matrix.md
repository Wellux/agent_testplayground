---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: scaffold
summary: "Who is allowed to approve what."
---

# Delegated Authority Matrix

In single-user mode, this matrix is mostly trivial: the user holds
every role. The matrix is here so multi-user mode (deferred) can
specialize without a redesign.

## Roles

| Role           | Description                                                       |
| -------------- | ----------------------------------------------------------------- |
| **Owner**      | Final approval authority; can approve every class up to CRITICAL.  |
| **Operator**   | Day-to-day. Can approve LOW + MEDIUM autonomously; HIGH with co-sign. |
| **Auditor**    | Read-only. Can challenge any approved entry, requiring re-review.  |
| **External**    | Outside parties; can propose only.                                 |

In single-user mode, the human user IS Owner + Operator + Auditor.
External is reserved for future contractors / clients with
proposal-only access.

## Matrix

| Operation class                        | Owner   | Operator      | Auditor       | External  |
| -------------------------------------- | ------- | ------------- | ------------- | --------- |
| LOW (read-only / non-destructive)        | approve | auto-apply    | challenge     | no access |
| MEDIUM (proposal-then-apply)            | approve | auto-apply    | challenge     | propose   |
| HIGH (canonical / system surface)        | approve | propose only   | challenge     | no access |
| CRITICAL — internal                     | approve | propose only   | challenge     | no access |
| CRITICAL — external send                | approve | propose only   | block         | no access |
| CRITICAL — financial / legal             | approve | propose only   | block         | no access |

"Block" = the role can preemptively halt the action regardless of
other approvals.

## Single-user mode (default)

The user holds Owner role implicitly. Approvals are **explicit edit to
proposal frontmatter** (`status: approved`).

## Multi-user mode (deferred — Round 7+)

When wired:

- Each role has a list of authorized identities in
  `governance/delegated-authority-matrix.md` frontmatter.
- Proposal notes carry an `approval_role:` field saying which role
  must approve.
- The chain refuses to apply until the matching role's identity has
  signed (signature mechanism TBD: GPG-signed git commit, or
  signed-Markdown-block).
- Auditor "challenges" land in `ledgers/audit-log.md` and force the
  apply to halt until re-reviewed by a higher role.

## Co-signing

For HIGH-risk operations the Operator may approve, but only with an
Owner co-sign. In Markdown:

```yaml
approvals:
  - role: operator
    actor: user@host
    at: 2026-05-09T12:00:00+00:00
  - role: owner
    actor: user@host       # different identity in multi-user mode
    at: 2026-05-09T13:00:00+00:00
```

In single-user, both rows are the same user; the artifact still
exists for audit symmetry.

## Override matrix

| Override level                                      | Allowed by      |
| --------------------------------------------------- | --------------- |
| Disable LOW gate temporarily                          | Owner            |
| Disable MEDIUM gate temporarily                       | Owner            |
| Disable HIGH gate temporarily                         | Owner + audit log |
| Disable CRITICAL gate                                | NEVER (refused)   |

## Cross-references

- `governance/human-in-the-loop-policy.md` — the asymmetry.
- `governance/approval-gates.md` — risk-class operations.
- `governance/audit-policy.md` — required artifacts.
- `docs/GOVERNANCE.md` § Roles.

## Next actions

- Single-user: nothing to do; the matrix is implicit.
- Multi-user (deferred): populate the frontmatter `roles:` list with
  authorized identities. Consider GPG-signed commits as the signature
  layer.
