# Feature Research

**Domain:** Offline academic media consolidation tool for undergrad use  
**Researched:** 2026-05-17  
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---|---|---|---|
| Course + discipline hierarchies | Mental model mirrors school structure | MEDIUM | Backbone for storage partitioning + dashboards |
| Multi-file ingestion with sane validation | Lecture dumps are bursts of heterogeneous files | MEDIUM | Extension allowlisting + hashing per SDD |
| Deterministic uploads + retries | Huge files + flaky laptops | MEDIUM | Atomic temp writes + chunked uploads later |
| Clear processing statuses | Confidence that GPU hours aren’t silently burning | MEDIUM | States `pending→processing→completed/failed`, UI tab |
| Recoverable pipelines | Overnight jobs crash occasionally | MEDIUM | Job ledger + watchdog + simplistic retry knobs |
| Local exports | Students must hand artifacts to notebooks / LMS | MEDIUM | ZIP packaging with metadata manifests |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| GPU-accelerated transcription without cloud | Sensitive lecture audio stays local yet searchable text emerges | HIGH | Differentiator flagged in PROJECT.md RTX storyline |
| Document fusion (merged PDF bundles) | One artifact for cramming alongside lecture text | MEDIUM | Alphabetical merges now—manual ordering backlog |
| HTMX responsiveness without SPA weight | Faster iteration aligned with MVP | MEDIUM | Aligns architecture with SDD stack |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---|---|---|---|
| Omni-format auto-OCR universal parser | Dreams of OCR everything | Complexity explosion + licensing | Deferred backlog per SDD |
| Full-text semantic search indexing | Desire for Spotlight-like recall | Embedding infra + UX heavy | Deferred local RAG stack |
| Real-time autosync/cloud backup | Convenience | Contradicts “no mandatory cloud unless opt-in backlog” | Optional future connectors |

## Feature Dependencies

```
[Course Hierarchy]
    └──requires──> [Filesystem Layout Contracts]
                           └──requires──> [Upload + hashing]

[GPU Transcription]
    └──requires──> [FFmpeg Normalize + WAV path]
                           └──requires──> [Jobs + locking]

[Merged PDF]
    └──requires──> [Doc uploads cataloged]

[ZIP Export]
    └──requires──> [Merged PDF + transcripts + originals listing]
                           └──requires──> [Download routes + streaming safeguards]
```

### Dependency Notes

- **Transcription depends on ingestion metadata** otherwise workers cannot correlate outputs.
- **ZIP export anchors on job completion** sequencing must never race partial writes—locks matter.

## MVP Definition

### Launch With (v1)

- [ ] Hierarchy CRUD powering storage roots  
- [ ] Upload + hashing + sanitized paths  
- [ ] FFmpeg normalization + Faster-Whisper transcription path with GPU-aware config  
- [ ] PDF merges + zipped export payloads  
- [ ] Processing tab with queue visibility + bounded parallelism controls  

### Add After Validation (v1.x)

- [ ] Manual ordering for merges + playlists per discipline  
- [ ] Rich dashboards for historical runs / diff transcripts  

### Future Consideration (v2+)

- [ ] OCR, semantic retrieval, notebooks integration per SDD backlog  

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Hierarchy + ingestion | HIGH | MEDIUM | P1 |
| Secure downloads | HIGH | LOW | P1 |
| GPU transcription pipeline | HIGH | HIGH | P1 |
| Logs + watchdog | MEDIUM | MEDIUM | P2 |
| Merge + ZIP | HIGH | MEDIUM | P1 |

## Competitor Feature Analysis

| Feature | Notion/Zotero | Generic desktop scrapers | Our Approach |
|---|---|---|---|
| Hierarchy | Workspace oriented | Loose folders | Opinionated slugged tree + mirrored DB |

## Sources

- `.planning/PROJECT.md`, `sdd.md` backlog sections  
- User workflow interviews implicit in PROJECT.md personas  

---
*Feature research for: acadeMIND workstation MVP*  
*Researched: 2026-05-17*
