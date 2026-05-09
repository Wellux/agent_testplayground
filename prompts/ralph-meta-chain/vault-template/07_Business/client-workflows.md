---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Pointer to per-client workflow notes (each gets its own folder)."
---

# Client Workflows

> Round 3+ wires the full per-client workflow folders. Round 1-2 only
> documents the surface.

## Pattern

When a client engagement starts, create
`07_Business/clients/<client-slug>/`:

- `brief.md`         — the client's needs as captured.
- `proposal.md`      — drafted proposal (linked from `business-entity/templates/offer-template.md`).
- `meetings/`         — per-meeting summaries.
- `deliverables/`     — work products.
- `commitments.md`   — pointer to relevant entries in `07_Business/commitment-ledger.md`.
- `follow-ups.md`    — drafts; never sent autonomously.

All client data carries `privacy: client` frontmatter. Per
`docs/SECURITY_PRIVACY.md`, that's HIGH-risk for any edit.

## GDPR

If client data is in scope:

- Each client folder has a `gdpr.md` with retention + erasure pointers.
- The autoupdate cron checks for `privacy: client` notes older than
  the retention window and proposes archive/erase.

## Cross-references

- `business-entity/workflows/` — per-workflow specs (lead-intake,
  proposal-drafting, ...).
- `business-entity/governance/gdpr-data-map.md` — Round 3 GDPR map.
- `docs/BUSINESS_ENTITY_SCOPE.md` § GDPR.
