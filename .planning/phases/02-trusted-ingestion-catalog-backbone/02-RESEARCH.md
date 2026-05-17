# Phase 2 — Research memo (trust ingestion spine)

**Researched:** 2026-05-17 (inline synthesizer — no detached researcher agent run)  
**Confidence:** MEDIUM-HIGH vs SDD + Phase 1 code

## 1. Multipart ingestion (FastAPI)

- `UploadFile.file` exposes sync spooled temp; **`read(size)` loops** hash + write without loading whole file (**UPL-01** chunked-friendly semantics).
- `python-multipart` already depended; cap body via Starlette **`max_upload_size`** on route or configurable limit enforced while streaming (**CFG-01** gap: add `max_upload_bytes` default in YAML).
- Reject uploads when total size exceeds cap mid-stream OR pre-check `Content-Length` when present (**defense-in-depth**).

## 2. Streaming SHA256 + duplicate detection

- `hashlib.sha256()` updated per chunk → single digest at end (**sdd §17**).
- DB constraint: `UNIQUE(discipline_id, sha256)` on catalogue table; IntegrityError mapped to HTTP **409** with PT-BR message “já existe”.

## 3. MIME / extension routing

Canonical bucket by **normalized extension first** (`pdf`→documentos, `mp4`→videos, `mp3|wav|m4a`→audios, `html|mhtml`→web, `txt|docx`→documentos) aligned with **`originais/` subtrees created in Phase 1**.  
Fallback: sniff `UploadFile.content_type`; if conflicts with extension, prefer **reject** unless both align (safer anti-confusion).

## 4. Path safety

- Join only under `(discipline resolved root / "originais" / bucket / sanitized_filename)`.  
- After resolve, **`path.relative_to(discipline_root)`** guard (same spirit as `_abs_under_project` in config loader).

## 5. Storage vs JOB/OBS splits

- **02-01** focuses artefacts table + ingestion; JOB insert “ingestion_ack” optional stub.  
- **02-02** links OBS-01 (**upload.log** / structured logging) + enumerating partials (**UPL-05** groundwork).  

## 6. Test strategy

- `TestClient` multipart `files=[("files", (...))]` with temp tiny payload; monkeypatch **`PROJECT_ROOT`** like Phase 1 tests.  
- Assert DB row exists, duplicate second POST returns conflict, rejects bad extension **`422`**.
