from __future__ import annotations

import subprocess
import unittest
from unittest import mock

import path_setup

from skillx import docker_health


class DockerHealthTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
