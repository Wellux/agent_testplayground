# CHANGELOG

All notable phases of the Ralph meta-chain shipped on branch
`claude/ralph-obsidian-cron-jobs-Mb4A9` toward [PR #1](https://github.com/Wellux/agent_testplayground/pull/1).

The work has two layers:

- **Phases 1-6**: the working reference implementation at root paths
  (`harness/`, `voice-server/`, `obsidian-ralph/`, `scripts/`).
- **Rounds 1-7**: the master-spec greenfield rebuild, all under
  `prompts/ralph-meta-chain/`. Coexists with the Phase 1-6 paths until
  Round 8 retires them via `git mv` migration apply.

Two layers, one branch. CI tests both. See `docs/ROADMAP.md` for the
phased rebuild plan.

---

## Round 11 (2026-05-09) — Launch documentation

Four new top-level docs to make the chain genuinely usable by someone
who hasn't been in the conversation history:

- **`docs/QUICKSTART_CLAUDE_CODE.md`** — git-clone-to-running guide
  for Claude Code. Prerequisites, 6-step path, troubleshooting, vault
  setup, optional cron registration. Targets <10 min from clone to
  first `/ralph-cron` invocation.
- **`docs/QUICKSTART_CODEX.md`** — same for OpenAI Codex CLI. Mirrors
  the Claude Code guide; documents Codex-specific differences
  (skills > prompts, no hooks, no Agent tool).
- **`docs/PRD.md`** — product requirements: problem statement, 6
  goals + 5 non-goals, 3 personas, user journey, architecture
  diagram, surface counts, success metrics (qualitative + quantitative),
  approval classes, 5 open questions for the next maintainer.
- **`docs/HANDOFF.md`** — comprehensive handoff for the next person:
  current state matrix, test counts (~204 cases), CI state, Kilo +
  Codex bot review history, 8 backlog items ordered by leverage with
  size estimates + designs, how-to-extend recipes (new axis, new MCP
  tool, new install target, new specialist skill), pointer index.

Plus updated entry points:
- top-level `README.md` — adds the quick-starts table at the top
- `prompts/ralph-meta-chain/README.md` — adds the new-here banner

## Round 10.4 (2026-05-09) — Codex P2-3 + P2-4 fixes

Two real correctness bugs in the Codex installer caught by the
Codex-bot review.

### P2-3: Codex prompts leaked to user-global `~/.codex/`

`install_codex.sh --scope project` (or vault) wrote prompts to the
user-global `$CODEX_HOME/prompts/` instead of the scoped install
target. Two consequences:
1. A "supposedly scoped install" silently mutated user-global Codex
   slash commands.
2. The scoped manifest then OWNED those global symlinks, so
   uninstalling a project install would remove user-global prompts.

Fix: `PROMPTS_DIR + TOML_FILE + MANIFEST_DIR` derived from `$SCOPE`
in a single case statement so all four artefact paths
(skills/prompts/toml/briefing) live under the same root per scope:

| Scope | Skills | Prompts | TOML |
| --- | --- | --- | --- |
| user | `~/.agents/skills/` | `~/.codex/prompts/` | `~/.codex/config.toml` |
| project | `<repo>/.agents/skills/` | `<repo>/.codex/prompts/` | `<repo>/.codex/config.toml` |
| vault | `<vault>/.agents/skills/` | `<vault>/.codex/prompts/` | `<vault>/.codex/config.toml` |

### P2-4: Uninstaller unconditionally stripped user-global config.toml

For project/vault installs, `WITH_MCP=no` (skips MCP) but the
uninstaller still always called `strip_mcp` against
`$CODEX_HOME/config.toml` — clobbering an unrelated user-scope MCP
block.

Fix: uninstaller reads the manifest's `with_mcp` and `toml_file` fields.
`strip_mcp()` short-circuits if `with_mcp == false`. Empty-dir
cleanup also became scope-aware so we never `rmdir $CODEX_HOME` on a
project uninstall.

### Tests added

`test_install_codex.bats` regression cases #20 and #21 (now 21/21):

- #20 pre-seeds `$CODEX_HOME/prompts/my-personal.md`, runs project
  install, asserts user-global still contains ONLY `my-personal.md`.
- #21 pre-seeds `$CODEX_HOME/config.toml` with a manually-managed
  `[mcp_servers.ralph]` block, runs project install + uninstall,
  asserts sha256 unchanged before / after / between, asserts uninstaller
  emits `manifest says with_mcp=false` skip line.

## Round 10.3 (2026-05-09) — Codex P2-2 follow-up: self-test side effects

`ralph_self_test` MCP tool said "read-only" but `harness self-test`
appends one row per check to `$VAULT/90-Meta/heal-checks.ndjson`.

Fix: added `--no-log` flag to `harness self-test`. MCP tool always
passes it (hardcoded into argv). The cron-owned `06-autoheal` axis
keeps the default logged mode for its audit trail.

## Round 10.2 (2026-05-09) — Codex P2-1 + P2-2 fixes

P2-1: install_codex.sh TOML merge could produce duplicate
`[mcp_servers.ralph]` tables (invalid TOML) when a user had a
manually-set or older-installer block without the marker comment.
Fixed: strip in two passes (marker-tagged + bare).

P2-2: `ralph_migration_dry_run` MCP tool advertised as read-only but
underlying script writes proposal Markdown. Fixed: tool description
now explicitly lists every file written + how to revert via
`git restore prompts/ralph-meta-chain/migration/`.

## Round 10.1 (2026-05-09) — MCP bug fixes + unified dispatcher

Three follow-ups on Rounds 9 + 10:

### MCP server bug fixes (caught by the new harness-integration tests)

- **`ralph_query` was passing `--limit`** to `harness query` but the
  CLI's flag is `--k`. Result: every semantic query failed with
  argparse error. Fixed.
- **`ralph_migration_dry_run` was calling `harness migration propose --dry-run`**
  but `harness` has no `migration` subcommand — migration is owned by
  `migration/scripts/ralph_propose_migration.sh`. Fixed: invokes the
  shell script and surfaces the proposed-moves + conflicts counts.

Both bugs slipped through Round 9 because the original tests only
exercised the protocol surface (initialize, tools/list, error paths)
without verifying the EXACT command-line constructed for the harness
shell-out. Added 4 regression tests with a fake `harness` binary on
PATH that records argv to a file, so future drift is caught.

### Unified `install.sh` dispatcher

`install/install.sh` is a single entry point that fans out to the
three per-target installers:

```bash
install.sh --target all                         # cron + claude-code + codex
install.sh --target claude-code,codex --scope user
install.sh --target codex --dry-run -- --without-mcp --without-prompts
install.sh --target all --uninstall
```

Per-target installers are still callable directly; the dispatcher is
purely additive. Honours `--scope`, `--dry-run`, `--uninstall`, and
forwards anything after `--` to each per-target installer (so
installer-specific flags like `--without-mcp` work without expanding
the dispatcher's own arg parser).

### Tests added (12 cases)

- `tests/test_install_dispatcher.bats` — covers usage errors, target
  expansion, `--scope` propagation, `--` passthrough, wet
  install/uninstall round-trip, dry-run.

### Counts

13 MCP server tests (was 9; +4 regression coverage) ✓
12 dispatcher bats tests (NEW) ✓
18 Codex installer bats tests ✓
13 Claude Code installer bats tests ✓
103 harness unit tests ✓

---

## Round 10 (2026-05-09) — Codex surface (shipped)

The chain becomes **executable from inside the OpenAI Codex CLI** too,
mirroring the Round 9 Claude Code install. The shared MCP server now
serves both agents (JSON config for Claude Code, TOML config for Codex).

### What landed

- **`install/install_codex.sh`** — Codex installer. `--scope user|project|vault`,
  `--dry-run`, `--uninstall`, `--with-mcp`/`--without-mcp`,
  `--without-prompts`. Idempotent; refuses to clobber; tracks every
  artefact in `<target>/.codex/.ralph-installed.json`.
- **`install/uninstall_codex.sh`** — symmetric uninstaller. Strips the
  `[mcp_servers.ralph]` block from `~/.codex/config.toml` (preserves
  user-added blocks byte-for-byte).
- **`install/AGENTS.template.md`** — Codex's auto-loaded briefing
  (equivalent of `CLAUDE.md`). Marker-tagged so the uninstaller can
  tell user-edited copies apart from RALPH-managed ones.
- **`install/CODEX_INSTALL.md`** — user-facing install guide with
  surface map, troubleshooting, coexistence notes.

### Surface mapping (Claude Code → Codex)

| Claude Code              | Codex equivalent              | Notes                                |
| ------------------------ | ----------------------------- | ------------------------------------ |
| `~/.claude/commands/`    | `~/.codex/prompts/`           | works; deprecated upstream            |
| `~/.claude/agents/`      | folded into `.agents/skills/` | Codex has no Agent-tool subagents    |
| `~/.claude/skills/`      | `~/.agents/skills/`           | direct mirror; same SKILL.md format  |
| `~/.claude/hooks/`       | _(none)_                      | Codex has no lifecycle hooks         |
| `~/.claude/.mcp.json`    | `~/.codex/config.toml`        | same MCP server; different format    |
| `CLAUDE.md`              | `AGENTS.md`                   | both auto-load from cwd-up           |

### What gets deployed

- **8 specialist skills** symlinked from `skills/<slug>/` →
  `<skills_root>/<slug>/`.
- **8 axis subagents** wrapped in skill directories (one
  `<axis>/SKILL.md` per axis, symlinked to `agents/ralph-<axis>.md`).
- **11 slash-command prompts** symlinked from `commands/*.md` →
  `~/.codex/prompts/*.md` (skip with `--without-prompts`).
- **`[mcp_servers.ralph]` block** appended to `~/.codex/config.toml`
  via text-merge that preserves all user content.
- **AGENTS.md briefing** copied to `<briefing_dir>/AGENTS.md` (only
  if not already present; never clobbers).

### Tests

- **`tests/test_install_codex.bats`** — 18 cases covering every
  install/uninstall path, including:
  - dry-run / wet / idempotent / clobber-refusal
  - TOML round-trip with pre-existing user content preserved
  - AGENTS.md marker handling (user-edited copies left alone)
  - `--without-mcp` / `--without-prompts` / `--scope project` paths
  - second-install AGENTS.md tracking (regression for the bug found
    during dev where user-kept files weren't re-tracked).
- CI's `bats` job extended with the Codex installer suite.

### Coexistence

Both installers can run independently and idempotently — they write
to disjoint paths. The shared `mcp-server/` is referenced by both;
re-installing one doesn't disturb the other.

### Verify

```bash
# Install both surfaces (or pick one)
prompts/ralph-meta-chain/install/install_claude_code.sh
prompts/ralph-meta-chain/install/install_codex.sh

# Then in a Codex session — implicit skill matching:
> "Promote the inbox notes from yesterday."
# Codex routes to ralph-memory skill via description match.

# Or explicitly:
> /ralph-cron
```

---

## Round 9 (2026-05-09) — Claude Code surface (shipped)

The chain becomes **executable from inside Claude Code** — interactive
slash commands, axis subagents, lifecycle hooks, an MCP server, and a
single idempotent installer that wires it all into `~/.claude/`,
`<repo>/.claude/`, or `$VAULT/.claude/`.

### New artefacts

- **`install/install_claude_code.sh`** — top-level installer.
  `--scope user|project|vault`, `--dry-run`, `--uninstall`, `--with-mcp`.
  Idempotent symlinker; refuses to clobber non-symlink files; tracks
  every artefact in `<target>/.claude/.ralph-installed.json`.
- **`install/uninstall_claude_code.sh`** — symmetric uninstaller.
  Removes only what the manifest tracks; preserves user-owned files.
- **`install/settings.template.json`** — reference settings.json.
- **`install/CLAUDE_CODE_INSTALL.md`** — user-facing install guide
  with surface map, troubleshooting, and verification steps.
- **3 new slash commands** for the missing axes: `/ralph-research`,
  `/ralph-compress`, `/ralph-evolve`.
- **`/ralph-cron`** — master dashboard showing all 8 axes (last run,
  status, next firing).
- **`agents/`** — 8 axis subagents (`ralph-research`, `ralph-memory`,
  `ralph-skills`, `ralph-interaction`, `ralph-compress`,
  `ralph-autoheal`, `ralph-evolve`, `ralph-update`) callable via
  `Agent(subagent_type=ralph-<axis>)`.
- **`hooks/session-start.sh`** — SessionStart hook surfacing chain
  state on every Claude Code launch (per-axis log line, inbox depth,
  open escalations, STOP sentinels). Fail-safe contract:
  never blocks, 10s timeout, no network.
- **`mcp-server/`** — zero-dep stdio MCP server exposing 4 read-only
  tools to Claude Code: `ralph_query`, `ralph_axis_status`,
  `ralph_self_test`, `ralph_migration_dry_run`. Implements
  newline-delimited JSON-RPC 2.0; ~300 LoC pure stdlib.

### Tests

- **`tests/test_install_claude_code.bats`** — 13 cases covering
  dry-run/wet/idempotent/clobber-refusal/uninstall/scope-isolation.
- **`tests/test_mcp_server.py`** — 9 protocol cases
  (initialize/ping/tools-list/tools-call/error-paths/notifications).

### CI

- New `mcp-server` job (`py_compile` + protocol smoke tests).
- `bats` job extended with the installer test suite.

### Verify

```bash
prompts/ralph-meta-chain/install/install_claude_code.sh --scope project
# then in any Claude Code session inside the repo:
/ralph-cron       # master dashboard
/ralph-memory     # per-axis dashboard
```

---

## Round 8 (2026-05-09) — Phase 1-6 retirement (shipped)

The destructive `git mv` migration that flips master-spec target
paths into the canonical layout. Five commits across three stages:

- **Stage A (`b8a6e8c`)** — read-only pipeline + RUNBOOK +
  pre-migrated retarget. Inventory → classify → propose runs clean,
  voice-multidevice retargets to `_archive/_pre-migrated/` because
  `prompts/ralph-meta-chain/docs/` already exists.
- **Stage B (`09e036e`)** — CI workflow backup + audit-log + dry-run
  apply. `STAGE_C_CI_WORKFLOW.yml` checked into git (the post-apply
  workflow). `--update-ci` flag added to the apply script; dry-run
  passes 6 gates.
- **Stage C apply (`2d2509a`)** — full apply: **65 `git mv`** moves,
  **14 path retargets** (pre-migrated archive), **1 atomic CI rewrite**
  (`.github/workflows/ci.yml` ← `STAGE_C_CI_WORKFLOW.yml`), 6 gates
  verified. Plus 3 Codex round-3 P2 fixes (compress.py YAML delimiter,
  voice-server same-second collisions, voice-server cwd).
- **Stage C P1 fixes (`f34c8c3`)** — post-apply path drift caught by
  Codex round 4: `harness/__init__.py` and `install_cron.sh` had
  `parents[N]` / `dirname/..` resolution that broke when the harness
  moved to `prompts/ralph-meta-chain/scripts/harness/`. Replaced with
  walk-up-to-`.git` `_find_repo_root()` helpers (4 regression tests).
- **Stage C `--dry-run` fix (`ac57b6b`)** — `install_cron.sh --dry-run`
  was requiring `claude` on PATH unconditionally; gated the check
  behind `[[ $DRY_RUN -eq 0 ]]`.

Result: `prompts/ralph-meta-chain/` is now the canonical layout. Old
root paths are either at master-spec targets via `git mv` or archived
under `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/<old>/`.
Rollback path: `migration/scripts/ralph_rollback_migration.sh` reads
`migration/rollback-plan.md` (mirror of moves) — all 65 moves are
reversible.

References: `migration/STAGE_C_PREVIEW.md`, `migration/STAGE_B_SUMMARY.md`,
`docs/ROUND_8_RUNBOOK.md`.

### Round 8 follow-up — Codex round-5 P2 fixes (`675c9fe`)

Three findings landed after Stage C; all fixed in one commit:

- Plugin `runHarness()` didn't pass `--vault` to the harness CLI, so
  "Run Full Index" / "Compress Current Note" / "Detect Duplicate
  Memory" / "Run Vault Diagnostics" hit the sample vault path from
  `config.example.yml` instead of the user's own.
- Voice-server captures emitted `type: voice-capture` only — no
  `ralph_type` / `created` — so the validator failed against the
  user's own inbox after the first capture. Added `ralph_type: memory`,
  `memory_layer: raw`, `memory_temperature: hot`, kept
  `type: voice-capture` as a more-specific subtype.
- `harness compress` rewrote notes with only `compressed_from` /
  `compressed_at`, stripping required fields. Now reads the original
  frontmatter and preserves `ralph_type`, `created`, `memory_layer`,
  `memory_temperature`, `tags`, `privacy` if present.

Plus 5 regression tests across `test_round6.py`, `test_smoke.py`,
`test_app.py`. Final test counts: **103 harness + 12 voice-server
= 115 unit tests**, all green.

---

## Audit (2026-05-09) — pre-Round 8 consolidation

State of the tree:

- 318 tracked files; 252 under `prompts/ralph-meta-chain/`.
- Privacy guard clean (no user identifier in tracked files).
- 72 harness tests + 9 voice-server tests = **81 unit tests**, all green.
- Both plugins (Phase 1-6 reference + Round 6 greenfield) tsc clean.
- All 4 JSON schemas parse as draft-07.
- All 5 Round 5 read-only validators pass against shipped trees.
- Migration read-only pipeline (inventory → classify → propose) detects
  60 candidate moves + 1 valid conflict (Round 1's voice-multidevice
  doc; resolution documented in `migration/migration-plan.md`).

Fixes applied this audit:

- Added missing frontmatter to `vault-template/README.md` and
  `vault-template/03_Skills/skill-template.md`.
- `ralph_check_links.sh` now skips angle-bracket placeholders
  (`[[<id>]]`, `[[<workflow>]]`) and meta-talk (`[[wikilinks]]`).
- Fixed broken `[[Pending Approvals]]` link in
  `vault-template/00_System/Ralph Control Panel.md`.
- Updated `CHANGELOG.md` (this file) and `docs/ROADMAP.md` for current state.

Round 8 (last; Phase 1-6 retirement via `harness migration apply
--confirmed`) is gated; explicit user-staged invocation required.

---

## Round 7 (2026-05-09) — Indexes + benchmarks + experiments scaffolds

21 files. Pure Markdown rubrics + index templates + experiment scaffolds.

- `prompts/ralph-meta-chain/indexes/` (7) — vault-index, memory-index,
  skill-index, prompt-index, provider-index, business-index + README.
  Authoring source for the corresponding vault-runtime catalogs.
- `prompts/ralph-meta-chain/benchmarks/` (7) — quality scorecards for
  memory, skills, prompt, interaction, business-action, migration. Each
  defines ≥ 3 scored axes (1-5) and explicit Pass thresholds.
- `prompts/ralph-meta-chain/experiments/` (4) — README + 3 .gitkeep
  (fixtures/outputs/reports). Auto-generated reports gitignored;
  curated `learnings-*.md` tracked.
- `harness/tests/test_round7.py` — 9 unittests verify file presence,
  frontmatter, cross-references, scored-axis count.

## Round 6 (2026-05-09) — Greenfield plugin + commands + skills + hooks

40 files.

- `prompts/ralph-meta-chain/obsidian-plugin/` (14) — TypeScript plugin
  with master-spec settings shape + Round 6 commands (Control Panel,
  Compress Current Note, Promote To Canonical, Vault Diagnostics, etc).
  Builds 20.9 KB main.js. Co-exists with Phase 1-6 `obsidian-ralph/`.
- `prompts/ralph-meta-chain/commands/` (8) — 7 slash-command Markdown
  templates (`/ralph-{memory,skill,experiment,autoheal,autoupdate,
  business-review,migration-plan}`) + README.
- `prompts/ralph-meta-chain/skills/` (9) — 8 specialist SKILL.md (memory-
  architect, prompt-evaluator, obsidian-vault-engineer, shell-safety-
  engineer, business-ops-analyst, repo-migration-engineer, provider-
  adapter-designer, context-compression-engineer) + README.
- `prompts/ralph-meta-chain/hooks/` (6) — 4 hook scripts (pre/post-
  tool-use, session-end, notification) + hooks.example.json + README.
  pre-tool-use.sh actively blocks `rm -rf /` etc.
- CI: new `plugin-greenfield` job tests the new plugin.
- 14 unit tests in `harness/tests/test_round6.py`.

## Round 5 (2026-05-09) — Bash shims + JSON schemas + bats stubs

36 files.

- `prompts/ralph-meta-chain/scripts/lib/` (11) — common, logging,
  config, markdown, frontmatter, scoring, git_safety, locks, approval,
  paths, reports.
- `prompts/ralph-meta-chain/scripts/ralph_*.sh` (15) — ralph_memory_
  optimize, _skills_optimize, _interaction_optimize, _context_compress,
  _index_vault, _ab_harness, _autoheal, _autoupdate_propose, _research_
  digest, _daily_report, _git_audit, _validate_frontmatter, _check_
  links, _provider_validate, _business_ledger_check.
- `prompts/ralph-meta-chain/config/` (4 schemas, draft-07) — config.yml,
  provider-interface, memory-frontmatter, experiment.
- `prompts/ralph-meta-chain/tests/` (4 bats stubs).
- 11 unit tests in `harness/tests/test_round5_shims.py`.
- Tactical bug fix: `lib/config.sh` `~/` expansion (sed replacement
  for `${v#~/}` which bash interprets as tilde-EXPANSION not literal-strip).

## Round 4 (2026-05-09) — Migration tooling + provider scaffolds

28 files.

- `prompts/ralph-meta-chain/migration/` (14) — 5 working Bash scripts
  (inventory / classify / propose / apply / rollback) with shared
  `lib/common.sh`, plus README + migration-plan. The `apply` script
  enforces six independent gates per `docs/APPROVAL_GATES.md` § Repo
  migration.
- `prompts/ralph-meta-chain/providers/` (17) — provider-interface.md
  (13-field contract) + claude-code/ (ACTIVE; 5 files) + openai-codex/
  / gemini-ai-studio/ (DEFERRED; 3 files each) + local-models/
  (PARTIAL; 4 files).
- 12 unit tests in `harness/tests/test_migration.py`.

## Round 3 (2026-05-09) — Business-entity scaffold

30 Markdown files; no scripts; no autonomous send/sign/pay paths.

- `prompts/ralph-meta-chain/business-entity/governance/` (7) —
  operating-model, approval-gates, human-in-the-loop-policy,
  risk-register, gdpr-data-map, audit-policy, delegated-authority-matrix.
- `prompts/ralph-meta-chain/business-entity/workflows/` (9) — lead-
  intake, proposal-drafting, invoice-preparation, client-follow-up,
  knowledge-work-delivery, vendor-comparison, meeting-summary, offer-
  review, task-delegation. Each draft-only; external-send is CRITICAL
  per `docs/APPROVAL_GATES.md` and never autonomous.
- `prompts/ralph-meta-chain/business-entity/ledgers/` (7) — append-
  only SOTs: decisions, commitments, pending-approvals, audit-log,
  external-communications, financial-actions (always-human), legal-
  actions (always-human).
- `prompts/ralph-meta-chain/business-entity/templates/` (6) — offer,
  client-brief, meeting-summary, task-delegation, approval-request,
  risk-review.

## Round 2 (2026-05-09) — Vault-template

62 files matching the master spec's 00_System through 99_Archive layout.

- `00_System/` (13) — Ralph Control Panel + 12 registries/control panels.
- `01_Inbox/` (4) — Daily / Voice / Research / Business.
- `02_Memory/` (15) — typed buckets (raw/episodic/.../canonical, hot/
  warm/cold).
- `03_Skills/` (1) — charlie947-schema template.
- `04_Harnesses/` (4) — A/B template + rubric + scorecards.
- `05_Research/` (3) — vault-side mirrors of `research/`.
- `06_Reports/` (6) — daily memory/skills/interaction + heal/update/digest.
- `07_Business/` (6) — ledgers + workflow pointer.
- `08_Providers/` (5) — provider-interface + claude-code + 3 deferred.
- `09_Migration/` (3) — inventory + proposed + rollback.
- `99_Archive/` (1) — append-only contract README.
- `scripts/install.sh` `seed_one()` extends to copy seed/ then
  vault-template/ in order, both `cp -n`.

## Round 1 (2026-05-08) — Research + 18 design docs

23 files. Pure Markdown.

- `prompts/ralph-meta-chain/research/` (5) — RESEARCH_NOTES.md
  (25 entries × 18 fields), RESEARCH_SYNTHESIS.md, github-watchlist.md,
  trend-scout.md, source-quality-rubric.md.
- `prompts/ralph-meta-chain/docs/` (18) — ARCHITECTURE, MEMORY_MODEL,
  CONTEXT_LIFECYCLE, CRON_JOBS, CLAUDE_CODE_INTEGRATION, OBSIDIAN_PLUGIN,
  AB_HARNESS, AUTOHEAL, AUTOUPDATE, PROVIDER_NEUTRAL_ARCHITECTURE,
  BUSINESS_ENTITY_SCOPE, VOICE_MULTI_DEVICE_FUTURE_SCOPE, SECURITY_PRIVACY,
  GOVERNANCE, APPROVAL_GATES, REPO_MIGRATION, ROADMAP, OPERATIONS_MANUAL.
  Every doc has Purpose / Usage / Safety notes / Cross-references /
  Next actions sections.

---

## Phase 6 — local CI mirror + day-1 sample inbox + Obsidian self-test command

- `harness self-test` — local CI mirror (privacy / shell / py_compile /
  unit-tests / plugin-tsc). Writes one ndjson row per check to
  `90-Meta/heal-checks.ndjson` so the autoheal prompt has structured input.
- `06-autoheal.md` updated to call `harness self-test` first; gh-CLI path
  is now the secondary fallback (was primary).
- `prompts/ralph-meta-chain/seed/00-Inbox/sample-capture.md` and
  `seed/10-Daily/2026-05-09.md` so the chain has something to ingest on
  the very first cron firing.
- Obsidian plugin gains a `Ralph: Run self-test` command.
- CHANGELOG.md (this file).

## Phase 5 — day-1 seed vault + Reflexion code loop + traces viewer

- `prompts/ralph-meta-chain/seed/` — first-day vault: schema (`CLAUDE.md`),
  starter skills (`recall`, `pr-from-branch` with Voyager prerequisites),
  starter prompts (`code-review`, `daily-summary` matching shipped fixtures),
  and bootstrap `user-profile.md`.
- `scripts/install.sh seed_vault()` — `cp -n` the seed tree into `$VAULT/`
  on first install (never overwrites).
- `harness reflect` — closes the Reflexion lesson loop in code: reads the
  most recent A/B pair from `metrics.ndjson`, asks the judge for one
  ≤80-char takeaway, and appends to the candidate's `reflections:`.
- `harness traces` — `--tail N [--axis X]` summarizes `metrics.ndjson`.
- 30 unit tests (21 harness + 9 voice-server).

## Phase 4 — 2026 agent-memory + self-evolving research

- `harness/harness/memory_backends.py` — pluggable selector with
  `local-sqlite-vec` (default), `cognee` (local-first graph), `letta`
  (OS-style tiered) opt-ins. Cited rationale: 2026 LongMemEval surveys
  (Zep 63.8% vs Mem0 49.0%); Atlan / vectorize.io / n1n.ai comparisons.
- Prompt 02 (skills): GEPA × MAP-Elites bins + Voyager skill curriculum.
- Prompt 07 (autoevolve): Reflexion lesson-loop; ADAS / OpenEvolve /
  EvoAgentX / OpenAI Cookbook citations.
- Prompt 08 (autoupdate): Cursor 3, Aider, Cline, Roo, Continue, Goose,
  Cognee, Letta, Mem0, Zep, GEPA, OpenEvolve, EvoAgentX, DSPy added.
  `harness ingest --creators @h1,@h2` resolves YouTube `@handle →
  channelId` and reads the per-channel RSS.

## Phase 3 — autoheal / autoevolve / autoupdate + voice-server

- New prompts `06-autoheal.md` (every 6h, Nate Herk supervisor pattern),
  `07-autoevolve.md` (weekly Sunday, Alex Finn ruthless iteration),
  `08-autoupdate.md` (weekly Monday, Matt Wolfe FutureTools weekly scan).
- `voice-server/` — FastAPI app for the Mac mini: `/ralph/voice` (Whisper
  local), `/ralph/run`, `/ralph/{stop,resume}`, `/ralph/status`,
  `/healthz`. Tailscale-aware origin guard.
- Apple Shortcuts JSON specs (iPhone/iPad/Watch/AirPods), Alexa Lambda +
  skill.json, Raycast extension stub.

## Phase 2 — cron installer + Obsidian plugin + Python harness + prompts 04/05

- `scripts/install.sh` / `uninstall.sh` — Linux cron + macOS launchd,
  idempotent, `--dry-run`, tagged `# RALPH-managed:` lines.
- `obsidian-ralph/` — TypeScript plugin (esbuild). Commands, status bar,
  log + metrics side-pane views.
- `harness/` — Python CLI (uv): `ab`, `embed`, `query`, `ingest`,
  `compress`. Storage = sqlite-vec + FTS5 (obra/knowledge-graph schema).
- New prompts `04-research-ingest.md`, `05-compress.md`.
- CHANGELOG retroactively notes this is when the system became "real".

## Phase 1 — three Ralph prompts + cron example

- `prompts/ralph-meta-chain/{01-memory,02-skills,03-interaction}.md`,
  `config.example.yml`, `crontab.example`, `README.md`.

## CI

A single `.github/workflows/ci.yml` runs four jobs on every PR + push:
privacy guard, shell, harness Python (py_compile + `unittest`),
voice-server Python (py_compile + `unittest`), obsidian-ralph TypeScript
(`tsc --noEmit` + esbuild build).
