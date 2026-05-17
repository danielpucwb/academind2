# Roadmap: acadeMIND

## Overview

Ship a vertically sliced workstation app: scaffolding + trusted ingestion first, deterministic GPU-backed media pipelines next, consolidate academic PDF artefacts, finish with zipped exports plus polished HTMX ergonomics—all aligned with the five MVP arcs captured in PROJECT.md/`sdd.md`.

## Phases

- [x] **Phase 1: Domain Shell & Foundations** — Courses/disciplines, configuration, `/health`, tabbed UX skeleton, foundational APIs.
- [x] **Phase 2: Trusted Ingestion & Catalog Backbone** — Multipart uploads, fingerprints, sanitized storage tree, originals UX, observability scaffolding.
- [ ] **Phase 3: Audio Normalization + GPU Whisper** — FFmpeg normalization, Faster-Whisper CUDA path with watchdog + queue visibility.
- [x] **Phase 4: Document Consolidation** — Deterministic alphabetical PDF merges surfaced in Processados.
- [ ] **Phase 5: Export Bundles + UX Completion** — ZIP exports, guarded downloads/reprocess tooling, Projekt-token styling without Projekt branding, audit logging.

## Phase Details

### Phase 1: Domain Shell & Foundations
**Goal**: Users can carve out courses/disciplines with deterministic anchors while devs inherit config + `/health` signals before heavy media enters the system.

**Mode:** mvp

**UI hint**: yes

**Depends on**: Nothing

**Requirements**: ORG-01, ORG-02, ORG-03, ORG-04, ORG-05, WEB-01, WEB-02, API-01, API-02, API-06, CFG-01

**Success Criteria**:
1. User can create/delete/rename (where allowed) course + discipline tuples that immediately materialize sanitized storage directories.
2. Dashboard lists courses with navigation depth at least course → discipline.
3. Visiting a discipline exposes the three IA tabs scaffolded (`Originais`, `Processados`, `Processamento`) even before those surfaces are populated.
4. `/health` returns structured JSON signalling SQLite readiness + FFmpeg binary probing + Whisper lazy-load sentinel.
5. `config.yaml` values load at startup and fail fast when required knobs are malformed.

**Plans**: 3 plans

Plans:

- [x] 01-01: Repository layout + SQLite schema bootstrap for hierarchy models.
- [x] 01-02: Router surface for hierarchy CRUD + HTMX stubs for dashboard/discipline shells.
- [x] 01-03: Config loader + observability scaffolding + `/health` composition.

---

### Phase 2: Trusted Ingestion & Catalog Backbone
**Goal**: Burst uploads funnel into deterministic originals buckets with fingerprints, guarding traversal + extension misuse.

**Mode:** mvp

**Depends on**: Phase 1

**Requirements**: UPL-01, UPL-02, UPL-03, UPL-04, UPL-05, API-03, JOB-01, OBS-01, WEB-03

**Success Criteria**:
1. User drags heterogeneous accepted files onto `Originais`, sees immediate validation feedback for rejects.
2. Duplicate SHA256 payloads short-circuit with friendly messaging.
3. Artefacts enumerate with actionable download/delete hooks without leaking unsanitized raw paths externally.
4. Job ledger rows persist with `pending` states even before FFmpeg touches data.
5. Upload/API logs include correlation identifiers referencing job identifiers.

**Plans**: 3 plans (waves **2a/2b/2c →** `02-01`/`02-02`/`02-03` in [.planning/phases/02-trusted-ingestion-catalog-backbone/](.planning/phases/02-trusted-ingestion-catalog-backbone/)

Plans:

- [x] 02-01: Multipart ingestion service + chunked temp handling + hashing pipeline. *(wave **2a** shipped)*
- [x] 02-02: Originals partials + JOB row lifecycle writes + OBS-01 log sink. *(wave **2b** shipped)*
- [x] 02-03: Frontend drag/drop affordances tying into HTMX progress placeholders. *(wave **2c** shipped)*

---

### Phase 3: Audio Normalization + GPU Whisper
**Goal**: Controlled subprocess pipeline feeds Faster-Whisper with CUDA safeguards, surfaced through Processing tab fidelity.

**Mode:** mvp

**Depends on**: Phase 2

**Requirements**: AUD-01, AUD-02, TRN-01, TRN-02, TRN-03, TRN-04, JOB-02, JOB-03, JOB-04, API-04, OBS-02, WEB-04

**Success Criteria**:
1. User presses “Process discipline” enqueueing deterministic jobs rather than saturating FastAPI threads.
2. FFmpeg invocations normalize supported media artifacts into Whisper-friendly WAVs using argv-array subprocesses logged to structured files.
3. Successful runs emit transcripts under `processados/transcricoes/` with deterministic naming + DB references.
4. GPU degrade path notifies operator via Processing tab cues when CUDA unavailable/warmup fails while still allowing deterministic failure records.
5. Watchdog terminates hung subprocess storms and marks jobs failed with explanatory diagnostics.

**Plans**: TBD

Plans:

- [ ] 03-01: Worker harness + concurrency locks guarding `processados/`.
- [ ] 03-02: FFmpeg + Whisper processors with configuration-driven model selection defaults (`large-v3`).
- [ ] 03-03: Processing UI stream (queue snapshot + log excerpts) powered by JOB states.

---

### Phase 4: Document Consolidation
**Goal**: Alphabetical merges of PDF artefacts generate `concatenado.pdf`, visible as a first-class artefact.

**Mode:** mvp

**Depends on**: Phase 3 *(merge shipped with interim `MergeLock`; replace with JOB-02 row lock when **`03-01`** executes)* 

**Requirements**: DOC-01

**Success Criteria**:
1. User taps merge action referencing current originals inventory and receives surfaced success/failure with explicit corrupt-page messaging.
2. Processados tab previews merged PDF linkage once produced.
3. Merge operation honours concurrency locks inherited from JOB subsystem.

**Plans**: 1 plan — [`04-document-consolidation`](.planning/phases/04-document-consolidation/)

Plans:

- [x] 04-01: `pypdf` merge orchestration + deterministic output pathing + failure telemetry.

---

### Phase 5: Export Bundles + UX Completion
**Goal**: Downloads + zipped exports land with streaming safety, branding alignment, rerun hygiene, auditing.

**Mode:** mvp

**Depends on**: Phase 4

**Requirements**: PKG-01, PKG-02, API-05, WEB-05, WEB-06, WEB-07, JOB-05, OBS-03

**Success Criteria**:
1. ZIP bundles include originals, transcripts, merges, manifests with stable checksum references.
2. Individual downloads streams cannot escape storage root through crafted IDs nor leak unsanitized server paths via error messages.
3. Processados tab surfaces artefacts with staleness indicators + regen cues.
4. Toasts/snackbars communicate UX outcomes without freezing HTMX swaps.
5. Visual tokens mimic `projekt-design-system.html` alignment while enforcing acadeMIND-only branding/copy.
6. Destructive download/delete operations emit OBS-03 audit stubs for local forensic recovery.

**Plans**: TBD

Plans:

- [ ] 05-01: ZIP builder + checksum manifest + guarded streaming responses.
- [ ] 05-02: Frontend polish hooks (toast system, Projekt-token styling overlays, rerun flows).
- [ ] 05-03: Operational hardening (audit logging, rerun dedupe safeguards).

---

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Domain Shell & Foundations | 3/3 | Complete | Phase 1 |
| 2. Trusted Ingestion Backbone | 3/3 | Complete · **02-01 … 02-03** | Phase 2 |
| 3. Audio Normalize + Whisper | 0/3 | Not started | — |
| 4. Document Consolidation | 1/1 | Complete · **04-01** | Phase 4 |
| 5. Export + UX Completion | 0/3 | Not started | — |
