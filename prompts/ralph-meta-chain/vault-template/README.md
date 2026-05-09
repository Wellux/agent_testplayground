# vault-template/

Canonical first-day vault tree per the master spec. `scripts/install.sh`
seeds these files into the user's vault on first install (`cp -n`,
never overwrites).

This supersedes the older `seed/` tree from Phase 1-6 — the seed tree
becomes a strict subset; vault-template adds the full 00_System through
99_Archive structure.

## Folders

| Folder           | Contains                                              |
| ---------------- | ----------------------------------------------------- |
| `00_System/`     | control panels + registries (Ralph's nervous system)  |
| `01_Inbox/`      | landing zones for raw captures                         |
| `02_Memory/`     | typed memory under raw/episodic/.../canonical          |
| `03_Skills/`     | skill template (real skills land in `40-Skills/`)     |
| `04_Harnesses/`  | A/B test scaffolds + scoring rubrics                  |
| `05_Research/`   | research watchlist mirror (sourced from `research/`)   |
| `06_Reports/`    | daily / weekly report placeholders                    |
| `07_Business/`   | business-entity ledgers + workflow surface            |
| `08_Providers/`  | provider adapter notes (Claude Code active; rest deferred) |
| `09_Migration/`  | migration plan + inventory + rollback                 |
| `99_Archive/`    | append-only archive (notes never disappear)           |

## Numbering

Two-digit prefixes keep folders sorted in Obsidian's file browser. They
also segment by lifecycle: 0x = system + raw, 1x-3x not used here
(reserved per Phase 1-6 numbering), 4x-6x = skills/prompts/interaction,
7x-9x = business + providers + meta. The full Phase 1-6 numbering uses
flat folders (`30-Notes/`, etc.); vault-template uses nested
`02_Memory/<type>/` for clarity inside Obsidian.

The two layouts coexist in the user's vault: 00-Inbox/ + 30-Notes/ etc.
remain canonical for the cron prompts (they reference Phase 1-6 paths);
vault-template adds the typed nested structure for Obsidian browsing.

## Cross-references

- `docs/MEMORY_MODEL.md` — typed memory layers.
- `docs/CRON_JOBS.md` — what each cron run reads/writes.
- `docs/OPERATIONS_MANUAL.md` — quick-start.
- `seed/` — Phase 1-6 starter content (still installed).
- `prompts/ralph-meta-chain/CLAUDE.md` — vault schema (mirrored at
  `00_System/Memory Taxonomy.md`).

## Next actions

`scripts/install.sh seed_vault()` already copies `seed/` content; Round 2
extends it to ALSO copy `vault-template/` content (`cp -n` so existing
files take precedence). Until that's wired, you can manually:

```bash
cp -nR prompts/ralph-meta-chain/vault-template/. "$VAULT/"
```
