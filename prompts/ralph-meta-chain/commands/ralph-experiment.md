---
description: |
  Triggers: "ralph experiment", "make this an experiment", "generate fixture",
  "A/B fixture from this"
allowed-tools:
  - "Read"
  - "Write"
  - "Bash(grep:*,find:*)"
---

# /ralph-experiment

Generate a promptfoo-shaped A/B fixture from the active note.
MEDIUM risk: writes a YAML fixture; does NOT run an A/B.

## Inputs

`$ARGUMENTS` — optional. Either a path or a fixture name. If empty,
the slug is derived from the active note's frontmatter `name` /
filename.

## Process

1. Read the active note. Expect either:
   - a prompt note (`50-Prompts/<name>.md`), OR
   - a transcript / case-study note that demonstrates good vs bad
     output.
2. Extract 1-3 test cases:
   - **vars:** the inputs the prompt consumes.
   - **assert:** observable predicates (`max-tokens`, `not-contains
     "Great question"`, `contains <expected-token>`).
3. Render to `$REPO/harness/fixtures/<slug>.yml` (or
   `$REPO/prompts/ralph-meta-chain/scripts/harness/fixtures/<slug>.yml`
   in Round 8+) using the promptfoo shape.
4. Append the fixture path to the source prompt's
   `validated_against:` frontmatter list (if the source is a prompt note).

## Output

Print the path to the new fixture + a one-line summary of the test
cases. Suggest the next step:

```
harness ab \
  --incumbent  $VAULT/50-Prompts/<name>.md \
  --candidate  $VAULT/50-Prompts/<name>.candidate.md \
  --fixture    harness/fixtures/<slug>.yml
```

## Safety

- MEDIUM risk: writes a fixture; no A/B run.
- Refuse if no clear test cases can be extracted (the source note
  needs explicit "if input X then expect Y" framing).

## Cross-references

- `docs/AB_HARNESS.md` § Fixture format.
- `vault-template/04_Harnesses/ab-test-template.md`.
- `harness/fixtures/code-review.yml`, `daily-summary.yml` — examples.
