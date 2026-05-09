---
description: |
  Triggers: "ralph autoheal", "self-test", "run the local CI mirror", "are we healthy"
allowed-tools:
  - "Read"
  - "Bash(harness:*,git:*)"
---

# /ralph-autoheal

Invoke the local CI mirror + summarize. LOW risk; read-only checks.

## Inputs

`$ARGUMENTS` — optional. Pass an axis name to run only one check
(`privacy | shell | python | unit-tests | plugin`).

## Process

1. Run `harness self-test` (with `--only $ARGUMENTS` if supplied).
2. Read the last 10 entries of `$VAULT/90-Meta/heal-checks.ndjson`.
3. Read the last 5 escalations from
   `$VAULT/60-Interactions/escalations.md`.

## Output

Render a Markdown report:

- **Self-test result** (rows: `name | ok | duration | detail`)
- **Recent heal-checks** (last 10)
- **Open escalations** (last 5)
- **Recommended action** — at most one sentence:
  - if all green: "no action; run `/ralph-autoupdate` weekly"
  - if anything red: name the specific failing check + suggested fix

## Safety

LOW risk. The self-test itself only reads files and runs `bash -n` /
`py_compile` / `tsc --noEmit` / privacy `git grep`. No mutations.

## Cross-references

- `prompts/ralph-meta-chain/06-autoheal.md` — the daily cron form.
- `harness/harness/self_test.py` — implementation.
- `docs/AUTOHEAL.md` — full design.
