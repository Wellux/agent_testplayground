# providers/

Provider adapter scaffolds. **Claude Code is the only ACTIVE runtime;**
the other three are deferred adapter specs the master spec asks us to
document so a future round can light them up without redesigning the
chain.

## Directory map

```
providers/
├── README.md                                 ← you are here
├── provider-interface.md                       13-field contract every adapter must satisfy
├── claude-code/                                ACTIVE
│   ├── README.md
│   ├── hooks.md
│   ├── commands.md
│   ├── skills.md
│   └── runtime-notes.md
├── openai-codex/                                DEFERRED
│   ├── README.md
│   ├── adapter-spec.md
│   └── deferred-implementation.md
├── gemini-ai-studio/                            DEFERRED
│   ├── README.md
│   ├── adapter-spec.md
│   └── deferred-implementation.md
└── local-models/                                PARTIAL (embeddings only)
    ├── README.md
    ├── adapter-spec.md
    ├── ollama-notes.md
    └── deferred-implementation.md
```

## Activation status (mirror)

| Provider              | Status   | Rationale                                              |
| --------------------- | -------- | ------------------------------------------------------ |
| Claude Code           | ACTIVE   | User-confirmed runtime choice.                          |
| OpenAI Codex CLI      | DEFERRED | Cloud-sandboxed variant ships code; user picked CC only.|
| Gemini AI Studio      | DEFERRED | Same; cloud-only.                                       |
| Local models (Ollama) | PARTIAL  | Embeddings already integrated; completion deferred.    |

See `vault-template/00_System/Provider Registry.md` for the daily-use
mirror, and `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` for the master
contract.

## The 13 fields

Every adapter must answer:

```yaml
prompt_input_format:
context_package_format:
memory_retrieval_package_format:
tool_permission_model:
file_read_write_model:
shell_execution_model:
approval_gate_model:
output_report_format:
error_format:
evaluation_format:
logging_format:
rollback_expectation:
provider_metadata:
```

Conformance to the format IS the test. See `provider-interface.md`.

## Activation gate

Lighting up a deferred adapter is HIGH-risk per
`docs/APPROVAL_GATES.md`. Required:

1. Populated 13-field `<vendor>/adapter-spec.md`.
2. Threat-model review (privacy + cost + capability).
3. Fixtures pass under the new adapter (existing
   `harness/fixtures/*.yml` should work; the harness adds
   `provider:` / `provider_version:` columns to every metrics row).
4. Explicit user approval in the activation proposal.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` — full spec.
- `docs/APPROVAL_GATES.md` § Provider / external — activation gates.
- `vault-template/00_System/Provider Registry.md` — vault mirror.
- `harness/harness/memory_backends.py` — the only currently-pluggable
  layer (embedding backends).

## Next actions

- If you only run Claude Code: skip the deferred adapter folders.
- Round 4 ships these specs as Markdown only. No code.
- Round 5+ adds adapter activation (HIGH risk; explicit user choice).
