---
ralph_type: provider
memory_layer: system
created: 2026-05-09
status: active
summary: "13-field interface every Ralph runtime adapter must satisfy."
---

# Provider Interface

Authoritative source: `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md`. Vault-side
copy so cron prompts can `Read` it.

Every adapter that wants to host a Ralph axis must satisfy these 13
fields. Conformance to the format IS the test for "Ralph runs on this
provider".

## Fields

```yaml
prompt_input_format:           # how prompts get fed
context_package_format:        # how CLAUDE.md + retrieved notes attach
memory_retrieval_package_format: # harness query result shape
tool_permission_model:          # allow/deny enforcement
file_read_write_model:          # vault-mutation contract
shell_execution_model:          # subprocess + Bash allow/deny
approval_gate_model:            # how the adapter pauses on HIGH/CRITICAL
output_report_format:           # Markdown report shape
error_format:                   # error rendering
evaluation_format:              # metrics.ndjson schema produced
logging_format:                  # log.md line shape
rollback_expectation:           # rollback mechanic
provider_metadata:              # id / version / capabilities
```

## Conformance

- **Conformant adapter** = all 13 fields populated AND fixtures
  produce identical metrics.ndjson rows (modulo `provider:` /
  `provider_version:` fields).
- **Partial adapter** = subset (e.g. embeddings-only). Documented but
  not auto-routed.
- **Non-conformant** = the harness refuses to run prompts through it.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` — full surface.
- `00_System/Provider Registry.md` — active vs deferred.
- `08_Providers/claude-code.md` — the canonical conformant adapter.
- `providers/` — Round 4+ scaffold target.
