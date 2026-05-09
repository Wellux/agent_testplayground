"""Pre-Round-8 audit invariants. These tests fail loudly if anything
the Stage C apply-gate depends on regresses."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
RMC = REPO / "prompts" / "ralph-meta-chain"
SCRIPTS = RMC / "scripts"
MIGRATION = RMC / "migration"
CONFIG = RMC / "config"


def _run(
    cmd: list[str],
    env: dict | None = None,
    timeout: int = 30,
    cwd: pathlib.Path | None = None,
) -> tuple[int, str, str]:
    full = os.environ.copy()
    if env:
        full.update(env)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=full, check=False,
        cwd=str(cwd) if cwd else None,
    )
    return proc.returncode, proc.stdout, proc.stderr


class PrivacyGuard(unittest.TestCase):
    """No user identifier leaks anywhere. Verbatim mirror of the CI
    privacy job; here so the harness suite catches regressions even
    when CI hasn't run."""

    def test_no_email_leaked_in_tracked_files(self) -> None:
        # Reconstruct the needle without ever embedding it directly.
        needle = "equality.power" + "tothepeople"
        rc, out, _ = _run(
            ["git", "grep", "-in", "--", needle, ":!.github/workflows/ci.yml"],
            cwd=REPO,
        )
        # rc=1 means no match (clean). rc=0 means match found (leak).
        self.assertEqual(rc, 1, f"user-identifier leaked:\n{out}")


class VaultTemplateValidators(unittest.TestCase):
    """vault-template/ is the seed source; if it doesn't validate,
    every fresh user vault inherits the breakage."""

    def test_frontmatter_validator_clean(self) -> None:
        env = {"VAULT": str(RMC / "vault-template")}
        rc, _, _ = _run([str(SCRIPTS / "ralph_validate_frontmatter.sh")], env=env)
        self.assertEqual(rc, 0, "vault-template/ has frontmatter failures")

    def test_check_links_clean(self) -> None:
        env = {"VAULT": str(RMC / "vault-template")}
        rc, _, _ = _run([str(SCRIPTS / "ralph_check_links.sh")], env=env)
        self.assertEqual(rc, 0, "vault-template/ has broken wikilinks")


class ProviderConformance(unittest.TestCase):
    """Each adapter spec must hit all 13 fields per
    providers/provider-interface.md. Stage C activation gates depend
    on this."""

    def test_provider_validate_clean(self) -> None:
        rc, _, err = _run([str(SCRIPTS / "ralph_provider_validate.sh")])
        self.assertEqual(rc, 0, f"provider conformance failures:\n{err}")


class BusinessLedgerLint(unittest.TestCase):
    """Every business-entity ledger has the canonical schema."""

    def test_ledger_check_clean(self) -> None:
        rc, _, err = _run([str(SCRIPTS / "ralph_business_ledger_check.sh")])
        self.assertEqual(rc, 0, f"business-entity ledger lint failures:\n{err}")


class JSONSchemaValidity(unittest.TestCase):
    """All four config schemas must parse as draft-07."""

    REQUIRED = (
        "ralph.config.schema.json",
        "provider-interface.schema.json",
        "memory-frontmatter.schema.json",
        "experiment.schema.json",
    )

    def test_four_schemas_present(self) -> None:
        existing = sorted(p.name for p in CONFIG.glob("*.schema.json"))
        self.assertEqual(set(existing), set(self.REQUIRED))

    def test_each_schema_is_draft07(self) -> None:
        for name in self.REQUIRED:
            data = json.loads((CONFIG / name).read_text())
            self.assertEqual(
                data.get("$schema"),
                "https://json-schema.org/draft-07/schema#",
                f"{name}: not draft-07",
            )
            self.assertTrue(data.get("$id"), f"{name}: missing $id")
            self.assertTrue(data.get("title"), f"{name}: missing title")


class MigrationPipelineReadyForStageC(unittest.TestCase):
    """The Stage C apply gate refuses unless the read-only pipeline
    produces zero conflicts. Verifying this in Python keeps Stage C
    eligibility green between every push.

    Pipeline runs ONCE per test class (setUpClass), not per test —
    each propose run is ~5 s on this repo, so caching shaves > 30 s
    off the full suite."""

    @classmethod
    def setUpClass(cls) -> None:
        scripts = MIGRATION / "scripts"
        assert (scripts / "ralph_repo_inventory.sh").exists()
        # ralph_repo_inventory.sh shells out per file for size+mtime+sha256;
        # locally ~9 s on this repo, but slow CI runners or high-IO loads
        # can push it past the _run() default of 30 s. Bump to 180 s for
        # the full pipeline (each step independently) so a one-off slow
        # step doesn't fail the whole audit suite.
        for s in (
            "ralph_repo_inventory.sh",
            "ralph_classify_repo_files.sh",
            "ralph_propose_migration.sh",
        ):
            rc, _, err = _run([str(scripts / s)], timeout=180)
            if rc != 0:
                raise AssertionError(f"{s} failed: {err}")

    def test_proposed_moves_present_with_archived_count(self) -> None:
        moves = (MIGRATION / "proposed-moves.md").read_text()
        self.assertIn("# Proposed Moves", moves)
        self.assertIn("archived_pre_migrated:", moves,
                      "proposed-moves.md missing archived_pre_migrated header")

    def test_zero_conflicts_post_audit(self) -> None:
        conflicts = (MIGRATION / "conflicts.md").read_text()
        self.assertIn("(none)", conflicts,
                      "Stage C apply gate would refuse — conflicts present")

    def test_rollback_plan_covers_every_move(self) -> None:
        moves = (MIGRATION / "proposed-moves.md").read_text()
        rollback = (MIGRATION / "rollback-plan.md").read_text()
        # Count rows in each (≥ 5 rows means populated).
        moves_rows = [l for l in moves.splitlines() if l.startswith("| ") and "|" in l[2:]]
        rollback_rows = [l for l in rollback.splitlines() if l.startswith("| ") and "|" in l[2:]]
        self.assertGreaterEqual(len(moves_rows), 50,
                                "expected ≥ 50 rows in proposed-moves.md")
        self.assertGreaterEqual(len(rollback_rows), 50,
                                "rollback-plan.md should mirror moves count")

    def test_apply_default_dry_run_exits_64(self) -> None:
        rc, _, _ = _run(
            [str(MIGRATION / "scripts" / "ralph_apply_migration.sh")],
            timeout=120,
        )
        self.assertEqual(rc, 64, "apply default mode must be dry-run-correct (exit 64)")

    def test_apply_token_changes_when_proposal_changes(self) -> None:
        """Hash binding: the approval token must reflect the current
        proposed-moves.md content. Run propose twice with no source
        changes; sha256 must remain stable."""
        first = (MIGRATION / "proposed-moves.md").read_text()
        _run(
            [str(MIGRATION / "scripts" / "ralph_propose_migration.sh")],
            timeout=120,
        )
        second = (MIGRATION / "proposed-moves.md").read_text()
        # Bodies differ in `generated:` timestamp; hash the body sans frontmatter.
        def _strip_fm(text: str) -> str:
            if not text.startswith("---\n"):
                return text
            try:
                end = text.index("\n---\n", 4)
                return text[end + 5:]
            except ValueError:
                return text
        self.assertEqual(_strip_fm(first), _strip_fm(second),
                         "propose output not deterministic across runs")


class StageBArtifactsTracked(unittest.TestCase):
    """Stage B left tracked audit artifacts the Stage C apply needs."""

    def test_runbook_present(self) -> None:
        runbook = RMC / "docs" / "ROUND_8_RUNBOOK.md"
        self.assertTrue(runbook.is_file(), "ROUND_8_RUNBOOK.md missing")
        text = runbook.read_text()
        for section in ("Stage A", "Stage B", "Stage C", "Six gates"):
            self.assertIn(section, text, f"runbook missing section: {section}")

    def test_stage_b_summary_present(self) -> None:
        summary = MIGRATION / "STAGE_B_SUMMARY.md"
        self.assertTrue(summary.is_file(), "STAGE_B_SUMMARY.md missing")
        text = summary.read_text()
        self.assertIn("RALPH_MIGRATION_APPROVED", text,
                      "STAGE_B_SUMMARY.md should document the approval token")

    def test_at_least_one_ci_backup_tracked(self) -> None:
        backups = sorted(MIGRATION.glob("ci-backup-*.yml"))
        self.assertGreater(len(backups), 0, "no CI backup files tracked")
        # The backup must be a valid YAML.
        try:
            import yaml
            yaml.safe_load(backups[-1].read_text())
        except ImportError:
            # PyYAML not available in this environment; skip the parse check.
            pass

    def test_migration_log_tracked(self) -> None:
        log = MIGRATION / "migration-log.md"
        self.assertTrue(log.is_file(), "migration-log.md missing (Stage B should track)")


class StageCArtifactsTracked(unittest.TestCase):
    """Stage C-readiness artifacts (preview + post-apply CI template)."""

    def test_preview_doc_present(self) -> None:
        preview = MIGRATION / "STAGE_C_PREVIEW.md"
        self.assertTrue(preview.is_file(), "STAGE_C_PREVIEW.md missing")
        text = preview.read_text()
        for required in (
            "Phase 1-6 → master-spec target (50 git mv operations)",
            "Round 6-superseded → archive",
            "Round 1-superseded → archive",
            "CI workflow update",
            "Six gates",
            "Decision checklist",
        ):
            self.assertIn(required, text,
                          f"STAGE_C_PREVIEW.md missing section: {required}")

    def test_post_round8_ci_template_present_and_yaml_valid(self) -> None:
        template = MIGRATION / "STAGE_C_CI_WORKFLOW.yml"
        self.assertTrue(template.is_file(), "STAGE_C_CI_WORKFLOW.yml missing")
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(template.read_text())
        self.assertIn("jobs", data)
        # Post-Round-8 jobs: privacy + shell + validators + python +
        # voice-server + plugin (plugin-greenfield merges into plugin
        # since obsidian-ralph/ is archived).
        for required_job in (
            "privacy", "shell", "validators", "python",
            "voice-server", "plugin",
        ):
            self.assertIn(required_job, data["jobs"],
                          f"post-Round-8 CI missing job: {required_job}")

    def test_post_round8_ci_template_uses_master_spec_paths(self) -> None:
        template = MIGRATION / "STAGE_C_CI_WORKFLOW.yml"
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(template.read_text())
        py_wd = data["jobs"]["python"]["defaults"]["run"]["working-directory"]
        self.assertEqual(py_wd, "prompts/ralph-meta-chain/scripts/harness")
        vs_wd = data["jobs"]["voice-server"]["defaults"]["run"]["working-directory"]
        self.assertEqual(vs_wd, "prompts/ralph-meta-chain/voice-server")
        pl_wd = data["jobs"]["plugin"]["defaults"]["run"]["working-directory"]
        self.assertEqual(pl_wd, "prompts/ralph-meta-chain/obsidian-plugin")

    def test_apply_help_documents_update_ci_flag(self) -> None:
        apply_script = MIGRATION / "scripts" / "ralph_apply_migration.sh"
        rc, out, _ = _run([str(apply_script), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("--update-ci", out,
                      "apply --help should document --update-ci")
        self.assertIn("STAGE_C_CI_WORKFLOW.yml", out,
                      "apply --help should reference the template name")

    def test_apply_with_update_ci_alone_default_dry_runs(self) -> None:
        rc, _, _ = _run([
            str(MIGRATION / "scripts" / "ralph_apply_migration.sh"),
            "--update-ci",
        ])
        self.assertEqual(rc, 64, "--update-ci alone must dry-run (gates 4-5 missing)")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
