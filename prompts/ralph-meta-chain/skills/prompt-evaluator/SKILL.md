---
name: prompt-evaluator
description: |
  Triggers: "prompt evaluator", "score this prompt", "is this prompt good",
  "rubric this", "judge this output", "rewrite this prompt".
when_to_use: |
  When the user wants a prompt scored against the rubric, or wants a
  rewrite proposed. Pure analysis; never auto-applies.
inputs:
  - prompt_path: $VAULT/50-Prompts/<name>.md or arbitrary path
  - fixture_path: harness/fixtures/<name>.yml (optional)
  - rewrite_axis: brevity | format | persona | safety (optional)
steps:
  - "Read the prompt + the matching fixture (if any) + the user-profile."
  - "Run harness ab if both incumbent + candidate exist; otherwise score one-arm."
  - "Score on the rubric (helpfulness / brevity / format), 1-5 each."
  - "Identify the top failure mode (banned phrases / over-tokens / format-miss)."
  - "If rewrite_axis is set, generate one candidate variant in 50-Prompts/<name>.candidate-N.md."
  - "Append a Reflexion lesson via harness reflect (≤ 80 chars)."
tools:
  - "Read"
  - "Write"
  - "Bash(harness ab:*,harness reflect:*,harness traces:*)"
failure_modes:
  - prompt has no `validated_against:` → suggest /ralph-experiment first
  - rubric judge unavailable (no ANTHROPIC_API_KEY) → defer with clear error
  - candidate auto-promoted to incumbent without user approval → REFUSE; HIGH-risk
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [recall]
is_prerequisite_of: []
links:
  - "[[docs/AB_HARNESS.md]]"
  - "[[04_Harnesses/eval-rubric.md]]"
  - "[[harness/harness/judge.py]]"
tags: [skill, specialist, prompt, evaluation]
---

# Prompt Evaluator

The role you assume when judging prompts (incumbent or candidate).
Discipline: never auto-promote; always cite the rubric scores; always
attribute failures to one or two causes (not a vague "this is bad").

## Canonical experiment

Given the day-1 fixture `harness/fixtures/code-review.yml` and the
incumbent `seed/50-Prompts/code-review.md`, the skill must:

1. Run `harness ab` (or one-arm score if no candidate exists).
2. Identify ≥ 1 specific failure mode (e.g. "preamble in case 2 dropped
   brevity to 3.2").
3. If `rewrite_axis: brevity` is set, generate
   `50-Prompts/code-review.candidate-N.md` with the preamble removed.
4. Score the new candidate; do NOT promote.

Output is a Markdown report ≤ 30 lines.
