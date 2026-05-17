from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.core.db import get_session
from app.exceptions import NotFoundError
from app.repositories import hierarchy as hier_repos
from app.repositories.catalogue import list_for_discipline
from app.services.artefact_service import delete_artefact_for_discipline
from app.services.ingestion_service import artefact_public

router = APIRouter(prefix="/api/disciplinas", tags=["catalogue"])


@router.get("/{discipline_id}/artefacts")
def list_artefacts(
    discipline_id: UUID,
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, object]:
    if hier_repos.get_discipline(session, discipline_id) is None:
        raise HTTPException(status_code=404, detail="Discipline not found.")
    rows = list_for_discipline(session, discipline_id)
    artefacts = [{**artefact_public(a), "sha256_prefix": (a.sha256[:12])} for a in rows]
    return {"discipline_id": str(discipline_id), "artefacts": artefacts}


@router.delete("/{discipline_id}/artefacts/{artefact_id}", status_code=204)
def remove_artefact(
    discipline_id: UUID,
    artefact_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    try:
        delete_artefact_for_discipline(session, request.app.state.settings, discipline_id, artefact_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Artefact not found.") from None
