import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import service
from inf_backend.settings import Settings
from inf_writer.demo import DemoModel
from inf_writer.models import Budget, ModelGateway


class ServiceIntegrationTests(unittest.TestCase):
    def test_default_generation_entry_uses_stable_longform_runtime(self):
        self.assertIs(service.generate, service.generate_longform)

    def test_create_generate_and_export_with_offline_model(self):
        settings = Settings(api_key="FAKE_TEST_KEY")
        budget = Budget(max_calls=8, max_cost_usd=0)
        gateway = ModelGateway(DemoModel(), budget)
        local_tmp = Path(__file__).resolve().parents[2] / "code" / "backend" / "data"
        local_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=local_tmp) as folder, patch.object(service, "BOOKS", Path(folder)):
            created = service.create_book(
                "demo-book", "守灯人", "身份核验故事", 2, 1000, settings=settings
            )
            self.assertEqual(created["metadata"]["title"], "守灯人")
            completed = service.generate_legacy(
                "demo-book", count=2, gateway=gateway, budget=budget, settings=settings
            )
            self.assertEqual(len(completed["state"].chapters), 2)
            self.assertEqual(completed["state"].active_facts()[0]["value"], "金色")
            exported = service.export_markdown(completed)
            self.assertIn("# 守灯人", exported)
            self.assertIn("## 第2章", exported)
            self.assertEqual(budget.calls, 8)


if __name__ == "__main__":
    unittest.main()
