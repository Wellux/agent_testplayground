---
name: daily-summary
last_rewritten: 2026-05-09
validated_against: ["harness/fixtures/daily-summary.yml"]
bin: terse-strict
reflections: []
---

# Summarize the day.

You are summarizing a personal log. Be terse, no preambles.

## Output format (MUST follow)
1. **Decisions**: bullet list of decisions taken today, ≤ 5. Skip if none.
2. **Open**: bullet list of unresolved items, ≤ 5. Skip if none.
3. **Tomorrow**: ≤ 3 bullets, each one a concrete next step.

## Forbidden
- Preambles ("Let's break this down", "I hope this helps").
- Empty sections — just omit.
- Editorializing; only cite what's in the transcript.

## Transcript
{{transcript}}
