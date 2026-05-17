"""PDF merge orchestration endpoints (DOC-01)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.db import get_session
from app.exceptions import MergeLockBusyError, NotFoundError, NothingToMergeError, PdfMergeRejectedError
from app.services.pdf_merge_service import PdfMergeService
from app.services.processados_lock import MergeLock

router = APIRouter(prefix="/api/disciplinas", tags=["documentos"])


def _pdf_merge_svc(request: Request, session: Annotated[Session, Depends(get_session)]) -> PdfMergeService:
    lock = getattr(request.app.state, "pdf_merge_lock", None)
    facade: MergeLock = lock if lock is not None else MergeLock()
    return PdfMergeService(session, request.app.state.settings, merge_lock=facade)


SvcDep = Annotated[PdfMergeService, Depends(_pdf_merge_svc)]


def _reject_payload(exc: PdfMergeRejectedError | NothingToMergeError) -> dict[str, object]:
    if isinstance(exc, NothingToMergeError):
        return {"ok": False, "reason": str(exc), "diagnostics": []}
    return {"ok": False, "reason": exc.reason_pt, "diagnostics": exc.diagnostics}


@router.post("/{discipline_id}/merge-pdfs")
async def merge_pdfs(discipline_id: UUID, svc: SvcDep) -> JSONResponse:
    """Merge alphabetical discipline PDF originals into ``processados/pdfs/concatenado.pdf``."""
    try:
        outcome = await svc.merge_discipline_pdf(discipline_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NothingToMergeError as exc:
        return JSONResponse(
            _reject_payload(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    except PdfMergeRejectedError as exc:
        return JSONResponse(_reject_payload(exc), status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    except MergeLockBusyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    diagnostics = [{"code": d.code, "message_pt": d.message_pt, "filename": d.filename} for d in outcome.diagnostics]

    payload = {"ok": True, "merged": outcome.to_json(), "diagnostics": diagnostics}
    return JSONResponse(payload, status_code=status.HTTP_200_OK)
