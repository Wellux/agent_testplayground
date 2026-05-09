# ROADMAP.md

## Purpose

The phased plan for the master-spec greenfield rebuild. Each round is a
discrete, scoped commit-set; the chain stays operational throughout
(Phase 1-6 reference implementation runs unchanged until the round that
explicitly retires it).

## Round-by-round

### Round 1 — Research + 18 design docs ✓

**Status:** in flight (this commit set).

Output: `research/RESEARCH_NOTES.md`, `RESEARCH_SYNTHESIS.md`,
`github-watchlist.md`, `trend-scout.md`, `source-quality-rubric.md`,
plus 18 docs/. ~25 files. Pure Markdown.

### Round 2 — Vault-template expansion

**Status:** planned.

Output: full `vault-template/00_System/` through `99_Archive/` tree per
master spec. Existing `seed/` content is preserved; vault-template
becomes a **superset** that any new vault clones from.

Files (~50 Markdown placeholders + 5 control panels):
- `vault-template/00_System/Ralph Control Panel.md`
- `vault-template/00_System/Memory Taxonomy.md`
- `vault-template/00_System/Skill Registry.md`
- `vault-template/00_System/Prompt Registry.md`
- `vault-template/00_System/Provider Registry.md`
- `vault-template/00_System/Interaction Preferences.md`
- `vault-template/00_System/Experiment Registry.md`
- `vault-template/00_System/Business Entity Control Panel.md`
- `vault-template/00_System/Repo Migration Control Panel.md`
- `vault-template/00_System/Change Log.md`
- `vault-template/02_Memory/{raw,episodic,semantic,procedural,preferences,interaction,entities,projects,decisions,business,system,canonical,hot,warm,cold}/`
- `vault-template/04_Harnesses/{ab-test-template,eval-rubric,prompt-scorecard,workflow-scorecard}.md`
- `vault-template/06_Reports/{daily-memory-report,daily-skills-report,daily-interaction-report,autoheal-report,autoupdate-proposal,research-digest}.md`
- `vault-template/08_Providers/{provider-interface,claude-code,openai-codex-deferred,gemini-ai-studio-deferred,local-models-deferred}.md`
- `vault-template/09_Migration/{inventory-report,proposed-moves,rollback-plan}.md`

`scripts/install.sh seed_vault()` extends to copy from vault-template if
present, falling back to `seed/`.

### Round 3 — Business-entity scaffold

**Status:** planned.

Output: full `business-entity/` Markdown tree per master spec. **No
scripts; no execution.** Only documents drafts and ledgers.

Files (~25 Markdown):
- governance: 7 files (operating-model, approval-gates,
  human-in-the-loop-policy, risk-register, gdpr-data-map, audit-policy,
  delegated-authority-matrix).
- workflows: 9 files (lead-intake, proposal-drafting, ...).
- ledgers: 7 files.
- templates: 6 files (offer, client-brief, meeting-summary, ...).

Round 3 must NOT activate any business autonomy. Per
`BUSINESS_ENTITY_SCOPE.md`, "send externally" is CRITICAL and never
autonomous.

### Round 4 — Migration tooling + provider scaffold

**Status:** planned.

Output (split into two commits):

(a) `migration/`:
- `migration/scripts/ralph_repo_inventory.sh` (LOW; read-only)
- `migration/scripts/ralph_classify_repo_files.sh` (LOW)
- `migration/scripts/ralph_propose_migration.sh` (MEDIUM)
- `migration/scripts/ralph_apply_migration.sh` (CRITICAL; gated)
- `migration/scripts/ralph_rollback_migration.sh` (HIGH)
- `migration/{README,migration-plan,inventory-report,file-classification,
  proposed-moves,conflicts,rollback-plan,migration-log}.md`

(b) `providers/`:
- `providers/{README,provider-interface}.md`
- `providers/claude-code/{README,hooks,commands,skills,runtime-notes}.md`
- `providers/openai-codex/{README,adapter-spec,deferred-implementation}.md`
- `providers/gemini-ai-studio/{README,adapter-spec,deferred-implementation}.md`
- `providers/local-models/{README,adapter-spec,ollama-notes,deferred-implementation}.md`

Migration `--apply` stays gated behind explicit invocation per
`APPROVAL_GATES.md`.

### Round 5 — Bash shims + JSON schemas + bats stubs

**Status:** planned.

Output:

- `scripts/ralph_*.sh` shims (5-15 lines each; wraps existing Python
  harness CLI):
  - `ralph_memory_optimize.sh` → wraps prompt #1 invocation.
  - `ralph_skills_optimize.sh` → wraps prompt #2.
  - `ralph_interaction_optimize.sh` → wraps prompt #3.
  - `ralph_context_compress.sh` → wraps prompt #5.
  - `ralph_index_vault.sh` → `harness embed --vault`.
  - `ralph_ab_harness.sh` → `harness ab`.
  - `ralph_autoheal.sh` → wraps prompt #6 / `harness self-test`.
  - `ralph_autoupdate_propose.sh` → wraps prompt #8.
  - `ralph_research_digest.sh` → `harness ingest`.
  - `ralph_daily_report.sh` → composite read of daily reports.
  - `ralph_git_audit.sh` → git log + diff summary.
  - `ralph_validate_frontmatter.sh` → schema check.
  - `ralph_check_links.sh` → broken `[[wikilink]]` scan.
  - `ralph_provider_validate.sh` → spec-conformance check.
  - `ralph_business_ledger_check.sh` → ledger schema check.
  - `scripts/lib/{common,logging,config,markdown,frontmatter,scoring,git_safety,locks,approval,paths,reports}.sh`.
- `config/ralph.config.schema.json`,
  `provider-interface.schema.json`, `memory-frontmatter.schema.json`,
  `experiment.schema.json`.
- `tests/test_shell_scripts.bats`, `test_harness.bats`,
  `test_migration_dry_run.bats`, `test_frontmatter_validation.bats`.

Round 5 adds bats to the CI workflow (gated; bats not currently in CI
image).

### Round 6 — Plugin rebuild + commands + skills + hooks

**Status:** planned.

Output:

- Greenfield Obsidian plugin at
  `prompts/ralph-meta-chain/obsidian-plugin/`. Functional parity with
  `obsidian-ralph/`; adds Round 6 commands (Compress Current Note,
  Promote To Canonical, Open Migration Control Panel, etc.).
- `prompts/ralph-meta-chain/commands/` slash-command Markdown templates.
- `prompts/ralph-meta-chain/skills/` SKILL.md files for the 8 specialist
  roles per master spec (memory-architect, prompt-evaluator, etc.).
- `prompts/ralph-meta-chain/hooks/` examples (pre-tool-use, post-tool-use,
  session-end, notification).

### Round 7 — Indexes + benchmarks + experiments

**Status:** planned.

Output:

- `prompts/ralph-meta-chain/indexes/` — vault-index, memory-index,
  skill-index, prompt-index, provider-index, business-index.
- `prompts/ralph-meta-chain/benchmarks/` — memory-quality, skill-quality,
  prompt-quality, interaction-quality, business-action-quality,
  migration-quality.
- `prompts/ralph-meta-chain/experiments/` — README, fixtures, outputs,
  reports.
- Updated bats coverage.

### Round 8 — Phase 1-6 retirement

**Status:** planned, last.

Output:
- `harness migration apply --confirmed` (the formal moment of retirement).
- `obsidian-ralph/` retired (now under `prompts/ralph-meta-chain/obsidian-plugin/`).
- `voice-server/` retired (now under `prompts/ralph-meta-chain/voice-server/`).
- `scripts/install.sh` retired (now under
  `prompts/ralph-meta-chain/install/install_cron.sh`).
- `harness/` Python package retired (the harness is now
  `prompts/ralph-meta-chain/scripts/harness/` with the same surface).

This is the only round that **deletes** anything (via `git mv` from old
path to new). The user must explicitly invoke and review.

## Sequencing notes

- Rounds 1-3 are **pure Markdown**. They cannot break tests.
- Rounds 4-7 add code under `prompts/ralph-meta-chain/` *additionally*.
  Old root-level dirs keep working.
- Round 8 retires the old paths.
- The master spec's `final implementation order` step (1-22) maps onto
  this roadmap: steps 1-2 = Round 1; steps 3-7 = Round 2; steps 8-12 =
  Rounds 3-5; steps 13-19 = Rounds 4-6; steps 20-22 = Rounds 7-8.

## Risk per round

| Round | Risk class | Reversible? |
| ----- | ---------- | ----------- |
| 1     | LOW        | yes (delete files) |
| 2     | LOW        | yes |
| 3     | LOW        | yes |
| 4     | MEDIUM     | yes (apply gated CRITICAL) |
| 5     | MEDIUM     | yes |
| 6     | MEDIUM     | yes (additive plugin) |
| 7     | LOW        | yes |
| 8     | CRITICAL   | rollback per `migration/rollback-plan.md` |

## Safety notes

- Rounds 1-7 do NOT modify the existing 34 unit tests + CI. They run
  unchanged.
- Round 8 modifies CI paths. A botched Round 8 breaks privacy guard +
  every CI job. Branch + draft PR mandatory.
- Each round must end with `harness self-test` green.

## Cross-references

- Master prompt: source of truth for the target architecture.
- `RESEARCH_NOTES.md` / `RESEARCH_SYNTHESIS.md` — Round 1 outputs that
  inform every subsequent round.
- `APPROVAL_GATES.md` — risk classes per round.
- `REPO_MIGRATION.md` — Round 8 mechanics.

## Next actions

For Round 1: this commit ships the docs + research foundation. To start
Round 2, open `vault-template/` design under
`prompts/ralph-meta-chain/seed/` for inspiration; the master spec lists
every file. Round 2 is ~50 Markdown placeholders — heavy on volume,
light on logic.
