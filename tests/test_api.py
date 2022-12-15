"""Basic tests for the API endpoints

SPDX-FileCopyrightText: 2022 CERT.at Gmbh <https://cert.at/>
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import subprocess
from typing import List
from unittest import TestCase

from fastapi.testclient import TestClient

from intelmq_api import dependencies
from intelmq_api.api import runner
from intelmq_api.config import Config
from intelmq_api.main import app
from intelmq_api.runctl import RunIntelMQCtl
from intelmq_api.version import __version__


class DummyConfig(Config):
    def __init__(self):
        # Prevent loading from file
        pass


class DummyRunner(RunIntelMQCtl):
    def _run_intelmq_ctl(self, args: List[str]) -> subprocess.CompletedProcess:
        # simulate dummy response from the CLI command
        return subprocess.CompletedProcess(args, 0, b'{"some": "json"}')


def dummy_runner():
    return DummyRunner([])


class TestApi(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app=app)
        dependencies.startup(DummyConfig())
        app.dependency_overrides[runner] = dummy_runner

    def tearDown(self) -> None:
        app.dependency_overrides = {}

    def test_version(self):
        response = self.client.get("/v1/api/version")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()["intelmq-api"], __version__)

    def test_ensure_response_get_values_and_is_json(self):
        json_paths = ["botnet?action=status", "bot?action=status&id=1",
                      "getlog?lines=1&id=1", "queues", "queues-and-status",
                      "bots", "check", "debug"]

        for path in json_paths:
            with self.subTest(path):
                response = self.client.get(f"/v1/api/{path}")
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.json(), dict)
                self.assertEqual(response.json(), {"some": "json"})
