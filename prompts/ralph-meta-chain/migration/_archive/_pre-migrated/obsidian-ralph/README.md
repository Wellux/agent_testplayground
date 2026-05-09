# obsidian-ralph

Obsidian plugin frontend for the Ralph meta-chain. Drives the five prompts
(`research → memory → skills → interaction → compress`) from inside the
vault, surfaces their log + metrics in side panes, and shows the per-axis
last-run status in the status bar.

## Install (dev)

From the repo root:

```bash
cd obsidian-ralph
npm install
npm run build           # produces main.js in this folder
```

Then symlink (or copy) the plugin into your vault:

```bash
ln -s "$PWD" "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

Reload Obsidian and enable **Ralph Meta-Chain** in *Settings → Community plugins*.

## Settings

- **Repo path** — absolute path to this repo (default: parent of the
  symlinked plugin folder).
- **Vault path** — auto-detected from Obsidian.
- **Ollama base URL** — only used by `harness query` invocations (default
  `http://localhost:11434`).

No secrets are stored here. Anthropic API keys live in `harness/.env`
(gitignored).

## Commands

| Command                                      | What it does                                  |
| -------------------------------------------- | --------------------------------------------- |
| `Ralph: Run research-ingest pass`            | spawn `claude -p` against `04-research-ingest.md` |
| `Ralph: Run memory pass`                     | … `01-memory-optimizer.md`                    |
| `Ralph: Run skills pass`                     | … `02-skills-optimizer.md`                    |
| `Ralph: Run interaction pass`                | … `03-interaction-optimizer.md`               |
| `Ralph: Run compress pass`                   | … `05-compress.md`                            |
| `Ralph: Run full chain (4 → 1 → 2 → 3)`      | sequential, stops on `<promise>COMPLETE</promise>` per axis |
| `Ralph: Pause` / `Ralph: Resume`             | touch / remove `$VAULT/90-Meta/STOP`          |
| `Ralph: Open log view`                       | side-pane tail of `90-Meta/log.md`            |
| `Ralph: Open metrics view`                   | side-pane sparklines from `metrics.ndjson`    |

## Inspirations

- `brianpetro/obsidian-smart-connections` — recovery on interrupted indexing,
  status-bar UX.
- `GoBeromsu/open-connections` — multi-provider settings shape.
- `obra/knowledge-graph` — Claude Code plugin pattern for vault automation.
- OMX (workflow layer for OpenAI Codex CLI) — HUD design.
