---
name: Bug report
about: Report a defect in the harness, plugin, voice-server, install scripts, or shell shims
title: "[bug] "
labels: ["bug"]
assignees: []
---

## Environment

- OS / version:
- Python version (`python --version`):
- Node version (`node --version`), if plugin issue:
- `claude --version` (if relevant):
- Branch / commit (`git rev-parse --short HEAD`):
- Component (harness / plugin / voice-server / install / shim):

## Reproduction

Steps to trigger the bug:

1.
2.
3.

Minimal command or fixture, if any:

```bash
# paste here
```

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened. Paste relevant log lines from `~/.ralph.log`,
`$VAULT/90-Meta/log.md`, or stderr — redact any user identifiers first.

```
# logs
```

## Approval class

Per `prompts/ralph-meta-chain/docs/APPROVAL_GATES.md`, what class is
the affected behavior?

- [ ] LOW — read-only / docs / fixtures
- [ ] MEDIUM — harness, plugin, shell shim
- [ ] HIGH — install/uninstall, frontmatter schema, migration scripts
- [ ] CRITICAL — migration apply, voice-server external egress,
      business-entity workflow firing

## Anything else?

Screenshots, related issues, hypothesis about cause.
