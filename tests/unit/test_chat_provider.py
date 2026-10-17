"""Protocol tests use only a loopback HTTP server and a fake credential."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code" / "core_engine"))
from inf_writer.chat_provider import ChatCompletionProvider, ProviderError
from inf_writer.models import Budget, ModelGateway, ModelRequest
from inf_writer.agents import build_agents
from inf_writer.demo import DemoModel
from inf_writer.domain import Snapshot
from inf_writer.runtime import Coordinator
from inf_writer.storage import FileStore


class ChatProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                cls.requests.append((self.path, dict(self.headers), body))
                response = cls.response(body) if callable(cls.response) else cls.response
                if cls.delay:
                    time.sleep(cls.delay)
                self.send_response(cls.status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                raw = response if isinstance(response, bytes) else json.dumps(response).encode()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        type(self).requests = []
        type(self).status = 200
        type(self).delay = 0
        type(self).response = self.reply()

    @staticmethod
    def reply(content='{"text":"离线假响应"}', finish="stop"):
        return {"choices": [{"message": {"role": "assistant", "content": content},
                             "finish_reason": finish}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}

    def provider(self, **kwargs):
        options = dict(endpoint=f"http://127.0.0.1:{self.server.server_port}/chat/completions",
                       model="local-fixture", api_key="FAKE_LOCAL_KEY",
                       input_usd_per_million=1, output_usd_per_million=2)
        options.update(kwargs)
        return ChatCompletionProvider(**options)

    def request(self):
        return ModelRequest("writer", "输出JSON", {"chapter_number": 1}, 100)

    def test_request_response_and_estimated_cost(self):
        reply = self.provider().complete(self.request())
        self.assertAlmostEqual(reply.cost_usd, 0.00002)
        path, headers, body = self.requests[0]
        self.assertEqual(path, "/chat/completions")
        self.assertEqual(headers["Authorization"], "Bearer FAKE_LOCAL_KEY")
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(json.loads(body["messages"][1]["content"])["chapter_number"], 1)
        self.assertEqual(body["max_tokens"], 100)
        self.assertFalse(body["stream"])

    def test_remote_disabled_by_default(self):
        with self.assertRaises(ValueError):
            self.provider(endpoint="https://example.invalid/chat/completions")
        self.assertEqual(self.requests, [])

    def test_explicit_non_thinking_request(self):
        self.provider(thinking_enabled=False).complete(self.request())
        self.assertEqual(self.requests[0][2]["thinking"], {"type": "disabled"})

    def test_insecure_remote_and_embedded_credentials_rejected(self):
        for endpoint in ("http://example.invalid/chat/completions",
                         "https://user:password@example.invalid/chat/completions",
                         "https://example.invalid/chat/completions?api_key=x"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                self.provider(endpoint=endpoint, allow_remote=True)

    def test_secret_not_in_repr_or_error(self):
        provider = self.provider()
        self.assertNotIn("FAKE_LOCAL_KEY", repr(provider))
        type(self).status = 401
        type(self).response = b"FAKE_LOCAL_KEY private server detail"
        with self.assertRaises(ProviderError) as caught:
            provider.complete(self.request())
        self.assertNotIn("FAKE_LOCAL_KEY", str(caught.exception))
        self.assertEqual(len(self.requests), 1)

    def test_redirect_not_followed(self):
        type(self).status = 302
        with self.assertRaises(ProviderError):
            self.provider().complete(self.request())
        self.assertEqual(len(self.requests), 1)

    def test_missing_usage_rejected(self):
        type(self).response = {"choices": self.reply()["choices"]}
        with self.assertRaises(ProviderError):
            self.provider().complete(self.request())

    def test_truncated_and_filtered_outputs_rejected(self):
        for reason in ("length", "content_filter", "tool_calls"):
            type(self).response = self.reply(finish=reason)
            with self.subTest(reason=reason), self.assertRaises(ProviderError):
                self.provider().complete(self.request())

    def test_malformed_and_oversized_responses_rejected(self):
        for raw in (b"not JSON", b"x" * 2048):
            type(self).response = raw
            with self.subTest(size=len(raw)), self.assertRaises(ProviderError):
                self.provider(max_response_bytes=1024).complete(self.request())

    def test_bad_usage_rejected(self):
        for usage in ({"prompt_tokens": True, "completion_tokens": 5},
                      {"prompt_tokens": -1, "completion_tokens": 5},
                      {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 99}):
            type(self).response = dict(self.reply(), usage=usage)
            with self.subTest(usage=usage), self.assertRaises(ProviderError):
                self.provider().complete(self.request())

    def test_timeout_does_not_retry_and_reservation_remains(self):
        type(self).delay = 0.15
        budget = Budget(max_cost_usd=1)
        gateway = ModelGateway(self.provider(timeout_seconds=0.03), budget, reserve_per_call=0.1)
        with self.assertRaises(ProviderError):
            gateway.complete(self.request())
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(budget.calls, 1)
        self.assertEqual(budget.cost_upper_usd, 0.1)
        time.sleep(0.2)  # Drain this local fixture handler before the next test.

    def test_config_rejects_invalid_limits_and_prices(self):
        for options in ({"timeout_seconds": 0}, {"input_usd_per_million": float("nan")},
                        {"output_usd_per_million": -1}, {"max_response_bytes": True},
                        {"api_key": "bad\r\nheader"}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.provider(**options)

    def test_four_agents_through_http_commit_one_chapter(self):
        def respond(body):
            # Deterministic local fixture, not real model generation.
            prompt = body["messages"][0]["content"]
            role = next(r for r, marker in (("planner", "规划智能体"), ("writer", "写作智能体"),
                                            ("memory", "记忆维护智能体"), ("reviewer", "审核智能体"))
                        if marker in prompt)
            fixture = DemoModel().complete(ModelRequest(role, prompt,
                json.loads(body["messages"][1]["content"])))
            return self.reply(fixture.content)

        type(self).response = respond
        root = Path(__file__).resolve().parents[2] / "code" / "backend" / "data" / "test-tmp"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            store = FileStore(folder)
            store.initialize(Snapshot("httpdemo", "写守灯人的故事"))
            budget = Budget(max_calls=4, max_cost_usd=1)
            coordinator = Coordinator(store, build_agents(ModelGateway(self.provider(), budget, 0.01)))
            outcome = coordinator.write_next("httpdemo", "chapter1")
            self.assertEqual(outcome.status, "COMMITTED", outcome.error)
            self.assertEqual(len(self.requests), 4)
            self.assertEqual(store.load("httpdemo").active_facts()[0]["value"], "灰色")
            self.assertAlmostEqual(budget.cost_upper_usd, 0.00008)


if __name__ == "__main__":
    unittest.main()
