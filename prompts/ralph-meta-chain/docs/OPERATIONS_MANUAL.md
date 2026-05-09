# OPERATIONS_MANUAL.md

## Purpose

The day-to-day playbook for running Ralph Meta Chain. Covers first
install, daily checks, weekly reviews, troubleshooting, and emergency
procedures. Pairs with `CRON_JOBS.md` (schedule reference) and
`AUTOHEAL.md` (automatic monitoring).

## Quick start

```bash
# 1. Clone + configure
git clone https://github.com/Wellux/agent_testplayground.git
cd agent_testplayground
cp prompts/ralph-meta-chain/config.example.yml \
   prompts/ralph-meta-chain/config.yml
$EDITOR prompts/ralph-meta-chain/config.yml   # set vault_path

# 2. Build the Obsidian plugin (optional)
cd obsidian-ralph && npm install && npm run build && cd ..
ln -s "$PWD/obsidian-ralph" "$VAULT/.obsidian/plugins/ralph-meta-chain"

# 3. Install the Python harness
cd harness && uv sync && cp .env.example .env && cd ..
$EDITOR harness/.env                          # add ANTHROPIC_API_KEY

# 4. Pull the local embedding model
ollama pull nomic-embed-text

# 5. Preview cron entries; install
./scripts/install.sh --dry-run
./scripts/install.sh

# 6. Confirm
tail -f ~/.ralph.log
```

## Daily checks (5 minutes)

Once a day, ideally before opening Obsidian:

1. **Status bar.** Open Obsidian; the status bar shows
   `🌀 Ralph · res ✓ · mem ✓ · …`. Any `…` after 30 minutes past the
   axis's scheduled time = check the log.
2. **Escalations.** Open
   `$VAULT/60-Interactions/escalations.md`. New entries = autoheal
   needs your attention.
3. **Inbox glance.** Open `$VAULT/00-Inbox/`. Yesterday's voice / web
   captures should be in `_processed/` by now; if they aren't, prompt
   #1 didn't run.

If everything's green: do nothing. The chain is doing its job.

## Weekly review (15 minutes)

Once a week (Sunday afternoon, before the autoevolve cron at 05:00 UTC
Monday):

1. **Read the autoupdate digest** at `00-Inbox/futuretools-YYYY-Www.md`.
   Skim the Releases + News + Proposed Bumps sections.
2. **Read the autoevolve proposals** in `30-Notes/<id>-evolve-*.md`
   with `status: open`. Approve or reject each.
3. **Read the metrics summary**: `harness traces --tail 200 --axis
   interaction`. Look for prompts losing 3 A/Bs in a row.
4. **Read this week's reflections**: `git grep "^  - " 50-Prompts/ |
   grep reflections` to see what Ralph learned.

Actions you might take:
- merge a bump-proposal: `cd harness && uv lock --upgrade-package <pkg>`
  + run unit tests + commit.
- approve a skill deprecation: edit
  `40-Skills/<slug>.md` to set `status: deprecated`.
- close an old escalation: edit
  `60-Interactions/escalations.md` to mark resolved.

## Pause / Resume

```bash
# Pause every cron firing
touch "$VAULT/90-Meta/STOP"

# Resume
rm    "$VAULT/90-Meta/STOP"
```

Or use the Obsidian command palette: `Ralph: Pause` / `Ralph: Resume`.

The voice-server `POST /ralph/{stop,resume}` endpoints have the same
effect.

## Manual axis run

To run a specific axis right now (e.g. after a big inbox dump):

```bash
# Memory promotion
claude -p "$(cat prompts/ralph-meta-chain/01-memory-optimizer.md)"

# Or via the Obsidian palette: Ralph: Run memory pass

# Or via the voice-server (if running):
curl -X POST http://localhost:7117/ralph/run \
  -H 'content-type: application/json' \
  -d '{"axis":"memory"}'
```

## Troubleshooting

### "Everything is `…` in the status bar"

- `$VAULT/90-Meta/ralph-state.json` doesn't exist or is stale. Run
  `harness self-test` to populate it.
- Check `~/.ralph.log` for cron errors.
- Verify `claude` is on PATH: `which claude`.
- Verify `harness/.env` has a valid `ANTHROPIC_API_KEY`.

### "Embeddings are blank"

- Ollama not running: `ollama serve` then
  `ollama pull nomic-embed-text`.
- `harness embed --vault` to reindex. Capped at 5 minutes; for big
  vaults run multiple times until convergence.

### "Prompt #1 isn't promoting anything"

- `$VAULT/00-Inbox/` empty.
- Daily note missing for today (some prompts skip on missing daily).
- Check `60-Interactions/escalations.md` for BLOCKER entries.

### "Self-test fails on plugin"

- Most likely `obsidian-ralph/node_modules/` missing.
  `cd obsidian-ralph && npm ci`.
- TypeScript errors: `cd obsidian-ralph && npx tsc --noEmit`.

### "harness ab returns rc=64"

- Argparse rejected the args. Run `harness ab --help`.
- Probably a missing `--fixture` path.

### "Cron drift"

- `crontab -l | grep '# RALPH-managed:'` should show 8 lines.
- Missing? Re-run `./scripts/install.sh`.
- Multiple? Run `./scripts/uninstall.sh` then reinstall.

### "Voice-server won't start"

- Port 7117 in use: `lsof -i :7117`.
- Tailscale not running: `tailscale up`.
- Whisper missing: `brew install whisper-cpp`.

## Emergency procedures

In order of escalation:

1. **STOP file** — `touch $VAULT/90-Meta/STOP` halts every cron at next
   tick. Reversible: `rm`.
2. **Uninstall cron** — `./scripts/uninstall.sh`. Removes only
   `# RALPH-managed:` entries. Reversible: re-run install.sh.
3. **Disable plugin** — Obsidian *Settings → Community plugins → Ralph
   Meta Chain → toggle off*. Reversible: toggle on.
4. **Disable voice-server** — `launchctl unload
   ~/Library/LaunchAgents/ai.ralph.voice-server.plist`. Reversible:
   `launchctl load`.
5. **Disable Tailscale** — `tailscale down`. Cuts off cross-device
   traffic. Reversible: `tailscale up`.
6. **Disable Alexa skill** — disable in Alexa app. Reversible.
7. **Revoke API key** — delete and regenerate at
   https://console.anthropic.com. Replace `harness/.env`.
8. **Restore vault from backup** — assumes user has Obsidian Sync /
   git / iCloud / Time Machine backup. Ralph never erases vault content,
   so this shouldn't be needed.

## Logs to watch

| Log                                      | What it tells you                           |
| ---------------------------------------- | ------------------------------------------- |
| `~/.ralph.log`                            | every cron firing's stdout/stderr           |
| `~/.ralph-voice.log`                      | every voice-server request                   |
| `$VAULT/90-Meta/log.md`                   | per-axis success summary (Karpathy format)   |
| `$VAULT/90-Meta/heal-log.md`              | per-heal-pass detail                          |
| `$VAULT/90-Meta/heal-checks.ndjson`       | per-check rows from `harness self-test`      |
| `$VAULT/90-Meta/metrics.ndjson`           | per-experiment rows from `harness ab`        |
| `$VAULT/60-Interactions/escalations.md`   | what needs your attention                     |

## Backups

The chain doesn't manage backups — the user does. Recommendations:

- **Vault**: Obsidian Sync OR git OR iCloud Drive. Pick one.
- **Repo**: GitHub. Already in place.
- **Crontab**: `~/.ralph-crontab.bak.<UTC-ts>` written automatically by
  install/uninstall.
- **Embeddings.db**: regenerable; `harness embed --vault` from scratch.
- **API key**: in a password manager, NOT only in `.env`.

## Safety notes

- **Never run `./scripts/install.sh --apply` from CI.** It modifies the
  user's host crontab. CI only runs `bash -n` syntax checks.
- **Review every CRITICAL proposal in `30-Notes/<id>-*.md` carefully.**
  Apply only after reading the rollback plan.
- **The chain runs on cron, not on event triggers.** A captured thought
  from your phone won't be promoted until the next 02:00 UTC firing.
  Run a manual memory pass if you need it sooner.

## Cross-references

- `CRON_JOBS.md` — schedule reference.
- `AUTOHEAL.md` — automatic monitoring.
- `APPROVAL_GATES.md` — risk classes.
- `SECURITY_PRIVACY.md` — emergency stop.
- `ROADMAP.md` — what's coming.
- Phase 1-6 reference: `harness/`, `voice-server/`, `obsidian-ralph/`,
  `scripts/`, `prompts/ralph-meta-chain/0[1-8]-*.md`.

## Next actions

If you've never run Ralph: follow Quick Start above.
If you have: skim Daily Checks every morning; do Weekly Review on
Sunday afternoon. Everything else is automatic.
