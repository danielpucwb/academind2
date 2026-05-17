from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CatalogueArtefact(SQLModel, table=True):
    __tablename__ = "catalogue_artefact"
    __table_args__ = (UniqueConstraint("discipline_id", "sha256", name="uq_catalogue_discipline_sha256"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    discipline_id: UUID = Field(foreign_key="discipline.id", index=True)
    sha256: str = Field(sa_column=Column(String(64), nullable=False))
    original_filename: str = Field(sa_column=Column(String(512), nullable=False))
    stored_relative_path: str = Field(sa_column=Column(String(1024), nullable=False))
    bucket: str = Field(sa_column=Column(String(64), nullable=False))
    mime_type: str | None = Field(default=None, sa_column=Column(String(256), nullable=True))
    byte_size: int = Field(ge=0)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )