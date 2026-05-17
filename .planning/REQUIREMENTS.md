# Requirements: acadeMIND

**Defined:** 2026-05-17  
**Core Value:** Graduate students ingest messy academic media locally—GPU transcription + consolidated downloads—without mandatory cloud reliance.

## v1 Requirements

### Hierarchy & UX Shell

- [ ] **ORG-01**: User can create a named academic **course** that persists locally and anchors storage mapping. _(Phase 1)_
- [ ] **ORG-02**: User can rename a course (metadata + slug rules) without breaking archived paths unintentionally—slug changes must be guarded or disallowed once files exist _(Phase 1)_.
- [ ] **ORG-03**: User can delete a course **only when** safeguards prevent orphaned blobs (confirmation + dependency checks). _(Phase 1)_
- [ ] **ORG-04**: User can create a discipline under a course with its own deterministic storage subtree. _(Phase 1)_
- [ ] **ORG-05**: User can delete a discipline with the same orphan safeguards as courses. _(Phase 1)_
- [ ] **WEB-01**: Dashboard renders the list/grid of courses with entry points aligned to PROJECT.md UX tone. _(Phase 1)_
- [ ] **WEB-02**: Discipline detail view exposes tabs for Originals / Processados / Processamento—even if downstream tabs start empty—with navigation mirroring PROJECT.md IA. _(Phase 1)_ 
- [ ] **WEB-07**: Presentation tokens (spacing/typography/components) derive from [`projekt-design-system.html`](e:/academind2/projekt-design-system.html); copy/branding stays **acadeMIND-only** (no Projekt naming). _(Phase 5 hardening)_ — _Note: scaffolding may begin Phase 1, completion tracked Phase 5._

### API Contracts (Thin HTTP Facade)

- [ ] **API-01**: Expose course collection + mutators documented in PROJECT.md (`GET/POST`, `DELETE`). _(Phase 1)_
- [ ] **API-02**: Expose discipline collection + destructive operations per SDD. _(Phase 1)_
- [ ] **API-03**: Multipart uploads land in the correct originals subtree grouped by MIME category conventions. _(Phase 2)_
- [ ] **API-04**: User can POST a batch processing trigger referencing a discipline; server acknowledges job creation and never blocks on GPU completion. _(Phase 3)_ 
- [ ] **API-05**: Authenticated-download equivalent for local trusted client—endpoints serve individual artefacts + ZIP payloads using streaming-safe responses. _(Phase 5)_ 
- [ ] **API-06**: `/health` reports uptime plus coarse subsystem signals (SQLite reachable, FFmpeg binary callable, whisper engine lazy-load flag). _(Phase 1)_

### Ingestion, Integrity & Catalog

- [ ] **UPL-01**: Drag/drop multi-file ingestion posts through the discipline **Originais** experience with chunked-friendly server handling. _(Phase 2)_ 
- [ ] **UPL-02**: Only accepted extensions (`pdf,txt,docx,html,mhtml,mp4,mp3,wav,m4a`) pass validation; rejects are surfaced with actionable errors. _(Phase 2)_ 
- [ ] **UPL-03**: Each upload persists `SHA256` fingerprint to suppress duplicates cleanly. _(Phase 2)_ 
- [ ] **UPL-04**: Stored paths never escape sanctioned `storage/cursos/<course>/<discipline>/...` anchors (sanitize + traversal checks). _(Phase 2)_ 
- [ ] **UPL-05**: Originals tab enumerates artefacts with preview metadata, download shortcut, destructive delete, optional “Reveal folder”. _(Phase 2)_ 

### Jobs, Concurrency & Resilience

- [ ] **JOB-01**: Persisted job rows capture `pending→processing→completed|failed` with timestamps plus diagnostic payloads surfaced in the Processing tab backlog. _(Phase 2)_ 
- [ ] **JOB-02**: At most **one active mutating processor** touches a discipline’s `processados/` tree simultaneously (explicit lock rows or equivalent). _(Phase 3)_ 
- [ ] **JOB-03**: User can enqueue processing from Processing tab referencing current backlog items. _(Phase 3)_ 
- [ ] **JOB-04**: Watchdog detects hung subprocess (>configurable timeout), marks failure, rotates logs—not silent stall. _(Phase 3)_ 
- [ ] **JOB-05**: Operators can rerun failed steps without duplicating artefacts (deterministic filenames + skip-if-hash matches). _(Phase 5 polish)_  

### Audio Normalization Path

- [ ] **AUD-01**: FFmpeg normalization pipeline converts heterogeneous media inputs to whisper-friendly WAV/PCM using **argv-list** subprocess invocations—no shell injection. _(Phase 3)_ 
- [ ] **AUD-02**: Each FFmpeg invocation appends structured log lines to rolling `ffmpeg.log`. _(Phase 3)_ 

### GPU Transcription

- [ ] **TRN-01**: faster-whisper runs with configured model (default **`large-v3`**) emitting UTF-8 `.txt`. _(Phase 3)_ 
- [ ] **TRN-02**: Runtime honors `cuda` device + FP16-ish compute when available; degrade path documented via `/health` + toast. _(Phase 3)_ 
- [ ] **TRN-03**: Transcripts persist under deterministic `processados/transcricoes/` paths referenced in SQLite. _(Phase 3)_ 
- [ ] **TRN-04**: Whisper jobs log to `whisper.log` capturing model + elapsed + failure reason codes. _(Phase 3)_ 

### Document Consolidation

- [ ] **DOC-01**: System merges discipline PDF originals alphabetically into `concatenado.pdf`, tolerating corrupt pages with explicit failure surfaced. _(Phase 4)_ 

### Packaging & Download

- [ ] **PKG-01**: User can assemble `exports/disciplina-export.zip` embedding originals, transcripts, merged PDF snapshot, slim `metadata.json`. _(Phase 5)_ 
- [ ] **PKG-02**: Download endpoints reuse streaming safeguards + zipped manifest hashing described in PROJECT.md backlog. _(Phase 5)_ 

### Observability & Configuration

- [ ] **CFG-01**: Startup loads `config.yaml` for storage roots, allowed extensions, Whisper model/language knobs, parallelism limits, uploads ceiling, FFmpeg/Whisper timeout budgets. _(Phase 1)_ 
- [ ] **OBS-01**: Upload/API logs land under `/logs/` with correlation IDs referencing job rows. _(Phase 2)_ 
- [ ] **OBS-02**: FFmpeg/Whisper transcripts of subprocess output append once the media pipeline runs. _(Phase 3)_ 
- [ ] **OBS-03**: Sensitive operations (destructive deletes, ZIP issuance) emit explicit audit stubs for local traceability. _(Phase 5)_ 

### Frontend Productivity Hooks

- [ ] **WEB-03**: Upload surfaces drag/drop cues + optimistic progress placeholders per PROJECT.md backlog. _(Phase 2)_ 
- [ ] **WEB-04**: Processing tab visualizes FIFO queue depth, ETA text (best-effort), link to aggregated logs excerpt. _(Phase 3)_ 
- [ ] **WEB-05**: Processados tab exposes transcripts + merged pdf + zipped export badges with staleness cues (pending/regenerating states). _(Phase 5)_ 
- [ ] **WEB-06**: Toasts/snackbars communicate success/failure with non-blocking patterns. _(Phase 5)_ 

## v2 Requirements

### Advanced Capture & Knowledge

- **SEM-01**: Semantic search/local embeddings powering recall across transcripts (deferred backlog).  
- **OCR-01**: Rasterized slides OCR pipeline tying into storage graph.  

### Collaboration & Connectivity

- **MULTI-01**: Multi-seat auth + quotas.  
- **SYNC-01**: Optional remote backup / Obsidian / Markdown interoperability.  

## Out of Scope

| Feature | Reason |
|---|---|
| Electron-first wrapper | Explicit SDD prohibition for MVP backbone—revisit packaging later. |
| Mandatory cloud ingestion | Violates PROJECT.md premise; optional integrations belong to SYNC backlog. |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| ORG-01 | Phase 1 | Pending |
| ORG-02 | Phase 1 | Pending |
| ORG-03 | Phase 1 | Pending |
| ORG-04 | Phase 1 | Pending |
| ORG-05 | Phase 1 | Pending |
| WEB-01 | Phase 1 | Pending |
| WEB-02 | Phase 1 | Pending |
| API-01 | Phase 1 | Pending |
| API-02 | Phase 1 | Pending |
| API-06 | Phase 1 | Pending |
| CFG-01 | Phase 1 | Pending |
| UPL-01 | Phase 2 | Pending |
| UPL-02 | Phase 2 | Pending |
| UPL-03 | Phase 2 | Pending |
| UPL-04 | Phase 2 | Pending |
| UPL-05 | Phase 2 | Pending |
| API-03 | Phase 2 | Pending |
| JOB-01 | Phase 2 | Pending |
| OBS-01 | Phase 2 | Pending |
| WEB-03 | Phase 2 | Pending |
| AUD-01 | Phase 3 | Pending |
| AUD-02 | Phase 3 | Pending |
| TRN-01 | Phase 3 | Pending |
| TRN-02 | Phase 3 | Pending |
| TRN-03 | Phase 3 | Pending |
| TRN-04 | Phase 3 | Pending |
| JOB-02 | Phase 3 | Pending |
| JOB-03 | Phase 3 | Pending |
| JOB-04 | Phase 3 | Pending |
| API-04 | Phase 3 | Pending |
| OBS-02 | Phase 3 | Pending |
| WEB-04 | Phase 3 | Pending |
| DOC-01 | Phase 4 | Pending |
| PKG-01 | Phase 5 | Pending |
| PKG-02 | Phase 5 | Pending |
| API-05 | Phase 5 | Pending |
| WEB-05 | Phase 5 | Pending |
| WEB-06 | Phase 5 | Pending |
| WEB-07 | Phase 5 | Pending |
| JOB-05 | Phase 5 | Pending |
| OBS-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 39 total  
- Mapped to phases: 39  
- Unmapped: 0 ✓  

---
*Requirements defined: 2026-05-17*  
*Last updated: 2026-05-17 after roadmap auto-generation*
