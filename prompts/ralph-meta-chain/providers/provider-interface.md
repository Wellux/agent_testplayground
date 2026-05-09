---
ralph_type: provider
memory_layer: system
stability: canonical
created: 2026-05-09
status: active
summary: "13-field contract every Ralph runtime adapter must satisfy."
---

# Provider Interface

Every adapter that hosts a Ralph axis MUST populate these 13 fields.
Conformance to the format is the test. The fields below are the same
13 listed in `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` and
`vault-template/08_Providers/provider-interface.md` — this file is the
authoring source.

## Field reference

### 1. `prompt_input_format`

How the adapter accepts a Ralph prompt file.

- Must accept Markdown via either stdin or a file path.
- Must preserve YAML frontmatter intact.
- Must support multi-megabyte prompts (some Ralph prompts pull the full
  vault `CLAUDE.md` into context).

### 2. `context_package_format`

How the adapter loads the vault `CLAUDE.md` + retrieved notes alongside
the prompt.

- Claude Code: auto-loads `CLAUDE.md` files from cwd-up and from
  `~/.claude/CLAUDE.md`.
- Adapter must replicate this auto-load semantics OR document the
  workaround (e.g. flatten into the prompt itself).

### 3. `memory_retrieval_package_format`

The format of `harness query` results when fed back into the model.

- Markdown bullets with `[[wikilinks]]` (current).
- Adapter must accept Markdown without conversion.

### 4. `tool_permission_model`

How the adapter enforces `config.yml` `permissions.allow` / `deny`.

- Claude Code: `.claude/settings.json` allow/deny + per-call user
  approval.
- Adapter must support a permission allowlist with deny-by-default.

### 5. `file_read_write_model`

How the adapter mutates vault files.

- Claude Code: Edit / Write tools, sandboxed to repo + `$VAULT`.
- Adapter must support: read any path the user authorizes, write only
  to authorized paths, never delete (Ralph archives instead).

### 6. `shell_execution_model`

How the adapter executes Bash subprocesses.

- Claude Code: Bash tool with allow/deny patterns.
- Adapter must support: argv-array execution (no shell-string
  injection), allowlist of commands, prompt user before non-allowed.

### 7. `approval_gate_model`

How the adapter pauses on HIGH/CRITICAL operations.

- Claude Code: user prompt for non-allowed tools; Stop hook for
  ralph-wiggum loop.
- Adapter must support: pause-and-prompt for any operation classified
  HIGH or CRITICAL per `docs/APPROVAL_GATES.md`.

### 8. `output_report_format`

How the adapter produces Markdown output.

- Stdout = Markdown report.
- Adapter must support producing structured Markdown matching the
  format prompts request.

### 9. `error_format`

How errors are rendered.

- Stderr = error message; exit code = error class.
- Standard exit codes:
  - 0 = success
  - 1 = generic failure
  - 64 = usage error / dry-run
  - 65 = data error
  - 66 = artifact missing
  - 67 = approval mismatch
  - 68 = environment error (dirty tree, etc.)

### 10. `evaluation_format`

The schema of `metrics.ndjson` rows the adapter produces.

- Same schema as Claude Code (per `docs/AB_HARNESS.md`):
  `{axis, fixture, started, incumbent_path, candidate_path, model,
   judge_model, arm, tokens, rubric, banned, latency, provider,
   provider_version}`.
- Adapter must add `provider:` and `provider_version:` so cross-
  provider A/B works.

### 11. `logging_format`

How log lines look.

- Karpathy LLM-Wiki format: `## [YYYY-MM-DD] axis | k=v ...` in
  `90-Meta/log.md`.
- Adapter must preserve this format.

### 12. `rollback_expectation`

How the adapter supports rollback on apply.

- Vault changes: `_archive/` mv (always reversible).
- Repo changes: git revert.
- Adapter must NEVER apply a HIGH/CRITICAL operation without a
  rollback path documented in advance.

### 13. `provider_metadata`

Identification + capabilities.

- `id: <stable-vendor-name>`
- `version: <version-string>`
- `capabilities: [tool-use, structured-output, function-calling,
   long-context, ...]`

## Conformance levels

- **Conformant adapter** = all 13 fields populated AND fixtures
  produce identical metrics.ndjson rows (modulo `provider:` /
  `provider_version:` fields).
- **Partial adapter** = subset (e.g. embeddings-only). Documented but
  not auto-routed for prompt completion.
- **Non-conformant** = harness refuses to run prompts through it.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` — full surface.
- `claude-code/runtime-notes.md` — the canonical conformant adapter.
- Each `<vendor>/adapter-spec.md` — per-adapter answers to the 13 fields.
