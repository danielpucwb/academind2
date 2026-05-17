# Project Research Summary

**Project:** acadeMIND  
**Domain:** Local workstation academic ingestion + GPU transcription tooling  
**Researched:** 2026-05-17  
**Confidence:** HIGH

## Executive Summary

acadeMIND is best implemented as a **modular FastAPI monolith** with an HTMX-rendered responsive UI backed by SQLite for metadata/job orchestration while large binaries live under a deterministic `storage/` tree. Research reaffirms Faster-Whisper + FFmpeg as the pragmatic pair for NVIDIA-class GPUs paired with guarded subprocess orchestration patterns and explicit job queues to shield the Async event loop.

The roadmap should prioritize **trusted ingestion + bookkeeping** ahead of heavyweight GPU workloads, then layering document consolidation/export after transcripts exist — matching both dependency reality and undergrad mental models reflected in PROJECT.md.

## Key Findings

### Recommended Stack

Python 3.10+ with FastAPI/Uvicorn, SQLite via SQLModel, FFmpeg CLI, **faster-whisper 1.2.1** with CUDA-aligned PyTorch wheels, and deterministic PDF merges via **pypdf**. Install-time smoke tests MUST confirm CUDA availability paths per `.planning/research/STACK.md`.

### Expected Features

**Must have**

- Opinionated academics hierarchy + sanitized storage mapping  
- Multi-type uploads + fingerprinting/trust safeguards  
- Job ledger with explicit states & watchdog-friendly logs  
- GPU transcription pipelines with graceful CPU fallback knobs  
- Merged scholarly PDF exports + zipped download bundles feeding HTMX UI tabs  

**Should have**

- Resilient FFmpeg argument discipline + zipped export manifests mirroring originals  

**Defer**

- OCR, embeddings, integrations — explicit backlog anchors in PROJECT.md  

### Architecture Approach

Monolith layering with dedicated **processors/** isolating GPU/long subprocess work from HTTP routers. Job rows act as deterministic state machines guarding packaging steps.

### Critical Pitfalls

1. **Blocking event loop via Whisper** — queue + worker pools (Phase 3).  
2. **Traversal / injection via filenames + FFmpeg quoting** — path resolve + argv lists (Phase 2-3).  
3. **Premature ZIP finalization** — strict job gating tying exports to completed dependents (Phase 5).  

## Implications for Roadmap

### Phase 1: Foundations + Structure

Aligns repos + scaffolding, `/health`, config ingestion, foundational models/routes powering empty UI shell.

### Phase 2: Ingestion + Catalog Backbone

Fingerprints uploads, enforces MIME/extension rules, manifests storage tree mirrored in DB — unlocks deterministic paths for later pipelines.

### Phase 3: Media Processing Core

Introduce FFmpeg normalization + Faster-Whisper GPU path integrated with concurrency caps + watchdog logging.

### Phase 4: Document Consolidation

Deterministic alphabetical merges referencing `pypdf`, bridging processed vs originals metadata.

### Phase 5: Export Bundles & UX Finish

Finalize ZIP payloads + polishing HTMX ergonomics incl. guarded re-processing controls flagged in PROJECT.md backlog.

### Research Flags

- **Phase 3:** Validate CUDA/driver pairing on target RTX workstation early (sparse failure logs otherwise).  

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Stack | HIGH | Anchored externally via PyPI Faster-Whisper release date |
| Features | MEDIUM-HIGH | Grounded heavily in authoritative SDD/PROJECT narratives |
| Architecture | MEDIUM-HIGH | Standard patterns tuned for workstation scope |
| Pitfalls | MEDIUM | GPU drivers + Windows quirks need device-specific smoke tests |

**Overall:** HIGH operational guidance assuming hardware smoke tests precede Phase 3 execution gates.

### Gaps to Address

- Precise FFmpeg build channel on Windows CI vs dev machine divergence—validate hashing with actual lecture samples in `/gsd-discuss-phase` before coding assumptions.

## Sources

Primary: Faster-Whisper PyPI manifest; FastAPI docs; PROJECT.md/Summary SDD ingestion.

Secondary: Institutional knowledge summarized in PROJECT.md Constraints.

---

*Research completed: 2026-05-17*  
*Ready for roadmap: yes*
