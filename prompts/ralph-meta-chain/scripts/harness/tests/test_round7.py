"""Smoke tests for Round 7 — indexes + benchmarks + experiments scaffolds."""
from __future__ import annotations

import pathlib
import re
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
INDEXES = RMC / "indexes"
BENCHMARKS = RMC / "benchmarks"
EXPERIMENTS = RMC / "experiments"


class IndexesPresent(unittest.TestCase):
    REQUIRED = (
        "README.md",
        "vault-index.md",
        "memory-index.md",
        "skill-index.md",
        "prompt-index.md",
        "provider-index.md",
        "business-index.md",
    )

    def test_seven_files(self) -> None:
        existing = sorted(p.name for p in INDEXES.glob("*.md"))
        self.assertEqual(set(existing), set(self.REQUIRED))

    def test_each_index_has_frontmatter(self) -> None:
        # README.md is exempt (human-prose entry point).
        for name in self.REQUIRED:
            if name == "README.md":
                continue
            text = (INDEXES / name).read_text()
            self.assertTrue(text.startswith("---\n"), f"{name}: no frontmatter")

    def test_each_cross_references_canonical_doc(self) -> None:
        # Every index should point at docs/, vault-template/, or other parts
        # of prompts/ralph-meta-chain/ — proves it's not orphaned.
        pattern = re.compile(r"(docs/|vault-template/|prompts/ralph-meta-chain/|harness/)")
        for name in self.REQUIRED:
            if name == "README.md":
                continue
            text = (INDEXES / name).read_text()
            self.assertRegex(text, pattern, f"{name}: no cross-references")


class BenchmarksPresent(unittest.TestCase):
    REQUIRED = (
        "README.md",
        "memory-quality.md",
        "skill-quality.md",
        "prompt-quality.md",
        "interaction-quality.md",
        "business-action-quality.md",
        "migration-quality.md",
    )

    def test_seven_files(self) -> None:
        existing = sorted(p.name for p in BENCHMARKS.glob("*.md"))
        self.assertEqual(set(existing), set(self.REQUIRED))

    def test_each_documents_pass_threshold(self) -> None:
        for name in self.REQUIRED:
            if name == "README.md":
                continue
            text = (BENCHMARKS / name).read_text()
            self.assertIn("Pass threshold", text, f"{name}: no Pass threshold section")

    def test_each_scorecard_has_axes(self) -> None:
        # Each scorecard must define ≥ 3 scored axes (1-5 each).
        for name in self.REQUIRED:
            if name == "README.md":
                continue
            text = (BENCHMARKS / name).read_text()
            # Count "### <axis> (1-5)" headings.
            axes = re.findall(r"^### .*?\(1-5\)", text, re.M)
            self.assertGreaterEqual(
                len(axes), 3, f"{name}: only {len(axes)} scored axes (≥ 3 required)"
            )


class ExperimentsScaffoldPresent(unittest.TestCase):
    def test_readme_and_three_gitkeeps(self) -> None:
        self.assertTrue((EXPERIMENTS / "README.md").is_file())
        for sub in ("fixtures", "outputs", "reports"):
            self.assertTrue((EXPERIMENTS / sub / ".gitkeep").is_file(),
                            f"missing experiments/{sub}/.gitkeep")

    def test_readme_references_harness_fixtures(self) -> None:
        text = (EXPERIMENTS / "README.md").read_text()
        self.assertIn("harness/fixtures/", text)
        self.assertIn("harness ab", text)


class CrossLinkedFromDocs(unittest.TestCase):
    """Round 7 deliverables should be findable from at least one
    docs/ or roadmap entry; otherwise they're orphans."""

    def test_indexes_referenced_in_at_least_one_doc(self) -> None:
        # ROADMAP.md is the canonical entry point for the rounds; it
        # explicitly mentions Round 7 outputs.
        roadmap = (RMC / "docs" / "ROADMAP.md").read_text()
        for word in ("indexes", "benchmarks", "experiments"):
            self.assertIn(word, roadmap, f"ROADMAP.md does not mention {word}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
