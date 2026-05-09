---
name: provider-adapter-designer
description: |
  Triggers: "provider adapter", "13 fields", "activate codex", "activate gemini",
  "wire local llama", "provider neutral".
when_to_use: |
  When considering activating a deferred provider adapter or
  populating a partial spec. NEVER auto-activates; producing a spec
  is LOW-risk; activating is HIGH-risk per docs/APPROVAL_GATES.md.
inputs:
  - vendor: openai-codex | gemini-ai-studio | local-models
  - target: spec | activation-proposal
steps:
  - "Read providers/provider-interface.md (the 13 fields)."
  - "Read providers/<vendor>/{README,adapter-spec,deferred-implementation}.md."
  - "If target=spec: populate the missing 13-field rows; output to providers/<vendor>/adapter-spec.md."
  - "If target=activation-proposal: write 30-Notes/<id>-activate-<vendor>.md with cost/privacy/threat-model rationale + status: open."
  - "NEVER edit harness/ to add adapter code without an approved proposal."
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Bash(grep:*,find:*)"
failure_modes:
  - vendor not in provider list → refuse
  - activation-proposal lacks threat-model section → refuse with TODO
  - any code edit attempted without approved proposal → REFUSE; HIGH-risk
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [recall]
is_prerequisite_of: []
links:
  - "[[providers/provider-interface.md]]"
  - "[[docs/PROVIDER_NEUTRAL_ARCHITECTURE.md]]"
  - "[[docs/APPROVAL_GATES.md]]"
tags: [skill, specialist, provider]
---

# Provider Adapter Designer

The role you assume when populating a deferred adapter or proposing
its activation. Discipline: spec first, code never; activation is the
user's explicit choice routed through the approval ledger.

## Canonical experiment

Given the partially-populated `providers/local-models/adapter-spec.md`
(embeddings ACTIVE, completion DEFERRED), the skill must:

1. Identify the missing rows under `# 1. ... # 13. ...`.
2. Populate them from `harness/harness/embeddings.py` (for the active
   path) and from research notes about Ollama completion (for the
   deferred path).
3. NOT edit `harness/harness/judge.py` to wire completion routing.
4. Write a separate `30-Notes/<id>-activate-local-completion.md`
   proposal with cost / model-size / calibration rationale, marked
   `status: open`.

Output: a diff of the spec changes + the proposal note.
