---
ralph_type: research
memory_layer: research
created: 2026-05-09
status: mirror
summary: "Vault-side mirror of research/github-watchlist.md."
---

# GitHub watchlist (vault mirror)

Authoritative source: `research/github-watchlist.md`. This vault-side
copy exists so cron prompts can `Read` it without depending on the
repo path being in scope.

When the source is updated, the next autoupdate cron firing rewrites
this mirror.

## Categories (fixed)

- Claude Code core
- Ralph-loop family
- Karpathy + auto-research
- Hermes / self-evolving
- Memory layer
- Obsidian
- Coding-CLI landscape
- OpenClaw / ClaudeClaw / Codex orchestration
- Storage + UX
- DSPy / programmatic prompting
- n8n (Nate Herk parity context)

## Adding a new repo

Edit `research/github-watchlist.md` (the SOT). The autoupdate cron
re-renders this file weekly.

## Cross-references

- `research/github-watchlist.md` — source of truth.
- `research/RESEARCH_NOTES.md` — per-source confidence/stability scores.
- `08-autoupdate.md` — weekly Monday cron that uses this list.
