from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Course(SQLModel, table=True):
    __tablename__ = "course"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nome: str = Field(sa_column=Column(String(240), nullable=False))
    slug: str = Field(sa_column=Column(String(120), unique=True, nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Discipline(SQLModel, table=True):
    __tablename__ = "discipline"
    __table_args__ = (UniqueConstraint("curso_id", "slug", name="uq_discipline_course_slug"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    curso_id: UUID = Field(foreign_key="course.id")
    nome: str = Field(sa_column=Column(String(240), nullable=False))
    slug: str = Field(sa_column=Column(String(120), nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
