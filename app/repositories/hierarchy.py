from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, select

from app.models.hierarchy import Course, Discipline


def list_courses(session: Session) -> Sequence[Course]:
    return session.exec(select(Course).order_by(Course.created_at)).all()


def get_course(session: Session, course_id: UUID) -> Course | None:
    return session.get(Course, course_id)


def get_course_by_slug(session: Session, slug: str) -> Course | None:
    return session.exec(select(Course).where(Course.slug == slug)).first()


def upsert_placeholders(session: Session, course: Course) -> Course:
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def list_disciplines_for_course(session: Session, curso_id: UUID) -> Sequence[Discipline]:
    stmt = select(Discipline).where(Discipline.curso_id == curso_id).order_by(Discipline.created_at)
    return session.exec(stmt).all()


def get_discipline(session: Session, disc_id: UUID) -> Discipline | None:
    return session.get(Discipline, disc_id)


def discipline_slug_taken(session: Session, curso_id: UUID, slug: str) -> bool:
    stmt = (
        select(Discipline.id)
        .where(Discipline.curso_id == curso_id)
        .where(Discipline.slug == slug)  # type: ignore[arg-type]
        .limit(1)
    )
    return session.exec(stmt).first() is not None
