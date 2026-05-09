"""Smoke tests for voice-server. No real network, no real claude binary."""
from __future__ import annotations

import os
import pathlib
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "voice-server"))


class _VaultFixture:
    """Spin up a scratch vault + minimal config and point env at it."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.vault = self.root / "vault"
        self.vault.mkdir()
        (self.vault / "90-Meta").mkdir()
        (self.vault / "90-Meta" / "ralph-state.json").write_text(
            '{"memory": {"date":"2026-05-08","status":"COMPLETE"}}',
            encoding="utf8",
        )
        os.environ["VAULT"] = str(self.vault)

    def cleanup(self) -> None:
        self.tmp.cleanup()


def _client_with_guard_disabled():
    """Build a TestClient that bypasses the origin guard. The guard is itself
    tested in OriginGuard below."""
    from fastapi.testclient import TestClient

    from voice_server.app import create_app
    from voice_server.auth import origin_guard

    app = create_app()
    app.dependency_overrides[origin_guard] = lambda: None
    return TestClient(app)


class HealthCheck(unittest.TestCase):
    def test_healthz(self) -> None:
        from fastapi.testclient import TestClient

        from voice_server.app import create_app

        # /healthz has no guard.
        client = TestClient(create_app())
        r = client.get("/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})


class StatusEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _VaultFixture()
        self.client = _client_with_guard_disabled()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_status_reads_state_json(self) -> None:
        r = self.client.get("/ralph/status")
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertEqual(body["vault"], str(self.fx.vault))
        self.assertFalse(body["stopped"])
        self.assertEqual(body["state"]["memory"]["status"], "COMPLETE")


class StopResume(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _VaultFixture()
        self.client = _client_with_guard_disabled()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_stop_creates_resume_removes(self) -> None:
        stop_path = self.fx.vault / "90-Meta" / "STOP"

        self.assertFalse(stop_path.exists())
        r = self.client.post("/ralph/stop")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(stop_path.exists())

        r = self.client.post("/ralph/resume")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(stop_path.exists())


class VoiceText(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _VaultFixture()
        self.client = _client_with_guard_disabled()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_voice_text_writes_inbox_file(self) -> None:
        r = self.client.post(
            "/ralph/voice",
            data={"text": "remember sqlite-vec is the storage shape", "source": "unit-test"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        wrote = self.fx.vault / r.json()["wrote"]
        body = wrote.read_text(encoding="utf8")
        self.assertIn("type: voice-capture", body)
        self.assertIn("source: unit-test", body)
        self.assertIn("sqlite-vec", body)

    def test_voice_audio_without_whisper_returns_503(self) -> None:
        # whisper-cli binary won't exist in CI — should 503 with a clear message.
        r = self.client.post(
            "/ralph/voice",
            files={"audio": ("a.wav", b"\x00\x01\x02", "audio/wav")},
            data={"source": "unit-test"},
        )
        self.assertEqual(r.status_code, 503, r.text)
        self.assertIn("whisper", r.json()["detail"].lower())

    def test_same_second_captures_dont_overwrite(self) -> None:
        """Regression: two requests in the same UTC second must both
        persist. Pre-fix, the second write_text replaced the first."""
        first = self.client.post(
            "/ralph/voice",
            data={"text": "first capture body", "source": "unit-test"},
        )
        second = self.client.post(
            "/ralph/voice",
            data={"text": "second capture body", "source": "unit-test"},
        )
        third = self.client.post(
            "/ralph/voice",
            data={"text": "third capture body", "source": "unit-test"},
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 200)

        # All three landed at distinct paths.
        paths = {first.json()["wrote"], second.json()["wrote"], third.json()["wrote"]}
        self.assertEqual(len(paths), 3, f"collision: {paths}")

        # Each file's body matches its post.
        bodies = []
        for r in (first, second, third):
            bodies.append((self.fx.vault / r.json()["wrote"]).read_text("utf8"))
        self.assertIn("first capture body", bodies[0])
        self.assertIn("second capture body", bodies[1])
        self.assertIn("third capture body", bodies[2])


class OriginGuard(unittest.TestCase):
    """Real guard exercised end-to-end. fastapi's TestClient sets the
    request.client.host to 'testclient' by default, which fails IP parse and
    triggers a 403 — exactly what we want for off-subnet rejection."""

    def setUp(self) -> None:
        self.fx = _VaultFixture()
        os.environ["RALPH_TRUSTED_SUBNETS"] = "10.0.0.0/8"

    def tearDown(self) -> None:
        self.fx.cleanup()
        os.environ["RALPH_TRUSTED_SUBNETS"] = "100.64.0.0/10,127.0.0.0/8,::1/128"

    def test_off_subnet_request_is_rejected(self) -> None:
        from fastapi.testclient import TestClient

        from voice_server.app import create_app

        client = TestClient(create_app())
        r = client.get("/ralph/status")
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
