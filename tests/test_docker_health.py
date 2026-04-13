from __future__ import annotations

import subprocess
import unittest
from unittest import mock

import path_setup

from skillx import docker_health


class DockerHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        docker_health._reset_fake_docker_health_state()

    def tearDown(self) -> None:
        docker_health._reset_fake_docker_health_state()

    def test_probe_docker_health_reports_internal_server_error(self) -> None:
        def fake_run(*args, **kwargs):
            command = args[0]
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="Internal Server Error\n",
                stderr="",
            )

        with mock.patch.object(docker_health.subprocess, "run", side_effect=fake_run):
            report = docker_health.probe_docker_health(min_memory_bytes=16_000_000_000)

        self.assertFalse(report["healthy"])
        self.assertEqual(report["category"], "daemon_internal_error")
        self.assertIn("internal API error", report["message"])

    def test_probe_docker_health_accepts_valid_memtotal(self) -> None:
        def fake_run(*args, **kwargs):
            command = args[0]
            if command[:2] == ["docker", "info"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout='{"MemTotal": 17179869184}\n',
                    stderr="",
                )
            if command[:2] == ["docker", "version"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout='{"Version": "27.0.0"}\n',
                    stderr="",
                )
            if command[:2] == ["docker", "ps"]:
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout='"demo-container"\n',
                    stderr="",
                )
            raise AssertionError(f"unexpected command: {command}")

        with mock.patch.object(docker_health.subprocess, "run", side_effect=fake_run):
            report = docker_health.probe_docker_health(min_memory_bytes=16_000_000_000)

        self.assertTrue(report["healthy"])
        self.assertEqual(report["category"], "healthy")
        self.assertEqual(report["docker_mem_bytes"], 17179869184)

    def test_probe_docker_health_supports_fault_injection_sequence(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {
                docker_health.FAKE_DOCKER_HEALTH_ENV: "internal_error_once,healthy_always",
            },
            clear=False,
        ):
            first = docker_health.probe_docker_health(min_memory_bytes=16_000_000_000)
            second = docker_health.probe_docker_health(min_memory_bytes=16_000_000_000)
            third = docker_health.probe_docker_health(min_memory_bytes=16_000_000_000)

        self.assertFalse(first["healthy"])
        self.assertEqual(first["category"], "daemon_internal_error")
        self.assertTrue(first["fault_injected"])
        self.assertEqual(first["fault_injection_scenario"], "internal_error")

        self.assertTrue(second["healthy"])
        self.assertEqual(second["category"], "healthy")
        self.assertTrue(second["fault_injected"])
        self.assertEqual(second["fault_injection_scenario"], "healthy")

        self.assertTrue(third["healthy"])
        self.assertEqual(third["fault_injection_scenario"], "healthy")

    def test_attempt_docker_recovery_supports_fault_injection(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {
                docker_health.FAKE_DOCKER_RECOVERY_ENV: "success",
            },
            clear=False,
        ):
            with mock.patch.object(docker_health.subprocess, "run") as mock_run:
                report = docker_health.attempt_docker_recovery()

        self.assertTrue(report["successful"])
        self.assertTrue(report["fault_injected"])
        self.assertEqual(report["fault_injection_mode"], "success")
        mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
