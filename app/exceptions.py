from __future__ import annotations


class DomainConflictError(RuntimeError):
    """Business rule violated (slug collision, guarded rename/delete). Maps to HTTP 409."""


class NotFoundError(LookupError):
    """Entity missing for requested id."""


class DuplicateArtefactError(DomainConflictError):
    """Same SHA256 fingerprint already catalogued under this discipline."""


class PayloadTooLargeError(ValueError):
    """Upload exceeds configured max_upload_bytes."""


class InvalidUploadExtensionError(ValueError):
    """Extension missing or disallowed."""


class NothingToMergeError(ValueError):
    """No catalogue PDFs eligible for merge under this discipline."""


class MergeLockBusyError(DomainConflictError):
    """Another mutation holds the processados/ merge lock for this discipline."""


class PdfMergeRejectedError(ValueError):
    """Batch rejected (encryption, corrupt input, conflicts). Carries diagnostics for API/HTMX."""

    def __init__(self, reason_pt: str, diagnostics: list[dict[str, str | None]]) -> None:
        super().__init__(reason_pt)
        self.reason_pt = reason_pt
        self.diagnostics = diagnostics
