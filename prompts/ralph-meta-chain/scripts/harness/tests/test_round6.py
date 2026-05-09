"""Smoke tests for Round 6 — greenfield plugin + commands + skills + hooks."""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import unittest

def _find_repo_root() -> pathlib.Path:
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("no .git ancestor found")


REPO = _find_repo_root()
RMC = REPO / "prompts" / "ralph-meta-chain"
PLUGIN_DIR = RMC / "obsidian-plugin"
COMMANDS_DIR = RMC / "commands"
SKILLS_DIR = RMC / "skills"
HOOKS_DIR = RMC / "hooks"


class GreenfieldPluginPresent(unittest.TestCase):
    def test_manifest_id_and_min_version(self) -> None:
        m = json.loads((PLUGIN_DIR / "manifest.json").read_text())
        self.assertEqual(m["id"], "ralph-meta-chain")
        self.assertTrue(m["isDesktopOnly"])
        self.assertGreaterEqual(int(m["minAppVersion"].split(".")[0]), 1)

    def test_required_files_present(self) -> None:
        for rel in (
            "package.json",
            "tsconfig.json",
            "esbuild.config.mjs",
            "styles.css",
            "README.md",
            "src/main.ts",
            "src/runner.ts",
            "src/log-view.ts",
            "src/metrics-view.ts",
            "src/control-panel-view.ts",
            "src/status-bar.ts",
            "src/settings.ts",
        ):
            self.assertTrue((PLUGIN_DIR / rel).is_file(), f"missing {rel}")

    def test_settings_match_master_spec_shape(self) -> None:
        text = (PLUGIN_DIR / "src" / "settings.ts").read_text()
        for key in (
            "vaultRoot",
            "repoRoot",
            "userIdentityEmail",
            "compressionThreshold",
            "hotMemoryWindowDays",
            "coldMemoryWindowDays",
            "enableExperimentalCommands",
            "enableAutoCompression",
            "enableGraphRanking",
            "enableBusinessEntityScaffold",
            "enableProviderNeutralScaffold",
        ):
            self.assertIn(key, text, f"settings.ts missing {key}")

    def test_round6_commands_registered(self) -> None:
        text = (PLUGIN_DIR / "src" / "main.ts").read_text()
        for cmd_id in (
            "ralph-control-panel",
            "ralph-run-full-index",
            "ralph-run-memory-index",
            "ralph-compress-current",
            "ralph-skill-from-note",
            "ralph-experiment-from-note",
            "ralph-promote-canonical",
            "ralph-archive-stale",
            "ralph-detect-duplicates",
            "ralph-create-business-approval",
            "ralph-open-provider-registry",
            "ralph-open-migration-control",
            "ralph-vault-diagnostics",
        ):
            self.assertIn(cmd_id, text, f"main.ts missing command id: {cmd_id}")

    def test_userIdentityEmail_default_empty(self) -> None:
        """Master-spec privacy: never default to a real identifier."""
        text = (PLUGIN_DIR / "src" / "settings.ts").read_text()
        m = re.search(r'userIdentityEmail:\s*"([^"]*)"', text)
        self.assertIsNotNone(m, "userIdentityEmail default not found")
        if m is not None:
            self.assertEqual(m.group(1), "", "userIdentityEmail default must be empty string")

    def test_skill_and_experiment_stubs_replaced_with_real_runner(self) -> None:
        """Round 6 shipped with two no-op stubs (Generate Skill From Current
        Note, Generate Experiment From Current Note). They were replaced
        with a real runCommandPromptOnNote() helper that composes the
        matching commands/<name>.md spec with the active note + spawns
        claude -p."""
        main_ts = (PLUGIN_DIR / "src" / "main.ts").read_text()
        runner_ts = (PLUGIN_DIR / "src" / "runner.ts").read_text()

        # Stubs are gone.
        self.assertNotIn("(stub) skill draft would derive", main_ts,
                         "skill stub still present in main.ts")
        self.assertNotIn("(stub) experiment fixture would derive", main_ts,
                         "experiment stub still present in main.ts")

        # Both callbacks now call runCommandPromptOnNote with the right command file.
        self.assertIn('runCommandPromptOnNote(', main_ts)
        self.assertIn('"ralph-skill.md"', main_ts,
                      "skill callback should reference ralph-skill.md")
        self.assertIn('"ralph-experiment.md"', main_ts,
                      "experiment callback should reference ralph-experiment.md")

        # The helper exists in runner.ts.
        self.assertIn("export async function runCommandPromptOnNote", runner_ts)
        # And it composes the prompt with $ARGUMENTS + COMPLETE-token semantics.
        self.assertIn("$ARGUMENTS", runner_ts)
        self.assertIn("<promise>COMPLETE</promise>", runner_ts)

    def test_runHarness_passes_vault_flag(self) -> None:
        """Codex round-5 P2: Plugin's harness commands must pass
        --vault s.vaultRoot. Otherwise harness falls back to
        config.example.yml's sample vault path even when the plugin
        has the right vault auto-detected."""
        runner_ts = (PLUGIN_DIR / "src" / "runner.ts").read_text()
        self.assertIn('"--vault"', runner_ts,
                      "runHarness must inject --vault from s.vaultRoot")
        # Specifically: the args splat must include argsWithVault, not raw args.
        self.assertIn("argsWithVault", runner_ts,
                      "spawn invocation must use argsWithVault, not raw args")


class CommandsTemplates(unittest.TestCase):
    SLUGS = (
        "ralph-cron",
        "ralph-memory",
        "ralph-skill",
        "ralph-experiment",
        "ralph-research",
        "ralph-compress",
        "ralph-evolve",
        "ralph-autoheal",
        "ralph-autoupdate",
        "ralph-business-review",
        "ralph-migration-plan",
    )

    def test_all_command_files_present(self) -> None:
        existing = sorted(p.stem for p in COMMANDS_DIR.glob("*.md") if p.stem != "README")
        self.assertEqual(set(existing), set(self.SLUGS))

    def test_each_has_frontmatter_and_required_sections(self) -> None:
        for slug in self.SLUGS:
            f = COMMANDS_DIR / f"{slug}.md"
            text = f.read_text()
            self.assertTrue(text.startswith("---\n"), f"{slug}: no frontmatter")
            self.assertIn("description:", text, f"{slug}: missing description")
            self.assertIn("allowed-tools", text, f"{slug}: missing allowed-tools")
            for section in ("## Inputs", "## Process", "## Output", "## Safety"):
                self.assertIn(section, text, f"{slug}: missing {section}")


class SkillsSpecialists(unittest.TestCase):
    SLUGS = (
        "memory-architect",
        "prompt-evaluator",
        "obsidian-vault-engineer",
        "shell-safety-engineer",
        "business-ops-analyst",
        "repo-migration-engineer",
        "provider-adapter-designer",
        "context-compression-engineer",
    )

    def test_eight_skill_dirs_present(self) -> None:
        existing = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
        self.assertEqual(set(existing), set(self.SLUGS))

    def test_each_has_SKILL_md_with_charlie947_schema(self) -> None:
        for slug in self.SLUGS:
            f = SKILLS_DIR / slug / "SKILL.md"
            self.assertTrue(f.is_file(), f"{slug}: missing SKILL.md")
            text = f.read_text()
            self.assertTrue(text.startswith("---\n"), f"{slug}: no frontmatter")
            for field in (
                "name:", "description:", "when_to_use:", "inputs:", "steps:",
                "tools:", "failure_modes:", "last_validated:", "metrics:",
                "prerequisites:", "is_prerequisite_of:",
            ):
                self.assertIn(field, text, f"{slug}: SKILL.md missing {field}")


class HooksExamples(unittest.TestCase):
    def test_required_hook_files_present(self) -> None:
        for rel in (
            "README.md",
            "hooks.example.json",
            "pre-tool-use.sh",
            "post-tool-use.sh",
            "session-end.sh",
            "notification.sh",
        ):
            self.assertTrue((HOOKS_DIR / rel).is_file(), f"missing {rel}")

    def test_hooks_example_json_parses(self) -> None:
        data = json.loads((HOOKS_DIR / "hooks.example.json").read_text())
        self.assertIn("hooks", data)
        for evt in ("PreToolUse", "PostToolUse", "Stop", "Notification"):
            self.assertIn(evt, data["hooks"], f"missing event type: {evt}")

    def test_hook_scripts_pass_bash_n(self) -> None:
        for sh in HOOKS_DIR.glob("*.sh"):
            rc = subprocess.run(
                ["bash", "-n", str(sh)], capture_output=True, text=True, check=False,
            ).returncode
            self.assertEqual(rc, 0, f"bash -n failed: {sh.name}")

    def test_pre_tool_use_blocks_forbidden_pattern(self) -> None:
        # Feed JSON that pretends Claude is about to run `rm -rf /`.
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}})
        proc = subprocess.run(
            [str(HOOKS_DIR / "pre-tool-use.sh")],
            input=payload, capture_output=True, text=True, check=False, timeout=5,
        )
        # Hook exits 0 but emits a block JSON.
        self.assertEqual(proc.returncode, 0)
        try:
            decision = json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            self.fail(f"pre-tool-use stdout not JSON: {proc.stdout!r}")
        self.assertEqual(decision.get("decision"), "block")

    def test_pre_tool_use_allows_safe_pattern(self) -> None:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls -la"}})
        proc = subprocess.run(
            [str(HOOKS_DIR / "pre-tool-use.sh")],
            input=payload, capture_output=True, text=True, check=False, timeout=5,
        )
        self.assertEqual(proc.returncode, 0)
        # Empty stdout = allow.
        self.assertEqual(proc.stdout.strip(), "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
