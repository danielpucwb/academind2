# Phase 1: Domain Shell & Foundations — Context

**Gathered:** 2026-05-17  
**Status:** Ready for planning  
**Source:** Synthesized from `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md` (discuss-phase skipped; `.planning/config.json` has `workflow.discuss_mode: discuss`)

<domain>

## Phase Boundary

Deliver the **walking skeleton**: FastAPI hosts HTMX-rendered CRUD over **courses** and **disciplines** persisted in SQLite, with deterministic `storage/cursos/<course-slug>/<discipline-slug>/` subtree creation/removal guarded by transactional rules; `config.yaml` loads at startup; `/health` reports DB + FFmpeg presence + Whisper engine readiness sentinel (lazy, no mandatory model download in Phase 1). Three UX tabs (**Originais**, **Processados**, **Processamento**) exist per discipline as shells with copy in Portuguese per SDD; future phases fill behaviour.

Success criteria derive from `.planning/ROADMAP.md` Phase 1 block.

</domain>

<decisions>

## Locked Technical Decisions

| ID | Decision | Notes |
|----|----------|-------|
| D-STACK | FastAPI + Uvicorn + Jinja2 + HTMX + Tailwind CDN (compile later) | Matches PROJECT.md stack; CDN acceptable for skeleton |
| D-ORM | SQLModel atop SQLite WAL file `database/academind.db` (path configurable) | Mirrors SDD schemas (UUID pk, timestamps) |
| D-SLUG | `python-slugify` for filesystem segments; disallow slug mutation once children exist unless explicit tooling defers rename to backlog | Implements ORG-02 guardrail |
| D-CONFIG | `config.yaml` at repo root (or configurable path via env default) validated by Pydantic model; fail-fast on malformed required keys | CFG-01 |
| D-HEALTH | Structured JSON `{ "status": "ok|degraded", "sqlite": bool, "ffmpeg": bool, "whisper_cuda": null|bool }`; Whisper probe only checks `torch.cuda.is_available()` OR config flag — **does not download weights** during `/health` | Phase 1 scope |
| D-UI-NAMES | Tabs labeled **Originais / Processados / Processamento**; surround copy PT-BR per `sdd.md` | WEB-02 |
| D-BRAND | Typography/spacing loosely follows [`projekt-design-system.html`](../../../projekt-design-system.html) tokens manually (no Projekt branded strings) | WEB-07 partial polish lands Phase 5 |

## Claude Discretion

- Exact Tailwind utility choices and HTMX swapping patterns (`hx-target` granularity).
- Minimal error toast implementation (could be `<div role="alert">` swap) pending Phase 5 polish.

</decisions>

<canonical_refs>

- `.planning/ROADMAP.md` — Phase 1 goal, reqs, success criteria  
- `.planning/REQUIREMENTS.md` — ORG/API/CFG/WEN trace rows  
- `sdd.md` — API sketches + folder taxonomy  
- `.planning/research/STACK.md` — pinned library guidance  

</canonical_refs>

<code_context>

Greenfield repo — Phase 1 introduces `app/` tree and packaging files; no incumbent modules to reconcile.

 Intended layout:

```
app/
├── main.py           # FastAPI factory + routers include + static/templates mount
├── core/
│   ├── config.py      # YamlSettings loader
│   ├── db.py          # Engine + SessionLocal + get_session
│   └── paths.py       # sanitize + storage root resolver
├── models/
│   └── hierarchy.py   # SQLModel Course, Discipline
├── repositories/
│   └── hierarchy.py   # CRUD + cascade delete safeguards
├── services/
│   └── hierarchy_service.py  # orchestrates repos + pathlib mkdir/rmtree guarded
├── api/
│   └── routes courses.py disciplines.py (+ __init__)
├── templates/         # base.html dashboard.html discipline.html fragments
├── static/            # placeholder CSS helpers
└── __init__.py
```

</code_context>

<specifics>

- Delete course/discipline cascades filesystem cleanup only after SQLite transaction succeeds.  
- `GET /` redirects or renders dashboard listing courses (`WEB-01`).  
- Provide HTML forms posting to FastAPI endpoints using `multipart/form-data` not required this phase aside from ordinary `application/x-www-form-urlencoded`.  
- Log startup configuration errors to stderr AND fail import of app if YAML invalid (**fail fast**).

</specifics>

<deferred>

- Upload pipeline, hashing, FFmpeg processing, Whisper runs (later phases per ROADMAP).  
- Formal Alembic migrations if team prefers migrate-after-skeleton (`create_all` acceptable walking skeleton).

</deferred>
