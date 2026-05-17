from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.models.catalogue import CatalogueArtefact


def get_by_id(session: Session, artefact_id: UUID) -> CatalogueArtefact | None:
    return session.get(CatalogueArtefact, artefact_id)


def exists_sha256(session: Session, discipline_id: UUID, digest_hex: str) -> bool:
    stmt = (
        select(CatalogueArtefact.id)
        .where(CatalogueArtefact.discipline_id == discipline_id)
        .where(CatalogueArtefact.sha256 == digest_hex.lower())  # type: ignore[arg-type]
        .limit(1)
    )
    return session.exec(stmt).first() is not None


def list_for_discipline(session: Session, discipline_id: UUID) -> list[CatalogueArtefact]:
    stmt = (
        select(CatalogueArtefact)
        .where(CatalogueArtefact.discipline_id == discipline_id)
        .order_by(CatalogueArtefact.created_at)  # type: ignore[attr-defined]
    )
    return list(session.exec(stmt).all())
