# Source-quality rubric

## Purpose

A consistent way to score every source we consider for adoption into Ralph
Meta Chain. Used by `RESEARCH_NOTES.md` (per-entry scores) and by future
`harness ingest` runs.

## Usage

For every source, fill the 18-field shape in `RESEARCH_NOTES.md`. Numeric
fields use this rubric:

### Confidence (0.0 – 1.0)

How sure are we the source describes what we'll see in the project today?

| Score | Meaning                                                              |
| ----- | -------------------------------------------------------------------- |
| 1.0   | Official primary doc + verified within last 30 days                  |
| 0.8   | Official doc, > 30 days old, or first-party blog post                |
| 0.6   | Reputable third-party survey citing primary sources                  |
| 0.4   | Single community blog post / Medium / Substack                       |
| 0.2   | Tweet / forum post / second-hand summary                             |
| 0.0   | Unverified rumor                                                     |

### Stability (0.0 – 1.0)

How likely is this pattern to remain valid in 6 months?

| Score | Meaning                                                              |
| ----- | -------------------------------------------------------------------- |
| 1.0   | Released as 1.x with backward-compat policy, or in CS literature     |
| 0.8   | Released as 0.x but actively maintained > 12 months                  |
| 0.6   | Active project < 12 months old, growing                              |
| 0.4   | Pre-release / beta / experimental flag                               |
| 0.2   | Single-author project, sporadic commits                              |
| 0.0   | Archived / abandoned                                                 |

### Freshness (qualitative note)

Free text. Examples:
- "verified live 2026-05-08"
- "ICLR 2026 Oral, paper from May 2025"
- "v0.13 released 2026-05-07"
- "last commit 8 weeks ago"

## Safety notes

- Never adopt a pattern from a source scoring < 0.4 confidence without
  verifying it in a primary doc.
- Never schedule a recurring `harness ingest` against a source scoring
  < 0.6 stability — write it to `00-Inbox/` for one-shot review instead.
- Treat **creator content** (Alex Finn, Matt Wolfe, Nate Herk) as signal,
  not source. Adopt the *patterns they describe*, never their content.

## Cross-references

- `RESEARCH_NOTES.md` — uses these scores per entry.
- `RESEARCH_SYNTHESIS.md` — aggregates by quartile.
- `docs/AUTOUPDATE.md` — autoupdate proposals must cite confidence/stability.

## Next actions

When adding a new source: copy the entry template at the top of
`RESEARCH_NOTES.md`, fill all 18 fields, score against this rubric, then
cite from at least one synthesis axis in `RESEARCH_SYNTHESIS.md`.
