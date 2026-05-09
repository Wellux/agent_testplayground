---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Append-only register of known business risks + mitigations + owners."
---

# Risk Register

Append-only. The autoupdate cron flags risks for review when their
`last_reviewed:` is > 90 days. Removal is HIGH-risk per
`docs/APPROVAL_GATES.md`.

## Schema (per entry)

```yaml
---
id: <YYYYMMDDHHMM>-<slug>
ledger: risk
created: <ISO_TS>
last_reviewed: <YYYY-MM-DD>
likelihood: low | medium | high
impact: low | medium | high
severity: derived from likelihood × impact
status: open | mitigated | accepted | retired
owner: <user-or-role>
related: ["[[<note>]]", "[[<workflow>]]"]
---

# <Risk title>

## What
<2-3 sentence description>

## Trigger conditions
- ...

## Mitigations
- (control 1 — owned by X)
- (control 2)

## Residual risk
<after mitigations: low | medium | high>

## Review cadence
- next review: <YYYY-MM-DD>
```

## Initial entries (typical)

### Operational

| Id (slug)               | Severity  | Status     | Owner        | Mitigation summary                       |
| ----------------------- | --------- | ---------- | ------------ | ---------------------------------------- |
| client-data-leak        | high      | mitigated   | owner        | privacy frontmatter + retention policy   |
| vault-content-loss       | high      | mitigated   | owner        | git + Obsidian Sync; append-only invariant |
| api-key-compromise       | medium    | mitigated   | owner        | .env gitignored; rotation procedure documented |
| dependency-supply-chain  | medium    | accepted    | owner        | renovate-style proposals; manual merge   |

### Reputational

| Id (slug)               | Severity  | Status   | Owner   | Mitigation summary                       |
| ----------------------- | --------- | -------- | ------- | ---------------------------------------- |
| autonomous-send-error    | critical  | mitigated | owner   | external-send is CRITICAL gate            |
| client-name-misattribution | medium  | open     | owner   | proposal-first review; private frontmatter |

### Legal / financial

| Id (slug)               | Severity  | Status   | Owner   | Mitigation summary                       |
| ----------------------- | --------- | -------- | ------- | ---------------------------------------- |
| unauthorized-commitment  | critical  | mitigated | owner   | NEVER autonomous category for commitments |
| contractual-overreach    | high      | mitigated | owner   | proposal-only contract drafts             |
| tax-noncompliance        | high      | accepted | owner   | tax filings always human                   |

(Replace placeholder rows with project-specific risks. The autoevolve
cron may surface new risks based on observed errors.)

## Severity derivation

| Likelihood / Impact | low | medium | high      |
| ------------------- | --- | ------ | --------- |
| **low**             | low | low    | medium    |
| **medium**          | low | medium | high      |
| **high**            | medium | high | critical  |

## Cross-references

- `governance/audit-policy.md` — how risk-related actions get logged.
- `governance/gdpr-data-map.md` — privacy-specific risks.
- `docs/SECURITY_PRIVACY.md` — full threat model.
- `vault-template/00_System/Repo Migration Control Panel.md` — migration risks.

## Next actions

- Replace placeholder rows with project-specific risks.
- Set `last_reviewed:` on each entry; the autoupdate cron will surface
  stale ones quarterly.
- Adding a new risk row is LOW; raising severity is MEDIUM; lowering
  severity is HIGH (per `docs/APPROVAL_GATES.md`).
