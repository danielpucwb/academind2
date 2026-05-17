# Plan 02-01 Summary — Wave 2a (trusted ingestion backbone)

Executed: 2026-05-17

## Delivered

- **`SettingsModel`**: `max_upload_bytes`, `upload_chunk_bytes` (defaults in `config.defaults.yaml` / example).
- **`CatalogueArtefact`** table + `exists_sha256` / `list_for_discipline` repository.
- **`IngestionService`**: streaming reads, SHA256 dedupe per discipline, sanitized names, paths under `originais/{bucket}/`, temp `.part` → atomic `os.replace`.
- **`POST /api/upload`**: `disciplina_id` (form) + repeatable `files`; **409** duplicate-only batch, **422** validation-only, **413** oversize-only; **200** with split arrays for mixed outcomes.
- **Tests**: `tests/test_ingestion.py` (PDF path, duplicate, `.exe` reject, unknown discipline).

## Verification

- `python -m compileall app`
- `python -m pytest -q`

## Note

SQLite `create_all` adds `catalogue_artefact` on new DBs. Existing local `database/academind.db` from before this change may need a wipe or manual migration to create the new table.
