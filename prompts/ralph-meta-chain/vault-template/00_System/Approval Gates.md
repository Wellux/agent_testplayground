---
ralph_type: system
memory_layer: system
memory_temperature: hot
stability: canonical
created: 2026-05-09
summary: "Vault-side mirror of the operation→risk-class matrix."
---

# Approval Gates

Authoritative source: `docs/APPROVAL_GATES.md`. This vault-side copy
exists so prompts can `Read` it at runtime without depending on the
repo path being in scope.

## Risk classes

- **LOW** — read-only or non-destructive scaffold; auto-applies inside budget.
- **MEDIUM** — mutates non-canonical state; recorded as proposal; auto-applies with audit.
- **HIGH** — mutates canonical state or system surface; explicit user approval required.
- **CRITICAL** — irreversible / externally-binding; explicit approval + audit + rollback plan.

## Quick reference (most-used operations)

| Operation                                              | Class    |
| ------------------------------------------------------ | -------- |
| append to `90-Meta/log.md`                              | LOW      |
| create new atomic note from inbox                       | LOW      |
| edit `30-Notes/<id>.md` body (non-canonical)             | MEDIUM   |
| edit canonical-stable note                              | HIGH     |
| compress note (mv to `_archive/`)                       | MEDIUM   |
| permanently erase a note                                | CRITICAL |
| install / modify cron                                    | HIGH     |
| activate Codex / Gemini / local-model adapter            | HIGH     |
| autoheal LOW fixes                                       | LOW      |
| send proposal/invoice externally                         | CRITICAL |
| apply repo-wide migration                                | CRITICAL |
| accept payment / make payment / sign contract            | CRITICAL (NEVER autonomous) |

## Override mechanism

To bypass a gate manually:

1. Document the override in `60-Interactions/overrides.md` with timestamp + rationale.
2. Set `RALPH_OVERRIDE_<axis>=1` in the manual invocation env.
3. Revert the override after the operation completes.

The chain logs every override invocation. CRITICAL overrides without
all three artifacts are themselves CRITICAL violations.

## Cross-references

- `docs/APPROVAL_GATES.md` — full matrix.
- `docs/GOVERNANCE.md` — risk-class policy.
- `00_System/Agent Operating Principles.md` — rules behind the classes.
- `90-Meta/log.md` — audit trail of every gate decision.
