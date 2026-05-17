# Phase 1 verification — Domain Shell & Foundations

Date: 2026-05-17

## Commands

```powershell
cd <repo-root>
python -m compileall app
python -m pytest -q
```

Optional manual:

```powershell
uvicorn app.main:app --reload
# browser: http://127.0.0.1:8000/ , http://127.0.0.1:8000/health
```

## Criteria met (walking skeleton)

- Hierarchy persisted in SQLite with slug rules and deterministic storage paths under `storage/cursos/`.
- REST + SSR flows create/list/delete courses and disciplines; discipline page shows Portuguese tab labels scaffold.
- `/health` JSON shape stable offline (FFmpeg absent → `status: degraded` when SQLite OK).
