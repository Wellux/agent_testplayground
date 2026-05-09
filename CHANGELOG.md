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
