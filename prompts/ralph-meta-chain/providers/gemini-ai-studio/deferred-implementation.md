---
ralph_type: provider
provider: gemini-ai-studio-deferred
status: deferred
created: 2026-05-09
summary: "What activating the Gemini AI Studio adapter would involve."
---

# Gemini AI Studio — Deferred Implementation

## Estimated work

| Component                              | Effort      |
| -------------------------------------- | ----------- |
| Populate `adapter-spec.md`              | 0.5 day     |
| Implement `harness/.../gemini_adapter.py`| 3-4 days   |
| Function-call schema mapping             | 1 day       |
| Local Bash bridge (no native bash tool)  | 1 day       |
| Long-context cost analysis               | 0.5 day     |
| Fixture replay against Gemini            | 1 day       |
| Threat-model review (cloud egress)       | 0.5-1 day   |
| Total                                    | ~7-9 days   |

## Pre-requisites (from user)

1. Approval to incur Gemini API costs.
2. Approval for cloud-egress (vault content potentially in context).
3. API key procurement from Google AI Studio.
4. Decision on model: 1.5 Pro / 2.0 Flash / Vertex equivalent.

## What the activation PR would contain

- `harness/harness/gemini_adapter.py`.
- A function-call wrapper for the local bash bridge.
- Fixture replay results showing parity with Claude Code on at least
  the two day-1 fixtures (`code-review`, `daily-summary`).

## Cross-references

- `providers/gemini-ai-studio/adapter-spec.md`.
- `docs/APPROVAL_GATES.md` § Provider activation.
