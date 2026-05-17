from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlmodel import Session

from app.core.config import SettingsModel
from app.core.paths import ensure_discipline_paths
from app.exceptions import NotFoundError
from app.models.hierarchy import Course, Discipline
from app.repositories import hierarchy as repos


def resolve_discipline_paths(
    session: Session,
    discipline_id: UUID,
    settings: SettingsModel,
) -> tuple[Course, Discipline, Path]:
    discipline = repos.get_discipline(session, discipline_id)
    if discipline is None:
        raise NotFoundError("Discipline not found")

    course = repos.get_course(session, discipline.curso_id)
    if course is None:
        raise NotFoundError("Course not found")

    root = ensure_discipline_paths(course.slug, discipline.slug, settings.storage_root_abs)
    return course, discipline, root
