# benchmarks/ — Quality scorecards per axis

Six scorecards per master spec. Each documents how Ralph SCORES the
output of one axis, and what thresholds gate the various proposal
classes (LOW / MEDIUM / HIGH / CRITICAL per `docs/APPROVAL_GATES.md`).

The scorecards are the **rubric authority**. The cron prompts and the
harness's `judge.py` reference these for their grading prompts.

## Files

| Scorecard                    | Axis it grades                 | Authoritative for                  |
| ---------------------------- | ------------------------------ | ---------------------------------- |
| `memory-quality.md`          | memory pass output              | `01-memory-optimizer.md`           |
| `skill-quality.md`           | skill execution                 | `02-skills-optimizer.md`            |
| `prompt-quality.md`          | prompt outputs (mirrors AB rubric) | `03-interaction-optimizer.md` + `harness ab` |
| `interaction-quality.md`     | tone / format conformance       | `03-interaction-optimizer.md`       |
| `business-action-quality.md` | business-entity workflow output | `business-entity/workflows/*.md`    |
| `migration-quality.md`        | migration reliability           | `migration/scripts/*.sh`             |

## Scoring conventions

- All rubric scores are 1.0 – 5.0 (mean of N axes).
- Pass threshold is rubric ≥ 3.5 unless the scorecard says otherwise.
- Scoring runs in `harness/harness/judge.py` (LLM judge with
  `temperature: 0.0`, JSON-only output).

## Cross-references

- `docs/AB_HARNESS.md` § Scoring rubric.
- `vault-template/04_Harnesses/eval-rubric.md` — vault-side per-output rubric.
- `harness/harness/judge.py` — implementation.
- `harness/fixtures/*.yml` — fixtures evaluate against these scorecards.
