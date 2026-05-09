# obsidian-plugin/ — Greenfield Obsidian Plugin (Round 6)

The master-spec target plugin. Functional parity with the Phase 1-6
reference at `obsidian-ralph/`, plus the Round 6 commands per
`docs/CLAUDE_CODE_INTEGRATION.md` and `docs/OBSIDIAN_PLUGIN.md`.

The Phase 1-6 plugin stays at `obsidian-ralph/` until Round 8 retires
it via the migration apply.

## Build

```bash
cd prompts/ralph-meta-chain/obsidian-plugin
npm install
npm run build              # esbuild → main.js
ln -s "$PWD" "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

Reload Obsidian → **Settings → Community plugins → Ralph Meta Chain**.

## Settings

All paths and feature flags from the master spec, defaulting to safe
behavior:

| Setting                         | Default | Notes                                                    |
| ------------------------------- | ------- | -------------------------------------------------------- |
| `vaultRoot`                      | auto-detected | from Obsidian's adapter                                |
| `repoRoot`                       | (empty) | absolute path to agent_testplayground checkout            |
| `userIdentityEmail`              | (empty) | metadata only; never OAuth — leave empty unless needed   |
| `compressionThreshold`            | 4000     | word-count above which a note is compress-eligible       |
| `hotMemoryWindowDays`             | 7        | demote to warm beyond this                                |
| `coldMemoryWindowDays`            | 90       | demote to cold beyond this                                |
| `enableExperimentalCommands`      | false    | gates HIGH-risk commands                                  |
| `enableAutoCompression`           | false    | allow compress without per-note confirm                   |
| `enableGraphRanking`              | false    | reserved                                                  |
| `enableBusinessEntityScaffold`    | true     | show business-entity routes                                |
| `enableProviderNeutralScaffold`   | true     | show provider registry routes                              |
| `claudeBin`                       | claude   | on PATH                                                   |
| `pythonBin`                       | python3  | on PATH                                                   |
| `maxIterations`                   | 8        | ralph-wiggum cutoff                                       |

## Commands

### Phase 1-6 parity

| Command                                  | What it does                                  |
| ---------------------------------------- | --------------------------------------------- |
| Ralph: Run research / memory / skills / interaction / compress / heal / evolve / update pass | spawn `claude -p <prompt>` |
| Ralph: Run full chain (4 → 1 → 2 → 3)   | sequential                                     |
| Ralph: Run self-test (local CI mirror)   | `python -m harness self-test`                 |
| Ralph: Pause / Resume                    | touch / remove `90-Meta/STOP`                  |
| Ralph: Open log view / metrics view      | side-pane views                                |

### Round 6 additions

| Command                                                | What it does                                                        |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| Ralph: Open Control Panel                              | new dashboard side-pane                                              |
| Ralph: Run Full Index                                  | `harness embed --vault-full`                                          |
| Ralph: Run Memory Index                                | `harness embed --since 24h`                                           |
| Ralph: Compress Current Note                           | `harness compress --note <active>`                                    |
| Ralph: Generate Skill From Current Note                | (stub — points at 02-skills-optimizer.md)                             |
| Ralph: Generate Experiment From Current Note           | (stub — points at 04_Harnesses/)                                       |
| Ralph: Promote Current Note To Canonical Memory        | sets `stability: canonical` in frontmatter (HIGH-risk)               |
| Ralph: Archive Stale Context                           | `harness compress --older-than 7d`                                    |
| Ralph: Detect Duplicate Memory                         | semantic-query for duplicates                                          |
| Ralph: Create Business Approval Request                | opens `business-entity/ledgers/pending-approvals.md`                  |
| Ralph: Open Provider Registry                          | opens `00_System/Provider Registry.md`                                |
| Ralph: Open Migration Control Panel                    | opens `00_System/Repo Migration Control Panel.md`                     |
| Ralph: Run Vault Diagnostics                           | runs `ralph_validate_frontmatter.sh` + `ralph_check_links.sh`         |

## Side panes

- **Control Panel** — status per axis, quick-action buttons, pending-approvals count.
- **Log view** — live tail of `90-Meta/log.md`.
- **Metrics view** — counts per axis + 60-day SVG sparklines for memory / skills / interaction.

## Privacy

The plugin runs entirely inside Obsidian's process. It:

- Never calls external AI APIs (the harness is the broker).
- Never implements OAuth.
- Never ships audio anywhere (voice paths go to the local Mac mini
  voice-server per Phase 3).
- Stores no secrets in plugin settings (Anthropic API keys live in
  `harness/.env`, gitignored).
- Has no telemetry, no auto-update beyond Obsidian's standard plugin
  marketplace.

## How this differs from `obsidian-ralph/`

- Lives at the master-spec path (`prompts/ralph-meta-chain/obsidian-plugin/`).
- Master-spec settings shape (`vaultRoot` / `repoRoot` /
  `enableBusinessEntityScaffold` / etc).
- Round 6 commands shipped (Control Panel, Promote To Canonical,
  Vault Diagnostics, etc).
- New Control Panel side pane.
- Tries new path first, falls back to old `harness/` for graceful
  coexistence during Round 7 / before Round 8 retirement.

## Cross-references

- `docs/OBSIDIAN_PLUGIN.md` — full design.
- `docs/CLAUDE_CODE_INTEGRATION.md` — slash-command surface.
- `docs/ROADMAP.md` § Round 6.
- `obsidian-ralph/` — Phase 1-6 reference (still functional; retires
  in Round 8).

## Next actions

- Build with `npm install && npm run build`.
- Symlink into your vault's `.obsidian/plugins/`.
- Round 7 wires this plugin's tests into `tests/test_shell_scripts.bats`.
- Round 8 retires `obsidian-ralph/`.
