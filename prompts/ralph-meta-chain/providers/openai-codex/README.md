---
ralph_type: provider
provider: openai-codex-deferred
status: deferred
created: 2026-05-09
summary: "OpenAI Codex CLI adapter — DEFERRED."
---

# Provider: OpenAI Codex CLI (DEFERRED)

The user picked Claude Code only. Codex's CLI is the closest peer (Rust,
75k stars by April 2026) and would be the most natural second adapter
if/when activation is requested.

## Why deferred

1. User explicitly picked Claude Code only.
2. Codex's cloud-sandboxed agent variant ships code to OpenAI infra
   (privacy concern documented in `docs/SECURITY_PRIVACY.md`).
3. Local-CLI variant is less mature than its cloud counterpart for the
   tool-rich workflows Ralph relies on.
4. No bandwidth in current rounds.

## Activation gate

Per `docs/APPROVAL_GATES.md`: HIGH risk, requires:

1. populated 13-field `adapter-spec.md`,
2. threat-model review (cloud sandbox cost + privacy + capability),
3. fixtures pass under the new adapter,
4. explicit user approval in the activation proposal.

## Files in this folder

- `README.md` ← you are here.
- `adapter-spec.md` — 13-field provider-interface answers (template).
- `deferred-implementation.md` — what the implementation work would
  involve; size estimate.

## Cross-references

- https://github.com/openai/codex — upstream.
- https://developers.openai.com/codex/cli — official docs.
- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: OpenAI Codex.

## Next actions

- If you want to add Codex as a comparison runtime: populate
  `adapter-spec.md`'s 13 fields, then propose activation per the gate
  above.
