"""Merge/processados concurrency guard until Phase 03-01 JOB-02 primitives land.

When ``app.services.job_processados_lock`` exports ``ProcessadosMutex``, it replaces
:class:`MergeLock` below (same async context API). Until then PyPI ``filelock`` wraps
``.metadata/.merge_pdf.lock`` per discipline with optional stale-timeout recovery.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

try:
    from app.services.job_processados_lock import ProcessadosMutex as MergeLock  # type: ignore[no-redef,unused-import]
except ImportError:
    from filelock import FileLock, Timeout

    from app.exceptions import MergeLockBusyError

    logger = logging.getLogger(__name__)

    _STALE_SECONDS_DEFAULT = float(os.environ.get("ACADEMIND_MERGE_LOCK_STALE_SEC", "300"))

    class MergeLock:
        """Advisory mutex anchored under ``metadata/`` (JOB-02 compatibility placeholder)."""

        def __init__(self, stale_after_seconds: float = _STALE_SECONDS_DEFAULT) -> None:
            self._stale_after = stale_after_seconds

        def _maybe_break_stale(self, lock_path: Path) -> None:
            if not lock_path.exists():
                return
            try:
                age = time.time() - lock_path.stat().st_mtime
            except OSError:
                return
            if age <= self._stale_after:
                return
            logger.warning(
                "Stale merge lock (>%.0fs) at %s; removing "
                "(replace with JOB-02 lock row when Phase 03 ships)",
                self._stale_after,
                lock_path,
            )
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Failed to remove stale lock %s", lock_path)

        @asynccontextmanager
        async def for_discipline_id(self, discipline_id: UUID, discipline_root: Path) -> AsyncIterator[None]:
            _ = discipline_id  # reserved for JOB-02 row keys
            meta = discipline_root / "metadata"
            meta.mkdir(parents=True, exist_ok=True)
            lock_path = meta / ".merge_pdf.lock"

            fl = FileLock(str(lock_path))
            self._maybe_break_stale(lock_path)

            def _enter_timeout() -> None:
                try:
                    fl.acquire(timeout=0)
                except Timeout as exc:
                    raise MergeLockBusyError(
                        "Outra operação está a atualizar processados nesta disciplina (bloqueio ativo)."
                    ) from exc

            await asyncio.to_thread(_enter_timeout)
            try:
                yield None
            finally:
                await asyncio.to_thread(fl.release)
