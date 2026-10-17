import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from openai import OpenAI
from tome_backend.providers.deepseek import Settings, DeepSeekModel
from tome_backend.service import create_book, generate, export_markdown, operation_lock
from tome_backend.checkpoints import load_checkpoint
from tome_agent.offline import group, entry


class EndToEndTests(unittest.TestCase):
    def test_real_sdk_transport_through_planner_and_chapter_loop(self):
        replies = [json.dumps({"content": stage}) for stage in ("premise", "synopsis", "acts")]
        replies += [json.dumps([{"title": "出发", "goal": "清点背包"}])]
        replies += [("write", {"text": "有火折"}), ("update", {"groups": [group("inventory", [entry(2, "有火折")])]}), "DONE"]
        iterator = iter(replies)
        requests = []
        def respond(request):
            requests.append(json.loads(request.content))
            response = next(iterator)
            message = {"role": "assistant", "content": response if isinstance(response, str) else ""}
            finish = "stop"
            if isinstance(response, tuple):
                name, args = response
                message["tool_calls"] = [{"id": f"c{len(requests)}", "type": "function",
                    "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}]
                finish = "tool_calls"
            return httpx.Response(200, json={"id": "test", "object": "chat.completion", "created": 0,
                "model": "deepseek-flash", "choices": [{"index": 0, "finish_reason": finish, "message": message}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}})
        client = OpenAI(api_key="fake-test-key", base_url="https://api.deepseek.com", max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(respond)))
        self.addCleanup(client.close)
        model = DeepSeekModel(Settings("fake"), client)
        with tempfile.TemporaryDirectory() as tmp, patch("tome_backend.service.BOOKS", Path(tmp)):
            workspace = create_book("sample", "样例", "出发清点背包", 1, 3, model)
            self.assertFalse(workspace.chapters)
            workspace = generate("sample", model=model)
            self.assertEqual(workspace.chapters[1], "有火折")
            self.assertEqual(load_checkpoint(Path(tmp) / "sample/book.json"), workspace)
            self.assertIn("有火折", export_markdown(workspace))
            self.assertEqual(len(requests), 7)
            self.assertFalse((Path(tmp) / "sample/operation.lock").exists())

    def test_operation_lock_rejects_concurrent_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.json"
            with operation_lock(path):
                with self.assertRaises(ValueError):
                    with operation_lock(path):
                        self.fail("Concurrent operation entered")
            self.assertFalse((path.parent / "operation.lock").exists())
