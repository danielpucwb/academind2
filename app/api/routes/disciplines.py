from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.db import get_session
from app.exceptions import DomainConflictError, NotFoundError
from app.services.hierarchy_service import HierarchyService

router = APIRouter(prefix="/api/disciplinas", tags=["disciplinas"])


def get_service(request: Request, session: Annotated[Session, Depends(get_session)]) -> HierarchyService:
    return HierarchyService(session, request.app.state.settings)


ServiceDep = Annotated[HierarchyService, Depends(get_service)]


class DisciplineCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=240)


class DisciplineOut(BaseModel):
    id: UUID
    curso_id: UUID
    nome: str
    slug: str


class DisciplineRename(BaseModel):
    nome: str = Field(min_length=1, max_length=240)


@router.get("", response_model=list[DisciplineOut])
def list_disciplines(curso_id: UUID, svc: ServiceDep) -> list[DisciplineOut]:
    try:
        svc.get_course_or_raise(curso_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    rows = svc.list_disciplines_models(curso_id)
    return [DisciplineOut(id=d.id, curso_id=d.curso_id, nome=d.nome, slug=d.slug) for d in rows]


@router.post("", response_model=DisciplineOut, status_code=201)
def create_discipline(curso_id: UUID, payload: DisciplineCreate, svc: ServiceDep) -> DisciplineOut:
    try:
        d = svc.create_discipline(curso_id, payload.nome)
        return DisciplineOut(id=d.id, curso_id=d.curso_id, nome=d.nome, slug=d.slug)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{discipline_id}", response_model=DisciplineOut)
def rename_discipline(discipline_id: UUID, payload: DisciplineRename, svc: ServiceDep) -> DisciplineOut:
    try:
        d = svc.rename_discipline(discipline_id, payload.nome)
        return DisciplineOut(id=d.id, curso_id=d.curso_id, nome=d.nome, slug=d.slug)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/{discipline_id}", status_code=204)
def delete_discipline(discipline_id: UUID, svc: ServiceDep) -> None:
    try:
        svc.delete_discipline(discipline_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
