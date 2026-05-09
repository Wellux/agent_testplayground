# Security policy

Ralph Meta Chain is a local-first agent: by default, the only network
egress is to the Anthropic API for Claude Code invocations. Embeddings
run locally via Ollama; voice / multi-device traffic stays on Tailscale;
business-entity workflows draft only and never auto-send.

## Reporting a vulnerability

Please **do not** open public GitHub issues for security-sensitive
reports.

- File a private security advisory:
  <https://github.com/Wellux/agent_testplayground/security/advisories/new>
- Or email the maintainer (contact via repo profile).

We aim to acknowledge within 7 days. For accepted reports, we coordinate
disclosure timing with the reporter.

## Supported versions

| Version            | Supported          |
| ------------------ | ------------------ |
| `main` HEAD        | ✅ — latest fixes shipped here |
| Round 8 + later    | ✅                 |
| Pre-Round-8 forks  | ❌ — please pull master-spec layout |

The active branch as of 2026-05-09 is
`claude/ralph-obsidian-cron-jobs-Mb4A9` (PR #1). Once merged,
`main` is the supported line.

## Threat model

See
[`prompts/ralph-meta-chain/docs/SECURITY_PRIVACY.md`](prompts/ralph-meta-chain/docs/SECURITY_PRIVACY.md)
for the full threat model. Key invariants:

1. **No real user identifiers in tracked files.** A privacy guard CI
   job blocks the canary phrase and rejects any commit that introduces
   it.
2. **No external embedding endpoints by default.** Embeddings go to
   `localhost:11434` (Ollama) only.
3. **API keys live in `.env` files** that are gitignored. The repo
   contains only `.env.example` templates.
4. **Voice-server has an origin guard.** By default, only
   `100.64.0.0/10`, `127.0.0.0/8`, and `::1/128` may reach the
   server. Off-subnet requests get 403.
5. **Migration apply is CRITICAL-gated.** It refuses to run without
   `--confirmed`, with a tracked CI backup written to
   `.github/workflows/ci-backup-<UTC>.yml` first.
6. **Business-entity workflows draft only.** "Send externally" is
   never autonomous per
   [`prompts/ralph-meta-chain/docs/BUSINESS_ENTITY_SCOPE.md`](prompts/ralph-meta-chain/docs/BUSINESS_ENTITY_SCOPE.md).

## What counts as a vulnerability

- Anything that could leak user data (vault content, API keys, voice
  recordings) outside the user's machine.
- Anything that bypasses the approval gates documented in
  [`prompts/ralph-meta-chain/docs/APPROVAL_GATES.md`](prompts/ralph-meta-chain/docs/APPROVAL_GATES.md).
- Anything that turns a draft proposal into an autonomous action without
  explicit user invocation.
- Path-traversal, command-injection, or arbitrary-write bugs in the
  harness, voice-server, plugin, install scripts, or shell shims.
- A regression in the privacy guard, voice-server origin guard, or
  embedding local-first guarantee.

## What is NOT a vulnerability

- The user opting into Tailscale-cross-device voice routing.
- The user manually running `harness migration apply --confirmed`.
- The user setting `RALPH_TRUSTED_SUBNETS` to allow more subnets.
- A.SaaS PR scanner timing out (Kilo etc.) — that is a CI
  configuration concern, not a security issue.

Thank you for helping keep Ralph Meta Chain safe.
