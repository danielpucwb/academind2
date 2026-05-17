# Phase 1 Technical Research — Domain Shell

**Phase:** 1 · Domain Shell & Foundations  
**Researched:** 2026-05-17  
**Status:** Complete

## Findings

1. **SQLite + concurrency:** WAL mode (`PRAGMA journal_mode=WAL`) keeps UI reads responsive while writes commit hierarchy mutations; adequate for single-user workstation MVP.
2. **FastAPI lifespan:** Prefer creating tables in `lifespan` startup hook or dedicated `init_db()` invoked once to avoid circular imports vs tests.
3. **Slug safety:** Combining `slugify(max_length=...)` plus regex allowlist `[a-z0-9\-]+` stops Windows path quirks; refuse empty slug output.
4. **HTMX CRUD UX:** Patterns: `hx-post` form -> return `HX-Redirect` or `hx-swap` partial templates; optimistic UI deferred.
5. **FFmpeg probing:** Use `subprocess.run(["ffmpeg","-version"], capture_output=True, timeout=5)` during `/health` only (not every request).
6. **Torch CUDA sentinel:** Lazy import inside health handler catching `ImportError`; if Torch absent treat `whisper_cuda: null`; if present evaluate `torch.cuda.is_available()` without initializing Whisper weights.

## Implications for Plans

Plans 01-01 isolate persistence; 01-02 adds HTTP/HTML surfaces; 01-03 fuses operational config + health diagnostics + storage directory enforcement hooks.

## RESEARCH COMPLETE
