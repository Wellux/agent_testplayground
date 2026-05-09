---
ralph_type: business
memory_layer: business
risk_class_default: LOW
created: 2026-05-09
status: scaffold
summary: "Score and rank candidate vendors from captured notes. Internal-only."
---

# Vendor Comparison

Pure internal workflow. Score 2-5 candidate vendors against a set of
criteria the user supplies, produce a ranked list + recommendation.

## Purpose

When evaluating tools / contractors / suppliers, produce a
comparison table that surfaces trade-offs cleanly. Reduces decision
inertia for the user.

## Inputs

- 2-5 vendor names + URLs (from `00-Inbox/` or `01_Inbox/Daily Capture.md`)
- comparison criteria (price / capability / risk / fit / etc.) — user
  provides; Ralph infers reasonable defaults from
  `vault-template/00_System/Interaction Preferences.md`
- optional: prior vendor comparisons in `30-Notes/` for style consistency

## Process

1. For each vendor, gather public-source data only (no scraping behind
   logins; the autoupdate cron may pre-cache data into
   `00-Inbox/futuretools-*.md`).
2. Score each vendor on each criterion (1-5).
3. Identify top trade-offs (e.g. "cheapest but lowest capability").
4. Render comparison table to
   `30-Notes/<id>-vendor-<topic>.md`.
5. Append a one-line recommendation note + uncertainty.
6. Append to `ledgers/decisions.md` if the user adopts the
   recommendation.

## Outputs

- `30-Notes/<id>-vendor-<topic>.md` (new file)
- `ledgers/decisions.md` (only if user adopts)

## Approval gates

| Step | Class | Gate                                      |
| ---- | ----- | ----------------------------------------- |
| 1-5  | LOW    | always allowed (internal note)             |
| 6    | LOW    | append-only ledger                          |
| —    | NONE   | "Purchase software / services" is NEVER autonomous (per `governance/approval-gates.md`) |

If the user wants to ACT on the recommendation, that's a separate
external-send and falls under proposal/follow-up workflows.

## Risk notes

- **Bias toward familiar vendors**: Ralph may rank vendors it has
  notes about higher than equally-good unknown ones. Mitigation:
  the rubric weights `capability` over `familiarity`.
- **Stale public data**: vendor pricing changes; Ralph cites the
  source URL + date and flags entries as `provisional` if older than
  30 days.
- **Conflict of interest**: Ralph never has a stake in a vendor;
  the user does. The user notes their own COI in the input.

## Ledger update requirements

| Trigger                                  | Append to                                |
| ---------------------------------------- | ---------------------------------------- |
| comparison drafted                        | (no ledger; the note IS the artifact)    |
| user adopts recommendation                | `ledgers/decisions.md`                   |

## Example output (excerpt)

```markdown
# Vendor comparison — embedding API providers

| Vendor       | Price  | Capability | Local-first | Notes                              |
| ------------ | ------ | ---------- | ----------- | ---------------------------------- |
| Ollama (local) | free   | 4          | yes         | already in use; nomic-embed-text   |
| Voyage         | paid   | 5          | no          | best benchmarks; cost varies        |
| OpenAI         | paid   | 5          | no          | familiar; ships data to OpenAI      |

## Recommendation
Ollama (local). Already integrated; matches local-first stance.
Re-evaluate quarterly.

## Uncertainty
- Voyage benchmarks not directly verified.
- OpenAI pricing assumed at standard rates; may shift.
```

## Cross-references

- `research/source-quality-rubric.md` — confidence/stability scoring.
- `04-research-ingest.md` — data gathering pipeline.
- `ledgers/decisions.md` — adoption record.

## Next actions

- For each vendor row: confirm the `Notes` column matches your
  experience.
- If recommendation adopted: append to `ledgers/decisions.md` with
  the rationale.
