# experiments/

Experiment harness scaffold. **Pure scaffolding** — the actual
fixtures live under `harness/fixtures/` (Phase 1-6 reference) or
`prompts/ralph-meta-chain/scripts/harness/fixtures/` (master-spec
target after Round 8). This folder is for **runtime artifacts** the
chain produces during experiment runs.

## Layout

```
experiments/
├── README.md                ← you are here
├── fixtures/                  symlink / mirror of harness/fixtures/
├── outputs/                   per-run output captures (gitignored)
└── reports/                   experiment reports (gitignored or curated)
```

## What goes where

### `fixtures/`

The promptfoo-shaped YAML fixtures the harness reads. **Do not
duplicate** `harness/fixtures/*.yml` here; symlink instead, OR wait
until Round 8 migration co-locates them.

For now, reading
`harness/fixtures/{code-review,daily-summary}.yml` is the source of
truth.

### `outputs/`

Per-run output captures:

- `outputs/<fixture>-<UTC-ts>/incumbent.txt`
- `outputs/<fixture>-<UTC-ts>/candidate.txt`
- `outputs/<fixture>-<UTC-ts>/judge-response.json`

These are **gitignored** (regenerated each run; volatile).

### `reports/`

Markdown experiment reports. Two flavors:

| Type                               | Tracked? | Generator                              |
| ---------------------------------- | -------- | -------------------------------------- |
| `report-<fixture>-<UTC-ts>.md`     | gitignored | `harness ab` writes one per A/B run    |
| `learnings-<topic>.md`              | tracked   | hand-written; cite multiple reports     |

The "learnings" notes are durable: they distill 3-5 reports into a
takeaway. Tracked.

## How to run an experiment

```bash
cd harness
python -m harness ab \
  --incumbent  $VAULT/50-Prompts/code-review.md \
  --candidate  $VAULT/50-Prompts/code-review.candidate-1.md \
  --fixture    fixtures/code-review.yml
# Writes 2 ndjson rows to $VAULT/90-Meta/metrics.ndjson.

python -m harness reflect \
  --candidate  $VAULT/50-Prompts/code-review.candidate-1.md
# Appends a Reflexion lesson to the candidate's frontmatter.

python -m harness traces --tail 20 --axis interaction
# Summarizes the recent A/B verdicts.
```

## Pass thresholds

Per `benchmarks/prompt-quality.md`:

- candidate WINS iff: `rubric_candidate ≥ rubric_incumbent`
  AND (`tokens_candidate ≤ tokens_incumbent` OR
  `banned_candidate < banned_incumbent`).
- 3 consecutive losses → autoevolve proposes rewrite-from-scratch.

## Cross-references

- `docs/AB_HARNESS.md` — full design.
- `benchmarks/prompt-quality.md` — scoring rubric.
- `harness/fixtures/{code-review,daily-summary}.yml` — day-1 fixtures.
- `harness/harness/{ab,judge,reflect,traces}.py`.
- `vault-template/00_System/Experiment Registry.md` — vault-side index.
- `indexes/prompt-index.md` — repo-side prompt registry template.
