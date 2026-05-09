---
ralph_type: provider
provider: claude-code
status: active
created: 2026-05-09
summary: "The active Ralph runtime — Claude Code."
---

# Provider: Claude Code (ACTIVE)

The Phase 1-6 reference implementation runs entirely on this surface.
Every prompt at `prompts/ralph-meta-chain/0[1-8]-*.md` is shaped for
Claude Code; every harness command (Round 5+ Bash shims) wraps a
Claude Code invocation.

## Files in this folder

- `README.md` ← you are here.
- `runtime-notes.md` — the 13-field provider-interface answers.
- `hooks.md` — pre/post-tool-use, session-end, notification.
- `commands.md` — slash command pattern (`.claude/commands/<name>.md`).
- `skills.md` — `.claude/skills/<name>.md` schema (charlie947).

## Why Claude Code

Per the master spec and Phase 1-6 history:

- Best-in-class tool surface (Read/Edit/Write/Bash/Grep/Glob/
  TodoWrite/Agent/Skill/Task/WebSearch/WebFetch/MCP).
- `CLAUDE.md` auto-loading is a first-class feature (Karpathy LLM-Wiki
  schema layer maps perfectly).
- Anthropic ralph-wiggum plugin gives us the canonical
  `<promise>COMPLETE</promise>` + `--max-iterations` exit contract.
- Hooks system enables fail-safe lifecycle integration.
- Single-binary install (`claude` CLI).

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` — full integration surface.
- `prompts/ralph-meta-chain/CLAUDE.md` — repo-level instructions.
- `seed/CLAUDE.md` — vault-level instructions seeded by install.sh.
- `vault-template/00_System/Provider Registry.md` — daily mirror.

## Next actions

- This is the active runtime; nothing to activate.
- If updating Claude Code itself, watch `08-autoupdate.md` for the
  release-feed entry that surfaces new versions.
