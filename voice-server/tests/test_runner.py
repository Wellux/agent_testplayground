"""Tests for the runner module — does not invoke `claude` for real."""
from __future__ import annotations

import asyncio
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "voice-server"))


class AxisToPrompt(unittest.TestCase):
    def test_all_eight_axes_mapped(self) -> None:
        from voice_server.runner import AXIS_TO_PROMPT

        self.assertEqual(set(AXIS_TO_PROMPT), {
            "research", "memory", "skills", "interaction",
            "compress", "heal", "evolve", "update",
        })

    def test_each_prompt_file_exists(self) -> None:
        from voice_server.runner import AXIS_TO_PROMPT
        ralph = REPO / "prompts" / "ralph-meta-chain"
        missing = [p for p in AXIS_TO_PROMPT.values() if not (ralph / p).exists()]
        self.assertEqual(missing, [], f"missing prompt files: {missing}")


class FakeClaudeRunner(unittest.TestCase):
    """Replace `claude` with a script that prints <promise>COMPLETE</promise>
    and exits non-zero (so the until-! loop terminates)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        fake = pathlib.Path(self.tmp) / "claude"
        fake.write_text(
            "#!/usr/bin/env bash\n"
            "echo '<promise>COMPLETE</promise>'\n"
            "exit 1\n"
        )
        fake.chmod(0o755)
        self.fake = fake
        self.prev_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{self.tmp}:{self.prev_path}"
        os.environ["RALPH_CLAUDE_BIN"] = str(fake)

    def tearDown(self) -> None:
        os.environ["PATH"] = self.prev_path
        os.environ.pop("RALPH_CLAUDE_BIN", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_run_axis_emits_promise_then_exits(self) -> None:
        from voice_server.runner import run_axis

        result = asyncio.run(run_axis("memory", max_iterations=3, hard_timeout_s=20))
        self.assertEqual(result.axis, "memory")
        self.assertTrue(result.promise_seen)
        self.assertEqual(result.iterations, 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
