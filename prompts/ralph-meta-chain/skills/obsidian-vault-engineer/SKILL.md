---
name: obsidian-vault-engineer
description: |
  Triggers: "vault engineer", "fix vault", "vault structure", "vault diagnostics",
  "frontmatter migration", "broken wikilinks".
when_to_use: |
  Vault structure issues — broken `[[wikilinks]]`, missing frontmatter,
  un-indexed sections, plugin compatibility, folder hierarchy reorganization.
inputs:
  - vault_path: $VAULT (auto-detected)
  - target: which subfolder / which type of fix
steps:
  - "Run ralph_validate_frontmatter.sh + ralph_check_links.sh."
  - "Read vault-template/ to compare against the canonical layout."
  - "Identify the smallest diff that brings the vault into compliance."
  - "If the diff is destructive, propose it as a 30-Notes/<id>-vault-fix-*.md."
  - "If the diff is additive (new control panel page, missing README), apply directly."
  - "Re-run validators after."
tools:
  - "Read"
  - "Edit"
  - "Write"
  - "Bash(bash:*,ralph_validate_frontmatter:*,ralph_check_links:*,find:*,grep:*)"
failure_modes:
  - destructive fix proposed without proposal note → refuse; route to /ralph-skill or /ralph-experiment
  - validator failure persistent after 3 attempts → escalate to 60-Interactions/escalations.md
  - plugin install path uncertain → emit Notice asking user to confirm symlink
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [recall, memory-architect]
is_prerequisite_of: []
links:
  - "[[docs/OBSIDIAN_PLUGIN.md]]"
  - "[[vault-template/]]"
  - "[[scripts/ralph_validate_frontmatter.sh]]"
  - "[[scripts/ralph_check_links.sh]]"
tags: [skill, specialist, obsidian, vault]
---

# Obsidian Vault Engineer

The role you assume when the vault is misshapen and the fix is
mechanical (not conceptual). Bias: prefer the smallest additive change;
avoid bulk rewrites; respect append-only.

## Canonical experiment

Given a scratch vault with:
- one note missing frontmatter,
- one wikilink to a missing target,
- one folder missing its README.md,

the skill must:

1. Run both validators; record the failure counts.
2. Add frontmatter (with `ralph_type: memory`, `created:`).
3. Either create the wikilink target as a `30-Notes/_archive/` redirect
   stub OR rewrite the link to the correct existing note.
4. Add the missing README.md.
5. Re-run validators; both must report 0 failures.

Time-cap: `ralph.experiment_minutes`.
