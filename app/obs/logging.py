"""Structured OBS lines for ingestion (OBS-01)."""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_LOGGERS: dict[str, logging.Logger] = {}


class _ObsFormatter(logging.Formatter):
    """One JSON object per line; payload comes from ``record.obs_payload``."""

    def format(self, record: logging.LogRecord) -> str:
        payload = getattr(record, "obs_payload", None)
        if isinstance(payload, dict):
            return json.dumps(payload, ensure_ascii=False)
        return json.dumps({"message": record.getMessage(), "level": record.levelname})


def attach_upload_observer(log_dir: Path) -> logging.Logger:
    """Idempotent rotating ``upload.log`` under ``log_dir``."""
    key = str(log_dir.resolve())
    if key in _LOGGERS:
        return _LOGGERS[key]

    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "upload.log"
    lg = logging.getLogger("obs.upload")
    lg.handlers.clear()
    lg.setLevel(logging.INFO)
    lg.propagate = False
    fh = RotatingFileHandler(str(path), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setFormatter(_ObsFormatter())
    fh.setLevel(logging.INFO)
    lg.addHandler(fh)
    _LOGGERS[key] = lg
    return lg


def log_upload(logger: logging.Logger | None, payload: dict[str, Any]) -> None:
    if logger is None:
        return
    logger.info("", extra={"obs_payload": payload})
