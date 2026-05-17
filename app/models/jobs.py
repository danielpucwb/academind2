from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, JSON
from sqlalchemy.types import UnicodeText
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(SQLModel, table=True):
    """JOB-01 ingestion ledger rows (minimal Phase 02-02 scaffolding)."""

    __tablename__ = "jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    discipline_id: UUID = Field(foreign_key="discipline.id", index=True)
    correlation_id: UUID = Field(index=True)
    artefact_id: UUID | None = Field(default=None, foreign_key="catalogue_artefact.id", nullable=True)
    upload_filename: str = Field(sa_column=Column(UnicodeText(512), nullable=False))
    status: JobStatus = Field(default=JobStatus.PENDING)
    diagnostics: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
