# Contributing

Thanks for your interest in Ralph Meta Chain. This document covers branch
convention, how to run tests, how to add fixtures, and the approval
gates each change is reviewed against.

## Branch convention

Active development happens on
`claude/ralph-obsidian-cron-jobs-Mb4A9` (the master-spec greenfield
branch tracked by PR #1). After PR #1 merges, the convention is:

- `main` — stable.
- `claude/<topic>-<id>` — feature branches; one per scoped task.
- `fix/<bug-id>` — bug fix branches.
- `docs/<topic>` — doc-only branches.

PRs land as draft until CI is green and the relevant approval gate is
satisfied.

## Approval gates

Every change is classified per
[`prompts/ralph-meta-chain/docs/APPROVAL_GATES.md`](prompts/ralph-meta-chain/docs/APPROVAL_GATES.md):

| Class    | Examples                                                   | Approval                |
| -------- | ---------------------------------------------------------- | ----------------------- |
| LOW      | Markdown edits, README updates, fixture YAML additions     | CI green                |
| MEDIUM   | Harness changes, plugin changes, new shell shims           | CI green + 1 review     |
| HIGH     | Migration scripts, install/uninstall, frontmatter schema   | CI green + 1 review + ack |
| CRITICAL | Migration `--apply`, voice-server external egress, business-entity workflow firing | Explicit user invoke + rollback plan in the PR body |

Tag the PR body with the class. CRITICAL changes must include the
specific rollback steps and a link to the relevant runbook.

## Local development

The canonical layout post-Round-8:

```
prompts/ralph-meta-chain/
├── 0[1-8]-*.md              # the 8 prompts
├── scripts/harness/         # Python CLI
├── obsidian-plugin/         # TypeScript plugin
├── voice-server/            # FastAPI dispatcher (gated)
├── install/install_cron.sh  # cron / launchd installer
└── docs/                    # 18+ canonical design docs
```

### Running tests

```bash
# Python harness (103 tests)
cd prompts/ralph-meta-chain/scripts/harness && uv sync
uv run python -m pytest tests/ -v

# Voice-server (12 tests)
cd prompts/ralph-meta-chain/voice-server && uv sync
uv run python -m pytest tests/ -v

# Obsidian plugin (typecheck + build)
cd prompts/ralph-meta-chain/obsidian-plugin && npm install
npx tsc --noEmit && npm run build

# Bash shell shim syntax
find prompts/ralph-meta-chain/scripts -name '*.sh' -print0 | \
  xargs -0 -n1 bash -n

# Read-only validators
./prompts/ralph-meta-chain/scripts/ralph_validate_frontmatter.sh
./prompts/ralph-meta-chain/scripts/ralph_check_links.sh
./prompts/ralph-meta-chain/scripts/ralph_provider_validate.sh
./prompts/ralph-meta-chain/scripts/ralph_business_ledger_check.sh

# Privacy guard (must return nothing)
git grep -in -- "$(printf 'equality\.power%s' 'tothepeople')" \
  ':!.github/workflows/ci.yml'
```

CI runs the same set across 8 jobs.

## Adding a fixture

A/B fixture files live at
`prompts/ralph-meta-chain/scripts/harness/fixtures/<axis>-<slug>.yml`.
They follow the [promptfoo](https://github.com/promptfoo/promptfoo)
shape:

```yaml
description: <one-liner>
prompts:
  - <variant-a>
  - <variant-b>
providers:
  - claude-code
tests:
  - vars: { input: <prompt-input> }
    assert:
      - type: contains
        value: <expected-substring>
```

Run with:
```bash
cd prompts/ralph-meta-chain/scripts/harness
uv run python -m harness ab --fixture fixtures/<axis>-<slug>.yml
```

## Adding a skill

Skill candidates live at
`prompts/ralph-meta-chain/skills/<slug>/SKILL.md` and follow the
template at `prompts/ralph-meta-chain/skills/skill-template.md`. The
plugin's "Generate Skill From Current Note" command produces a draft
from any vault note.

## Style

- **Markdown:** GitHub-flavored, `# H1` only at file top, content
  flows from the doc skeleton at
  `prompts/ralph-meta-chain/docs/CLAUDE.md`.
- **Python:** Black-default formatting, type hints on public APIs,
  `from __future__ import annotations`.
- **TypeScript:** Strict mode, no `any`, follow the existing plugin
  patterns at `obsidian-plugin/src/`.
- **Bash:** `set -euo pipefail` at the top of every shim,
  `bash -n` clean.

## Privacy

- Never commit a real user identifier (email, full name, account ID)
  to a tracked file. Local secrets live in `*.local.yml` / `.env*`
  (gitignored) only.
- The privacy guard CI job blocks any tracked file that contains the
  canary phrase.
- See [`prompts/ralph-meta-chain/docs/SECURITY_PRIVACY.md`](prompts/ralph-meta-chain/docs/SECURITY_PRIVACY.md)
  for the threat model.

## Governance

Per
[`prompts/ralph-meta-chain/docs/GOVERNANCE.md`](prompts/ralph-meta-chain/docs/GOVERNANCE.md):

- **Autonomous actions** (LOW only): A/B fixtures, fixture-only
  experiment runs, validator scans, traces, reflections.
- **Proposal-only** (MEDIUM/HIGH): autoupdate bumps, autoevolve
  promotions, schema evolutions.
- **Never autonomous** (CRITICAL): migration apply, business-entity
  external sends, voice-server cross-network egress.

CRITICAL changes are gated on explicit user invocation in every code
path.

## Reporting bugs / requesting features

Use the issue templates under `.github/ISSUE_TEMPLATE/`. Please tag
the approval class.

## Code of conduct

This project follows the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md).
