# AUTOHEAL.md

## Purpose

Specifies the heal axis: a six-hourly supervisor that surveys the chain's
heartbeat, runs a local CI mirror (`harness self-test`), fixes safe
drift, and escalates the rest. Inspired by Nate Herk's "centralized
assistant managing specialized sub-agents" pattern and Hermes Agent's
heartbeat + zombie detection.

## Cadence

Cron: `15 */6 * * *` (every 6 hours, offset 15 min from compress to
avoid contention). Hard cap 10 minutes; max 4 iterations.

## Inputs

- `90-Meta/ralph-state.json` — last-run-per-axis pointers.
- `90-Meta/log.md` tail.
- `90-Meta/metrics.ndjson`.
- `90-Meta/heal-checks.ndjson` — written by `harness self-test`.
- (Optional) PR check status via `mcp__github__pull_request_read get_check_runs`.
- `00-Inbox/_processed/`, `30-Notes/_archive/` for filesystem drift.

## Modes

| Flag             | Meaning                                                  |
| ---------------- | -------------------------------------------------------- |
| `--check`         | run `harness self-test` only; print summary; no writes   |
| `--dry-run`       | propose fixes; touch nothing                              |
| `--apply-safe`    | apply LOW-risk fixes; escalate the rest                   |
| `--report`        | render heal report only; do not run checks               |

The cron firing runs `--apply-safe`. Manual invocations typically use
`--check` or `--dry-run`.

## Diagnoses

| Symptom                                         | Threshold                                  | Severity  |
| ----------------------------------------------- | ------------------------------------------ | --------- |
| axis missing from `ralph-state.json`             | first run                                  | INFO      |
| `last_run.date` ≥ 2 days old (daily axes)        |                                            | WARN      |
| `last_run.timestamp` ≥ 25 hours old (compress)   |                                            | WARN      |
| `last_run.status != "COMPLETE"` for 2 runs       |                                            | ERROR     |
| `harness self-test` privacy fail                 |                                            | BLOCKER   |
| `harness self-test` shell fail                   |                                            | ERROR     |
| `harness self-test` python fail                  |                                            | ERROR     |
| `harness self-test` plugin fail                  |                                            | WARN      |
| broken `[[wikilink]]`                            | target archived/missing                    | INFO      |
| `embeddings.db` 0 bytes                          |                                            | WARN      |
| Ollama unreachable                               | `curl /api/embeddings` fails                | INFO      |
| `claude` not on PATH                             |                                            | ERROR     |
| `harness` not on PATH                            |                                            | ERROR     |
| stale `STOP` file                                | > 7 days old                                | INFO      |
| cron drift (Linux)                                | no `# RALPH-managed:` lines                | ERROR     |

## Safe fixes (`--apply-safe`)

- create missing vault subfolders (`mkdir -p`),
- rewrite broken `[[wikilink]]` whose target was archived → link to the
  `_archive/<id>-original.md` path,
- empty `embeddings.db` → call `harness embed --vault-full` (capped at
  5 minutes; bail on error),
- chmod scripts executable,
- create missing `90-Meta/heal-checks.ndjson` placeholder.

Safe fixes apply without approval (LOW risk).

## Escalations

Anything not in the safe-fix list lands in
`60-Interactions/escalations.md` as:

```markdown
## [<UTC ISO>] <severity> — <axis> — <one-line symptom>
**Diagnosis:** <2-3 sentences>
**Suggested fix:** <bash one-liner OR "manual: <description>">
**Will retry in:** <next-heal-window>
```

Severities: `INFO | WARN | ERROR | BLOCKER`. BLOCKER means the chain
cannot make progress until the user acts. The Obsidian status bar shows
the highest-severity open escalation.

## Local CI mirror

`harness self-test` runs five checks (one ndjson row per check):

1. **privacy** — `git grep` for the user-identifier needle, excluding
   the workflow file via pathspec.
2. **shell** — `bash -n scripts/install.sh scripts/uninstall.sh`.
3. **python** — `python -m py_compile harness/* voice-server/voice_server/*`.
4. **unit-tests** — `python -m unittest discover -s harness/tests`.
5. **plugin** — `npx tsc --noEmit -p obsidian-ralph/tsconfig.json`
   (skipped gracefully if `node_modules` missing).

Each check produces a `CheckResult` row in `90-Meta/heal-checks.ndjson`:

```json
{"name":"privacy","started":"2026-05-09T12:00:00+00:00",
 "duration_s":0.3,"rc":1,"ok":true,"detail":"no leaks"}
```

(Convention: rc=1 for `git grep` is success — no match found.)

## Logging

Every heal pass appends one line to `90-Meta/log.md`:

```
## [<YYYY-MM-DD HH>] heal | fixed=<F> escalated=<E>
```

Plus per-pass detail to `90-Meta/heal-log.md`:

```
## [<UTC ISO>] heal | zombies=<Z> stuck=<S> fixed=<F> escalated=<E>
```

## Loop predicate

Continue if (zombies remain AND fix-budget remains AND no oscillation).
Otherwise emit `<promise>COMPLETE</promise>` and exit non-zero.

Oscillation = a fix that re-introduces a symptom within the same pass.
Detected by re-running the diagnostic after each fix.

## Safety notes

- Heal is **read-mostly**. Only LOW-risk fixes are auto-applied.
- BLOCKER-class symptoms always escalate (never auto-fix), even if a
  technical fix exists. Example: privacy leak.
- Heal cannot disable itself (`uninstall.sh --uninstall` is the only
  way; that's a HIGH-risk operation per `APPROVAL_GATES.md`).
- The PR-check fallback uses `mcp__github__*` only when available; the
  primary signal is local self-test.

## Cross-references

- `CONTEXT_LIFECYCLE.md` — heal is the observe-loop's monitoring side.
- `CRON_JOBS.md` — schedule + install.
- `APPROVAL_GATES.md` — risk classes for heal proposals.
- `SECURITY_PRIVACY.md` — why privacy is the BLOCKER class.
- Phase 1-6 reference: `prompts/ralph-meta-chain/06-autoheal.md`,
  `harness/harness/self_test.py`,
  `harness/harness/__main__.py` (`self-test` subcommand).

## Next actions

Run `harness self-test --only privacy` to check the most important
single guardrail. Then `harness self-test` (no flag) to populate
`heal-checks.ndjson`. The cron heal axis takes over from there.
