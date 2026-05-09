# harness — Ralph meta-chain CLI

Python CLI invoked from the daily prompts. Subcommands:

| Subcommand                                          | Purpose                                                                     |
| --------------------------------------------------- | --------------------------------------------------------------------------- |
| `harness ab`                                        | A/B two prompts on a fixture; rubric-judged; writes `metrics.ndjson`        |
| `harness embed --note <p>` / `--vault` / `--since`  | Embed via local Ollama → `sqlite-vec` + FTS5 single-file DB                 |
| `harness query --semantic "<q>" [--k 10]`           | Hybrid retrieval (vec + FTS5 reciprocal-rank-fusion)                        |
| `harness ingest --topics ai,hermes,...`             | GitHub trending + ossinsights → `00-Inbox/trending-YYYY-MM-DD.md`           |
| `harness compress --note <p>` / `--weekly --iso-week`| Summarize and archive bloated notes; weekly daily-note rollups              |

## Setup

```bash
cd harness
uv sync                 # or: python -m venv .venv && pip install -e .
cp .env.example .env    # add ANTHROPIC_API_KEY (gitignored)
```

Ollama must be running locally (default `http://localhost:11434`) with
`nomic-embed-text` pulled:

```bash
ollama pull nomic-embed-text
```

## Storage

`$VAULT/90-Meta/embeddings.db` — single SQLite file with two virtual tables:
- `vec_notes` (sqlite-vec) for vector ANN
- `fts_notes` (FTS5) for keyword

This mirrors `obra/knowledge-graph`'s schema so a future migration is trivial.

## Fixture format (`fixtures/*.yml`)

Promptfoo-shaped, deliberately:

```yaml
description: code-review fixture
prompts:
  - file://../../prompts/ralph-meta-chain/50-Prompts/code-review.md   # incumbent (relative to fixture file)
tests:
  - vars:
      diff: |
        diff --git a/foo.py b/foo.py
        - print(x)
        + print(x, flush=True)
    assert:
      - { type: max-tokens, value: 600 }
      - { type: not-contains, value: "Great question" }
```

Users can later run `promptfoo eval -c fixtures/code-review.yml` directly
without modification.
