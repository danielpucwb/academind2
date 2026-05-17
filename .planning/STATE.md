# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-17)

**Core value:** Students consolidate academic media locally with GPU-assisted transcription packaged for download—no mandatory cloud.
**Current focus:** Phase 2 ingestion waves (**02‑02** / **02‑03**) shipped; prioritize **Phase 3** FFmpeg/Whisper (`03-01`) and JOB‑02 concurrency hardening.

## Current Position

Phase: **3 pending** (`03-01` worker/locks) — Phase 4 **04-01** merged; Phase 2 catalog backbone (**02‑01** … **02‑03**) complete.

## Accumulated Context

### Decisions

- Follow monolithic FastAPI + HTMX per PROJECT.md/`sdd.md`.
- Faster-Whisper default `large-v3` guarded by degrade path cues.
- PDF merge adopts `pypdf` + `metadata/.merge_pdf.lock` **until JOB-02-backed mutex replaces it**.

### Pending Todos

- Replace interim merge **`FileLock`** shim once **`03-01`** exports hardened worker locks (`job_processados_lock.ProcessadosMutex` hook wired in `processados_lock.py`).

### Blockers/Concerns

- Smoke-test NVIDIA driver + FFmpeg availability on workstation before trusting Phase 3 estimates.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Research | OCR / embeddings / semantic recall | Planned backlog | PROJECT.md |

## Session Continuity

Last session: 2026-05-17
Stopped at: **Phase 2** waves **02-02**/02‑03 landed (catalog API, JOB ledger unlink on delete, HTMX originals). Next: **`03-01`** worker harness / JOB‑02-backed merge lock unless reprioritized.
Resume file: None
