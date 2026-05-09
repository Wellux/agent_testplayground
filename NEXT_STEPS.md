# NEXT_STEPS.md

Post-merge handoff for `Wellux/agent_testplayground` after PR #1
landed (2026-05-09). The master-spec greenfield is now on `main`.

## State of the repo

- `main` HEAD includes Rounds 1-8 (research → docs → vault-template →
  business-entity → migration → providers → bash shims → JSON schemas
  → bats stubs → plugin rebuild → indexes/benchmarks/experiments →
  Phase 1-6 retirement via `git mv`).
- A follow-up PR is open with **5 post-merge polish commits**:
  - Bundle A: 3 Codex round-5 P2 fixes + 5 regression tests.
  - Bundle B: 5 doc updates (ROADMAP ✓, CHANGELOG Round 8 entry,
    OPS_MANUAL paths, CLAUDE.md, root README rewrite).
  - Bundle C: 7 GitHub convention files (LICENSE, CONTRIBUTING,
    SECURITY, CODE_OF_CONDUCT, 2 issue templates, PR template).
  - Bundle D: 4 legacy-path breadcrumb READMEs (`harness/`,
    `voice-server/`, `obsidian-ralph/`, `scripts/`).
  - Bundle E: indexing bootstrap shim + `INDEXING.md` + this file.

Final test counts: **103 harness + 12 voice-server = 115 unit tests**,
all green; both plugins tsc clean; `bash -n` clean; privacy clean;
all 5 read-only validators clean.

## Codex feedback summary

Across 5 review rounds, Codex surfaced 13 P1/P2 findings; all 13 are
fixed with regression tests:

- **Round 1**: 3 × P2 (reflect.py YAML delimiter, voice-server
  same-second collisions, voice-server cwd inheritance).
- **Round 2**: 3 × P2 (deferred to round 1 because they recurred).
- **Round 3**: 3 × P2 (compress.py YAML delimiter, voice-server
  same-second, voice-server cwd) — landed with Stage C apply.
- **Round 4**: 2 × P1 path drift (`harness/__init__.py` and
  `install_cron.sh` post-Round-8 path resolution).
- **Round 5**: 3 × P2 (plugin `runHarness()` missing `--vault`,
  voice-server frontmatter missing `ralph_type` / `created`, harness
  compress stripping required frontmatter).

All fixes use the walk-up-to-`.git` pattern for repo root resolution
(replaces fragile `parents[N]`).

## Pre-merge options for the follow-up PR

1. **Wait for CI green + admin-merge.** Follow-up PR is small and
   reviewable; CI will run all 8 jobs.
2. **Disable Kilo branch-protection.** Kilo (external SaaS scanner)
   kept timing out on the 29k-line first PR. The follow-up PR is
   smaller (~24 files) so Kilo may pass — but if it fails again,
   disable as required check.
3. **Just merge.** This is your repo; `gh pr merge --admin` is fine.

## Post-merge install (real host)

```bash
# 1. Clone fresh
git clone https://github.com/Wellux/agent_testplayground.git
cd agent_testplayground

# 2. Configure
cp prompts/ralph-meta-chain/config.example.yml \
   prompts/ralph-meta-chain/config.yml
$EDITOR prompts/ralph-meta-chain/config.yml      # set vault_path

# 3. Sync the harness
cd prompts/ralph-meta-chain/scripts/harness && uv sync \
   && cp .env.example .env
$EDITOR prompts/ralph-meta-chain/scripts/harness/.env  # ANTHROPIC_API_KEY
cd -

# 4. Install Ollama + bootstrap the vault index
brew install ollama coreutils       # or curl install on Linux
ollama serve &
./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh           # dry-run
./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh --apply   # real

# 5. Install cron / launchd
./prompts/ralph-meta-chain/install/install_cron.sh --dry-run
./prompts/ralph-meta-chain/install/install_cron.sh

# 6. Tail the log
tail -f ~/.ralph.log
```

## Plugin install

```bash
cd prompts/ralph-meta-chain/obsidian-plugin
npm install && npm run build
ln -s "$PWD" "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

Then in Obsidian: *Settings → Community plugins → Ralph Meta Chain →
toggle on*. Set `repoRoot` and `vaultRoot` in plugin settings.

## First-week health checks

Daily (5 min):
- Status bar should show `🌀 Ralph · res ✓ · mem ✓ · skl ✓ · int ✓`.
- Glance at `$VAULT/60-Interactions/escalations.md`.
- Glance at `$VAULT/00-Inbox/`; yesterday's captures should be in
  `_processed/`.

Weekly (15 min, Sunday before 05:00 UTC Monday):
- Read autoupdate digest at `00-Inbox/futuretools-YYYY-Www.md`.
- Read autoevolve proposals in `30-Notes/<id>-evolve-*.md`.
- `cd prompts/ralph-meta-chain/scripts/harness && uv run python -m harness traces --tail 200 --axis interaction`.

Tune budgets in `prompts/ralph-meta-chain/config.yml` if any axis is
hitting `max_tokens` or `max_seconds`.

## Failure modes + rollback

- **Cron drift**: re-run
  `./prompts/ralph-meta-chain/install/install_cron.sh`.
- **Plugin crash**: disable in Obsidian settings; re-build.
- **Voice-server stuck**: `launchctl unload …`; re-load when ready.
- **Round 8 rollback**: last resort. Run
  `./prompts/ralph-meta-chain/migration/scripts/ralph_rollback_migration.sh`.
  Returns the tree to pre-Stage-C layout. CI workflow restored from
  most recent `ci-backup-<UTC>.yml`.

See `prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md` (Emergency
procedures) for the full escalation order.

## Future rounds (deferred)

| Round | Scope                                     | Trigger                       |
| ----- | ----------------------------------------- | ----------------------------- |
| 9     | Activate one provider adapter             | Codex CLI (most mature) or local Ollama |
| 10    | Voice multi-device runtime                | Per `VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` phased plan |
| 11    | Business-entity workflows firing on cron  | Per-workflow approval; "send externally" stays manual forever |
| 12+   | Adapter parity (Codex + Gemini + local)   | After Round 9 telemetry shows gaps |

Each round opens its own PR with a CRITICAL approval-class review.

## Single-page navigation

| Doc                                                                  | When to read                          |
| -------------------------------------------------------------------- | ------------------------------------- |
| [`README.md`](README.md)                                              | First touch; overview + quick start   |
| [`CONTRIBUTING.md`](CONTRIBUTING.md)                                  | Before opening a PR                   |
| [`SECURITY.md`](SECURITY.md)                                          | Before reporting a vulnerability      |
| [`prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md`](prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md) | Daily / weekly playbook |
| [`prompts/ralph-meta-chain/docs/INDEXING.md`](prompts/ralph-meta-chain/docs/INDEXING.md) | Embedding bootstrap          |
| [`prompts/ralph-meta-chain/docs/ROADMAP.md`](prompts/ralph-meta-chain/docs/ROADMAP.md) | Round-by-round shipping log |
| [`prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md`](prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md) | Round 8 mechanics + rollback |
| [`prompts/ralph-meta-chain/docs/APPROVAL_GATES.md`](prompts/ralph-meta-chain/docs/APPROVAL_GATES.md) | Risk classification |
| [`prompts/ralph-meta-chain/CHANGELOG.md`](prompts/ralph-meta-chain/CHANGELOG.md) | What shipped when               |

You're set. Run the install, watch the first cron tick, enjoy.
