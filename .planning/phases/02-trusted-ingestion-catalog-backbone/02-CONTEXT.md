# Phase 2: Trusted Ingestion & Catalog Backbone — Context

**Gathered:** 2026-05-17  
**Status:** Ready for planning wave **2a** (plan **02-01**)  
**Source:** `.planning/ROADMAP.md`, `.phase` split per roadmap bullets; Discuss-phase skipped (`workflow.discuss_mode`).

## Naming: “Phase 2a”

`/gsd-plan-phase 2a` is interpreted as **Phase 2, Wave A**, matching roadmap item **02-01** (backend ingestion + hashing + safe storage wiring). Waves **02-02** and **02-03** remain sequential follow-ups (`2b`, `2c`) and have their own PLAN stubs in this folder.

## Domain boundary (full Phase 2)

Burst **multipart uploads** land under each discipline’s `originais/{documentos|videos|audios|web}` tree per SDD taxonomy, with:

- Extension allow-list (`allowed_extensions`) and MIME sanity checks (**UPL-02**).
- **SHA256** computed during streaming ingestion; duplicates short-circuit with clear feedback (**UPL-03**).
- Paths resolved only under `storage/cursos/<course-slug>/<discipline-slug>/` with sanitized filenames — no traversal escapes (**UPL-04**).
- **API-03**: HTTP surface places bytes in the correct subtree by category convention.
- **JOB-01**, **OBS-01**, **UPL-05**, **WEB-03**: scheduled in waves **02-02 / 02-03** (catalog UI, job ledger wiring, correlation logging, HTMX UX).

Depends on Phase 1: `HierarchyService`, `ensure_discipline_paths`, existing course/discipline FK graph.

## Wave 2a (02-01) scope fence

Implement **persisted catalogue rows + ingestion pipeline + POST upload API**.  
**Out of scope for 02-01:** originals HTMX partials (**02-02**/**03**), full JOB lifecycle UI, OBS-structured upload.log correlators (**02-02**), drag/drop progress chrome (**03**).  
**Allowed overlap:** Minimal `jobs` row insert on upload is optional; if omitted, JOB-01 is satisfied exclusively in **02-02**.

## Locked / inherited decisions

| ID | Decision |
|----|----------|
| D-STACK | FastAPI + SQLModel SQLite + Jinja HTMX retained from Phase 1 |
| D-STORAGE | Physical tree mirrors `paths.ensure_discipline_paths`; uploads never write outside resolved `discipline_tree_root(...).resolve()` |
| D-HASH | SHA256 of raw bytes streamed from client; uniqueness scoped per `(disciplina_id, sha256)` |
| D-NAME | Store original filename for display separately from on-disk sanitized name |
| D-MVP-2a | Prefer synchronous service called from FastAPI endpoint with chunked reads; aiofiles acceptable if wired consistently |

## Claude discretion

Exact on-disk naming (`{slug}_{suffix}` vs partial hash prefix); temp file strategy (`tempfile.SpooledTemporaryFile` vs write to `.part` then rename).

## Canonical refs

- `.planning/ROADMAP.md` — Phase 2 success criteria  
- `.planning/REQUIREMENTS.md` — UPL-*, API-03, JOB-01, OBS-01, WEB-03  
- `sdd.md` — §13 upload, §17 fingerprints, originals tree  
- `app/core/paths.py`, `app/services/hierarchy_service.py`  
