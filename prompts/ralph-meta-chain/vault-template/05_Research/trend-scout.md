---
ralph_type: research
memory_layer: research
created: 2026-05-09
status: mirror
summary: "Vault-side mirror of research/trend-scout.md."
---

# Trend scout (vault mirror)

Authoritative source: `research/trend-scout.md`.

## Active streams

| Stream                                | Type      | Frequency  | Opt-in? |
| ------------------------------------- | --------- | ---------- | ------- |
| @AlexFinnOfficial                     | creator   | weekly     | no      |
| @mreflow                              | creator   | weekly     | no      |
| @nateherk                             | creator   | weekly     | no      |
| @matthew_berman                       | creator   | weekly     | no      |
| FutureTools.io news feed              | news      | weekly     | no      |
| Anthropic blog index                  | vendor    | irregular  | no      |
| OpenAI blog index                     | vendor    | irregular  | no      |
| Hugging Face daily papers              | papers    | daily      | YES     |
| arXiv cs.AI trending                  | papers    | daily      | YES     |

Opt-in streams require `RALPH_HF_PAPERS=1` / `RALPH_ARXIV=1` etc. set
in the autoupdate cron entry's environment.

## Cross-references

- `research/trend-scout.md` — source of truth.
- `research/source-quality-rubric.md` — confidence/stability scoring.
- `08-autoupdate.md` — weekly Monday cron.
- `harness ingest --creators @h1,@h2,...` — RSS fetcher.
