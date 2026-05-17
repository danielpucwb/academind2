from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import update
from sqlmodel import Session

from app.core.config import SettingsModel
from app.core.paths import assert_resolved_under_anchor, ensure_discipline_paths
from app.exceptions import NotFoundError
from app.models.jobs import Job
from app.repositories import catalogue as catalogue_repo
from app.repositories import hierarchy as hier_repos


def delete_artefact_for_discipline(session: Session, settings: SettingsModel, discipline_id: UUID, artefact_id: UUID) -> None:
    row = catalogue_repo.get_by_id(session, artefact_id)
    if row is None or row.discipline_id != discipline_id:
        raise NotFoundError("Artefact not found under this discipline.")

    discipline = hier_repos.get_discipline(session, discipline_id)
    if discipline is None:
        raise NotFoundError("Discipline not found.")
    course = hier_repos.get_course(session, discipline.curso_id)
    if course is None:
        raise NotFoundError("Course not found.")

    root = ensure_discipline_paths(course.slug, discipline.slug, settings.storage_root_abs)
    abs_path = (root / row.stored_relative_path).resolve()
    assert_resolved_under_anchor(abs_path, Path(root))

    now = datetime.now(timezone.utc)
    session.execute(
        update(Job)
        .where(Job.artefact_id == artefact_id)
        .values(artefact_id=None, updated_at=now)
    )

    session.delete(row)
    session.commit()

    abs_path.unlink(missing_ok=True)
