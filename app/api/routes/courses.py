from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.core.db import get_session
from app.exceptions import DomainConflictError, NotFoundError
from app.services.hierarchy_service import HierarchyService

router = APIRouter(prefix="/api/cursos", tags=["cursos"])


def get_service(request: Request, session: Annotated[Session, Depends(get_session)]) -> HierarchyService:
    return HierarchyService(session, request.app.state.settings)


ServiceDep = Annotated[HierarchyService, Depends(get_service)]


class CourseCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=240)


class CourseOut(BaseModel):
    id: UUID
    nome: str
    slug: str


class CourseRename(BaseModel):
    nome: str = Field(min_length=1, max_length=240)


@router.get("", response_model=list[CourseOut])
def list_courses(svc: ServiceDep) -> list[CourseOut]:
    rows = svc.list_courses_models()
    return [CourseOut(id=c.id, nome=c.nome, slug=c.slug) for c in rows]


@router.post("", response_model=CourseOut, status_code=201)
def create_course(payload: CourseCreate, svc: ServiceDep) -> CourseOut:
    try:
        c = svc.create_course(payload.nome)
        return CourseOut(id=c.id, nome=c.nome, slug=c.slug)
    except DomainConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{course_id}", response_model=CourseOut)
def rename_course(course_id: UUID, payload: CourseRename, svc: ServiceDep) -> CourseOut:
    try:
        c = svc.rename_course(course_id, payload.nome)
        return CourseOut(id=c.id, nome=c.nome, slug=c.slug)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DomainConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: UUID, svc: ServiceDep) -> None:
    try:
        svc.delete_course(course_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
