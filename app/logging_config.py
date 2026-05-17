from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.core.config import SettingsModel
from app.obs.logging import attach_upload_observer


def configure_logging(settings: SettingsModel, *, verbose: bool = True) -> None:
    """Configure root logger (stdout always; rotating file optional)."""

    handlers: list[logging.Handler] = []
    stdout = logging.StreamHandler()
    stdout.setLevel(logging.DEBUG if verbose else logging.INFO)
    stdout.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    handlers.append(stdout)

    if settings.logging_dir_abs:
        base = settings.logging_dir_abs
        fh = RotatingFileHandler(
            base / "academind.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handlers.append(fh)
        attach_upload_observer(base)

    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)
