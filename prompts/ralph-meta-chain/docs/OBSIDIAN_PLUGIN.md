# OBSIDIAN_PLUGIN.md

## Purpose

Specification for the Obsidian plugin surface that drives Ralph Meta Chain
from inside the user's vault. The Phase 1-6 reference implementation
already ships at `obsidian-ralph/` with a working command palette,
status bar, and side-pane views. The master-spec greenfield target is
`prompts/ralph-meta-chain/obsidian-plugin/`; this doc captures the
canonical contract going forward.

## Plugin metadata

```json
{
  "id": "ralph-meta-chain",
  "name": "Ralph Meta Chain",
  "minAppVersion": "1.5.0",
  "isDesktopOnly": true
}
```

Desktop-only is non-negotiable: the plugin spawns subprocesses (`claude`,
`python -m harness`) which Obsidian Mobile can't host.

## Commands

| ID                          | Palette name                                  | Risk class | Backed by                                |
| --------------------------- | --------------------------------------------- | ---------- | ---------------------------------------- |
| `ralph-run-research`        | Ralph: Run research-ingest pass               | MEDIUM     | `claude -p 04-research-ingest.md`        |
| `ralph-run-memory`          | Ralph: Run memory pass                        | MEDIUM     | `claude -p 01-memory-optimizer.md`       |
| `ralph-run-skills`          | Ralph: Run skills pass                        | MEDIUM     | `claude -p 02-skills-optimizer.md`       |
| `ralph-run-interaction`     | Ralph: Run interaction pass                   | MEDIUM     | `claude -p 03-interaction-optimizer.md`  |
| `ralph-run-compress`        | Ralph: Run compress pass                      | MEDIUM     | `claude -p 05-compress.md`               |
| `ralph-run-heal`            | Ralph: Run autoheal pass                      | MEDIUM     | `claude -p 06-autoheal.md`               |
| `ralph-run-evolve`          | Ralph: Run autoevolve pass                    | HIGH       | `claude -p 07-autoevolve.md`             |
| `ralph-run-update`          | Ralph: Run autoupdate pass                    | MEDIUM     | `claude -p 08-autoupdate.md`             |
| `ralph-run-full-chain`      | Ralph: Run full chain (4 → 1 → 2 → 3)         | HIGH       | sequential                                |
| `ralph-pause`               | Ralph: Pause (touch 90-Meta/STOP)             | LOW        | filesystem                                |
| `ralph-resume`              | Ralph: Resume                                  | LOW        | filesystem                                |
| `ralph-open-log`            | Ralph: Open log view                          | LOW        | side-pane                                 |
| `ralph-open-metrics`        | Ralph: Open metrics view                      | LOW        | side-pane                                 |
| `ralph-self-test`           | Ralph: Run self-test (local CI mirror)        | LOW        | `harness self-test`                       |
| (Round 6+) `ralph-control-panel` | Ralph: Open Control Panel                | LOW        | new view                                  |
| (Round 6+) `ralph-compress-current` | Ralph: Compress Current Note          | MEDIUM     | `harness compress --note <active>`        |
| (Round 6+) `ralph-promote-canonical` | Ralph: Promote Current Note To Canonical | HIGH    | edits frontmatter                         |

## Side-panes

- **Log view** (`LOG_VIEW_TYPE = ralph-log-view`) — live tail of
  `$VAULT/90-Meta/log.md`, last 200 lines, polled every 5 s.
- **Metrics view** (`METRICS_VIEW_TYPE = ralph-metrics-view`) — parses
  `metrics.ndjson`, renders 60-day SVG sparklines per axis, polled
  every 10 s.
- (Round 6+) **Control Panel** — single view summarizing pending
  approvals, escalations, autoupdate proposals, and one-click "Run
  axis" buttons.

## Status bar

`🌀 Ralph · res ✓ · mem ✓ · skl ✓ · int ✓ · cmp ✓ · hal ✓ · evo … · upd …`

Refreshed every 30 s. `✓` = today's axis status is COMPLETE in
`ralph-state.json`; `…` = pending. When `STOP` exists, prefix changes
to `⏸ Ralph`.

## Settings

```ts
interface RalphSettings {
  repoPath: string;          // absolute path to agent_testplayground checkout
  vaultPath: string;          // auto-detected from Obsidian
  claudeBin: string;          // default "claude"
  maxIterations: number;      // mirrors ralph-wiggum --max-iterations
  // Round 6+:
  ollamaUrl: string;          // default http://localhost:11434
  enableHighRiskCommands: boolean;  // default false (gates evolve / migration)
  enableExperimentalViews: boolean;  // default false
}
```

No secrets are ever stored in plugin settings. Anthropic API key lives
in `harness/.env` (gitignored). The plugin spawns `python3 -m harness`
which reads its own env.

## File API rules

The plugin operates on **plain Markdown** via Obsidian's Vault API:

- `vault.read(file)` to ingest content.
- `vault.append(file, text)` to add to log files.
- `vault.create(file, content)` for new notes.
- `vault.process(file, fn)` for atomic edits.

Never:
- call external AI APIs from inside the plugin (harness is the broker),
- implement OAuth (no Google / Apple / etc.),
- ship audio bytes anywhere (voice paths go to the local voice-server),
- delete vault files (rename to `_archive/` instead).

## Privacy

- The plugin runs **inside Obsidian's process**; it cannot see other
  applications or files outside the vault unless the user explicitly
  configures a path in settings.
- Logs surfaced in the Log view are exactly what's in
  `$VAULT/90-Meta/log.md` — no extra logging the plugin keeps for
  itself.
- The plugin never phones home (no telemetry, no auto-update except
  through Obsidian's standard plugin marketplace once published).

## Build

```bash
cd obsidian-ralph                    # Phase 1-6 reference path
npm install
npm run build                        # esbuild → main.js
ln -s "$PWD" "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

CI runs `npx tsc --noEmit -p tsconfig.json` + `npm run build` on every
push.

## Safety notes

- All Run-Pass commands invoke MEDIUM-risk operations (cron-equivalent).
  HIGH-risk commands (evolve, full-chain, future migration apply) are
  gated by `enableHighRiskCommands` in settings.
- The plugin shells out to `claude` and `python3` by absolute name from
  PATH. The user can override via settings if a non-default install
  location is needed.
- Spawn failures surface as Obsidian Notices; they also append to the
  log view automatically.

## Cross-references

- `ARCHITECTURE.md` — where the plugin sits.
- `CLAUDE_CODE_INTEGRATION.md` — the corresponding Claude Code surface.
- `CRON_JOBS.md` — the same axes run on cron without the plugin.
- `AUTOHEAL.md` — heal calls `harness self-test`; the plugin exposes
  the same.
- Phase 1-6 reference: `obsidian-ralph/manifest.json`,
  `obsidian-ralph/src/main.ts`, `obsidian-ralph/src/runner.ts`,
  `obsidian-ralph/src/log-view.ts`, `obsidian-ralph/src/metrics-view.ts`,
  `obsidian-ralph/src/status-bar.ts`.

## Next actions

To use the plugin today: `cd obsidian-ralph && npm install && npm run
build`, then symlink into `.obsidian/plugins/`. Enable from
*Settings → Community plugins* and set the repo path. The full
greenfield rebuild lands at `prompts/ralph-meta-chain/obsidian-plugin/`
in Round 6.
