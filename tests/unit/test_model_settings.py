import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import generation, service, settings
from memory_runtime.writing import WritingSession


class ModelSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, {}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        root = patch.object(settings, "BACKEND_ROOT", self.root)
        root.start()
        self.addCleanup(root.stop)

    def test_old_deepseek_book_survives_provider_switch(self):
        (self.root / ".env").write_text(
            "DEEPSEEK_API_KEY=sk-old-test-key\n", encoding="utf-8"
        )
        old = settings.Settings.load().public_config()
        cfg = settings.configure_model("openai", "gpt-4o", "", "sk-openai-test-key")
        self.assertEqual(cfg.provider, "openai")
        self.assertIsNone(cfg.thinking)
        gateway, _ = service._gateway(cfg)
        self.assertEqual(gateway.provider.token_limit_field, "max_completion_tokens")
        self.assertIsNone(gateway.provider.thinking_enabled)
        self.assertNotIn("sk-openai-test-key", str(cfg.public_config()))
        restored = settings.Settings.for_book(old)
        self.assertEqual(restored.api_key, "sk-old-test-key")
        self.assertEqual(restored.public_config(), old)
        self.assertIn(
            "DEEPSEEK_API_KEY=sk-old-test-key",
            (self.root / ".env").read_text(encoding="utf-8"),
        )

    def test_custom_provider_name_is_persisted_and_validated(self):
        cfg = settings.configure_model(
            "compatible", "qwen-plus", "https://example.com/v1", "safe-key", "通义千问"
        )
        self.assertEqual(cfg.provider_name, "通义千问")
        self.assertEqual(settings.Settings.load().provider_name, "通义千问")
        self.assertNotIn("provider_name", cfg.public_config())
        with self.assertRaises(ValueError):
            settings.configure_model(
                "compatible", "qwen-plus", "https://example.com/v1", "safe-key", "坏名称\nINJECTED=yes"
            )

    def test_connection_test_does_not_save_and_checks_provider_response(self):
        from unittest.mock import Mock

        connection = Mock()
        connection.getresponse.return_value.status = 200
        connection.getresponse.return_value.read.return_value = b'{"choices":[{"message":{"content":"OK"}}]}'
        with patch.object(settings.http.client, "HTTPSConnection", return_value=connection):
            self.assertTrue(settings.test_model_connection("compatible", "qwen", "https://example.com/v1", "safe-key", "千问"))
            self.assertFalse((self.root / ".env").exists())
            connection.getresponse.return_value.status = 401
            with self.assertRaisesRegex(ValueError, "HTTP 401"):
                settings.test_model_connection("compatible", "qwen", "https://example.com/v1", "safe-key", "千问")
            self.assertFalse((self.root / ".env").exists())

    def test_saved_endpoint_key_can_be_reused_without_disclosure(self):
        settings.configure_model("compatible", "first", "https://example.com/v1", "saved-key", "服务商")
        result = settings.configure_model("compatible", "second", "https://example.com/v1", "", "服务商")
        self.assertEqual(result.api_key, "saved-key")
        self.assertNotIn("saved-key", str(result.public_config()))
        with self.assertRaises(ValueError):
            settings.configure_model("compatible", "model", "https://another.example/v1", "", "其他")

    def test_multiple_endpoints_keep_distinct_credentials(self):
        endpoint = "https://example.com/compatible-mode/v1/chat/completions"
        compatible = settings.configure_model(
            "compatible", "qwen-plus", endpoint, "key-one"
        )
        old = compatible.public_config()
        gateway, _ = service._gateway(compatible)
        self.assertEqual(gateway.provider.token_limit_field, "max_tokens")
        self.assertIsNone(gateway.provider.thinking_enabled)
        settings.configure_model("openai", "gpt-4o", "", "key-two")
        self.assertEqual(settings.Settings.for_book(old).api_key, "key-one")
        self.assertEqual(settings.Settings.load().api_key, "key-two")
        self.assertIsNone(generation.price_for(old)["rates"])
        self.assertIsNone(
            generation.price_for({**old, "model": "deepseek-chat"})["rates"]
        )

    def test_compatible_base_url_reuses_full_endpoint_credentials(self):
        base_url = "https://example.com/compatible-mode/v1"
        endpoint = base_url + "/chat/completions"
        original = settings.configure_model(
            "compatible", "qwen-plus", endpoint, "old-key"
        )
        for address in (base_url, base_url + "/", endpoint, endpoint + "/"):
            with self.subTest(address=address):
                cfg = settings.configure_model(
                    "compatible", "qwen-plus", address, "new-key"
                )
                self.assertEqual(cfg.public_config(), original.public_config())
                self.assertEqual(settings.Settings.load().endpoint, endpoint)
                self.assertEqual(
                    settings.Settings.for_book(original.public_config()).api_key,
                    "new-key",
                )
        cfg = settings.configure_model(
            "compatible", "qwen-plus", "https://example.com", "new-key"
        )
        self.assertEqual(cfg.endpoint, "https://example.com/chat/completions")

    def test_existing_checkpoint_remains_resumable_after_switch(self):
        (self.root / ".env").write_text(
            "DEEPSEEK_API_KEY=sk-old-test-key\n", encoding="utf-8"
        )
        with patch.object(service, "BOOKS", self.root / "books"):
            book = service.create_book(
                "old-book", "旧作", "故事", 2, 1000, settings=settings.Settings.load()
            )
            plan = service._longform_plan(book["metadata"])
            session = WritingSession(
                service.book_path("old-book") / "longform-runs" / "initial",
                object(),
                plan,
            )
            service._atomic_json(
                service._longform_pointer("old-book"),
                {
                    "checkpoint": session.latest_checkpoint.relative_to(
                        service.book_path("old-book")
                    ).as_posix()
                },
            )
            settings.configure_model("openai", "gpt-4o", "", "sk-new-test-key")
            recovered = service._load_longform_book("old-book", plan)
            self.assertEqual(recovered["chapters"], [])
            self.assertEqual(
                settings.Settings.for_book(book["metadata"]["model"]).api_key,
                "sk-old-test-key",
            )

    def test_invalid_config_does_not_modify_existing_file(self):
        path = self.root / ".env"
        path.write_text("DEEPSEEK_API_KEY=sk-existing\n", encoding="utf-8")
        for endpoint in (
            "http://example.com/v1/chat/completions",
            "https://user:pass@example.com/chat/completions",
            "https://127.0.0.1/chat/completions",
            "https://example.com/chat/completions\nX=1",
            "https://@example.com/v1",
            "https://example.com/v1?token=secret",
            "https://example.com/v1#fragment",
            "https://localhost/v1",
            "https://example.com:8443/v1",
            "https://example.com/v1\\chat",
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                settings.configure_model("compatible", "model", endpoint, "safe-key")
        with self.assertRaises(ValueError):
            settings.configure_model("openai", "gpt-4o", "", "bad\nINJECTED=yes")
        self.assertEqual(
            path.read_text(encoding="utf-8"), "DEEPSEEK_API_KEY=sk-existing\n"
        )


if __name__ == "__main__":
    unittest.main()
