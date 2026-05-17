from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session

from app.models.jobs import Job, JobStatus


def utcnow_naive_fallback() -> datetime:
    """SQLite TIMESTAMP comparison convenience."""
    return datetime.now(timezone.utc)


def insert_job(
    session: Session,
    *,
    discipline_id: UUID,
    correlation_id: UUID,
    upload_filename: str,
    status: JobStatus = JobStatus.PENDING,
    diagnostics: dict | None = None,
) -> Job:
    now = utcnow_naive_fallback()
    row = Job(
        discipline_id=discipline_id,
        correlation_id=correlation_id,
        upload_filename=upload_filename[:512],
        status=status,
        diagnostics=diagnostics,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.flush()
    return row


def update_job(
    session: Session,
    job_id: UUID,
    *,
    status: JobStatus,
    artefact_id: UUID | None = None,
    diagnostics: dict | None = None,
) -> Job | None:
    row = session.get(Job, job_id)
    if row is None:
        return None
    row.status = status
    row.updated_at = datetime.now(timezone.utc)
    if artefact_id is not None:
        row.artefact_id = artefact_id
    if diagnostics is not None:
        row.diagnostics = diagnostics
    session.add(row)
    session.flush()
    return row
