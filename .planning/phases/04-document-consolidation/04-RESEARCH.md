# Phase 4 — Research memo (`pypdf` merge spine)

**Researched:** 2026-05-17 (inline; no spawned researcher agent)  
**Confidence:** MEDIUM-HIGH for MVP merge; MEDIUM on corrupt-page fidelity until spike.

## Ordering

- Stable **Unicode case-insensitive sort** (`str.casefold` on **`original_filename`**, tie-break SHA256 hex) aligns “alfabética” UX without slug surprises.
- Filter inputs: **`bucket == documentos`** (or MIME `application/pdf`) **and** `stored_relative_path` prefix `originais/documentos/`.

## Merge mechanics (`pypdf` ≥5.x)

- `PdfWriter`/`PdfReader`; append pages sequentially; decrypt only if trivial user-password backlog (MVP **reject encrypted** PDFs with clear PT-BR error).
- **Corrupt fragments:** wrap per-document open in try/except; optional **per-page extraction** catching `PdfReadError`, collecting `(filename, page_index, repr)` summaries for JSON + UI snippet (caps list length).

## Atomicity & failure modes

1. Emit to **`processados/pdfs/concatenado.pdf.tmp-<uuid>`** then `os.replace` → final **`concatenado.pdf`**.  
2. On total failure delete temp; preserve previous **`concatenado.pdf`**.  
3. MVP default **all-or-nothing** merge; surfaced diagnostics over silent truncation (DOC-01).

## Concurrency (`JOB-02`)

Preferred: lock façade from **`03-01`**. Interim shim: **`portalocker`** discipline lock file OR SQLite advisory semantics — PLAN spells removal once Phase 3 lock ships.

## API surface sketches

| Endpoint | Verb | Notes |
|----------|-----|-------|
| `/api/disciplinas/{discipline_id}/merge-pdfs` | `POST` | Idempotent rerun overwrites deterministic output |
| SSR / HTMX | `POST` | Button on **Processados** mirrors API + partial swap |

Structured JSON **`{ ok, artefact {…}, diagnostics[] }`** without leaking absolute filesystem paths — align with ingest envelope idioms (`stored_relative_path` only).

## Test vectors

Checked-in **minimal valid PDF** blobs under **`tests/fixtures/pdfs/`**; corruption via truncation/truncated xref fixtures.
