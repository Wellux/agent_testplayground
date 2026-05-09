---
ralph_type: memory
memory_layer: raw
memory_temperature: hot
created: 2026-05-09
status: scaffold
summary: "Business-class captures (leads, clients, vendors). Round 3+ wired."
---

# Business Inbox

> **Scaffold only.** Round 3 wires the `business-entity/` workflows;
> until then this file documents the future surface.

When Round 3 lands, this is where:

- Lead intake captures land (from a meeting transcript or a Shortcut).
- Vendor comparisons get drafted.
- Meeting summaries land before being filed under
  `business-entity/ledgers/`.
- Pre-approval drafts queue.

Per `docs/BUSINESS_ENTITY_SCOPE.md`, **everything** here is
draft/internal. External-send actions are CRITICAL gates and never
autonomous.

## Capture format (Round 3+)

```yaml
---
ralph_type: business
memory_layer: business
privacy: client
created: <YYYY-MM-DD>
client_id: <slug>      # optional
intent: lead | vendor | meeting | offer | follow-up
status: draft
---

# <Title>

## Context
...

## Action proposed
...

## Pending approval
- [ ] approval required from owner
```

## Cross-references

- `docs/BUSINESS_ENTITY_SCOPE.md` — what Ralph may/may-not do.
- `00_System/Business Entity Control Panel.md`.
- `business-entity/` — Round 3 scaffold target.
- `07_Business/` — daily-use ledgers to be linked from Round 3.
