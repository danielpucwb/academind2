<!-- GSD:project-start source:PROJECT.md -->
## Project

**acadeMIND**

**acadeMIND** is a desktop-first application with a responsive local web UI for undergraduate students who want one place to collect, ingest, organize, process, and consolidate academic materials (PDFs, slides, handouts, lecture recordings, audio, exported web captures). Execution is **local on Windows 11**, with optional paths for Docker/PyInstaller later—not required for MVP.

The product pairs a modular **FastAPI + SQLite + HTMX/Tailwind** experience with filesystem-first storage and GPU-accelerated transcription (CUDA / **faster-whisper**) for media-heavy workflows.

**Core Value:** A grad student can point the app at a course and discipline folder, ingest messy sources, kick off deterministic batch processing locally, then download transcripts, concatenated PDFs, and packaged exports—all **without mandatory cloud**.

### Constraints

- **Platform**: Desktop-first Windows 11 local runtime; responsiveness still expected via browser shells.
- **Privacy / connectivity**: Offline-friendly; optional cloud integrations only later.
- **Tech stack alignment**: FastAPI service, SQLModel/Pydantic, SQLite relational store matching SDD schemas, FFmpeg + faster-whisper + PyTorch CUDA + pypdf stack.
- **Disk safety**: Enforce sanitized paths, hashing for dedupe, locks to avoid simultaneous writers corrupting artefacts.
- **Performance**: Controlled parallelism respecting GPU saturation and UI responsiveness budgets.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|---|---|---|---|
| Python | >=3.10 (3.12 LTS wherever possible on Windows dev) | Service + workers | Matches SDD baseline; aligns with Faster-Whisper + FastAPI toolchain |
| FastAPI | 0.115+ | HTTP API + templating glue | Lightweight async API for local HTMX app; predictable dependency injection patterns |
| Uvicorn | 0.30+ | ASGI runtime | Canonical FastAPI pairing; trivial local dev ergonomics (`--reload`) |
| SQLModel | 0.0.22+ OR keep SQLAlchemy/Core if preferred | SQLite ORM-ish models | Faster CRUD authoring with Pydantic alignment; downgrade path to bare SQLAlchemy if friction appears |
| SQLite | 3.45+ bundled | Canonical metadata/job store | Local-only durability; WAL mode avoids writer stalls under UI polling |
| Jinja2 | 3.x | SSR templates feeding HTMX | Native FastAPI templating workflow |
| FFmpeg | Rolling release binaries (prefer `ffmpeg-master-latest-win64`) | Normalize & extract PCM | lingua franca for media decode; offload GPU work to Whisper, not FFmpeg |
| faster-whisper | 1.2.1 (PyPI beta line) | CTranslate2 inference | Faster + lower VRAM footprint vs raw PyTorch Whisper; documented CUDA acceleration path |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---|---|---|---|
| pydantic-settings / PyYAML loader | pydantic-settings 2.x | `config.yaml` parsing | Immediately—configuration drives models, parallelism, uploads |
| torch + torchaudio + CUDA builds | Torch 2.5+ CU124 wheels typical | Whisper dependency / experimentation | Prefer CUDA wheels pinned to toolkit actually installed (`nvidia-smi`) |
| pypdf | 5.x | Deterministic merges | Lightweight merge path for PDF consolidation |
| python-slugify | 8.x | Safe directory names | Enforce deterministic storage slugging aligned with PROJECT.md traversal rules |
| aiofiles | 24.x | Async filesystem IO | Keeps uploads responsive under parallel chunk writes |
| watchdog | optional 4.x | Hung subprocess detection backlog | Tie into OPS watchdog backlog from SDD |
| FFmpeg CLI wrapper (`ffmpeg-python` optional) | 0.2.x OR raw `subprocess` | Deterministic FFmpeg invocations | Use subprocess if wrappers obscure argv construction |
### Development Tools
| Tool | Purpose | Notes |
|---|---|---|
| Ruff | Python lint/format | Faster than flake8+pylfmt combo locally |
| Pytest + httpx.AsyncClient | API tests | Simulate HTMX-heavy flows via ASGI lifespans |
## Installation
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|---|---|---|
| faster-whisper + CTranslate2 | `openai-whisper` GPU | Prefer if you accept heavier VRAM churn or need WhisperX diarization out-of-band |
| Monolithic FastAPI | Separate SPA (React/Vue) | Contradicts SDD MVP speed; revisit if HTMX ergonomics crumble |
| SQLite | DuckDB embedded | Interesting for analytics-heavy pipelines; SQLite plenty for relational scope here |
## What NOT to Use
| Avoid | Why | Use Instead |
|---|---|---|
| Electron-only architecture | Increases footprint vs responsive local web surfaces | FastAPI serving HTMX shells per SDD |
## Stack Patterns by Variant
- Prefer `medium` Faster-Whisper model + `compute_type=int8_float16`; guard UI with degraded-mode banner via `/health`.
- Prefer `medium`/`small`, chunk long audio (>30 min lectures) deterministically prior to Whisper.
## Version Compatibility
| Package A | Compatible With | Notes |
|---|---|---|
| faster-whisper@1.2.1 | `ctranslate2` CUDA wheels pinned by dependency | Installing CPU-only builds quietly kills GPU throughput—confirm `pip show ctranslate2` includes CUDA linkage |
| torch@cu124 | NVIDIA driver ≥ `550.x` typical | Smoke test `torch.cuda.is_available()` on boot |
## Sources
- [https://pypi.org/project/faster-whisper/](https://pypi.org/project/faster-whisper/) — release + Python floor verification  
- PROJECT.md constraints + `.planning/PROJECT.md` — authoritative local-first scope  
- [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/) — async / dependency patterns recap  
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
