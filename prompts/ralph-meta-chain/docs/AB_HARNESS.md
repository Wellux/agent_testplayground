# AB_HARNESS.md

## Purpose

The A/B harness is how Ralph turns "I rewrote a prompt" into "I have
evidence the rewrite is better". Specifies the fixture format, scoring,
MAP-Elites bin geometry, and the Reflexion lesson loop.

## Fixture format (promptfoo-shaped)

```yaml
description: <fixture name>

prompts:
  - file://<relative-path-to-prompt>.md   # incumbent

tests:
  - description: <test case name>
    vars:
      <variable>: |
        <test input>
    assert:
      - { type: max-tokens,    value: 600 }
      - { type: not-contains,  value: "Great question" }
      - { type: contains,      value: "<expected token>" }
```

Why promptfoo: a future user can drop `promptfoo eval -c <fixture>`
without modifying the file. Today, the harness uses its own runner.

Day-1 fixtures shipped: `harness/fixtures/code-review.yml`,
`harness/fixtures/daily-summary.yml`. Matching seed prompts at
`prompts/ralph-meta-chain/seed/50-Prompts/`.

## Scoring rubric

Each arm gets four metrics:

1. **rubric** (1.0 - 5.0) — average of helpfulness / brevity /
   format-compliance, scored by an LLM judge with a strict JSON-only
   prompt (`harness/harness/judge.py`).
2. **tokens** (int) — output token count (Anthropic SDK usage field).
3. **banned** (int) — count of forbidden phrases hit ("Great question",
   "I'd be happy to", "Certainly!", "As an AI") plus failed asserts
   (max-tokens / not-contains / contains).
4. **latency** (float seconds) — wall time of the SDK call.

## Verdict rule

Keep candidate iff:

```
rubric_candidate ≥ rubric_incumbent
  AND
( tokens_candidate ≤ tokens_incumbent
  OR
  banned_candidate < banned_incumbent )
```

Returns:

- `0` = candidate wins (replace incumbent, archive prior under
  `_rejected/<name>-<date>.md`).
- `1` = incumbent wins (archive candidate under
  `50-Prompts/_rejected/<name>-<date>.md`).
- `2` = tie / inconclusive (re-run next pass).

## MAP-Elites bins

GEPA's diversity-preserving heuristic, applied at the prompt-rewrite
layer. Each candidate carries `bin: <axis>` in frontmatter. Default bin
geometry:

```
bin = "<token-cost-bucket>-<format-strictness-bucket>"

token-cost-bucket   = terse  | medium  | verbose
format-strictness   = loose  | medium  | strict
```

Nine cells. Per cell, keep the best survivor in
`50-Prompts/_population/<name>/<bin>.md`. Why preserve diversity: a
"verbose-strict" prompt might be the right tool for a different fixture
later; killing it because "terse-strict" beat it on today's fixture
loses combinatorial reuse.

## Reflexion lesson loop

After each A/B run, `harness reflect --candidate <path>` reads the most
recent metrics row pair from `metrics.ndjson`, asks the judge for one
≤ 80-char takeaway, and appends to the candidate's
`reflections:` frontmatter:

```yaml
reflections:
  - "[2026-05-09] preamble killed terse rubric (-0.4)"
  - "[2026-05-12] missing format header dropped score (-0.3)"
```

A candidate that accumulates three reflections of the same flavor (e.g.
three "preamble killed score" entries) gets a free re-rewrite next
pass — Ralph notices the pattern is sticky and tries a different
direction.

## Population A/B (GEPA)

`02-skills-optimizer.md` and `07-autoevolve.md` spawn populations of 3
candidates per evolutionary axis (brevity-max, format-strict,
persona-shift). Each candidate runs through `harness ab` against the
canonical fixture. The MAP-Elites cell receives whichever candidate
wins its bin; global best is promoted to incumbent.

## Metrics ndjson schema

Each `harness ab` call writes two rows (one per arm) to
`90-Meta/metrics.ndjson`:

```json
{"axis":"interaction","fixture":"code-review","started":"2026-05-09T12:00:00+00:00",
 "incumbent_path":"50-Prompts/code-review.md",
 "candidate_path":"50-Prompts/code-review.candidate-1.md",
 "model":"claude-sonnet-4-6","judge_model":"claude-sonnet-4-6",
 "arm":"incumbent","tokens":420,"rubric":4.2,"banned":0,"latency":3.1}
{"axis":"interaction","fixture":"code-review","started":"2026-05-09T12:00:00+00:00",
 ...,"arm":"candidate","tokens":380,"rubric":4.5,"banned":0,"latency":2.9}
```

`harness traces --tail N --axis interaction` summarizes these.

## Determinism

- Anthropic SDK calls use `temperature=0.0` for both arms.
- The same fixture inputs, same model, same prompts → reproducible
  output (modulo SDK randomness in the < 1% range).
- The judge runs with `temperature=0.0` and `max_tokens=128`, JSON-only
  output.

## Safety notes

- A/B is **expensive**: each run costs ~4 model calls (incumbent,
  candidate, judge × 2). The cron schedule limits this:
  `budgets.interaction.max_ab_experiments: 3` per pass.
- Banned-phrase list is hard-coded for now. Extending it is a LOW-risk
  change in `harness/harness/judge.py`.
- The harness writes to `metrics.ndjson` even on failure (with
  `verdict: error`). Heal picks up persistent failures.
- Candidates that lose are **archived, not deleted**. They live in
  `50-Prompts/_rejected/` and `40-Skills/_rejected/`.

## Cross-references

- `CONTEXT_LIFECYCLE.md` — where the harness sits in the loop.
- `MEMORY_MODEL.md` — how prompt frontmatter maps to memory types.
- `CLAUDE_CODE_INTEGRATION.md` — the prompts being A/B-tested live in
  `$VAULT/50-Prompts/`.
- `OBSIDIAN_PLUGIN.md` — the plugin shows A/B verdicts in the metrics
  view.
- Phase 1-6 reference: `harness/harness/ab.py`, `harness/harness/judge.py`,
  `harness/harness/reflect.py`, `harness/fixtures/*.yml`,
  `prompts/ralph-meta-chain/seed/50-Prompts/*.md`.

## Next actions

To run an A/B: `harness ab --incumbent A --candidate B --fixture F.yml`.
Then `harness reflect --candidate B` to record the lesson. View results
via `harness traces --tail 50 --axis interaction` or in the Obsidian
metrics side-pane.
