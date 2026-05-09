# APPROVAL_GATES.md

## Purpose

Concrete operation-by-operation gate matrix. For every action the chain
or the user might take, classify it (LOW / MEDIUM / HIGH / CRITICAL per
`GOVERNANCE.md`) and specify what's required to apply it.

## Matrix

### Memory operations

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| append to `90-Meta/log.md`                             | LOW      | budget.memory remaining             |
| create atomic note from inbox                           | LOW      | budget.memory.max_promotions        |
| update MOC (add note to existing)                       | LOW      | budget.memory.max_mocs              |
| create new MOC                                          | LOW      | budget.memory.max_mocs              |
| tag a note `#orphan`                                    | LOW      | within budget                       |
| edit `30-Notes/<id>.md` body                            | MEDIUM   | append-only `## Ralph YYYY-MM-DD`   |
| edit `30-Notes/<id>.md` flagged `stability: canonical` | HIGH     | explicit approval                   |
| compress note (mv to `_archive/`, replace with summary)| MEDIUM   | proposal recorded                   |
| compress canonical note                                | HIGH     | explicit approval                   |
| permanently erase a note                                | CRITICAL | approval + audit + rollback (future)|

### Skills operations

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| create new skill                                       | MEDIUM   | budget.skills.max_new                |
| amend stale skill                                      | MEDIUM   | budget.skills.max_amended            |
| deprecate skill (status flip)                          | HIGH     | explicit approval                   |
| permanently erase skill                                | CRITICAL | approval + audit + rollback         |

### Prompt operations

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| spawn candidate variants in `_population/`             | MEDIUM   | budget.evolve.max_population_spawn  |
| run `harness ab` (A/B comparison)                      | LOW      | within budget                       |
| append `reflections:` line                             | LOW      | within budget                       |
| promote candidate to incumbent                         | HIGH     | explicit approval                   |
| permanently erase prompt                               | CRITICAL | approval + audit + rollback         |

### Cron / system

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| `harness self-test` (read-only)                         | LOW      | always allowed                      |
| autoheal LOW fixes (mkdir, chmod)                       | LOW      | within budget                       |
| autoheal escalation (write to escalations.md)           | LOW      | within budget                       |
| install cron / launchd                                 | HIGH     | explicit invocation of install.sh   |
| modify cron entries                                    | HIGH     | explicit invocation                 |
| install Claude Code hooks                              | HIGH     | explicit invocation + scope review  |
| disable origin guard                                    | CRITICAL | approval + threat-model review      |

### Voice / multi-device

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| `POST /ralph/voice` text → inbox                       | LOW      | within Tailscale boundary           |
| `POST /ralph/voice` audio → Whisper                    | LOW      | within Tailscale boundary           |
| `POST /ralph/run` (axis run)                           | MEDIUM   | rate-limit per axis                 |
| `POST /ralph/stop`                                     | LOW      | within boundary                     |
| enable Cloudflare Tunnel for Alexa                      | HIGH     | explicit setup; threat-model review |
| enable always-listening voice                           | CRITICAL | approval + audit + emergency stop   |
| enable remote execution channels                        | CRITICAL | approval + audit + rollback         |

### Business entity (Round 3+)

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| draft proposal (internal)                              | LOW      | within budget                       |
| draft client follow-up (internal)                       | LOW      | within budget                       |
| draft invoice (internal)                                | MEDIUM   | proposal recorded                   |
| send proposal externally                                | CRITICAL | approval + audit + ledger entry     |
| send invoice externally                                 | CRITICAL | approval + audit + ledger entry     |
| accept payment                                          | CRITICAL | NEVER autonomous; human-only        |
| make payment                                            | CRITICAL | NEVER autonomous; human-only        |
| sign contract                                           | CRITICAL | NEVER autonomous; human-only        |
| make tax filing                                         | CRITICAL | NEVER autonomous; human-only        |
| access bank / accounting / payroll systems              | CRITICAL | NEVER autonomous; human-only        |
| access email / calendar / CRM without explicit consent  | CRITICAL | NEVER autonomous; human-only        |
| make legal claim                                        | CRITICAL | NEVER autonomous; human-only        |

### Repo migration

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| `harness migration --inventory` (read-only)             | LOW      | always allowed                      |
| `harness migration --classify`                          | LOW      | always allowed                      |
| `harness migration --propose` (writes proposal)         | MEDIUM   | within budget                       |
| `harness migration --apply` (moves files)               | CRITICAL | approval + audit + rollback plan    |
| `harness migration --rollback`                          | HIGH     | explicit invocation                 |

### Provider / external

| Operation                                              | Class    | Gate                                |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| call Anthropic API (Claude Code, harness)              | LOW      | always allowed (default runtime)    |
| call Ollama on localhost                               | LOW      | always allowed                      |
| `harness ingest --topics` against GitHub               | MEDIUM   | `RALPH_AUTOUPDATE_NETWORK=1`        |
| `harness ingest --creators` against YouTube RSS         | MEDIUM   | `RALPH_AUTOUPDATE_NETWORK=1`        |
| activate Codex / Gemini / local-model adapter           | HIGH     | per-adapter config + threat review  |
| OAuth to Google / Apple / Alexa                         | CRITICAL | NEVER autonomous; human-only        |
| any vendor API requiring credentials                    | CRITICAL | NEVER autonomous; human-only        |

## Operational rules

1. **Default mode is dry-run / proposal-only.** When in doubt, generate
   a proposal note in `30-Notes/`, don't apply.
2. **Every CRITICAL operation requires four artifacts**: the proposal,
   the approval (explicit), the audit-log entry, and the rollback plan.
3. **Approval is never inferred.** Silence ≠ assent.
4. **Risk-class downgrades are themselves HIGH-risk.** Moving an
   operation from HIGH to MEDIUM in this matrix is a HIGH-risk edit.
5. **Never autonomous categories** (NEVER autonomous; human-only) are
   absolute. The chain refuses outright; even with `approvalMode:
   auto-medium`, these stay gated.

## Override mechanism

A user with the right context can bypass a gate by:

1. Documenting the override in `60-Interactions/overrides.md` with a
   timestamp and rationale.
2. Setting `RALPH_OVERRIDE_<axis>=1` in the environment of the manual
   invocation.
3. Reverting the override after the operation.

The chain logs every override invocation. Overriding a CRITICAL gate
without setting all three artifacts is itself a CRITICAL violation.

## Safety notes

- **Defaults are paranoid.** New users should keep `approvalMode:
  proposal-first` for the first month.
- **The matrix is the contract.** If an operation isn't in the matrix,
  the chain treats it as HIGH (proposal-only) until the user adds it.
- **CRITICAL "NEVER autonomous"** means: even if a user manually
  configures the chain to run such an operation, it refuses. To do
  these things, the user does them themselves outside Ralph.

## Cross-references

- `GOVERNANCE.md` — risk-class policy this matrix implements.
- `SECURITY_PRIVACY.md` — privacy threat model that shapes class
  assignments.
- `AUTOHEAL.md` — escalation routing for proposals waiting on approval.
- `BUSINESS_ENTITY_SCOPE.md` — business-entity gate specifics (Round 3+).
- Phase 1-6 reference: the existing prompts honor these gates implicitly;
  this matrix names them.

## Next actions

Skim the matrix end-to-end once. Pick five operations you expect to do
weekly; confirm their class is what you'd expect. If any look too
permissive or too strict for your context, edit `config.yml`'s
`approvalMode` first; only then propose changes to this matrix.
