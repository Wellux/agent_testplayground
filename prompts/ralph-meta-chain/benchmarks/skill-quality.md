---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for skill execution + skill files."
---

# Skill Quality Scorecard

Grades skills (the procedural memory under `40-Skills/`) on two
levels: **per-execution** (was the skill applied correctly to a task?)
and **per-file** (does the skill file's schema and steps hold up?).

## Per-execution rubric (1-5 each)

### success (1-5)

Did the skill's steps reach the expected output?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | Reached expected output; no detours                       |
| 4     | Reached output; one off-script step                       |
| 3     | Reached output but skipped a step                         |
| 2     | Partial output; stuck                                     |
| 1     | Failed                                                    |

### efficiency (1-5)

Token cost vs the canonical-experiment baseline.

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | ≤ 0.7× baseline tokens                                    |
| 4     | 0.7-1.0× baseline                                         |
| 3     | 1.0-1.3× baseline                                         |
| 2     | 1.3-2.0× baseline                                         |
| 1     | > 2× baseline (regression)                                |

### safety (1-5)

Did the skill respect the failure_modes + tools allowlist?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | All failure_modes honored; no tools outside allowlist     |
| 3     | Minor allowlist drift (e.g. used `mv` when not declared)   |
| 1     | Used a denied tool (e.g. `rm`)                              |

## Per-file rubric (1-5 each)

### schema (1-5)

Does the skill file conform to `memory-frontmatter.schema.json` (skill
extension)?

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | All required + Voyager prerequisites + canonical experiment |
| 4     | Required + canonical experiment; no Voyager links            |
| 3     | Required only                                                |
| 1     | Missing canonical experiment OR steps                          |

### last_validated (≤ 14d)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | last_validated ≤ 7d                                       |
| 4     | last_validated ≤ 14d                                      |
| 3     | last_validated 14-30d                                     |
| 1     | last_validated > 30d (autoevolve will surface)             |

## Pass thresholds

- Per-execution: rubric ≥ 3.5 to count as a success in
  `metrics.ndjson`.
- Per-file: schema score = 5 to ship a new skill; ≥ 3 to keep an
  amended one.
- `success_rate` (over 14d, ≥ 5 invocations) < 0.6 → `07-autoevolve`
  proposes deprecation.

## Voyager curriculum check

A skill's `prerequisites:` MUST point at active skills (not
deprecated, not non-existent). The `02-skills-optimizer.md` writer
refuses to ship a skill whose declared prereq is missing.

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Skills.
- `prompts/ralph-meta-chain/02-skills-optimizer.md`.
- `prompts/ralph-meta-chain/07-autoevolve.md` § Step 2 fitness.
- `seed/40-Skills/recall.md`, `pr-from-branch.md`.
- `skills/*` (Round 6 specialists).
