from datetime import datetime, timezone
import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch

from inf_backend import official_pricing as pricing


class OfficialPricingTests(unittest.TestCase):
    def test_network_failure_uses_verified_prices_and_does_not_retry_each_estimate(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(pricing, "CACHE", Path(directory) / "cache.json"), \
                patch.object(pricing, "_cached", None), patch.object(pricing, "_attempted_at", None), \
                patch.object(pricing.http.client, "HTTPSConnection") as connection:
            connection.return_value.request.side_effect = OSError("offline")
            table = pricing.get_table()
            self.assertEqual(table["models"], pricing.SNAPSHOT)
            self.assertEqual(table["status"], "cached")
            self.assertEqual(pricing.get_table(), table)
            connection.assert_called_once()

    def test_beijing_peak_boundaries_and_weekends(self):
        for clock, expected in (("08:59", "off_peak"), ("09:00", "peak"), ("11:59", "peak"),
                                ("12:00", "off_peak"), ("13:59", "off_peak"), ("14:00", "peak"),
                                ("17:59", "peak"), ("18:00", "off_peak")):
            with self.subTest(clock=clock):
                self.assertEqual(pricing.period_at(datetime.fromisoformat(f"2026-10-26T{clock}:00+08:00")), expected)
        self.assertEqual(pricing.period_at(datetime(2026, 10, 26, 1, tzinfo=timezone.utc)), "peak")
        for day in ("2026-10-24", "2026-10-25", "2026-10-01", "2026-02-23", "2026-10-10"):
            self.assertEqual(pricing.period_at(datetime.fromisoformat(f"{day}T10:00:00+08:00")), "off_peak")

    def test_prices_aliases_unknown_models_and_snapshot_status(self):
        snapshot = {"models": pricing.SNAPSHOT, "checked_at": "2026-10-24", "status": "cached"}
        with patch.object(pricing, "get_table", return_value=snapshot):
            peak = pricing.quote("deepseek-flash", datetime.fromisoformat("2026-10-26T09:00:00+08:00"))
            self.assertEqual(peak["rates"], {"input": 2, "output": 8, "cache_hit": .04})
            off = pricing.quote("deepseek-v4-pro", datetime.fromisoformat("2026-10-24T09:00:00+08:00"))
            self.assertEqual(off["rates"]["input"], 4.5)
            self.assertEqual(off["peak_rates"]["output"], 27)
            old = pricing.quote("deepseek-chat")
            self.assertIn("不代表已确认", old["warning"])
            self.assertEqual(old["model"], "deepseek-flash")
            self.assertEqual(pricing.quote("deepseek-v4-flash")["model"], "deepseek-flash")
            self.assertIsNone(pricing.quote("unknown-model")["rates"])
            self.assertEqual(peak["status"], "cached")

    def test_official_table_parser_validates_structure(self):
        rows = [
            ["模型", "deepseek-flash", "deepseek-v4-pro"],
            ["百万tokens输入（缓存命中）", "空闲时段", "0.02元", "0.15元"],
            ["高峰时段", "0.04元", "0.30元"],
            ["百万tokens输入（缓存未命中）", "空闲时段", "1元", "4.5元"],
            ["高峰时段", "2元", "9元"],
            ["百万tokens输出", "空闲时段", "4元", "13.5元"],
            ["高峰时段", "8元", "27元"],
        ]
        document = "<table>" + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows) + "</table>"
        document += "周一至周五，不含中国法定节假日，9:00 - 12:00、14:00 - 18:00"
        self.assertEqual(pricing.parse_prices(document), pricing.SNAPSHOT)
        with self.assertRaises(ValueError):
            pricing.parse_prices(document.replace("8元", "未知"))
        with self.assertRaises(ValueError):
            pricing.parse_prices(document.replace("9:00 - 12:00", "8:00 - 13:00"))


if __name__ == "__main__":
    unittest.main()
