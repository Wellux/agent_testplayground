---
description: |
  Triggers: "ralph autoupdate", "what's new this week", "weekly digest",
  "open futuretools"
allowed-tools:
  - "Read"
  - "Bash(grep:*,find:*)"
---

# /ralph-autoupdate

Open this week's autoupdate digest. Read-only; LOW risk.

## Inputs

`$ARGUMENTS` — optional ISO week (`YYYY-Www`). Defaults to current week.

## Process

1. Compute target week (or use `$ARGUMENTS`).
2. Read `$VAULT/00-Inbox/futuretools-<week>.md` if present.
3. List any open bump-proposals at
   `$VAULT/30-Notes/<id>-bump-*.md` with `status: open`.
4. Read the corresponding line from `$VAULT/90-Meta/log.md`:
   `## [<date>] update | releases=R news=N bumps_proposed=B`.

## Output

Render a Markdown report:

- **Week summary** (one-line counts)
- **Notable releases** (top 5)
- **Notable news** (top 5)
- **Open bump-proposals** (link list)
- **Recommended action** — typically "open the digest in Obsidian".

If no digest file exists for the week, suggest running
`08-autoupdate.md` manually:

```
RALPH_AUTOUPDATE_NETWORK=1 claude -p "$(cat 08-autoupdate.md)"
```

## Safety

LOW risk: read-only. Proposing or applying a bump is the user's
explicit decision per `docs/AUTOUPDATE.md` § Risk classification.

## Cross-references

- `prompts/ralph-meta-chain/08-autoupdate.md`.
- `docs/AUTOUPDATE.md`.
- `research/github-watchlist.md`, `research/trend-scout.md`.
