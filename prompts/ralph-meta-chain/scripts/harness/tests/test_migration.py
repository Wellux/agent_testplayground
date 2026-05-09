"""Smoke tests for the Round 4 migration scripts. Read-only path only;
apply / rollback are gated and we never call them with --apply --confirmed
in CI."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
import unittest

def _find_repo_root() -> pathlib.Path:
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("no .git ancestor found")


REPO = _find_repo_root()
SCRIPTS = REPO / "prompts" / "ralph-meta-chain" / "migration" / "scripts"
MIG_DIR = REPO / "prompts" / "ralph-meta-chain" / "migration"


def _run(cmd: list[str], cwd: pathlib.Path = REPO, env: dict | None = None,
         timeout: int = 30) -> tuple[int, str, str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout, env=full_env, check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


class HelpFlags(unittest.TestCase):
    """Per the master spec: every script must support --help."""

    def test_inventory_help(self) -> None:
        rc, out, _ = _run([str(SCRIPTS / "ralph_repo_inventory.sh"), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("Read-only repo file walker", out)

    def test_classify_help(self) -> None:
        rc, out, _ = _run([str(SCRIPTS / "ralph_classify_repo_files.sh"), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("migration class", out)

    def test_propose_help(self) -> None:
        rc, out, _ = _run([str(SCRIPTS / "ralph_propose_migration.sh"), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("proposed-moves", out)

    def test_apply_help(self) -> None:
        rc, out, _ = _run([str(SCRIPTS / "ralph_apply_migration.sh"), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("CRITICAL", out)
        # Should explicitly enumerate the six gates / exit codes.
        for code in ("64", "65", "66", "67", "68"):
            self.assertIn(code, out, f"--help should document exit code {code}")

    def test_rollback_help(self) -> None:
        rc, out, _ = _run([str(SCRIPTS / "ralph_rollback_migration.sh"), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("Reverse a prior migration apply", out)


class InventoryWalker(unittest.TestCase):
    """The inventory script is read-only and idempotent."""

    def test_inventory_writes_report(self) -> None:
        rc, _, _ = _run([str(SCRIPTS / "ralph_repo_inventory.sh")])
        self.assertEqual(rc, 0)
        out = MIG_DIR / "inventory-report.md"
        self.assertTrue(out.exists())
        body = out.read_text()
        self.assertIn("# Inventory Report", body)
        self.assertIn("| Path | Bytes | mtime UTC | sha256 |", body)
        # Should list at least the main README + this test file.
        self.assertIn("README.md", body)


class ClassifyAndPropose(unittest.TestCase):
    """Classification + proposal pipeline."""

    def test_classify_runs_inventory_if_missing(self) -> None:
        # Remove inventory; classify should regenerate.
        inv = MIG_DIR / "inventory-report.md"
        if inv.exists():
            inv.unlink()
        rc, _, _ = _run([str(SCRIPTS / "ralph_classify_repo_files.sh")])
        self.assertEqual(rc, 0)
        cls = MIG_DIR / "file-classification.md"
        self.assertTrue(cls.exists())
        body = cls.read_text()
        self.assertIn("# File Classification", body)
        self.assertIn("| Class | Count |", body)

    def test_propose_writes_three_artifacts(self) -> None:
        rc, _, _ = _run([str(SCRIPTS / "ralph_propose_migration.sh")])
        # rc 0 (no conflicts) OR rc 65 (conflicts present) — both acceptable.
        self.assertIn(rc, (0, 65))
        for name in ("proposed-moves.md", "rollback-plan.md", "conflicts.md"):
            self.assertTrue((MIG_DIR / name).exists(), f"missing {name}")
        moves = (MIG_DIR / "proposed-moves.md").read_text()
        self.assertIn("# Proposed Moves", moves)

    def test_propose_retargets_pre_migrated_to_archive(self) -> None:
        """Pre-Round-8: when a target path already exists (an earlier
        round superseded it), the source must be retargeted to
        migration/_archive/_pre-migrated/ rather than reported as a
        conflict. Post-Round-8: nothing left to retarget — but conflicts
        must still report zero."""
        _run([str(SCRIPTS / "ralph_propose_migration.sh")])
        moves = (MIG_DIR / "proposed-moves.md").read_text()
        conflicts = (MIG_DIR / "conflicts.md").read_text()
        self.assertIn("(none)", conflicts, "conflicts.md must always be (none)")
        # Pre-Round-8 only: assert the retarget mechanism worked. Detect
        # by presence of obsidian-ralph/ at the repo root (Phase 1-6
        # reference still alive). After Stage C, that dir is empty/gone
        # and the assertion is vacuous; skip rather than fail.
        if (REPO / "obsidian-ralph" / "manifest.json").exists():
            self.assertIn(
                "_archive/_pre-migrated/", moves,
                "expected _archive/_pre-migrated/ retargets in proposed-moves.md",
            )
            self.assertIn(
                "obsidian-ralph/", moves,
                "obsidian-ralph/ should appear in retargeted moves",
            )


class ApplyGates(unittest.TestCase):
    """Apply must refuse unless ALL six gates pass. CI never sets the
    approval token, so apply must always refuse here."""

    def test_apply_default_dry_run_or_refuse(self) -> None:
        # Ensure proposal artifacts exist first.
        _run([str(SCRIPTS / "ralph_propose_migration.sh")])
        rc, out, err = _run([str(SCRIPTS / "ralph_apply_migration.sh")])
        # Acceptable outcomes:
        # - rc 64 (default dry-run; no --apply --confirmed)
        # - rc 65 (conflicts present; refusing)
        self.assertIn(rc, (64, 65), f"unexpected rc={rc}; stderr={err}")

    def test_apply_with_apply_confirmed_but_no_token_refuses(self) -> None:
        _run([str(SCRIPTS / "ralph_propose_migration.sh")])
        rc, _, err = _run(
            [str(SCRIPTS / "ralph_apply_migration.sh"), "--apply", "--confirmed"]
        )
        # Acceptable: rc 65 (conflicts), rc 67 (token mismatch), or rc 68 (dirty tree).
        self.assertIn(rc, (65, 67, 68), f"unexpected rc={rc}; stderr={err}")


class RollbackGates(unittest.TestCase):
    """Rollback must refuse without --apply --confirmed."""

    def test_rollback_default_dry_run(self) -> None:
        # Ensure rollback-plan exists.
        _run([str(SCRIPTS / "ralph_propose_migration.sh")])
        rb = MIG_DIR / "rollback-plan.md"
        if not rb.exists():
            self.skipTest("rollback-plan.md not generated (likely conflicts)")
        rc, out, err = _run([str(SCRIPTS / "ralph_rollback_migration.sh")])
        self.assertEqual(rc, 64)
        # `ralph_log` writes "DRY RUN" to stderr; the inverse moves go to
        # stdout. Post-Stage-C the rollback plan has 0 inverse moves so
        # stdout is empty — but the DRY RUN message on stderr is the
        # canonical signal that the script defaulted to dry-run.
        self.assertIn("DRY RUN", err)


class CommonShOK(unittest.TestCase):
    """Shellcheck-style smoke: bash -n on every script."""

    def test_bash_n_on_all_scripts(self) -> None:
        for f in sorted(SCRIPTS.rglob("*.sh")):
            rc, _, err = _run(["bash", "-n", str(f)])
            self.assertEqual(rc, 0, f"bash -n failed on {f.name}: {err}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
