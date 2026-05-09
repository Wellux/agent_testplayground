---
ralph_type: provider
provider: openai-codex-deferred
status: deferred
created: 2026-05-09
summary: "What activating the OpenAI Codex adapter would involve."
---

# OpenAI Codex — Deferred Implementation

Estimate of the engineering work required to activate this adapter.
Round 5+ if/when the user approves activation.

## Estimated work

| Component                              | Effort      |
| -------------------------------------- | ----------- |
| Populate `adapter-spec.md`              | 0.5 day     |
| Implement `harness/.../codex_adapter.py` | 2-3 days   |
| Permission allowlist mapping            | 1 day       |
| Hook stubs (Codex-equivalent)            | 1-2 days    |
| Fixture replay against Codex            | 1 day       |
| Cost-aware routing in autoupdate         | 1 day       |
| Threat-model review                      | 0.5 day     |
| Total                                    | ~7-10 days  |

## Pre-requisites (from user)

1. Approval to incur Codex API costs.
2. Approval for the cloud-sandbox path's data-egress profile.
3. Decision on whether Codex becomes a parallel runtime (run both)
   or a fallback (Claude Code primary; Codex on outage).

## What the activation PR would contain

- `harness/harness/codex_adapter.py` — new module implementing the
  13-field provider interface.
- `harness/harness/__main__.py` — `--provider` flag added; default
  stays `claude-code`.
- `harness/fixtures/*.yml` — annotated with provider-portable
  metadata (no schema change).
- Tests: smoke + 2-3 fixture replays.

## What the activation PR would NOT contain

- Hook script equivalents (Claude Code hooks stay Claude-Code-only).
- Slash commands (Codex doesn't have them).
- The autoupdate cron's release-feed scanner — that's already there
  for `openai/codex` per `08-autoupdate.md`.

## Cross-references

- `providers/openai-codex/adapter-spec.md` — the 13-field template.
- `docs/APPROVAL_GATES.md` § Provider — activation gate.
- `docs/ROADMAP.md` § Round 5+ — when this could land.

## Next actions

- Open a proposal note in `30-Notes/` titled "Activate Codex adapter"
  with the cost / privacy / capability rationale.
- Wait for explicit user approval per the activation gate.
