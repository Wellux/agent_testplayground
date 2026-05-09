# obsidian-ralph/ — Phase 1-6 reference (superseded in Round 6, retired in Round 8)

This directory is empty post-Round-8 (2026-05-09). The greenfield
Obsidian plugin lives at:

> **Canonical location:** `prompts/ralph-meta-chain/obsidian-plugin/`

The original Phase 1-6 reference plugin is preserved at:

> **Archive:** `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/obsidian-ralph/`

## Why two paths existed

Round 6 (2026-05-09) shipped the master-spec greenfield plugin at
`obsidian-plugin/` with functional parity plus the new commands
(Compress Current Note, Promote To Canonical, Open Migration Control
Panel, Generate Skill From Current Note, etc.). The Phase 1-6 plugin
at `obsidian-ralph/` continued to work in parallel until Round 8
retargeted it to the archive (the canonical target was already taken,
so the migration uses the pre-migrated archive convention).

## Symlinking from your vault

The Obsidian plugin link should point at the canonical path:

```bash
cd prompts/ralph-meta-chain/obsidian-plugin && npm install && npm run build
ln -s "$PWD" "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

## Migration mechanics

See `prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md`.
