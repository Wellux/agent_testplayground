# voice-server/ — Phase 1-6 reference (retired in Round 8)

This directory is empty post-Round-8 (2026-05-09). The FastAPI voice
dispatcher moved via `git mv` to its master-spec target path:

> **Canonical location:** `prompts/ralph-meta-chain/voice-server/`

The original Phase 1-6 reference implementation is preserved at:

> **Archive:** `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/voice-server/`

## Why this breadcrumb exists

Round 8's `ralph_apply_migration.sh --confirmed` performed 65 `git mv`
moves. Tooling, IDE link-following, and external pointers may still
expect `voice-server/` at the repo root — this README catches them
and routes them to the canonical path.

## Runtime status

The voice-server runtime stays gated per
`prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`.
The origin guard restricts incoming requests to Tailscale subnets
(`100.64.0.0/10`) plus loopback by default. Alexa / external egress
is opt-in only.

## Migration mechanics

See `prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md`.
