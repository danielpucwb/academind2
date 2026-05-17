# Phase 4: Document Consolidation — Context

**Gathered:** 2026-05-17  
**Status:** Ready for planning (`/gsd-plan-phase 4`)  
**Sources:** `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` (DOC-01), `sdd.md` §10 concatenação, existing `paths.ensure_discipline_paths` tree.

## Boundary

Produce **`concatenado.pdf`** inside each discipline’s **`processados/pdfs/`** by **deterministically merging all PDF artefacts** originating from originals inventory, ordered **alphabetically by basename** (`sdd.md`: ordem alfabética; drag-reorder deferido).

Fulfill **DOC-01**: tolerant handling of corrupted PDF pages/objects with **actionable surfaced failure** copy (Portuguese UX tone); never emit raw server filesystem paths to clients.

## Dependencies & sequencing risks

Roadmap declares **Depends on: Phase 3** so **JOB concurrency / `processados/` locks** (JOB-02) exist before mutating merges. If execution skips Phase 3, **04-01 must either** (a) land only after **`03-01` lock primitives** ship, **or** (b) temporarily implement an interim **SQLite/file advisory lock** with an explicit deprecation note in PLAN — planner choice documented in **`04-RESEARCH.md`** / **`04-01-PLAN.md`**.

Upstream **catalogue** today (`catalogue_artefact`, bucket `documentos`) is the natural source list for qualifying PDF inputs (`stored_relative_path` / `original_filename`; filter `mime`/`suffix` ≡ `pdf`).

## Locked decisions (`04-RESEARCH` may refine)

| ID | Decision |
|----|-----------|
| D-PDF-LIB | `pypdf` (per STACK + SDD) for merge; avoid shelling out GUI tools |
| D-OUTPUT | Canonical filename **`concatenado.pdf`** fixed under `processados/pdfs/` (overwrite or version policy in PLAN) |
| D-PATHSAFE | Writes validated with same `paths.assert_resolved_under_anchor`/`discipline_tree_root` discipline as ingestion |
| D-UX-HOME | Surfaced predominantly on **`Processados`** tab with HTMX-triggered merge + structured JSON response |
| D-BRAND | acadeMIND-only copy; Projekt-token styling parity deferred to Phase 5 hardening |

## Out of scope (Phase 5+)

ZIP export embedding merge, guarded streaming download (**PKG**), audit OBS-03 stubs, drag-to-reorder PDF list before merge.

## Canonical refs

- `.planning/ROADMAP.md` Phase 4 success criteria  
- `sdd.md` §10 Concatenação (library, filename, alphabetical)  
- `app/core/paths.py` (`processados/pdfs/` scaffold)  
- `app/models/catalogue.py`, `app/repositories/catalogue.py`  
