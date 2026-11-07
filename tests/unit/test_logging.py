"""Verify local logs are bounded and do not contain exception details."""

import logging
import tempfile
import unittest
from logging.handlers import RotatingFileHandler
from pathlib import Path

from inf_backend.logging_setup import configure_logging, log_failure, logger


class LocalLoggingTests(unittest.TestCase):
    def tearDown(self):
        for handler in list(logger.handlers):
            if isinstance(handler, RotatingFileHandler):
                logger.removeHandler(handler)
                handler.close()

    def test_failure_log_omits_secrets_and_reuses_handler(self):
        with tempfile.TemporaryDirectory() as folder:
            path = configure_logging(folder)
            configure_logging(folder)
            self.assertEqual(
                sum(isinstance(h, RotatingFileHandler) for h in logger.handlers), 1
            )
            log_failure("Generation", ValueError("sk-private secret story"), "job123")
            for handler in logger.handlers:
                handler.flush()
            output = path.read_text(encoding="utf-8")
            self.assertIn("type=ValueError job=job123", output)
            self.assertNotIn("sk-private", output)
            self.assertNotIn("secret story", output)
            self.tearDown()

    def test_log_rotates_and_reconfiguration_changes_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            first = configure_logging(folder, "first.log")
            handler = next(
                h for h in logger.handlers if isinstance(h, RotatingFileHandler)
            )
            handler.maxBytes = 100
            logger.info("x" * 120)
            logger.info("y" * 120)
            self.assertTrue(Path(str(first) + ".1").exists())
            second = configure_logging(folder, "second.log")
            logger.info("second destination")
            for item in logger.handlers:
                item.flush()
            self.assertIn("second destination", second.read_text(encoding="utf-8"))
            self.assertEqual(
                sum(isinstance(h, RotatingFileHandler) for h in logger.handlers), 1
            )
            self.tearDown()

    def test_logger_does_not_propagate_to_root(self):
        with tempfile.TemporaryDirectory() as folder:
            configure_logging(folder)
            self.assertEqual(logger.level, logging.INFO)
            self.assertFalse(logger.propagate)
            self.tearDown()
