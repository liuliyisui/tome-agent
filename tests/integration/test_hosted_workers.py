"""Separate hosted workers keep user files and settings in separate homes."""

import json
import tempfile
import unittest
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from inf_backend.hosted_workers import WorkerPool, WorkerUnavailable


class HostedWorkerTests(unittest.TestCase):
    def test_users_get_separate_services_and_persistent_files(self):
        with tempfile.TemporaryDirectory() as folder:
            pool = WorkerPool(Path(folder), limit=2)
            try:
                first = pool.get("a" * 32)
                second = pool.get("b" * 32)
                self.assertNotEqual(first, second)
                self.assertEqual(pool.get("a" * 32), first)
                with self.assertRaises(WorkerUnavailable):
                    pool.get("c" * 32)
                client = build_opener(ProxyHandler({}))
                body = json.dumps(
                    {
                        "title": "独立作品",
                        "prompt": "测试作品隔离",
                        "chapters": 1,
                        "target_units": 500,
                    }
                ).encode()
                request = Request(
                    f"http://127.0.0.1:{first}/api/books",
                    body,
                    {"Content-Type": "application/json"},
                )
                with client.open(request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                with client.open(f"http://127.0.0.1:{second}/api/books") as response:
                    self.assertEqual(json.load(response)["books"], [])
                model = json.dumps({"api_key": "sk-" + "a" * 32}).encode()
                request = Request(
                    f"http://127.0.0.1:{first}/api/config",
                    model,
                    {"Content-Type": "application/json"},
                )
                with client.open(request, timeout=10) as response:
                    self.assertTrue(json.load(response)["configured"])
                with client.open(f"http://127.0.0.1:{second}/api/config") as response:
                    self.assertFalse(json.load(response)["configured"])
                self.assertTrue(
                    list((Path(folder) / ("a" * 32)).rglob("metadata.json"))
                )
                pool.release("a" * 32)
                pool.release("a" * 32)
                pool.release("b" * 32)
                pool.used["a" * 32] -= 301
                third = pool.get("c" * 32)
                self.assertNotEqual(third, second)
                self.assertNotIn("a" * 32, pool.workers)
            finally:
                pool.close()
            with self.assertRaises(WorkerUnavailable):
                pool.get("d" * 32)
