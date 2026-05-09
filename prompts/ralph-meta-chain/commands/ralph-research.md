---
description: |
  Triggers: "ralph research", "fetch new repos", "what's trending", "ingest research",
  "what arrived overnight"
allowed-tools:
  - "Read"
  - "Bash(harness:*,grep:*,find:*,wc:*,jq:*)"
---

# /ralph-research

Show what the nightly research pass pulled into `$VAULT/00_Inbox/research/`
and the topic-by-topic breakdown. LOW risk; read-only; never re-fetches.

## Inputs

`$ARGUMENTS` — optional. One of:

- `today` (default) — last 24h
- `yesterday`
- `this-week`
- a single ISO date `YYYY-MM-DD`
- a topic slug (e.g. `meta-prompting`) — filter to a single topic

## Process

1. Read the most recent `$VAULT/00_Inbox/research/<date>-digest.md`.
2. Read `$VAULT/90-Meta/log.md` and grep for the matching
   `## [<date>] research |` line — extract `repos=`, `inbox_files=`,
   `dedupe_skipped=` counters.
3. List the topics covered (from
   `prompts/ralph-meta-chain/research/watchlist.md` cross-referenced
   with what actually shipped).
4. List the 5 most-recent repo notes under `$VAULT/00_Inbox/research/`
   (sorted newest-first). Surface their titles + the `tags:`
   frontmatter line.
5. Note any topics from the watchlist that produced **zero hits** —
   these are signal that either the topic is dead or the dedupe
   threshold is too tight.

## Output

Markdown report:

- **Counters** — `repos=N inbox_files=N dedupe_skipped=N` for the
  matched day.
- **Top arrivals** (newest 5, with `[[wikilinks]]`).
- **Topic coverage** (covered / silent split).
- **Recommended action** — one sentence: "no action" / "consider
  re-tuning topic X" / "watchlist entry Y churned to zero — drop or
  rename".

## Safety

Read-only. Never edits, never re-runs the research fetch. The actual
fetch is owned by the cron'd `04-research-ingest.md` pass.

## Cross-references

- `prompts/ralph-meta-chain/04-research-ingest.md`
- `prompts/ralph-meta-chain/research/watchlist.md`
- `prompts/ralph-meta-chain/scripts/ralph_research_digest.sh`
