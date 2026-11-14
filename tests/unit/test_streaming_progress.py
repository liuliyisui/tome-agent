"""Streaming prose progress keeps accounting and incomplete data safe."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from inf_backend import service
from inf_backend.service import count_units
from inf_backend.settings import Settings
from inf_backend.streaming import (
    ProseProgressProvider,
    _partial_json_prose,
    describe_prose_request,
)
from tome_writer.chat_provider import ChatCompletionProvider, ProviderError
from tome_writer.models import Budget, ModelGateway, ModelRequest


class Response:
    status = 200

    def __init__(self, events):
        self.lines = iter(
            [
                *(
                    b"data: " + json.dumps(e, ensure_ascii=False).encode() + b"\n\n"
                    for e in events
                ),
                b"data: [DONE]\n\n",
            ]
        )

    def readline(self, limit):
        return next(self.lines, b"")


class Connection:
    def __init__(self, response):
        self.response = response
        self.closed = False

    def request(self, method, path, body, headers):
        self.body = json.loads(body)

    def getresponse(self):
        return self.response

    def close(self):
        self.closed = True


class StreamingProgressTests(unittest.TestCase):
    def setUp(self):
        self.provider = ChatCompletionProvider(
            "http://127.0.0.1/chat/completions", "test", "key", 1, 2
        )
        self.updates = []
        self.adapter = ProseProgressProvider(
            self.provider, self.updates.append, count_units
        )
        self.request = ModelRequest(
            "writer", "写作", {"output_mode": "plain_prose"}, 100
        )

    def test_streams_actual_prose_and_returns_provider_usage(self):
        events = [
            {
                "choices": [{"delta": {"content": "甲来"}, "finish_reason": None}],
                "usage": None,
            },
            {
                "choices": [{"delta": {"content": "了。"}, "finish_reason": None}],
                "usage": None,
            },
            {"choices": [{"delta": {}, "finish_reason": "stop"}], "usage": None},
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                },
            },
        ]
        connection = Connection(Response(events))
        with patch(
            "inf_backend.streaming.http.client.HTTPConnection", return_value=connection
        ):
            reply = self.adapter.complete(self.request)
        self.assertEqual(self.updates[1], {"live_units": 2, "live_phase": "writing"})
        self.assertEqual(reply.content, "甲来了。")
        self.assertEqual((reply.input_tokens, reply.output_tokens), (10, 3))
        self.assertEqual(
            self.updates[-1], {"live_units": 3, "live_phase": "processing"}
        )
        self.assertTrue(connection.body["stream"])
        self.assertTrue(connection.closed)

    def test_main_writer_json_stream_reports_only_prose(self):
        request = ModelRequest("writer", "写作", {}, 100)
        events = [
            {
                "choices": [
                    {
                        "delta": {"content": '{"type":"prose","text":"甲'},
                        "finish_reason": None,
                    }
                ]
            },
            {"choices": [{"delta": {"content": '来了。"}'}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                },
            },
        ]
        connection = Connection(Response(events))
        with (
            patch(
                "inf_backend.streaming.http.client.HTTPConnection",
                return_value=connection,
            ),
            patch("inf_backend.streaming.time.monotonic", side_effect=[1, 2]),
        ):
            reply = self.adapter.complete(request)
        self.assertEqual(reply.content, '{"type":"prose","text":"甲来了。"}')
        self.assertEqual([item["live_units"] for item in self.updates], [0, 1, 3, 3])
        self.assertEqual(connection.body["response_format"], {"type": "json_object"})

    def test_normal_stage_writer_stream_counts_its_actual_prose_field(self):
        request = ModelRequest("writer", "写作", {"stage_task": {}}, 100)
        events = [
            {
                "choices": [
                    {
                        "delta": {"content": '{"new_stage_text":"雨'},
                        "finish_reason": None,
                    }
                ]
            },
            {"choices": [{"delta": {"content": '停了。"}'}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                },
            },
        ]
        connection = Connection(Response(events))
        with (
            patch(
                "inf_backend.streaming.http.client.HTTPConnection",
                return_value=connection,
            ),
            patch("inf_backend.streaming.time.monotonic", side_effect=[1, 2]),
        ):
            result = self.adapter.complete(request)
        self.assertEqual(json.loads(result.content)["new_stage_text"], "雨停了。")
        self.assertEqual([item["live_units"] for item in self.updates], [0, 1, 3, 3])

    def test_partial_json_handles_escapes_and_nested_text(self):
        self.assertEqual(
            _partial_json_prose('{"other":{"text":"无关"},"text":"甲\\u4e'), "甲"
        )
        self.assertEqual(
            _partial_json_prose('{"other":{"text":"无关"},"text":"甲\\u4e2d'), "甲中"
        )
        self.assertEqual(_partial_json_prose('{"text":"甲\\"乙'), '甲"乙')
        self.assertEqual(_partial_json_prose('{"other":{"text":"无关"}'), "")

    def test_progress_arrives_before_local_stream_finishes(self):
        first_sent = threading.Event()
        release = threading.Event()
        updates = []
        received = threading.Event()
        result = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()

                def send(value):
                    self.wfile.write(
                        b"data: "
                        + json.dumps(value, ensure_ascii=False).encode("utf-8")
                        + b"\n\n"
                    )
                    self.wfile.flush()

                send(
                    {
                        "choices": [
                            {
                                "delta": {"content": '{"new_stage_text":"雨'},
                                "finish_reason": None,
                            }
                        ]
                    }
                )
                first_sent.set()
                if release.wait(5):
                    send(
                        {
                            "choices": [
                                {
                                    "delta": {"content": '停了。"}'},
                                    "finish_reason": None,
                                }
                            ]
                        }
                    )
                    send({"choices": [{"delta": {}, "finish_reason": "stop"}]})
                    send(
                        {
                            "choices": [],
                            "usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 3,
                                "total_tokens": 13,
                            },
                        }
                    )
                    self.wfile.write(b"data: [DONE]\n\n")
                    self.wfile.flush()

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        provider = ChatCompletionProvider(
            f"http://127.0.0.1:{server.server_port}/chat/completions",
            "test",
            "key",
            1,
            2,
        )

        def on_progress(value):
            updates.append(value)
            if value["live_units"] == 1:
                received.set()

        adapter = ProseProgressProvider(provider, on_progress, count_units)

        def generate():
            try:
                result.append(adapter.complete(ModelRequest("writer", "写作", {}, 100)))
            except Exception as exc:
                result.append(exc)

        worker = threading.Thread(target=generate, daemon=True)
        worker.start()
        try:
            self.assertTrue(first_sent.wait(5))
            self.assertTrue(received.wait(5), "字数应在响应结束前更新")
            self.assertTrue(worker.is_alive())
        finally:
            release.set()
            worker.join(5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(result), 1)
        self.assertEqual(json.loads(result[0].content)["new_stage_text"], "雨停了。")
        self.assertEqual(updates[-1]["live_units"], 3)

    def test_missing_usage_is_rejected_and_not_reported_as_complete(self):
        events = [
            {"choices": [{"delta": {"content": "未完成"}, "finish_reason": "stop"}]}
        ]
        with patch(
            "inf_backend.streaming.http.client.HTTPConnection",
            return_value=Connection(Response(events)),
        ):
            with self.assertRaises(ProviderError):
                self.adapter.complete(self.request)
        self.assertNotIn(
            "processing", [update["live_phase"] for update in self.updates]
        )

    def test_length_rewrite_keeps_completed_stages_and_draft_separate(self):
        book = {
            "prepared_events": {
                "2": {"stage_realizations": [{"text": "前文"}, {"text": "已完成"}]}
            }
        }
        request = ModelRequest(
            "writer",
            "写作",
            {
                "chapter_number": 2,
                "current_draft": "甲" * 1800,
                "stage_task": {"unit_number": 3, "total_units": 4},
            },
            100,
        )
        details = describe_prose_request(book, request, count_units)
        self.assertEqual(
            details,
            {
                "live_completed_units": 5,
                "live_unit_number": 3,
                "live_unit_total": 4,
                "live_draft_units": 1800,
            },
        )
        self.assertEqual(
            describe_prose_request(
                book,
                ModelRequest("writer", "写作", {"chapter_number": 3}, 100),
                count_units,
            )["live_completed_units"],
            0,
        )

    def test_generation_installs_streaming_provider_for_supported_model(self):
        config = Settings(api_key="test-key")
        gateway = ModelGateway(self.provider, Budget(20, 100, 100))
        metadata = {"target_chapters": 2, "model": config.public_config()}

        def check_session(_path, wrapped, _plan, book=None):
            self.assertIsInstance(
                wrapped.gateway.gateway.provider, ProseProgressProvider
            )
            raise RuntimeError("provider checked")

        with (
            patch.object(service, "_metadata", return_value=metadata),
            patch.object(service, "_longform_plan", return_value={}),
            patch.object(service, "_load_longform_book", return_value=None),
            patch.object(service, "_gateway", return_value=(gateway, None)),
            patch.object(
                service,
                "load_writing_style",
                return_value={"instructions": "", "reference": ""},
            ),
            patch.object(service, "load_book_skills", return_value=[]),
            patch.object(service, "list_skills", return_value=[]),
            patch.object(service, "WritingSession", side_effect=check_session),
            self.assertRaisesRegex(RuntimeError, "provider checked"),
        ):
            service.generate_longform(
                "book-a", settings=config, progress=lambda _update: None
            )

    def test_non_prose_requests_keep_existing_provider(self):
        request = ModelRequest("planner", "规划", {}, 100)
        with patch.object(ChatCompletionProvider, "complete", return_value="unchanged"):
            self.assertEqual(self.adapter.complete(request), "unchanged")
        self.assertEqual(self.updates, [])
