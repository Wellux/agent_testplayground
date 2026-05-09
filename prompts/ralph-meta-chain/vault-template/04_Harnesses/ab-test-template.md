---
ralph_type: experiment
memory_layer: experiment
created: 2026-05-09
status: template
summary: "Template for an A/B fixture file (promptfoo-shaped)."
---

# A/B test template

Save as `harness/fixtures/<name>.yml` (NOT in this vault — the harness
expects fixtures under the repo). The template is here for browsability
inside Obsidian.

```yaml
description: <fixture name>

prompts:
  - file://<relative-path-to-incumbent-prompt>.md

tests:
  - description: <test case 1>
    vars:
      <variable1>: |
        <input>
    assert:
      - { type: max-tokens,    value: 600 }
      - { type: not-contains,  value: "Great question" }
      - { type: contains,      value: "<expected>" }

  - description: <test case 2>
    vars:
      <variable1>: |
        <different input>
    assert:
      - { type: max-tokens,    value: 800 }
      - { type: not-contains,  value: "Certainly!" }
```

## Run

```bash
harness ab \
  --incumbent  50-Prompts/<name>.md \
  --candidate  50-Prompts/<name>.candidate-1.md \
  --fixture    harness/fixtures/<name>.yml
```

Returns exit code 0 (candidate wins), 1 (incumbent wins), 2 (tie).
Writes 2 metrics rows per test case to `90-Meta/metrics.ndjson`.

## After A/B

Run `harness reflect --candidate 50-Prompts/<name>.candidate-1.md` to
record the Reflexion lesson. The judge synthesizes a one-line takeaway
and appends it to the candidate's `reflections:` frontmatter.

## Cross-references

- `docs/AB_HARNESS.md` — full fixture format + scoring + verdict rule.
- `04_Harnesses/eval-rubric.md` — per-output scoring.
- `04_Harnesses/prompt-scorecard.md` — accumulated A/B history per prompt.
- `00_System/Experiment Registry.md` — index of every fixture.
