"""Smoke tests for the harness CLI. No network, no API key, no Ollama."""
from __future__ import annotations

import json
import os
import pathlib
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


class MemoryBackends(unittest.TestCase):
    """The default selector returns None (current code path); explicit
    cognee/letta selections should error cleanly when packages are absent."""

    def test_default_returns_none(self) -> None:
        from harness.memory_backends import select_backend
        self.assertIsNone(select_backend("", vault=pathlib.Path("/tmp"), model="x"))
        self.assertIsNone(select_backend("local-sqlite-vec", vault=pathlib.Path("/tmp"), model="x"))

    def test_unknown_backend_raises(self) -> None:
        from harness.memory_backends import select_backend
        with self.assertRaises(ValueError):
            select_backend("not-a-backend", vault=pathlib.Path("/tmp"), model="x")

    def test_cognee_missing_pkg_errors(self) -> None:
        # cognee is not in the harness deps; picking it should fail clearly.
        from harness.memory_backends import select_backend
        with self.assertRaises(RuntimeError):
            select_backend("cognee", vault=pathlib.Path("/tmp"), model="x")


class ReflectAppend(unittest.TestCase):
    def test_appends_to_empty_list(self) -> None:
        from harness.reflect import _append_reflection
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "cand.md"
            p.write_text("---\nname: x\nreflections: []\n---\n\nbody\n")
            self.assertTrue(_append_reflection(p, "[2026-05-09] terse rubric ok"))
            text = p.read_text()
            self.assertIn('reflections:\n  - "[2026-05-09] terse rubric ok"', text)

    def test_appends_when_no_field_exists(self) -> None:
        from harness.reflect import _append_reflection
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "cand.md"
            p.write_text("---\nname: x\n---\n\nbody\n")
            self.assertTrue(_append_reflection(p, "[2026-05-09] new"))
            text = p.read_text()
            self.assertIn("reflections:", text)
            self.assertIn('- "[2026-05-09] new"', text)
            self.assertIn("\nbody\n", text)

    def test_skips_when_no_frontmatter(self) -> None:
        from harness.reflect import _append_reflection
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "no-fm.md"
            p.write_text("# just a body, no frontmatter\n")
            self.assertFalse(_append_reflection(p, "x"))


class HeuristicVerdict(unittest.TestCase):
    def test_candidate_wins_when_better_rubric_and_fewer_tokens(self) -> None:
        from harness.reflect import _heuristic_verdict
        v = _heuristic_verdict(
            inc={"rubric": 3.5, "tokens": 600, "banned": 0},
            can={"rubric": 4.0, "tokens": 500, "banned": 0},
        )
        self.assertEqual(v, "candidate-wins")

    def test_incumbent_wins_when_higher_rubric(self) -> None:
        from harness.reflect import _heuristic_verdict
        v = _heuristic_verdict(
            inc={"rubric": 4.5, "tokens": 600, "banned": 0},
            can={"rubric": 3.0, "tokens": 500, "banned": 0},
        )
        self.assertEqual(v, "incumbent-wins")


class TracesView(unittest.TestCase):
    def test_returns_1_on_empty_file(self) -> None:
        import io, contextlib
        from harness import traces as traces_mod
        with tempfile.TemporaryDirectory() as d:
            vault = pathlib.Path(d) / "vault"
            (vault / "90-Meta").mkdir(parents=True)
            os.environ["VAULT"] = str(vault)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = traces_mod.run(tail=10, axis=None, vault_override=str(vault),
                                    config_path=str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"))
            self.assertEqual(rc, 1)
            self.assertIn("(no rows)", buf.getvalue())

    def test_summarizes_by_axis(self) -> None:
        import io, contextlib
        from harness import traces as traces_mod
        with tempfile.TemporaryDirectory() as d:
            vault = pathlib.Path(d) / "vault"
            (vault / "90-Meta").mkdir(parents=True)
            (vault / "90-Meta" / "metrics.ndjson").write_text(
                '{"axis":"memory","verdict":"validated"}\n'
                '{"axis":"memory","verdict":"refuted"}\n'
                '{"axis":"skills","verdict":"validated"}\n',
                encoding="utf8",
            )
            os.environ["VAULT"] = str(vault)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = traces_mod.run(tail=100, axis=None, vault_override=str(vault),
                                    config_path=str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"))
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("memory: 2", out)
            self.assertIn("skills: 1", out)


class SeedTreeShipped(unittest.TestCase):
    """Verify the seed/ tree exists and contains the canonical first-day files."""

    def test_seed_files_present(self) -> None:
        seed = REPO / "prompts" / "ralph-meta-chain" / "seed"
        self.assertTrue(seed.is_dir())
        for rel in (
            "CLAUDE.md",
            "40-Skills/recall.md",
            "40-Skills/pr-from-branch.md",
            "50-Prompts/code-review.md",
            "50-Prompts/daily-summary.md",
            "60-Interactions/user-profile.md",
            "00-Inbox/sample-capture.md",
            "10-Daily/2026-05-09.md",
        ):
            self.assertTrue((seed / rel).is_file(), f"missing seed file: {rel}")


class SelfTest(unittest.TestCase):
    """The privacy + shell + python checks should all pass on the current
    tree. Plugin check is best-effort (skipped if no node_modules)."""

    def test_privacy_check_passes(self) -> None:
        from harness.self_test import _check_privacy
        c = _check_privacy(REPO)
        self.assertTrue(c.ok, c.detail)
        self.assertEqual(c.name, "privacy")

    def test_shell_check_passes(self) -> None:
        from harness.self_test import _check_shell
        c = _check_shell(REPO)
        self.assertTrue(c.ok, c.detail)

    def test_python_check_passes(self) -> None:
        from harness.self_test import _check_python
        c = _check_python(REPO)
        self.assertTrue(c.ok, c.detail)

    def test_writes_ndjson_row_per_check(self) -> None:
        from harness.self_test import run
        with tempfile.TemporaryDirectory() as d:
            vault = pathlib.Path(d) / "vault"
            (vault / "90-Meta").mkdir(parents=True)
            os.environ["VAULT"] = str(vault)
            rc = run(only="privacy",
                     vault_override=str(vault),
                     config_path=str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"))
            ndjson = (vault / "90-Meta" / "heal-checks.ndjson").read_text()
            self.assertEqual(rc, 0)
            self.assertEqual(len(ndjson.strip().splitlines()), 1)
            row = json.loads(ndjson.strip().splitlines()[0])
            self.assertEqual(row["name"], "privacy")
            self.assertTrue(row["ok"])


class CreatorRender(unittest.TestCase):
    def test_render_creators_groups_by_handle(self) -> None:
        from harness.ingest import _render_creators
        items = [
            {"channel": "AlexFinnOfficial", "title": "Claude Code in 25 min",
             "url": "https://www.youtube.com/watch?v=aaa", "published": "2026-04-15T12:00:00+00:00"},
            {"channel": "mreflow", "title": "AI news",
             "url": "https://www.youtube.com/watch?v=bbb", "published": "2026-04-15T13:00:00+00:00"},
            {"channel": "AlexFinnOfficial", "title": "Vibe coding 101",
             "url": "https://www.youtube.com/watch?v=ccc", "published": "2026-04-16T12:00:00+00:00"},
        ]
        out = _render_creators("2026-05-09", items)
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("type: research", out)
        self.assertIn("source: youtube-creators", out)
        self.assertIn("## @AlexFinnOfficial", out)
        self.assertIn("## @mreflow", out)
        self.assertIn("Claude Code in 25 min", out)
        self.assertIn("Vibe coding 101", out)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
