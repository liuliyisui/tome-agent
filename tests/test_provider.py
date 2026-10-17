import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch, Mock
import httpx
from openai import OpenAI
from tome_agent.providers.deepseek import Settings, DeepSeekModel
from tome_agent.agent import ToolCall


class ProviderTests(unittest.TestCase):
    def client(self, payload, capture):
        def respond(request):
            capture.append(json.loads(request.content))
            return httpx.Response(200, json=payload)
        return OpenAI(api_key="fake-test-key", base_url="https://api.deepseek.com", max_retries=0,
                      http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    def payload(self, tool_calls=None):
        return {"id": "test", "object": "chat.completion", "created": 0, "model": "deepseek-flash",
            "choices": [{"index": 0, "finish_reason": "tool_calls" if tool_calls else "stop",
                         "message": {"role": "assistant", "content": "" if tool_calls else "DONE",
                                     "reasoning_content": "test reasoning", "tool_calls": tool_calls}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}

    def test_tool_parsing_and_reasoning_history(self):
        capture = []
        calls = [{"id": "c1", "type": "function", "function": {"name": "read", "arguments": '{"chapter":1}'}}]
        client = self.client(self.payload(calls), capture)
        self.addCleanup(client.close)
        model = DeepSeekModel(Settings("fake", thinking=True), client)
        history = [{"role": "assistant", "content": "", "reasoning_content": "old reasoning"}]
        result = model.complete(history, [{"type": "function", "function": {"name": "read", "parameters": {"type": "object"}}}])
        self.assertEqual(result.calls, [ToolCall("c1", "read", {"chapter": 1})])
        self.assertEqual(result.reasoning_content, "test reasoning")
        self.assertEqual(capture[0]["messages"][0]["reasoning_content"], "old reasoning")
        self.assertEqual(capture[0]["thinking"], {"type": "enabled"})
        self.assertEqual(model.total_tokens, 15)

    def test_budget_stops_next_request(self):
        capture = []
        client = self.client(self.payload(), capture)
        self.addCleanup(client.close)
        model = DeepSeekModel(Settings("fake", max_requests=1), client)
        model.complete([{"role": "user", "content": "test"}], [])
        with self.assertRaises(ValueError):
            model.complete([], [])
        self.assertEqual(len(capture), 1)

    def test_malformed_tool_json_is_rejected(self):
        payload = self.payload([{"id": "c", "type": "function", "function": {"name": "read", "arguments": "bad"}}])
        client = self.client(payload, [])
        self.addCleanup(client.close)
        with self.assertRaises(ValueError):
            DeepSeekModel(Settings("fake"), client).complete([], [])

    def test_env_fallback_and_secret_repr(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("DEEPSEEK_API_KEY=fake-secret\nDEEPSEEK_MODEL=\n", encoding="utf-8")
            with patch.dict("os.environ", {}, clear=True):
                settings = Settings.load(path)
            self.assertEqual(settings.model, "deepseek-flash")
            self.assertNotIn("fake-secret", repr(settings))
            path.write_text("DEEPSEEK_API_KEY=fake\nDEEPSEEK_BASE_URL=https://other.example\n", encoding="utf-8")
            with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
                Settings.load(path)
