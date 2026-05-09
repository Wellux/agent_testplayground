# Trend scout

## Purpose

Per-source signal stream that complements `github-watchlist.md`. Where the
watchlist tracks *code* (release tags), this file tracks *trends* — papers,
creator videos, blog posts, surveys, conference talks.

## Usage

The 08-autoupdate cron reads this file's "Active streams" table to know
which RSS / scraped feeds to pull. New streams are added below; deprecated
streams are moved to "Deprecated streams" (never deleted — provenance).

## Active streams

| Stream                                       | Type        | Frequency  | Notes                                  |
| -------------------------------------------- | ----------- | ---------- | -------------------------------------- |
| @AlexFinnOfficial (YouTube RSS)              | creator     | weekly     | Claude Code / vibe-coding workflows    |
| @mreflow (YouTube RSS)                       | creator     | weekly     | FutureTools weekly news roundup        |
| @nateherk (YouTube RSS)                      | creator     | weekly     | n8n + AI agent automation              |
| @matthew_berman (YouTube RSS)                | creator     | weekly     | hands-on agent-stack walkthroughs      |
| FutureTools.io news feed                     | news        | weekly     | curated AI tools + news                |
| Anthropic blog index                         | vendor      | irregular  | Claude Code, SDK release notes         |
| OpenAI blog index                            | vendor      | irregular  | Codex parity awareness only            |
| Hugging Face daily papers (opt-in)           | papers      | daily      | gated; only if user enables            |
| arXiv cs.AI trending (opt-in)                | papers      | daily      | gated                                  |
| ICLR / NeurIPS / ICML accepted lists         | conferences | yearly     | one-shot scrape per cycle              |

## Deprecated streams

(none yet — first round)

## Stream entry template

```yaml
---
name: <handle or feed name>
type: creator | news | vendor | papers | conferences | misc
url: https://...
frequency: daily | weekly | monthly | irregular
opt_in: true | false       # true = requires explicit env var to enable
last_consumed: YYYY-MM-DD  # filled by harness ingest
last_signal_strength: 0.0-1.0
notes: |
  ...
---
```

## Scoring streams

After each consumed week, the autoevolve cron updates `last_signal_strength`
on the entry based on:

- Did any item from this stream lead to a `30-Notes/<id>-bump-*.md`
  proposal? (+0.3)
- Did any item match an open hypothesis? (+0.2)
- Were items duplicates of last week's? (-0.2)
- Was the stream silent for two consecutive weeks? (-0.3)

Streams scoring < 0.3 over a 4-week window are flagged for deprecation
(but never auto-deprecated — proposal only).

## Safety notes

- **Creator content is signal, not source.** The chain extracts patterns
  from creator videos, never their prose / video titles / thumbnails.
- **Opt-in streams require an explicit env var.** `RALPH_HF_PAPERS=1`,
  `RALPH_ARXIV=1`. Default off.
- **YouTube RSS scraping.** The harness resolves @handle → channelId by
  scraping the channel page (no YouTube API key needed). If YouTube
  changes that markup, the resolver returns 404 cleanly and the stream
  reports zero items that week.
- **No automatic posting.** Ralph never posts to YouTube, blog comments,
  X, or any other platform. Read-only signal consumption only.

## Cross-references

- `RESEARCH_NOTES.md` — Alex Finn / Matt Wolfe / Nate Herk / Matthew Berman
  entries.
- `RESEARCH_SYNTHESIS.md` — Section 2 (weak patterns) covers what NOT to
  copy from creator content.
- `docs/AUTOUPDATE.md` — runtime semantics.
- `prompts/ralph-meta-chain/08-autoupdate.md` — the prompt that consumes
  this file.

## Next actions

To add a stream: copy the entry template into "Active streams" and
populate `RESEARCH_NOTES.md` with a corresponding scored entry. Then run
`harness ingest --creators @<handle>` (or appropriate flag) to verify the
fetcher works. Streams that fail to fetch on the first run get flagged
in the next 06-autoheal pass.
