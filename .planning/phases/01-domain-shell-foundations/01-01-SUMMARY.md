# Plan 01-01 Summary — Repository layout & hierarchy persistence

Executed: 2026-05-17

## Outcomes

- Python package scaffold under `app/` with SQLModel-backed `Course` and `Discipline` tables (UUID PKs, slug constraints, timestamps).
- `HierarchyService` implements create/rename/delete with slug uniqueness and filesystem sync under configurable `storage_root`; rename blocked when scaffolded trees contain files.
- `PROJECT_ROOT` in `app/core/paths.py` corrected to repository root (`parents[2]`) so `config.defaults.yaml` and SQLite paths resolve next to the repo, not under `app/`.

## Verification

- `python -m compileall app`
