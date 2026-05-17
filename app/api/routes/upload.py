from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlmodel import Session

from app.core.db import get_session
from app.exceptions import NotFoundError
from app.repositories import hierarchy as hier_repos
from app.services.ingestion_service import IngestionService
from app.services.upload_batch_service import run_upload_burst

router = APIRouter(prefix="/api", tags=["upload"])


def get_ingestion(request: Request, session: Annotated[Session, Depends(get_session)]) -> IngestionService:
    return IngestionService(session, request.app.state.settings)


IngDep = Annotated[IngestionService, Depends(get_ingestion)]


@router.post(
    "/upload",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["disciplina_id", "files"],
                        "properties": {
                            "disciplina_id": {"type": "string", "format": "uuid"},
                            "files": {"type": "array", "items": {"type": "string", "format": "binary"}},
                        },
                    }
                }
            }
        }
    },
)
async def upload_files(
    disciplina_id: Annotated[UUID, Form()],
    files: Annotated[list[UploadFile], File()],
    ing: IngDep,
) -> dict[str, object]:
    if not files:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="At least one file is required.")
    if hier_repos.get_discipline(ing.session, disciplina_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discipline not found.")

    try:
        bundle = await run_upload_burst(ing, disciplina_id, files)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if bundle.too_large and not bundle.created and not bundle.duplicates and not bundle.rejected:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"payload_too_large": bundle.too_large},
        )
    if bundle.rejected and not bundle.created and not bundle.duplicates and not bundle.too_large:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"rejected": bundle.rejected},
        )
    if bundle.duplicates and not bundle.created and not bundle.rejected and not bundle.too_large:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"duplicates": bundle.duplicates},
        )

    return {
        "created": bundle.created,
        "duplicates": bundle.duplicates or [],
        "rejected": bundle.rejected or [],
        "payload_too_large": bundle.too_large or [],
        "correlation_id": str(bundle.correlation_id),
    }
