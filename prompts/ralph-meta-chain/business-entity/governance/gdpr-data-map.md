---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Where client data lives, retention, and erasure procedure."
---

# GDPR Data Map

If client / personal data lives in the vault, this file tracks where,
for how long, and how to erase it. The autoupdate cron checks for
notes whose `privacy: client` and `created:` exceeds the retention
window and proposes archive / erase.

> **Disclaimer.** This is an operational data map, NOT legal advice.
> Compliance with GDPR / CCPA / your local privacy law is the
> operator's responsibility. Have a qualified professional review.

## Per-subject schema

```yaml
---
subject_id: <pseudonym, never the real name>
created: <YYYY-MM-DD>      # consent date
purposes: [contract-execution, support, project-delivery]
data_categories: [contact-info, billing, project-content]
retention_window_days: 730  # 2y default; project-specific
hot_window_days: 180         # while engagement active
cold_window_days: 365         # after engagement ends
right_to_erasure: documented in ledgers/financial-actions.md if any billing exists
last_reviewed: <YYYY-MM-DD>
---
```

## Locations the data may be in

| Path                                          | Privacy class default | Retention applies? |
| --------------------------------------------- | --------------------- | ------------------ |
| `30-Notes/` w/ `privacy: client`               | client                 | yes                |
| `00-Inbox/_processed/` w/ `privacy: client`     | client                 | yes                |
| `business-entity/templates/client-brief-template.md` filled-in | client | yes  |
| `business-entity/ledgers/external-communications.md` w/ counterparty | client | yes |
| `business-entity/ledgers/commitments.md` w/ counterparty | client | yes |
| `business-entity/ledgers/financial-actions.md` w/ counterparty | client | yes (legal-minimum) |
| `vault-template/07_Business/clients/<slug>/`    | client                 | yes                |

The cron prompts honor `privacy:` frontmatter; HIGH-risk to edit any
file flagged `privacy: client`.

## Retention windows (defaults)

| Phase                 | Days  | Demotion target                       |
| --------------------- | ----- | ------------------------------------- |
| Hot (active client)    | 180   | warm                                  |
| Warm (recent client)   | 365   | cold                                  |
| Cold (archived)         | 730   | frozen                                 |
| Frozen                  | indefinite | retained for legal-minimum only |

Override per-subject in the per-subject schema above.

## Right-to-erasure procedure

1. User invokes (Round 5+): `harness erase --subject <id>`.
2. The harness lists every file with `privacy: client` AND
   `subject_id: <id>` (CRITICAL list — display, don't act).
3. User explicitly confirms with `--confirmed`.
4. The harness:
   - moves matching atomic notes to `99_Archive/_erased/<id>-<UTC>/`.
   - rewrites references in indexes (still as broken `[[wikilinks]]`,
     not silent removal).
   - appends an entry to `ledgers/financial-actions.md` (legal-minimum
     retention applies for any billing-related data — flag for human).
5. The user follows up on the legal-minimum data manually.

`harness erase` is **NEVER autonomous**. It always requires explicit
invocation + `--confirmed`.

## Per-subject entries

(populate as engagements start)

```markdown
## subject-001

```yaml
subject_id: subject-001
created: 2026-05-09
purposes: [contract-execution]
data_categories: [contact-info, project-content]
retention_window_days: 730
hot_window_days: 180
cold_window_days: 365
right_to_erasure: tracked
last_reviewed: 2026-05-09
```

```

## Cross-references

- `docs/SECURITY_PRIVACY.md` § Privacy specifics.
- `governance/audit-policy.md` — how erase actions get logged.
- `vault-template/02_Memory/` — typed memory buckets.
- `vault-template/07_Business/client-workflows.md` — per-client folders.

## Next actions

- Confirm the retention defaults match your legal context.
- Any per-subject entries land below the per-subject section.
- The autoupdate cron quarterly check is the safety net — don't rely on
  it as the only review.
