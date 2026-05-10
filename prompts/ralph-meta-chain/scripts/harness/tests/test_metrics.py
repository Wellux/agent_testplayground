"""B1: skill-metrics infrastructure.

Tests the record() / roll_up() / render_* surface of harness.metrics
plus the end-to-end CLI path (harness metrics record / roll-up).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import pathlib
import subprocess
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
HARNESS_DIR = REPO / "prompts" / "ralph-meta-chain" / "scripts" / "harness"
sys.path.insert(0, str(HARNESS_DIR))


class TestRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name) / "vault"
        (self.vault / "90-Meta").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_record_appends_one_row_with_required_fields(self) -> None:
        from harness import metrics

        row = metrics.record(self.vault, skill="ralph-memory", ok=True, tokens=1234, ms=4500)
        self.assertEqual(row["kind"], "skill_invocation")
        self.assertEqual(row["skill"], "ralph-memory")
        self.assertTrue(row["ok"])
        self.assertEqual(row["tokens"], 1234)
        self.assertEqual(row["ms"], 4500)
        # ts is auto-generated, ISO-Z format.
        self.assertRegex(row["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        # Persisted as a single ndjson line.
        path = self.vault / "90-Meta" / "metrics.ndjson"
        lines = path.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        on_disk = json.loads(lines[0])
        self.assertEqual(on_disk, row)

    def test_record_omits_optional_fields_when_none(self) -> None:
        from harness import metrics

        row = metrics.record(self.vault, skill="memory-architect", ok=False)
        self.assertNotIn("tokens", row)
        self.assertNotIn("ms", row)
        self.assertNotIn("axis", row)
        self.assertFalse(row["ok"])

    def test_record_accepts_explicit_axis_and_ts(self) -> None:
        from harness import metrics

        ts = "2026-05-09T12:00:00Z"
        row = metrics.record(
            self.vault, skill="ralph-research", ok=True, axis="research", ts=ts
        )
        self.assertEqual(row["axis"], "research")
        self.assertEqual(row["ts"], ts)

    def test_record_rejects_empty_skill_name(self) -> None:
        from harness import metrics

        with self.assertRaises(ValueError):
            metrics.record(self.vault, skill="", ok=True)
        with self.assertRaises(ValueError):
            metrics.record(self.vault, skill=None, ok=True)  # type: ignore[arg-type]


class TestRollUp(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name) / "vault"
        (self.vault / "90-Meta").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_empty_vault_returns_empty_dict(self) -> None:
        from harness import metrics

        self.assertEqual(metrics.roll_up(self.vault), {})

    def test_aggregates_invocations_correctly(self) -> None:
        from harness import metrics

        # 3 successes + 1 failure for ralph-memory; 1 success for memory-architect.
        for ok, tokens, ms in [(True, 1000, 2000), (True, 1500, 3000), (True, 1200, 2500), (False, None, None)]:
            metrics.record(self.vault, skill="ralph-memory", ok=ok, tokens=tokens, ms=ms)
        metrics.record(self.vault, skill="memory-architect", ok=True, tokens=800, ms=1500)

        rollup = metrics.roll_up(self.vault, window_days=0)  # 0 = all-time
        self.assertEqual(set(rollup), {"ralph-memory", "memory-architect"})

        m = rollup["ralph-memory"]
        self.assertEqual(m["invocations"], 4)
        self.assertEqual(m["successes"], 3)
        self.assertEqual(m["failures"], 1)
        self.assertAlmostEqual(m["success_rate"], 0.75, places=4)
        # mean_tokens averaged over the 3 with tokens (1000,1500,1200) = 1233.33
        self.assertAlmostEqual(m["mean_tokens"], (1000 + 1500 + 1200) / 3.0, places=2)

        ma = rollup["memory-architect"]
        self.assertEqual(ma["invocations"], 1)
        self.assertEqual(ma["success_rate"], 1.0)
        self.assertEqual(ma["mean_tokens"], 800.0)

    def test_window_filtering_drops_old_rows(self) -> None:
        from harness import metrics

        old_ts = "2026-01-01T00:00:00Z"
        new_ts = "2026-05-09T12:00:00Z"
        metrics.record(self.vault, skill="ralph-memory", ok=True, ts=old_ts)
        metrics.record(self.vault, skill="ralph-memory", ok=True, ts=new_ts)

        # Reference time = 2026-05-09T13:00:00Z. 7-day window keeps only the new one.
        ref = _dt.datetime(2026, 5, 9, 13, 0, 0, tzinfo=_dt.timezone.utc)
        rollup = metrics.roll_up(self.vault, window_days=7, now=ref)
        self.assertEqual(rollup["ralph-memory"]["invocations"], 1)

        # Window=0 ⇒ no filter ⇒ keeps both.
        rollup_all = metrics.roll_up(self.vault, window_days=0)
        self.assertEqual(rollup_all["ralph-memory"]["invocations"], 2)

    def test_ignores_non_skill_invocation_kinds(self) -> None:
        """The metrics.ndjson file is shared with axis-run rows. Roll-up
        must filter on kind == skill_invocation."""
        from harness import append_metric, metrics

        # Existing axis-run schema doesn't have `kind`.
        append_metric(self.vault, {"ts": "2026-05-09T01:00:00Z", "axis": "memory", "promotions": 4})
        # And other plausible kinds.
        append_metric(self.vault, {"ts": "2026-05-09T02:00:00Z", "kind": "axis_run", "axis": "memory"})
        # Our row.
        metrics.record(self.vault, skill="ralph-memory", ok=True)

        rollup = metrics.roll_up(self.vault, window_days=0)
        self.assertEqual(set(rollup), {"ralph-memory"})
        self.assertEqual(rollup["ralph-memory"]["invocations"], 1)

    def test_tolerates_malformed_lines(self) -> None:
        from harness import metrics

        path = self.vault / "90-Meta" / "metrics.ndjson"
        path.write_text(
            "this is not json\n"
            '{"kind": "skill_invocation", "skill": "ralph-memory", "ok": true, "ts": "2026-05-09T12:00:00Z"}\n'
            '{"ts": "bad-timestamp", "kind": "skill_invocation", "skill": "x", "ok": true}\n'
            "\n"
        )
        rollup = metrics.roll_up(self.vault, window_days=0)
        # Malformed lines + bad-timestamp row are dropped; the well-formed one survives.
        self.assertEqual(set(rollup), {"ralph-memory"})

    def test_last_invoked_uses_max_timestamp(self) -> None:
        from harness import metrics

        for ts in ["2026-05-09T01:00:00Z", "2026-05-09T05:00:00Z", "2026-05-09T03:00:00Z"]:
            metrics.record(self.vault, skill="ralph-memory", ok=True, ts=ts)
        rollup = metrics.roll_up(self.vault, window_days=0)
        self.assertEqual(rollup["ralph-memory"]["last_invoked"], "2026-05-09T05:00:00Z")


class TestRendering(unittest.TestCase):
    def test_render_markdown_empty(self) -> None:
        from harness import metrics

        self.assertIn("no skill invocations", metrics.render_markdown({}))

    def test_render_markdown_sorts_by_invocations_desc(self) -> None:
        from harness import metrics

        rollup = {
            "low-traffic": {"invocations": 1, "successes": 1, "failures": 0,
                            "success_rate": 1.0, "mean_tokens": None,
                            "median_ms": None, "p95_ms": None,
                            "last_invoked": "2026-05-09T01:00:00Z"},
            "high-traffic": {"invocations": 50, "successes": 45, "failures": 5,
                             "success_rate": 0.9, "mean_tokens": 1234.5,
                             "median_ms": 2300.0, "p95_ms": 6700.0,
                             "last_invoked": "2026-05-09T22:00:00Z"},
        }
        md = metrics.render_markdown(rollup)
        # high-traffic should appear before low-traffic.
        self.assertLess(md.index("high-traffic"), md.index("low-traffic"))
        # Numbers rendered as expected.
        self.assertIn("1234", md)  # mean_tokens int-cast
        self.assertIn("90%", md)   # success_rate as percentage

    def test_render_json_round_trips(self) -> None:
        from harness import metrics

        rollup = {"x": {"invocations": 1, "success_rate": 1.0}}
        decoded = json.loads(metrics.render_json(rollup))
        self.assertEqual(decoded, rollup)


class TestCLI(unittest.TestCase):
    """End-to-end via `python -m harness metrics ...`. Verifies argparse
    wiring + the --ok/--fail mutually exclusive group + --format flag.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = pathlib.Path(self.tmp.name) / "vault"
        (self.vault / "90-Meta").mkdir(parents=True)
        self.env = os.environ.copy()
        self.env["VAULT"] = str(self.vault)
        # Use the example config so resolve_vault picks up the env override.
        self.env["PYTHONUNBUFFERED"] = "1"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-m", "harness", "--vault", str(self.vault), *args]
        return subprocess.run(
            cmd, cwd=str(HARNESS_DIR), env=self.env, capture_output=True, text=True, timeout=30
        )

    def test_metrics_record_and_roll_up_round_trip(self) -> None:
        cp = self._run("metrics", "record", "--skill", "ralph-memory", "--ok", "--tokens", "1500", "--ms", "3000")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("recorded", cp.stderr)

        cp = self._run("metrics", "roll-up", "--window", "0", "--format", "json")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        rollup = json.loads(cp.stdout)
        self.assertIn("ralph-memory", rollup)
        self.assertEqual(rollup["ralph-memory"]["invocations"], 1)
        self.assertEqual(rollup["ralph-memory"]["mean_tokens"], 1500.0)

    def test_metrics_record_requires_ok_or_fail(self) -> None:
        cp = self._run("metrics", "record", "--skill", "x")
        self.assertNotEqual(cp.returncode, 0)
        # argparse mutually-exclusive-group error.
        self.assertIn("required", (cp.stderr + cp.stdout).lower())

    def test_metrics_roll_up_md_format_default(self) -> None:
        self._run("metrics", "record", "--skill", "ralph-memory", "--ok")
        cp = self._run("metrics", "roll-up", "--window", "0")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        # Default --format md → table header.
        self.assertIn("| skill |", cp.stdout)
        self.assertIn("`ralph-memory`", cp.stdout)


if __name__ == "__main__":
    unittest.main()
