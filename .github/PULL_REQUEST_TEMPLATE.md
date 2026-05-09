## Summary

What this PR does, in 1-3 bullets.

-
-

## Approval class

Per `prompts/ralph-meta-chain/docs/APPROVAL_GATES.md`:

- [ ] LOW — Markdown / docs / fixtures only
- [ ] MEDIUM — harness / plugin / shell-shim code
- [ ] HIGH — install/uninstall, schema, migration scripts
- [ ] CRITICAL — migration apply, external egress, business-entity firing

## How tested

- [ ] Harness unit tests (`uv run pytest`) green
- [ ] Voice-server unit tests green
- [ ] Plugin tsc + build clean
- [ ] Bash shims `bash -n` clean
- [ ] Read-only validators (`ralph_validate_frontmatter.sh`,
      `ralph_check_links.sh`, `ralph_provider_validate.sh`,
      `ralph_business_ledger_check.sh`) green
- [ ] Privacy guard clean (no canary phrase in tracked files)
- [ ] CI green on this branch

If a regression test was added, link the test name and what it
guards against:

## Rollback plan

How to revert this change if it breaks. Required for HIGH / CRITICAL.

For migration / schema / install changes: link the runbook
(`prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md`,
`prompts/ralph-meta-chain/migration/rollback-plan.md`).

## Cross-references

- Related issue:
- Related docs:
- Related Codex / review feedback:
