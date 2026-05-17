# Plan 01-02 Summary — Hierarchy REST + HTMX UI shell

Executed: 2026-05-17

## Outcomes

- JSON API: `/api/cursos` (GET/POST/PATCH/DELETE) and `/api/disciplinas` (GET query `curso_id`, POST/PATCH/DELETE) wired through `HierarchyService` with 404/409 mapping.
- HTML: dashboard (`GET /`), per-course discipline list (`GET /cursos/{id}`), discipline detail skeleton with tabs **Originais · Processados · Processamento** (`GET /cursos/.../disciplinas/{id}`), HTMX partials for row updates.
- Regression tests (`tests/test_health_placeholder.py`) exercise API flow, `/`, `/health`, and Portuguese tab scaffold.

## Verification

- `python -m compileall app`
- `python -m pytest -q`
