# Walking Skeleton — acadeMIND

**Phase:** 1  
**Generated:** 2026-05-17

## Capability Proven End-to-End

Operator runs `uvicorn app.main:app --reload`, opens the dashboard in a browser, **creates a course and discipline**, sees three placeholder tabs under the discipline, and hits `/health` receiving JSON proving SQLite connectivity plus FFmpeg probe state—persisted rows and scaffolded directories mirror metadata.

## Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI + Starlette templating | Core stack mandated by PROJECT.md / SDD |
| Data layer | SQLModel + SQLite WAL | Minimal ops overhead for workstation deployment |
| UI transport | SSR Jinja partials + HTMX | Ships skeleton without SPA build pipeline |
| Config | YAML + pydantic validators | Mirrors SDD `config.yaml` story |
| Storage coupling | Service layer merges DB + pathlib | Keeps traversal guards centralized |

## Stack Touched in Phase 1

- [ ] Project scaffold (dependencies, package layout)
- [ ] Routing — `/`, `/disciplinas/{id}`, API routers
- [ ] Database — SQLModel definitions + CRUD exercised via routes
- [ ] UI — forms + tabs (static shells) triggering real writes
- [ ] Ops — `/health`, structured logging stubs, FFmpeg probe

## Out of Scope (Deferred to Later Slices)

- File ingestion, hashing, FFmpeg media transforms, Whisper, PDF merges, ZIP exports
- AuthN/Z (single-user implicit trust localhost)
- Production packaging (Docker/PyInstaller)

## Subsequent Slice Plan

- Phase 2: Burst uploads + catalog + originals UX  
- Phase 3: FFmpeg + Faster-Whisper pipeline + job queue fidelity  
- Phase 4: PDF merge surfaced in Processados  
- Phase 5: ZIP packaging + UX polish + audit logging  
