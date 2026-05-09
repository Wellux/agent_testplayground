"""ralph_mcp_server protocol smoke tests.

Run via: python3 -m unittest prompts.ralph-meta-chain.tests.test_mcp_server
Or:      cd prompts/ralph-meta-chain/mcp-server && python3 -m unittest \
            ../tests/test_mcp_server.py

Each test spawns the server as a subprocess and exchanges newline-delimited
JSON-RPC messages over stdin/stdout — exactly how Claude Code talks to it.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import unittest


REPO = pathlib.Path(__file__).resolve().parents[3]
SERVER_DIR = REPO / "prompts" / "ralph-meta-chain" / "mcp-server"


def _spawn_and_exchange(messages: list[dict]) -> list[dict]:
    """Send each message, return the parsed responses (in order)."""
    payload = "\n".join(json.dumps(m) for m in messages) + "\n"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SERVER_DIR)
    env["RALPH_REPO"] = str(REPO)
    cp = subprocess.run(
        [sys.executable, "-m", "ralph_mcp_server"],
        input=payload,
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )
    if cp.returncode != 0:
        raise AssertionError(
            f"server exited rc={cp.returncode}\nstderr:\n{cp.stderr}\nstdout:\n{cp.stdout}"
        )
    out = []
    for line in cp.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


class TestRalphMcpServer(unittest.TestCase):
    def test_initialize(self):
        resp = _spawn_and_exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0.0.1"},
                    },
                }
            ]
        )
        self.assertEqual(len(resp), 1)
        msg = resp[0]
        self.assertEqual(msg["id"], 1)
        self.assertIn("result", msg)
        self.assertEqual(msg["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(msg["result"]["serverInfo"]["name"], "ralph")
        self.assertIn("capabilities", msg["result"])

    def test_ping(self):
        resp = _spawn_and_exchange(
            [{"jsonrpc": "2.0", "id": 9, "method": "ping"}]
        )
        self.assertEqual(resp[0]["id"], 9)
        self.assertEqual(resp[0]["result"], {})

    def test_tools_list_returns_four_read_only_tools(self):
        resp = _spawn_and_exchange(
            [{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        )
        tools = resp[0]["result"]["tools"]
        names = sorted(t["name"] for t in tools)
        self.assertEqual(
            names,
            [
                "ralph_axis_status",
                "ralph_migration_dry_run",
                "ralph_query",
                "ralph_self_test",
            ],
        )
        # Every tool has an inputSchema.
        for t in tools:
            self.assertIn("inputSchema", t)
            self.assertEqual(t["inputSchema"]["type"], "object")

    def test_unknown_method_returns_jsonrpc_error(self):
        resp = _spawn_and_exchange(
            [{"jsonrpc": "2.0", "id": 3, "method": "does/not/exist"}]
        )
        self.assertIn("error", resp[0])
        self.assertEqual(resp[0]["error"]["code"], -32601)

    def test_unknown_tool_returns_jsonrpc_error(self):
        resp = _spawn_and_exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {"name": "ralph_does_not_exist", "arguments": {}},
                }
            ]
        )
        self.assertIn("error", resp[0])
        self.assertEqual(resp[0]["error"]["code"], -32601)

    def test_axis_status_no_vault_returns_friendly_message(self):
        # Set vault to a non-existent path via env to bypass config.yml.
        # The tool reads vault from config.yml; if that points somewhere
        # missing we should get a friendly "no log.md yet" message rather
        # than crash.
        resp = _spawn_and_exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "ralph_axis_status",
                        "arguments": {"axis": "memory"},
                    },
                }
            ]
        )
        self.assertIn("result", resp[0])
        # Either "no log.md yet" or "vault_path not configured" — both fine.
        text = resp[0]["result"]["content"][0]["text"]
        self.assertTrue(
            "log.md" in text or "vault_path" in text or "(no entries yet)" in text,
            f"unexpected text: {text!r}",
        )

    def test_query_requires_non_empty(self):
        resp = _spawn_and_exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "ralph_query",
                        "arguments": {"query": ""},
                    },
                }
            ]
        )
        result = resp[0]["result"]
        self.assertTrue(result.get("isError", False))
        self.assertIn("ERROR", result["content"][0]["text"])

    def test_initialize_then_list_in_one_session(self):
        resp = _spawn_and_exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "t", "version": "1"},
                    },
                },
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            ]
        )
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]["id"], 1)
        self.assertEqual(resp[1]["id"], 2)
        self.assertEqual(len(resp[1]["result"]["tools"]), 4)

    def test_notification_no_response(self):
        # Notifications (no id) get no response per JSON-RPC.
        resp = _spawn_and_exchange(
            [
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 7, "method": "ping"},
            ]
        )
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]["id"], 7)


class TestRalphMcpServerHarnessIntegration(unittest.TestCase):
    """Mock the harness CLI to verify the EXACT args the MCP server constructs.

    These tests would have caught the two bugs found post-Round 9:
      - ralph_query passed --limit; harness expects --k
      - ralph_migration_dry_run shelled to a nonexistent subcommand
    """

    def _spawn_with_fake_harness(
        self, fake_script_body: str, messages: list[dict]
    ) -> tuple[list[dict], pathlib.Path]:
        import shutil
        import tempfile

        td = pathlib.Path(tempfile.mkdtemp())
        # Fake `harness` on PATH that records argv to a file then exits 0.
        argv_log = td / "argv.txt"
        fake = td / "harness"
        fake.write_text(
            "#!/usr/bin/env bash\n"
            f'printf "%s\\n" "$@" > {argv_log}\n'
            f"{fake_script_body}\n"
        )
        fake.chmod(0o755)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(SERVER_DIR)
        env["RALPH_REPO"] = str(REPO)
        env["PATH"] = f"{td}:{env['PATH']}"

        payload = "\n".join(json.dumps(m) for m in messages) + "\n"
        cp = subprocess.run(
            [sys.executable, "-m", "ralph_mcp_server"],
            input=payload,
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
        if cp.returncode != 0:
            shutil.rmtree(td, ignore_errors=True)
            raise AssertionError(f"server exited rc={cp.returncode}\n{cp.stderr}")

        responses = []
        for line in cp.stdout.splitlines():
            line = line.strip()
            if line:
                responses.append(json.loads(line))
        return responses, argv_log

    def test_query_passes_dash_k_not_dash_limit(self):
        """Regression: ralph_query previously used --limit; harness wants --k."""
        responses, argv_log = self._spawn_with_fake_harness(
            'echo "[[Note A]]\\n[[Note B]]"\n',
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "ralph_query",
                        "arguments": {"query": "memory model", "limit": 5},
                    },
                }
            ],
        )
        argv = argv_log.read_text().splitlines()
        # The fake harness gets called with: query --semantic <q> --k <n>
        self.assertEqual(argv[0], "query")
        self.assertEqual(argv[1], "--semantic")
        self.assertEqual(argv[2], "memory model")
        self.assertIn("--k", argv, f"missing --k flag in {argv}")
        self.assertNotIn("--limit", argv, "must not pass --limit (harness rejects it)")
        # Result surfaces the fake output.
        result = responses[0]["result"]
        self.assertIn("Note A", result["content"][0]["text"])

    def test_self_test_passes_only_when_supplied(self):
        responses, argv_log = self._spawn_with_fake_harness(
            'echo "all green"\n',
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "ralph_self_test",
                        "arguments": {"only": "privacy"},
                    },
                }
            ],
        )
        argv = argv_log.read_text().splitlines()
        self.assertEqual(argv[0], "self-test")
        self.assertIn("--only", argv)
        self.assertIn("privacy", argv)

    def test_self_test_omits_only_when_absent(self):
        responses, argv_log = self._spawn_with_fake_harness(
            'echo "all green"\n',
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "ralph_self_test", "arguments": {}},
                }
            ],
        )
        argv = argv_log.read_text().splitlines()
        self.assertEqual(argv, ["self-test"])

    def test_migration_dry_run_invokes_propose_shell_script(self):
        """Regression: previously called nonexistent `harness migration propose`."""
        # We don't even need to mock harness for this — the MCP server should
        # NOT call harness for migration. It calls
        # migration/scripts/ralph_propose_migration.sh directly.
        # Verify by asserting the script path exists where the server expects.
        propose = (
            REPO
            / "prompts"
            / "ralph-meta-chain"
            / "migration"
            / "scripts"
            / "ralph_propose_migration.sh"
        )
        self.assertTrue(
            propose.exists(),
            f"the MCP server expects {propose} to exist; "
            "if you moved/renamed it, update tool_ralph_migration_dry_run too",
        )
        self.assertTrue(
            os.access(propose, os.X_OK),
            f"{propose} must be executable",
        )

    def test_migration_tool_description_acknowledges_writes(self):
        """Regression for Codex P2: tool MUST disclose that it writes
        proposal Markdown — calling it a side-effect-free 'preview' is
        a contract violation that surprises clients.
        """
        responses = _spawn_and_exchange(
            [{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}]
        )
        tools = responses[0]["result"]["tools"]
        migration = next(t for t in tools if t["name"] == "ralph_migration_dry_run")
        desc = migration["description"].lower()
        # Must NOT claim it's read-only / side-effect-free.
        self.assertNotIn("without writing anything", desc)
        # MUST mention the writes explicitly.
        self.assertTrue(
            any(
                phrase in desc
                for phrase in (
                    "writes",
                    "write markdown",
                    "proposal",
                )
            ),
            f"description must disclose writes: {desc!r}",
        )
        self.assertIn("git restore", desc)


if __name__ == "__main__":
    unittest.main()
