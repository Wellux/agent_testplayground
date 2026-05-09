---
ralph_type: report
memory_layer: report
memory_temperature: hot
created: 2026-05-09
status: active
summary: "This week's autoupdate digest + proposed bumps."
---

# Autoupdate Proposal

Updated every Monday at 06:00 UTC by `08-autoupdate.md`. The full digest
lives at `00-Inbox/futuretools-YYYY-Www.md`; this file is the tldr.

## This week

| Metric                | Count |
| --------------------- | ----- |
| Releases scanned      | —     |
| News items            | —     |
| Bumps proposed        | —     |

## Proposed bumps (top 5)

(populated by the cron — `[[wikilinks]]` to
`30-Notes/<id>-bump-<package>-<version>.md`)

## Notable releases

(per-tool one-liners — usually 3-5 items)

## Notable news

(usually 3-5 FutureTools / Anthropic blog items)

## Recommended action

If you want to apply one of the bump proposals:

1. Open the proposal note. Read the test-plan + rollback-plan.
2. Run the test plan in a feature branch (e.g.
   `cd harness && uv lock --upgrade-package <pkg>`).
3. Run `harness self-test` to confirm no regressions.
4. Commit + open PR.

The autoupdate cron does NOT auto-apply bumps. That's your call.

## Cross-references

- `08-autoupdate.md` — the source cron prompt.
- `00-Inbox/futuretools-YYYY-Www.md` — full weekly digest.
- `research/github-watchlist.md` — what's being scanned.
- `docs/AUTOUPDATE.md` — full design.
