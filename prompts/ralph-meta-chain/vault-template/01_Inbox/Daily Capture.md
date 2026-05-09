---
ralph_type: memory
memory_layer: raw
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Quick text capture lane — promoted to atomic notes overnight."
---

# Daily Capture

The "scratch pad" lane. Anything you type here is treated as a raw
capture and processed by the next memory pass at 02:00 UTC.

The cron prompt:

1. Reads new entries below the `## Today` separator.
2. Promotes each to `30-Notes/<id>-<slug>.md` with frontmatter.
3. Moves the original capture to `00-Inbox/_processed/`.
4. Backlinks 10-15 related wiki pages.

## Today

(write below this line)

## Capture format suggestion

You don't need frontmatter — the memory pass adds it. But hints help:

- Lead with a one-line summary.
- Use `#tags` so the memory pass can suggest MOC creation.
- Use `[[wikilinks]]` if you already know the target.
- Mark sensitive items with `(client)` or `(private)` so privacy
  frontmatter is set correctly.

## Cross-references

- `00_System/Memory Lifecycle.md` — what happens to your capture.
- `01-memory-optimizer.md` — the cron prompt that processes this file.
- `06_Reports/daily-memory-report.md` — your captures by date.
