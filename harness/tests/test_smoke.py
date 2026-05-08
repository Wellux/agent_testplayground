"""Smoke tests for the harness CLI. No network, no API key, no Ollama."""
from __future__ import annotations

import datetime as _dt
import io
import json
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "harness"))


class ImportSmoke(unittest.TestCase):
    """Every module must at least import cleanly."""

    def test_imports(self) -> None:
        import harness  # noqa: F401
        from harness import ab, compress, embeddings, ingest, judge, __main__  # noqa: F401


class RenderPrompt(unittest.TestCase):
    """The promptfoo-style {{var}} substitution should be plain string replace."""

    def test_render_substitutes_named_vars(self) -> None:
        from harness.ab import _render_prompt
        out = _render_prompt("Hello {{name}}, count={{n}}", {"name": "Ralph", "n": 3})
        self.assertEqual(out, "Hello Ralph, count=3")

    def test_render_leaves_unknown_vars_alone(self) -> None:
        from harness.ab import _render_prompt
        out = _render_prompt("Hi {{name}}, nothing={{missing}}", {"name": "X"})
        self.assertEqual(out, "Hi X, nothing={{missing}}")


class JudgeBanned(unittest.TestCase):
    """Banned-phrase counter is pure local logic; verify it without API calls."""

    def test_count_banned_phrases(self) -> None:
        from harness.judge import _count_banned
        self.assertEqual(_count_banned("clean output"), 0)
        self.assertEqual(_count_banned("Great question! As an AI, I'd be happy to help."), 3)

    def test_check_asserts(self) -> None:
        from harness.judge import _check_asserts
        text = "short reply containing the word flush"
        self.assertEqual(_check_asserts(text, [{"type": "max-tokens", "value": 100}]), 0)
        self.assertEqual(_check_asserts(text, [{"type": "max-tokens", "value": 1}]), 1)
        self.assertEqual(_check_asserts(text, [{"type": "contains", "value": "flush"}]), 0)
        self.assertEqual(_check_asserts(text, [{"type": "not-contains", "value": "flush"}]), 1)


class IngestRender(unittest.TestCase):
    """Trending → markdown rendering should be deterministic + frontmatter-shaped."""

    def test_render_emits_frontmatter_and_sections(self) -> None:
        from harness.ingest import _render
        rows = [
            {"topic": "hermes", "full": "NousResearch/hermes-agent",
             "url": "https://github.com/NousResearch/hermes-agent",
             "desc": "self-improving agent", "stars_today": 312},
            {"topic": "claude-code", "full": "anthropics/claude-code",
             "url": "https://github.com/anthropics/claude-code",
             "desc": "Claude Code CLI", "stars_today": 0},
        ]
        seen: set[str] = set()
        out = _render("2026-05-08", ["hermes", "claude-code"], rows, seen)
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("type: research", out)
        self.assertIn("topics: [hermes, claude-code]", out)
        self.assertIn("## NousResearch/hermes-agent — ★ +312 today", out)
        self.assertIn("- Tags: [#trending, #hermes]", out)

    def test_render_marks_seen(self) -> None:
        from harness.ingest import _render
        rows = [
            {"topic": "ai", "full": "foo/bar", "url": "https://github.com/foo/bar",
             "desc": "x", "stars_today": 5},
        ]
        seen = {"https://github.com/foo/bar"}
        out = _render("2026-05-08", ["ai"], rows, seen)
        self.assertIn("(seen)", out)


class EmbedSinceParser(unittest.TestCase):
    def test_parse_since_units(self) -> None:
        from harness.embeddings import _parse_since
        self.assertEqual(_parse_since("30s"), 30)
        self.assertEqual(_parse_since("5m"), 300)
        self.assertEqual(_parse_since("2h"), 7200)
        self.assertEqual(_parse_since("1d"), 86400)
        with self.assertRaises(ValueError):
            _parse_since("nope")


class ConfigLoader(unittest.TestCase):
    """Loader should fall back to config.example.yml when config.yml missing."""

    def test_falls_back_to_example(self) -> None:
        from harness import load_config
        cfg = load_config(str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"))
        self.assertIn("vault_path", cfg)
        self.assertIn("budgets", cfg)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
