---
ralph_type: system
memory_layer: system
memory_temperature: frozen
created: 2026-05-09
status: active
summary: "Append-only archive — notes never disappear."
---

# 99_Archive/

The terminal destination for compressed-original notes, deprecated
skills, rejected prompt candidates, and any other content that's been
displaced by an append-only operation.

## What lands here

| Source                              | Subdirectory                       | Triggered by                          |
| ----------------------------------- | ---------------------------------- | ------------------------------------- |
| `30-Notes/<id>.md` (compressed)     | `30-Notes/_archive/<id>-original.md` | `harness compress` / 05-compress prompt |
| `40-Skills/<slug>.md` (deprecated)  | `40-Skills/_rejected/<slug>-<date>.md` | 02-skills-optimizer / 07-autoevolve  |
| `50-Prompts/<name>.candidate-N.md` (lost A/B) | `50-Prompts/_rejected/<name>-<date>.md` | 03-interaction-optimizer        |
| `00-Inbox/voice-<UTC>.md` (promoted) | `00-Inbox/_processed/`             | 01-memory-optimizer                  |
| Anything user-archived               | `99_Archive/<topic>/`              | manual                                |

## Hard rule

> **Notes here are NEVER deleted.** Restoration is `mv` from
> `_archive/` back to the live path.

The `harness erase` command (Round 5+) is the ONLY mechanism that
permanently deletes content, and it requires CRITICAL approval per
`docs/APPROVAL_GATES.md`.

## Restoration

To bring a compressed original back:

```bash
mv "$VAULT/30-Notes/_archive/<id>-original.md" "$VAULT/30-Notes/<id>.md"
# Re-embed it:
harness embed --note "30-Notes/<id>.md"
```

To bring a deprecated skill back:

```bash
mv "$VAULT/40-Skills/_rejected/<slug>-<date>.md" "$VAULT/40-Skills/<slug>.md"
# Edit frontmatter: status: active
```

## Cross-references

- `00_System/Memory Lifecycle.md` § Compression rules.
- `docs/APPROVAL_GATES.md` § Memory operations (CRITICAL erase).
- `docs/SECURITY_PRIVACY.md` § Right to erasure (GDPR-compliant erase).
