from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.exceptions import DuplicateArtefactError, InvalidUploadExtensionError, NotFoundError, PayloadTooLargeError
from app.models.jobs import JobStatus
from app.obs.logging import log_upload as obs_log_upload
from app.repositories import jobs as jobs_repo
from app.services.ingestion_service import IngestionService, artefact_public

_obs = logging.getLogger("obs.upload")


@dataclass(slots=True)
class UploadBatchResult:
    created: list[dict[str, object]]
    duplicates: list[dict[str, str]]
    rejected: list[dict[str, str]]
    too_large: list[dict[str, str]]
    correlation_id: UUID


async def run_upload_burst(ing: IngestionService, disciplina_id: UUID, files: list[UploadFile]) -> UploadBatchResult:
    correlation_id = uuid4()
    obs_log_upload(
        _obs,
        {
            "event": "upload_batch_started",
            "discipline_id": str(disciplina_id),
            "correlation_id": str(correlation_id),
            "file_count": len(files),
        },
    )

    created: list[dict[str, object]] = []
    duplicates: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    too_large: list[dict[str, str]] = []

    for uf in files:
        fname = (uf.filename or "upload").rsplit("/", 1)[-1]
        ledger = jobs_repo.insert_job(
            ing.session,
            discipline_id=disciplina_id,
            correlation_id=correlation_id,
            upload_filename=fname,
            status=JobStatus.PENDING,
        )
        jobs_repo.update_job(
            ing.session,
            ledger.id,
            status=JobStatus.PROCESSING,
        )
        obs_log_upload(
            _obs,
            {
                "event": "upload_file_started",
                "correlation_id": str(correlation_id),
                "job_id": str(ledger.id),
                "filename": fname,
            },
        )
        ing.session.commit()

        try:
            row = await ing.ingest_upload(disciplina_id, uf)
            jobs_repo.update_job(
                ing.session,
                ledger.id,
                status=JobStatus.COMPLETED,
                artefact_id=row.id,
            )
            ing.session.commit()
            created.append(artefact_public(row))
            obs_log_upload(
                _obs,
                {
                    "event": "upload_file_completed",
                    "correlation_id": str(correlation_id),
                    "job_id": str(ledger.id),
                    "artefact_id": str(row.id),
                    "sha256_prefix": row.sha256[:16],
                    "filename": fname,
                },
            )
        except DuplicateArtefactError as exc:
            duplicates.append({"filename": fname, "detail": str(exc)})
            jobs_repo.update_job(
                ing.session,
                ledger.id,
                status=JobStatus.FAILED,
                diagnostics={"code": "duplicate", "detail": str(exc)},
            )
            ing.session.commit()
            obs_log_upload(
                _obs,
                {
                    "event": "upload_file_failed",
                    "correlation_id": str(correlation_id),
                    "job_id": str(ledger.id),
                    "code": "duplicate",
                    "filename": fname,
                },
            )
        except InvalidUploadExtensionError as exc:
            rejected.append({"filename": fname, "detail": str(exc)})
            jobs_repo.update_job(
                ing.session,
                ledger.id,
                status=JobStatus.FAILED,
                diagnostics={"code": "validation", "detail": str(exc)},
            )
            ing.session.commit()
            obs_log_upload(
                _obs,
                {
                    "event": "upload_file_failed",
                    "correlation_id": str(correlation_id),
                    "job_id": str(ledger.id),
                    "code": "validation",
                    "filename": fname,
                },
            )
        except PayloadTooLargeError as exc:
            too_large.append({"filename": fname, "detail": str(exc)})
            jobs_repo.update_job(
                ing.session,
                ledger.id,
                status=JobStatus.FAILED,
                diagnostics={"code": "too_large", "detail": str(exc)},
            )
            ing.session.commit()
            obs_log_upload(
                _obs,
                {
                    "event": "upload_file_failed",
                    "correlation_id": str(correlation_id),
                    "job_id": str(ledger.id),
                    "code": "too_large",
                    "filename": fname,
                },
            )
        except NotFoundError:
            raise

    obs_log_upload(
        _obs,
        {
            "event": "upload_batch_finished",
            "discipline_id": str(disciplina_id),
            "correlation_id": str(correlation_id),
            "created": len(created),
            "duplicates": len(duplicates),
            "rejected": len(rejected),
            "too_large": len(too_large),
        },
    )

    return UploadBatchResult(
        created=created,
        duplicates=duplicates,
        rejected=rejected,
        too_large=too_large,
        correlation_id=correlation_id,
    )
