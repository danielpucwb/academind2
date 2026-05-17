from __future__ import annotations

import subprocess
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, text

from app.core.db import get_session

router = APIRouter(tags=["health"])


def _ffmpeg_available(binary: str) -> tuple[bool, str | None]:
    try:
        proc = subprocess.run(
            [binary, "-version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        ok = proc.returncode == 0
        hint = proc.stderr.strip()[:200] or proc.stdout.strip()[:200] or None
        return ok, None if ok else hint
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, None


def _torch_cuda_available() -> bool | None:
    try:
        import torch  # type: ignore[import-not-found]

        return bool(torch.cuda.is_available())
    except Exception:
        return None


@router.get("/health")
def health_check(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, Any]:
    # Registered before `/static` in `main` so diagnostics are never shadowed by static mounts.
    settings = request.app.state.settings
    sqlite_ok = False
    try:
        session.exec(text("SELECT 1"))
        sqlite_ok = True
    except Exception:
        sqlite_ok = False

    ffmpeg_bin = settings.ffmpeg_path
    ffmpeg_ok, _hint = _ffmpeg_available(ffmpeg_bin)
    whisper_cuda = _torch_cuda_available()

    if sqlite_ok and ffmpeg_ok:
        status = "ok"
    elif sqlite_ok:
        status = "degraded"
    else:
        status = "error"

    return {
        "status": status,
        "sqlite": sqlite_ok,
        "ffmpeg": ffmpeg_ok,
        "whisper_cuda": whisper_cuda,
    }
