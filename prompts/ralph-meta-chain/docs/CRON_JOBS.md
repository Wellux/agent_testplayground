# CRON_JOBS.md

## Purpose

The canonical cron schedule for Ralph Meta Chain, plus the install /
uninstall flow. Mirrors `prompts/ralph-meta-chain/crontab.example` and
`scripts/install.sh`, with explanations of why each axis lives at its
slot.

## Schedule (UTC)

| Time         | Axis        | Prompt                          | Hard cap | Iterations | Why this slot                                 |
| ------------ | ----------- | ------------------------------- | -------- | ---------- | --------------------------------------------- |
| `0 1 * * *`  | research    | `04-research-ingest.md`         | 25 min   | 8          | feeds inbox before memory wakes               |
| `0 2 * * *`  | memory      | `01-memory-optimizer.md`        | 25 min   | 8          | promotes inbox → atomic notes; embeds         |
| `0 3 * * *`  | skills      | `02-skills-optimizer.md`        | 25 min   | 8          | reads fresh notes for repeated patterns       |
| `0 4 * * *`  | interaction | `03-interaction-optimizer.md`   | 25 min   | 8          | A/B-tests with skills + memory ready          |
| `30 * * * *` | compress    | `05-compress.md`                | 10 min   | 4          | hourly bloat watch                            |
| `15 */6 *`   | heal        | `06-autoheal.md`                | 10 min   | 4          | supervisor heartbeat (Nate Herk pattern)      |
| `0 5 * * 0`  | evolve      | `07-autoevolve.md`              | 30 min   | 8          | weekly fitness pass after Sunday's daily run  |
| `0 6 * * 1`  | update      | `08-autoupdate.md`              | 25 min   | 8          | weekly tool/news scan (FutureTools cadence)   |

Outer wrapper for each entry:

```bash
timeout <hard-cap> bash -c \
  'i=0; until ! claude -p "$(cat $RALPH/<prompt>)" || [ $((i+=1)) -ge <max-iter> ]; do :; done'
```

**Why `until !`**: the prompt exits 0 to signal "more work to do" and
non-zero (or emits `<promise>COMPLETE</promise>`) to signal "done". The
shell loop re-feeds the same prompt while the workspace is still
producing changes — the Wiggum technique.

## Install (Linux: cron)

```bash
./scripts/install.sh --dry-run        # preview
./scripts/install.sh                  # install
```

`install.sh` is idempotent. It tags every managed line with
`# RALPH-managed: <axis>`, backs up the existing crontab to
`~/.ralph-crontab.bak.<UTC-ts>`, and refuses to clobber unmanaged entries.

## Install (macOS: launchd)

`install.sh` detects Darwin and writes
`~/Library/LaunchAgents/ai.ralph.<axis>.plist` per axis from
`scripts/launchd/ai.ralph.axis.plist.tmpl`. The template handles three
schedule shapes:

- `Hour: -1` → hourly (template post-processed to drop the Hour key).
- `Hour: -6` → every 6h via `StartInterval=21600`.
- weekly axes inject `Weekday: <0..6>` (0=Sun, 1=Mon).

Each plist is loaded via `launchctl load` after write.

## Uninstall

```bash
./scripts/uninstall.sh                # removes only `# RALPH-managed:` entries
./scripts/uninstall.sh --dry-run      # preview
```

Backs up the existing crontab before write. On macOS, plists are renamed
to `<file>.removed.<UTC-ts>` (never deleted) after `launchctl unload`.

## Pause / Resume

The chain honors `$VAULT/90-Meta/STOP`. Touch the file to halt every
prompt at its next firing; remove it to resume.

```bash
touch "$VAULT/90-Meta/STOP"     # pause
rm    "$VAULT/90-Meta/STOP"     # resume
```

The Obsidian plugin exposes `Ralph: Pause` / `Ralph: Resume` commands;
the voice-server exposes `POST /ralph/{stop,resume}`. All routes target
the same file.

## Budget envelope

Each axis has a budget block in `config.yml` capping per-pass work:

```yaml
budgets:
  memory:      { max_promotions: 10, max_mocs: 3, max_hypotheses: 5 }
  skills:      { max_new: 3, max_amended: 5, max_hypotheses: 5 }
  interaction: { max_user_profile_updates: 1, max_prompt_rewrites: 5, max_ab_experiments: 3 }
  research:    { max_repos: 30, max_inbox_files: 1 }
  compress:    { max_compressions: 5, max_weekly_rollups: 1, token_threshold: 4000 }
  heal:        { max_fixes: 3, max_escalations: 5 }
  evolve:      { max_proposals: 5, max_population_spawn: 3 }
  update:      { max_release_feeds: 12, max_bump_proposals: 5, max_news_items: 10 }
```

## Safety notes

- Cron install is HIGH-risk (modifies user state outside the repo).
  `install.sh` requires explicit invocation; never auto-installs.
- Backups are mandatory. `--dry-run` is the default expectation when
  unsure.
- Time caps + iteration caps + STOP file = three independent kill
  switches.
- The chain does **not** run on a fresh clone until `config.yml` exists
  (gitignored). `install.sh` refuses without it.

## Cross-references

- `prompts/ralph-meta-chain/crontab.example` — the entries themselves.
- `scripts/install.sh` / `scripts/uninstall.sh` — the installer.
- `scripts/launchd/ai.ralph.axis.plist.tmpl` — macOS template.
- `ARCHITECTURE.md` — where cron fits in the system.
- `APPROVAL_GATES.md` — why install is HIGH-risk.
- `AUTOHEAL.md` — heal detects cron drift and proposes reinstall.

## Next actions

To install Ralph: read `OPERATIONS_MANUAL.md` § Quick start, then run
`./scripts/install.sh --dry-run`. If the preview looks right, run
`./scripts/install.sh`. Tail `~/.ralph.log` to confirm cron firings.
