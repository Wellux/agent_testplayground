---
ralph_type: research
memory_layer: research
created: 2026-05-09
status: active
summary: "Free-form research jottings — fed to the memory pass."
---

# Source notes

A scratch pad for research observations. Anything you write here below
the `## Capture` separator gets ingested by the next memory pass and
linked into the appropriate atomic notes.

## Capture

(write below this line)

## Format suggestion

```markdown
## <YYYY-MM-DD> — <project name>

- url: https://...
- topic: <category>
- noted: <one-line takeaway>
- adopt: <what Ralph should adopt, if anything>
- reject: <what Ralph should not adopt>
- confidence: 0.0-1.0
- stability: 0.0-1.0
```

The memory pass converts each entry into an atomic note in
`30-Notes/`. If the entry is research-pattern-shaped (per
`research/source-quality-rubric.md`), an entry also gets added to
`research/RESEARCH_NOTES.md`.

## Cross-references

- `research/source-quality-rubric.md` — confidence/stability rubric.
- `research/RESEARCH_NOTES.md` — formal entry shape.
- `04-research-ingest.md` — daily 01:00 cron.
- `01-memory-optimizer.md` — the prompt that promotes these.
