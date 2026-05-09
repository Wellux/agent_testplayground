"""Auto-approval contract: every read-only slash command's allowed-tools
must be a subset of the permissions.allow set in config.example.yml,
so the command runs without prompting the user (B4).

Read-only commands are the LOW-risk dashboards in commands/ralph-*.md
that don't write to the vault. MEDIUM-risk ones (ralph-experiment,
ralph-skill, ralph-migration-plan) are explicitly allowed to need
Write/Edit/specific Bash patterns; this test still checks them.

Regression for HANDOFF.md backlog item B4. Without this test, future
edits to allowed-tools could re-introduce git:* / bash:* style
breadth and silently cause permission prompts on previously-quiet
commands.
"""

from __future__ import annotations

import pathlib
import re
import unittest


REPO = pathlib.Path(__file__).resolve().parents[3]
COMMANDS_DIR = REPO / "prompts" / "ralph-meta-chain" / "commands"
CONFIG_YML = REPO / "prompts" / "ralph-meta-chain" / "config.example.yml"


def _parse_yaml_allow_list() -> list[str]:
    """Extract the permissions.allow list from config.example.yml.

    Mirrors the awk/regex parser in install_claude_code.sh so this
    test catches drift between what the installer ships and what the
    commands declare.
    """
    allow: list[str] = []
    in_perm = False
    in_allow = False
    in_deny = False
    pattern = re.compile(r'^\s*-\s*"(.+)"\s*$')
    for raw in CONFIG_YML.read_text().splitlines():
        stripped = raw.lstrip()
        if raw.startswith("permissions:"):
            in_perm = True
            continue
        if (
            in_perm
            and not raw.startswith((" ", "\t"))
            and stripped
            and not stripped.startswith("#")
        ):
            in_perm = False
            in_allow = in_deny = False
        if not in_perm:
            continue
        if stripped.startswith("allow:"):
            in_allow, in_deny = True, False
            continue
        if stripped.startswith("deny:"):
            in_allow, in_deny = False, True
            continue
        m = pattern.match(raw)
        if m and in_allow:
            allow.append(m.group(1))
    return allow


def _parse_command_allowed_tools(path: pathlib.Path) -> list[str]:
    """Extract allowed-tools list from a slash command's YAML frontmatter."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    if end == -1:
        return []
    fm = text[4:end]
    out: list[str] = []
    in_block = False
    pattern = re.compile(r'^\s*-\s*"(.+)"\s*$')
    for raw in fm.splitlines():
        if raw.startswith("allowed-tools:"):
            in_block = True
            continue
        if in_block and raw and not raw.startswith((" ", "\t")):
            in_block = False
        if not in_block:
            continue
        m = pattern.match(raw)
        if m:
            out.append(m.group(1))
    return out


def _tool_matches_allow(tool: str, allow_set: list[str]) -> bool:
    """Return True if `tool` (a command's allowed-tools entry) is auto-
    approved by some pattern in `allow_set`.

    Claude Code's matching is exact-string for now (we don't try to
    glob); we additionally accept the case where a Bash() pattern
    bundles multiple sub-commands and any one of them appears in the
    allow set.
    """
    # Read / Write / Edit / Agent / TodoWrite — exact match.
    if tool in allow_set:
        return True
    # Compound Bash patterns: "Bash(a:*,b:*,c:*)" — split and each
    # sub-pattern must be coverable.
    m = re.match(r"^Bash\((.+)\)$", tool)
    if m:
        sub_patterns = [s.strip() for s in m.group(1).split(",")]
        for sp in sub_patterns:
            target = f"Bash({sp})"
            # Direct match on a single-pattern Bash() entry.
            if target in allow_set:
                continue
            # Or covered by a compound Bash() entry that includes this sub.
            covered = False
            for allowed in allow_set:
                am = re.match(r"^Bash\((.+)\)$", allowed)
                if not am:
                    continue
                allowed_subs = [s.strip() for s in am.group(1).split(",")]
                if sp in allowed_subs:
                    covered = True
                    break
            if not covered:
                return False
        return True
    # Write/Edit special: vault-scoped pattern.
    if tool == "Write" and "Write($VAULT/**)" in allow_set:
        return True
    if tool == "Edit" and "Edit($VAULT/**)" in allow_set:
        return True
    if tool == "Read" and "Read(**)" in allow_set:
        return True
    return False


class AutoApprovalContract(unittest.TestCase):
    """Every slash command's allowed-tools must be subset of the
    settings.json allowlist, so /ralph-* commands never prompt.
    """

    def setUp(self) -> None:
        self.allow_list = _parse_yaml_allow_list()
        self.assertGreater(
            len(self.allow_list), 0, "config.example.yml has no permissions.allow"
        )

    def test_all_command_allowed_tools_are_subset_of_allowlist(self) -> None:
        violations: list[tuple[str, str]] = []
        for cmd in sorted(COMMANDS_DIR.glob("ralph-*.md")):
            for tool in _parse_command_allowed_tools(cmd):
                if not _tool_matches_allow(tool, self.allow_list):
                    violations.append((cmd.name, tool))
        if violations:
            msg = "Slash commands declare tools not in permissions.allow:\n"
            for name, tool in violations:
                msg += f"  {name}: {tool}\n"
            msg += (
                "\nFix: either tighten the command's allowed-tools to use "
                "patterns already in config.example.yml's permissions.allow, "
                "or add a specific allow pattern there. Avoid broad patterns "
                "like Bash(git:*) or Bash(bash:*) — they unnecessarily widen "
                "the user's permission grant."
            )
            self.fail(msg)

    def test_no_command_uses_overbroad_bash_patterns(self) -> None:
        """Forbid dangerous broad patterns. These would auto-approve far
        more than the command actually needs, defeating the safety
        contract."""
        forbidden = {"Bash(git:*)", "Bash(bash:*)", "Bash(sh:*)", "Bash(*)", "Bash(*:*)"}
        violations: list[tuple[str, str]] = []
        for cmd in sorted(COMMANDS_DIR.glob("ralph-*.md")):
            for tool in _parse_command_allowed_tools(cmd):
                m = re.match(r"^Bash\((.+)\)$", tool)
                if not m:
                    continue
                for sp in (s.strip() for s in m.group(1).split(",")):
                    candidate = f"Bash({sp})"
                    if candidate in forbidden:
                        violations.append((cmd.name, candidate))
        if violations:
            msg = "Slash commands use forbidden over-broad Bash patterns:\n"
            for name, pat in violations:
                msg += f"  {name}: {pat}\n"
            self.fail(msg)


if __name__ == "__main__":
    unittest.main()
