"""Smoke tests for the harness CLI. No network, no API key, no Ollama."""
from __future__ import annotations

import json
import os
import pathlib
import sys
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

    def test_default_config_path_resolves_to_repo_root(self) -> None:
        """Regression: post-Round-8 the harness lives at
        prompts/ralph-meta-chain/scripts/harness/. Pre-fix,
        `_default_config_path` used `here.parents[2]` which gave
        prompts/ralph-meta-chain/scripts/, then appended
        `prompts/ralph-meta-chain/config.yml` — producing
        `.../scripts/prompts/ralph-meta-chain/config.yml` (doubled).

        After the walk-up fix, the path should land at the actual
        repo root + prompts/ralph-meta-chain/config.yml."""
        from harness import _default_config_path, _find_repo_root
        default = _default_config_path()
        # Must include exactly ONE `prompts/ralph-meta-chain/` segment.
        as_str = str(default)
        self.assertEqual(as_str.count("prompts/ralph-meta-chain/"), 1,
                         f"path doubled: {default}")
        # Repo root must contain a .git dir (sanity that walk-up worked).
        repo = _find_repo_root()
        self.assertTrue((repo / ".git").exists(),
                        f"_find_repo_root() returned {repo} but no .git there")
        # Default-config path must equal repo / prompts / ralph-meta-chain / config.yml
        expected = repo / "prompts" / "ralph-meta-chain" / "config.yml"
        self.assertEqual(default, expected)

    def test_load_config_no_args_falls_back_to_example(self) -> None:
        """Regression for the same path-doubling bug: any harness command
        invoked without --config must still resolve. Pre-fix this raised
        FileNotFoundError because the default path was nonsense."""
        from harness import load_config
        cfg = load_config()  # no args → use default
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

    def test_preserves_yaml_delimiter_when_reflections_is_last_line(self) -> None:
        """Regression: shipped seed prompts have `reflections: []` as the
        last frontmatter line. Without the trailing-newline normalize,
        the rewrite would produce `... ok"---` (closing fence glued to
        the new list item), corrupting the YAML."""
        from harness.reflect import _append_reflection
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "shipped-shape.md"
            # Match exactly what seed/50-Prompts/code-review.md ships with.
            p.write_text(
                "---\n"
                "name: code-review\n"
                "last_rewritten: 2026-05-09\n"
                'validated_against: ["harness/fixtures/code-review.yml"]\n'
                "bin: terse-strict\n"
                "reflections: []\n"
                "---\n"
                "\n"
                "# Review the diff below.\n"
            )
            self.assertTrue(_append_reflection(p, "[2026-05-09] terse rubric ok"))
            text = p.read_text()
            # Closing --- must be on its own line.
            self.assertIn('"[2026-05-09] terse rubric ok"\n---\n', text,
                          f"frontmatter corruption: {text!r}")
            # Body must be untouched.
            self.assertIn("# Review the diff below.\n", text)
            # Round-trip yaml-load to be sure.
            try:
                import yaml
            except ImportError:
                return
            front_end = text.index("\n---", 3)
            front = yaml.safe_load(text[3:front_end])
            self.assertEqual(front["reflections"], ["[2026-05-09] terse rubric ok"])


class CompressPreservesFrontmatter(unittest.TestCase):
    """Codex round-5 P2: harness compress must preserve required
    frontmatter on the rewritten note. Pre-fix the replacement only
    had `compressed_from` + `compressed_at`, missing `ralph_type` +
    `created` — so vault validators rejected every compressed note."""

    def test_extracts_and_preserves_required_fields(self) -> None:
        from harness.compress import _extract_frontmatter, _PRESERVE_FM_FIELDS
        body = (
            "---\n"
            "ralph_type: memory\n"
            "memory_layer: semantic\n"
            "memory_temperature: warm\n"
            "created: 2026-04-15\n"
            "tags: [project, ralph]\n"
            "privacy: private\n"
            "stability: stable\n"
            "irrelevant_field: foo\n"
            "---\n\n"
            "# Some note\n"
        )
        fields, rest = _extract_frontmatter(body)
        # Top-level scalar fields are extracted.
        self.assertEqual(fields.get("ralph_type"), "memory")
        self.assertEqual(fields.get("created"), "2026-04-15")
        self.assertIn("memory_layer", fields)
        self.assertIn("memory_temperature", fields)
        # _PRESERVE_FM_FIELDS includes ralph_type + created at minimum.
        self.assertIn("ralph_type", _PRESERVE_FM_FIELDS)
        self.assertIn("created", _PRESERVE_FM_FIELDS)
        # Body after frontmatter survives intact.
        self.assertIn("# Some note", rest)

    def test_write_compressed_emits_required_fields(self) -> None:
        from harness.compress import _write_compressed
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d) / "30-Notes" / "test-note.md"
            target.parent.mkdir(parents=True)
            preserved = {
                "ralph_type": "memory",
                "memory_layer": "semantic",
                "memory_temperature": "warm",
                "created": "2026-04-15",
                "tags": "[project, ralph]",
                "privacy": "private",
            }
            _write_compressed(
                target, "_archive/test-note-original.md",
                "Compressed summary text.",
                preserved,
            )
            text = target.read_text()
            # Required fields per memory-frontmatter.schema.json.
            self.assertIn("ralph_type: memory", text)
            self.assertIn("created: 2026-04-15", text)
            # Useful preserved fields.
            self.assertIn("memory_layer: semantic", text)
            self.assertIn("memory_temperature: warm", text)
            self.assertIn("tags: [project, ralph]", text)
            self.assertIn("privacy: private", text)
            # Compression-specific fields layered on top.
            self.assertIn("compressed_from:", text)
            self.assertIn("compressed_at:", text)
            self.assertIn("Compressed summary text.", text)
            self.assertIn("> Archived: [[test-note-original]]", text)

    def test_write_compressed_defaults_when_legacy_note_missing_fields(self) -> None:
        """Legacy note without ralph_type still produces a valid
        rewritten note (defaults to ralph_type: memory)."""
        from harness.compress import _write_compressed
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d) / "test-legacy.md"
            _write_compressed(
                target, "_archive/test-legacy-original.md",
                "Summary.",
                preserved={},  # No fields — legacy file.
            )
            text = target.read_text()
            self.assertIn("ralph_type: memory", text)
            self.assertIn("memory_layer: semantic", text)
            self.assertIn("created: ", text)


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

    def test_no_log_skips_ndjson_write(self) -> None:
        """Regression for Codex P2: MCP-driven self-test must NOT mutate
        the heal-checks audit log. The --no-log flag suppresses the
        append while still returning the check rc + detail.
        """
        from harness.self_test import run
        with tempfile.TemporaryDirectory() as d:
            vault = pathlib.Path(d) / "vault"
            (vault / "90-Meta").mkdir(parents=True)
            os.environ["VAULT"] = str(vault)
            rc = run(only="privacy",
                     vault_override=str(vault),
                     config_path=str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"),
                     no_log=True)
            self.assertEqual(rc, 0)
            # The audit file must not have been created.
            self.assertFalse((vault / "90-Meta" / "heal-checks.ndjson").exists())

    def test_only_short_circuits_other_checks(self) -> None:
        """Regression: --only=privacy must NOT run _check_unit_tests
        (which would re-discover SelfTest and recurse for minutes)."""
        from harness import self_test as st

        called: list[str] = []
        original_unit = st._check_unit_tests
        original_plugin = st._check_plugin

        def boom_unit(_repo):
            called.append("unit-tests")
            raise AssertionError("unit-tests check should not run when only=privacy")

        def boom_plugin(_repo):
            called.append("plugin")
            raise AssertionError("plugin check should not run when only=privacy")

        st._CHECK_REGISTRY["unit-tests"] = boom_unit  # type: ignore[assignment]
        st._CHECK_REGISTRY["plugin"] = boom_plugin     # type: ignore[assignment]
        try:
            with tempfile.TemporaryDirectory() as d:
                vault = pathlib.Path(d) / "vault"
                (vault / "90-Meta").mkdir(parents=True)
                rc = st.run(
                    only="privacy",
                    vault_override=str(vault),
                    config_path=str(REPO / "prompts" / "ralph-meta-chain" / "config.yml"),
                )
            self.assertEqual(rc, 0)
            self.assertEqual(called, [])
        finally:
            st._CHECK_REGISTRY["unit-tests"] = original_unit
            st._CHECK_REGISTRY["plugin"] = original_plugin


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
