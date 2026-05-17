# acadeMIND

## What This Is

**acadeMIND** is a desktop-first application with a responsive local web UI for undergraduate students who want one place to collect, ingest, organize, process, and consolidate academic materials (PDFs, slides, handouts, lecture recordings, audio, exported web captures). Execution is **local on Windows 11**, with optional paths for Docker/PyInstaller later—not required for MVP.

The product pairs a modular **FastAPI + SQLite + HTMX/Tailwind** experience with filesystem-first storage and GPU-accelerated transcription (CUDA / **faster-whisper**) for media-heavy workflows.

## Core Value

A grad student can point the app at a course and discipline folder, ingest messy sources, kick off deterministic batch processing locally, then download transcripts, concatenated PDFs, and packaged exports—all **without mandatory cloud**.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Hierarchical academics model: courses, disciplines, and attachments with stable disk layout (`storage/cursos/...`).
- [ ] Multi-type upload cataloged in SQLite (`originais/` tree by category) plus integrity checks (fingerprints via SHA256) and safe filename handling / path traversal protection.
- [ ] Controlled processing pipeline(s): FFmpeg audio extraction + normalization jobs, Whisper transcription on NVIDIA RTX GPU, PDF merge utilities, deterministic exports (ZIP/metadata).
- [ ] Operational visibility: queued jobs (`pending`/`processing`/`completed`/`failed`), logging per subsystem, concurrency locks, timeouts/watchdog safeguards, retries/resume primitives.
- [ ] Responsive web UX: dashboards, drill-down discipline tabs (Originals / Processed / Processing controls), downloads, drag-and-drop upload, modest progress/error feedback—to design tokens mirrored from [`projekt-design-system.html`](e:/academind2/projekt-design-system.html) while keeping **acadeMIND branding** only (never reuse Projekt names/logos).
- [ ] `config.yaml`-driven knobs (paths, whisper model/language, parallelism, limits) plus `GET /health`.
- [ ] Local-only deployment story (dev `uvicorn` now; eventual packaging optional).

### Out of Scope

- OCR, semantic search, local RAG/embeddings/chat tutor experiences, flashcards—these explicitly live on the future backlog documented in [`sdd.md`](e:/academind2/sdd.md).
- Electron-only or cloud-mandatory architectures; heavyweight Node backends as the primary processor; sprawling microservices.
- Multi-user auth, SSO, remote synchronization (Obsidian/export markdown integrations are backlog).
- Real-time lecture streaming or lecture capture ingestion beyond user-provided uploads (no live classroom capture subsystem in MVP unless later requested).

## Context

- Canonical idea + SDD narrative: [`sdd.md`](e:/academind2/sdd.md) (Portuguese source of functional goals, MVP phases, backlog, UX notes).
- Reference visual tokens/components (not Projekt branded UI copy): [`projekt-design-system.html`](e:/academind2/projekt-design-system.html).
- MVP slices from SDD roadmap: scaffolding + ingestion; GPU transcription pipeline; PDF merge; ZIP export bundles; refining UI ergonomics afterward.
- Target hardware posture: NVIDIA RTX 4080 (+ CUDA toolkit 12+), ample RAM/NVMe; processing should never hard-block the lightweight web UI threads (async/offloaded workers assumption).

## Constraints

- **Platform**: Desktop-first Windows 11 local runtime; responsiveness still expected via browser shells.
- **Privacy / connectivity**: Offline-friendly; optional cloud integrations only later.
- **Tech stack alignment**: FastAPI service, SQLModel/Pydantic, SQLite relational store matching SDD schemas, FFmpeg + faster-whisper + PyTorch CUDA + pypdf stack.
- **Disk safety**: Enforce sanitized paths, hashing for dedupe, locks to avoid simultaneous writers corrupting artefacts.
- **Performance**: Controlled parallelism respecting GPU saturation and UI responsiveness budgets.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Monolithic FastAPI + HTMX (no Electron for MVP backend) | Minimizes moving parts vs SDD exclusions | — Pending implementation |
| faster-whisper + CUDA `large-v3` MVP default | Highest quality-cost trade on local GPU | — Pending implementation |
| Filesystem-backed canonical tree + SQLite metadata mirrors | Transparent recovery + aligns with backlog migration story | — Pending implementation |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. Is “What This Is” still accurate? → Update when reality drifts

**After each milestone** (via `/gsd-complete-milestone`):

1. Full section review against shipped behaviour
2. Core Value sanity check versus user feedback/time saved
3. Audit Out-of-Scope reasons plus backlog contenders
4. Refresh Context around hardware/OS lessons learned

---

*Last updated: 2026-05-17 after project initialization*
