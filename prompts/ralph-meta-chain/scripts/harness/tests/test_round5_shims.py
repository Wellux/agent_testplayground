"""Smoke tests for the Round 5 shims + JSON schemas. Mirrors the bats
files at prompts/ralph-meta-chain/tests/, but uses unittest so CI
(without bats installed) still validates."""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

def _find_repo_root() -> pathlib.Path:
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("no .git ancestor found")


REPO = _find_repo_root()
SCRIPTS = REPO / "prompts" / "ralph-meta-chain" / "scripts"
CONFIG_DIR = REPO / "prompts" / "ralph-meta-chain" / "config"
SHIM_NAMES = (
    "ralph_memory_optimize.sh",
    "ralph_skills_optimize.sh",
    "ralph_interaction_optimize.sh",
    "ralph_context_compress.sh",
    "ralph_index_vault.sh",
    "ralph_ab_harness.sh",
    "ralph_autoheal.sh",
    "ralph_autoupdate_propose.sh",
    "ralph_research_digest.sh",
    "ralph_daily_report.sh",
    "ralph_git_audit.sh",
    "ralph_validate_frontmatter.sh",
    "ralph_check_links.sh",
    "ralph_provider_validate.sh",
    "ralph_business_ledger_check.sh",
    "ralph_bootstrap_embed.sh",
)


def _run(cmd: list[str], env: dict | None = None, timeout: int = 20) -> tuple[int, str, str]:
    full = os.environ.copy()
    if env:
        full.update(env)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=full, check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ShimsPresent(unittest.TestCase):
    def test_all_shims_present(self) -> None:
        existing = sorted(p.name for p in SCRIPTS.glob("ralph_*.sh"))
        self.assertEqual(set(existing), set(SHIM_NAMES),
                         f"shim list mismatch:\n  got: {existing}")

    def test_each_shim_has_help_with_USAGE(self) -> None:
        for name in SHIM_NAMES:
            path = SCRIPTS / name
            self.assertTrue(path.exists(), f"missing shim: {name}")
            rc, out, _ = _run([str(path), "--help"])
            self.assertEqual(rc, 0, f"{name} --help exited {rc}")
            self.assertIn("USAGE", out, f"{name} --help has no USAGE block")


class LibBashSyntax(unittest.TestCase):
    def test_lib_files_pass_bash_n(self) -> None:
        lib_dir = SCRIPTS / "lib"
        files = sorted(lib_dir.glob("*.sh"))
        self.assertGreaterEqual(len(files), 11, "expected ≥ 11 lib files")
        for f in files:
            rc, _, err = _run(["bash", "-n", str(f)])
            self.assertEqual(rc, 0, f"bash -n failed on {f.name}: {err}")


class JsonSchemas(unittest.TestCase):
    def test_4_schemas_present(self) -> None:
        names = sorted(p.name for p in CONFIG_DIR.glob("*.schema.json"))
        self.assertEqual(set(names), {
            "ralph.config.schema.json",
            "provider-interface.schema.json",
            "memory-frontmatter.schema.json",
            "experiment.schema.json",
        })

    def test_each_schema_is_parseable_draft7(self) -> None:
        for f in CONFIG_DIR.glob("*.schema.json"):
            data = json.loads(f.read_text())
            self.assertEqual(
                data.get("$schema"),
                "https://json-schema.org/draft-07/schema#",
                f"{f.name}: $schema is not draft-07",
            )
            self.assertIn("$id", data)
            self.assertIn("title", data)


class ValidatorsAgainstShippedTree(unittest.TestCase):
    def test_provider_validate_passes(self) -> None:
        rc, _, _ = _run([str(SCRIPTS / "ralph_provider_validate.sh")])
        self.assertEqual(rc, 0)

    def test_business_ledger_check_passes(self) -> None:
        rc, _, _ = _run([str(SCRIPTS / "ralph_business_ledger_check.sh")])
        self.assertEqual(rc, 0)


class ValidatorsAgainstScratchVault(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.vault = pathlib.Path(self.tmp) / "vault"
        for sub in ("30-Notes", "40-Skills", "90-Meta"):
            (self.vault / sub).mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, rel: str, body: str) -> None:
        p = self.vault / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def test_validate_frontmatter_clean(self) -> None:
        self._write("30-Notes/ok.md",
                    "---\nralph_type: memory\ncreated: 2026-05-09\n---\n# ok\n")
        rc, _, _ = _run(
            [str(SCRIPTS / "ralph_validate_frontmatter.sh")],
            env={"VAULT": str(self.vault)},
        )
        self.assertEqual(rc, 0)

    def test_validate_frontmatter_flags_missing_field(self) -> None:
        self._write("30-Notes/bad.md",
                    "---\ncreated: 2026-05-09\n---\n# missing ralph_type\n")
        rc, _, _ = _run(
            [str(SCRIPTS / "ralph_validate_frontmatter.sh")],
            env={"VAULT": str(self.vault)},
        )
        self.assertGreaterEqual(rc, 1)

    def test_check_links_flags_broken(self) -> None:
        self._write(
            "30-Notes/note.md",
            "---\nralph_type: memory\ncreated: 2026-05-09\n---\n[[orphan-target]]\n",
        )
        rc, _, err = _run(
            [str(SCRIPTS / "ralph_check_links.sh")],
            env={"VAULT": str(self.vault)},
        )
        self.assertGreaterEqual(rc, 1, f"expected nonzero, stderr={err}")
        self.assertIn("broken link", err)

    def test_check_links_clean_when_target_exists(self) -> None:
        self._write(
            "30-Notes/note.md",
            "---\nralph_type: memory\ncreated: 2026-05-09\n---\n[[other]]\n",
        )
        self._write(
            "30-Notes/other.md",
            "---\nralph_type: memory\ncreated: 2026-05-09\n---\n# other\n",
        )
        rc, _, _ = _run(
            [str(SCRIPTS / "ralph_check_links.sh")],
            env={"VAULT": str(self.vault)},
        )
        self.assertEqual(rc, 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
