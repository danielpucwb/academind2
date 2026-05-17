# Architecture Research

**Domain:** Monolithic workstation service orchestrating ingestion + asynchronous media workers  
**Researched:** 2026-05-17  
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────┐
│             Browser Surface (local HTMX + Tailwind UI)       │
├──────────────────────────────────────────────────────────────┤
│                 FastAPI Application Host                      │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌───────────────┐ │
│  │ Routers   │ │ Services │ │ Job Runner │ │ File Bridge  │ │
│  └──────────┘ └──────────┘ └────────────┘ └───────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                 Worker / Task Layer (threads or asyncio BG) │
│  FFmpeg normalizer ──► faster-whisper engine ─► artifact IO │
└──────────────────────────────────────────────────────────────┘
│ Storage Layout (`storage/cursos/<slug>/<discipline>/…`) │
│ SQLite (metadata, jobs, file fingerprints) │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|---|---|---|
| API routers | Thin HTTP façade + multipart intake | FastAPI routers with dependency-injected settings |
| Service layer | Business rules translating HTTP→disk | Python modules coordinating repositories |
| Repository layer | Persist models + transactional updates | SQLModel CRUD adapters |
| Processor workers | FFmpeg + Whisper + merges | Dedicated modules + subprocess isolation |

## Recommended Project Structure

```
app/
├── api/            # routers grouped by bounded context
├── core/           # settings, lifecycle, locks, logging setup
├── services/       # orchestration workflows (upload ingest, enqueue job)
├── processors/     # media-specific orchestrations (ffmpeg, whisper, pdf)
├── models/         # pydantic/sqlmodel schemas
├── repositories/   # persistence helpers
├── templates/      # jinja/htmx snippets
├── static/         # tailwind bundles, alpine helpers
├── jobs/           # optional queue objects + watchers
└── main.py         # composition root / FastAPI wiring
storage/ ... config/ logs/ ...
```

### Structure Rationale

- **processors/** isolates GPU/long-running concerns from routers to keep latency predictable.
- **services/** expresses user stories (course creation, ingestion, processing kickoff).

## Architectural Patterns

### Pattern 1: Outbox-ish Job Rows

**What:** Persist job intent + deterministic state transitions before spawning subprocesses.  
**When to use:** Any GPU work that can fail mid-flight.  
**Trade-offs:** Requires cleanup tasks but prevents phantom UI success.

### Pattern 2: Filesystem Canonical + DB Mirror

**What:** Paths never guessed ad hoc—computed from hashed slugs anchored in relational graph.  
**When to use:** Personal-scale storage with manual exploration via Explorer.  

### Pattern 3: Watchdog Boundary

**What:** Dedicated supervisor tracking subprocess PIDs/timeouts surfaced to UI log channel.  

## Data Flow

### Upload + Catalog Flow

```
UI multipart posts
 → FastAPI handler streams to storage temp
 → SHA256 + metadata persisted
 → response hydrates dashboard partial
Worker picks job
 → FFmpeg extracts mono PCM
 → faster-whisper writes transcript txt
 → state transitions + zipped export manifest updates
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|---|---|
| Single user local | Threads/async tasks sufficient |
| Household multi-seat | Separate Windows accounts + duplication (future backlog) |

## Anti-Patterns

### Anti-Pattern: GPU Work on Request Threads

Blocking event loop freezes HTMX responsiveness—spawn background tasks/process pools.

### Anti-Pattern: Mutable Shared Paths Strings

Prefer Path objects validated against storage root anchors to kill traversal exploits.

## Integration Points

### External Services

None mandatory for MVP (local execution only).

## Sources

- `sdd.md` architecture blueprint  
- FastAPI layering guidance + HTMX SSR references  

---
*Architecture research for: acadeMIND*  
*Researched: 2026-05-17*
