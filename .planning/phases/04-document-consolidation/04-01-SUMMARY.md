# 04-01 Wave Summary — DOC-01 Merge

**Executed:** 2026-05-17  
**Artifacts:** alphabetical PDF merge driven by catalogue rows under `originais/documentos/`, emitting `processados/pdfs/concatenado.pdf` via atomic `os.replace`.

## Behaviour

- **Selection:** catalogue rows scoped to discipline, bucket `documentos`, relative path prefix `originais/documentos/`, suffix `.pdf`, sorted alphabetically by upload basename (`original_filename`).
- **Guards:** encrypted PDF rejected (`encrypted_pdf`). Corrupt/unreadable inputs stop the batch with diagnostics (`corrupt_pdf`). Advisory lock shim under `metadata/.merge_pdf.lock` (**interim JOB-02** — replace via `job_processados_lock.ProcessadosMutex` when Phase `03-01` ships).
- **API:** `POST /api/disciplinas/{discipline_id}/merge-pdfs` (`200`, `422` structured payload, `409` busy lock, `404` missing discipline).
- **UI:** discipline page HTMX swaps for Originais/Processados; Processados submits `Gerar concatenado.pdf` to `/ui/disciplinas/{id}/merge-pdfs` swapping `merge_feedback`.

## Deferred / Ops

- Manual smoke: uvicorn workstation + open merged `concatenado.pdf` externally (outside automated tests).
- When JOB-02 primitives exist, migrate lock file shim to authoritative worker mutex and drop stale-timeout recovery if redundant.
