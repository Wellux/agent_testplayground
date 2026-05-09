---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only ledger of every external-bound communication."
---

# External Communications Ledger

> **Append-only.** Every message that leaves the boundary (proposal
> sent, invoice forwarded, follow-up emailed, contract executed) gets
> a row here. The send itself is CRITICAL and never autonomous — Ralph
> drafts, the user sends, and either party logs the send here.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: external-communication
ts: <ISO_TS>
direction: outbound | inbound
counterparty: <name>
counterparty_subject_id: <gdpr-pseudonym>     # if privacy: client
channel: email | proposal-tool | accounting-tool | calendar | manual | phone | meeting
subject: "<one-line subject>"
related: ["[[<commitment-id>]]", "[[<proposal-note>]]", "[[<approval-id>]]"]
attachments: [<filename>, ...]
audit_log_ref: "[[<audit-log-id>]]"     # cross-link
---

# <Subject>

## Summary
<one paragraph: what was sent, what response (if any) was received>

## Approval (if outbound)
- approver: <user>
- approved_at: <ISO_TS>

## Sent
- sent_by: <user>
- sent_at: <ISO_TS>
- channel: <channel>

## Received (if inbound)
- received_at: <ISO_TS>
- response_pending: true | false

## Follow-up due
- by: <YYYY-MM-DD>
- handled_in: "[[<follow-up-note>]]"
```

## Outbound (sent)

(append below; sorted by `ts` DESC)

## Inbound (received)

(separate log of incoming counterparty communications, since the
client-follow-up workflow needs to know what's been received)

## Bounced / failed

(if a send fails, log here so retry tracking is auditable)

## Cross-references

- `workflows/proposal-drafting.md`, `client-follow-up.md`,
  `invoice-preparation.md`, `knowledge-work-delivery.md`.
- `ledgers/audit-log.md` — every outbound entry must reference an
  audit-log entry (CRITICAL invariant).
- `governance/gdpr-data-map.md` — counterparty data carries GDPR
  obligations.
