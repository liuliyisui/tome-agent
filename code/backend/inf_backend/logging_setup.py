"""Configure local diagnostic logs without collecting request or story contents."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("tome")


def configure_logging(directory, filename="tome.log"):
    """Write bounded UTF-8 logs; reuse the handler when called more than once."""
    target = Path(directory) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target = target.resolve()
    for handler in list(logger.handlers):
        if (
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename) == target
        ):
            return target
        if isinstance(handler, RotatingFileHandler):
            logger.removeHandler(handler)
            handler.close()
    handler = RotatingFileHandler(
        target, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return target


def log_failure(operation, exc, job_id=None):
    """Log only application-controlled fields and the exception class."""
    logger.error(
        "%s failed: type=%s job=%s", operation, type(exc).__name__, job_id or "-"
    )
