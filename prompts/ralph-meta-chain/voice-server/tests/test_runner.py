"""Tests for the runner module — does not invoke `claude` for real."""
from __future__ import annotations

import asyncio
import os
import pathlib
import shutil
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

    def test_run_axis_runs_from_repo_root(self) -> None:
        """Regression: the documented launchd plist starts voice-server
        with cwd=voice-server/, so subprocess.run claude inherited that
        cwd and the axis prompts (which read repo-relative paths like
        prompts/ralph-meta-chain/config.yml) broke."""
        # Replace fake claude with one that prints PWD then the promise.
        marker = pathlib.Path(self.tmp) / "claude-pwd-check"
        marker.write_text(
            "#!/usr/bin/env bash\n"
            "pwd\n"
            "echo '<promise>COMPLETE</promise>'\n"
            "exit 1\n"
        )
        marker.chmod(0o755)
        os.environ["RALPH_CLAUDE_BIN"] = str(marker)

        # Run from a different cwd to prove the runner overrides it.
        prev_cwd = os.getcwd()
        try:
            scratch = pathlib.Path(self.tmp) / "elsewhere"
            scratch.mkdir()
            os.chdir(scratch)

            from voice_server.runner import run_axis
            result = asyncio.run(run_axis("memory", max_iterations=2, hard_timeout_s=20))
        finally:
            os.chdir(prev_cwd)

        # claude printed pwd; the runner must have set cwd to repo root,
        # not to the scratch dir.
        self.assertIn(str(REPO), result.tail,
                      f"expected repo root in pwd output; got tail: {result.tail!r}")
        self.assertNotIn("/elsewhere", result.tail,
                         f"runner inherited the wrong cwd: {result.tail!r}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
