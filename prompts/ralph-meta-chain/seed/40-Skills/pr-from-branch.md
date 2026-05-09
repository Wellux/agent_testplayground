---
name: pr-from-branch
description: |
  Open a draft GitHub PR from the current branch. Triggers: "open a PR",
  "create pull request from this branch", "draft PR for the current work",
  "ship this branch".
when_to_use: |
  After committing on a feature branch, when the user asks for a PR or when
  CI is green. Skip if the branch already has an open PR.
inputs:
  - branch: current git branch (auto-detected via `git rev-parse --abbrev-ref HEAD`)
  - title:  optional; default = last commit subject (≤ 70 chars)
  - body:   optional; default = "## Summary" + bullets from `git log` + "## Test plan"
steps:
  - Verify branch tracks origin and is pushed (`git status --short`).
  - If not pushed: `git push -u origin <branch>`.
  - Compose title (≤ 70 chars) and body (Summary + Test plan).
  - Use mcp__github__create_pull_request with draft=true.
tools:
  - "Bash(git status,git log:*,git rev-parse:*,git push:*)"
  - "mcp__github__create_pull_request"
failure_modes:
  - branch not tracking remote → push first, then retry
  - PR already exists for this head → return its URL via mcp__github__list_pull_requests
  - no commits since base → refuse with explanation
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: ["recall"]
is_prerequisite_of: []
links: ["[[recall]]"]
tags: [skill, github, pr]
---

# pr-from-branch

Compose and open a draft PR for the current branch. Title is bounded; body
follows the user's preferred Summary + Test plan shape (see
`60-Interactions/user-profile.md`).

## Canonical experiment
Run on a scratch worktree with one fixture commit; assert exit 0 and the
returned PR URL is parseable. Time-cap: `ralph.experiment_minutes`.
