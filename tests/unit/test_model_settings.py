import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import generation, service, settings


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

    def test_invalid_config_does_not_modify_existing_file(self):
        path = self.root / ".env"
        path.write_text("DEEPSEEK_API_KEY=sk-existing\n", encoding="utf-8")
        for endpoint in (
            "http://example.com/v1/chat/completions",
            "https://user:pass@example.com/chat/completions",
            "https://127.0.0.1/chat/completions",
            "https://example.com/chat/completions\nX=1",
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
