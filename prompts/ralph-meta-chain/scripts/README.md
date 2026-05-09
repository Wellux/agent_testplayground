# scripts/

Bash shims that wrap the Phase 1-6 Python harness CLI + scheduled
prompts. Per `docs/ROADMAP.md` Round 5: each shim is 5–15 lines and
delegates to the existing `python -m harness` subcommand or to
`claude -p "$(cat ...)"`. Shared logic lives under `lib/`.

## Layout

```
scripts/
├── README.md                                ← you are here
├── lib/                              (11 helpers; sourced)
│   ├── common.sh                              flags + log/warn/error
│   ├── logging.sh                             Karpathy log-line writers
│   ├── config.sh                              read config.yml; resolve $VAULT
│   ├── markdown.sh                            frontmatter / body / wikilinks
│   ├── frontmatter.sh                         schema validation (basic)
│   ├── scoring.sh                             rubric mean + verdict math
│   ├── git_safety.sh                          require-clean / refuse-force-push
│   ├── locks.sh                               flock-based mutex per shim
│   ├── approval.sh                            approval ledger helpers
│   ├── paths.sh                               vault subfolder paths
│   └── reports.sh                             frontmatter + table writers
├── ralph_memory_optimize.sh         (LOW)     wraps prompt #1 invocation
├── ralph_skills_optimize.sh         (LOW)     wraps prompt #2
├── ralph_interaction_optimize.sh    (MEDIUM)  wraps prompt #3
├── ralph_context_compress.sh        (MEDIUM)  wraps prompt #5
├── ralph_index_vault.sh             (LOW)     `harness embed --vault-full`
├── ralph_ab_harness.sh              (LOW)     `harness ab` passthrough
├── ralph_autoheal.sh                (LOW)     wraps prompt #6 + `harness self-test`
├── ralph_autoupdate_propose.sh      (LOW)     wraps prompt #8
├── ralph_research_digest.sh         (LOW)     `harness ingest`
├── ralph_daily_report.sh            (LOW)     read-only summary of today's logs
├── ralph_git_audit.sh               (LOW)     git log + diff summary
├── ralph_validate_frontmatter.sh    (LOW)     walks $VAULT/*.md; checks frontmatter
├── ralph_check_links.sh             (LOW)     scans broken `[[wikilinks]]`
├── ralph_provider_validate.sh       (LOW)     spec-conformance check
└── ralph_business_ledger_check.sh   (LOW)     ledger-schema check
```

## Conventions

Every shim:

1. Sources `lib/common.sh` and (where relevant) `lib/logging.sh`,
   `lib/config.sh`, `lib/markdown.sh`, etc.
2. Supports `--help` and prints a standardized header.
3. Defaults to dry-run for any mutating operation.
4. Honors `90-Meta/STOP` (skips silently when present).
5. Logs one Karpathy-format line per run to `90-Meta/log.md`.

## Coexistence with Phase 1-6

The Phase 1-6 reference implementation under `harness/`,
`voice-server/`, `obsidian-ralph/`, `scripts/install.sh` is unchanged.
These shims are **additional surface** that doesn't conflict:

- `ralph_memory_optimize.sh` invokes `claude -p` against the existing
  `prompts/ralph-meta-chain/01-memory-optimizer.md`.
- `ralph_ab_harness.sh` invokes `python -m harness ab "$@"` against
  the existing `harness/harness/ab.py`.
- `ralph_validate_frontmatter.sh` is a NEW capability not covered by
  the harness; it implements vault-side validation.

When Round 8 retires the legacy paths, the shims continue to work —
they're written to find the harness via `git rev-parse` + relative
paths, not hard-coded `harness/` locations.

## Cross-references

- `docs/ROADMAP.md` § Round 5 — the spec for this round.
- `docs/CRON_JOBS.md` — when each shim fires (when wired into cron).
- `prompts/ralph-meta-chain/scripts/lib/*.sh` — the helpers each shim sources.
- `scripts/install.sh` — Phase 1-6 cron installer (still the canonical
  install path; calls `claude -p` directly, NOT these shims, for
  minimum-dependency reasons).

## Next actions

- These shims are reference utilities; cron fires `claude -p` directly.
  Use the shims for ad-hoc local invocation: `./ralph_memory_optimize.sh`.
- Round 6+ may register these as `.claude/commands/` slash-command
  handlers.
