# Pitfalls Research

**Domain:** Local media-heavy Python stacks on Windows workstations  
**Researched:** 2026-05-17  
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Blocking the ASGI Loop with Whisper

**What goes wrong:** Transcription dominates event loop threads → UI freezes, uploads stall.  

**Why it happens:** Whisper feels “just another function call” during MVP crunch.  

**How to avoid:** Dedicated worker queue (threads or subprocess) + explicit concurrency caps in `config.yaml`.  

**Warning signs:** Increasing request latency during processing tab activity.  

**Phase to address:** Phase 3 (audio pipeline).

---

### Pitfall 2: Path Traversal via Sloppy Joins

**What goes wrong:** Crafted filenames escape `storage/` roots.  

**Why it happens:** `os.path.join` + unsanitized user strings.  

**How to avoid:** Resolve paths, enforce commonpath with storage root constant, whitelist extensions.  

**Warning signs:** Odd `..` fragments in uploads or zipped exports referencing foreign drives.  

**Phase to address:** Phase 2 (ingestion).

---

### Pitfall 3: FFmpeg Argument Injection

**What goes wrong:** Malicious filenames break CLI quoting or overwrite unintended outputs.  

**Why it happens:** String interpolation into shell vs argv list mishandled on Windows quoting.  

**How to avoid:** Always `subprocess` with argument lists; never shell=True for user-fed names.  

**Warning signs:** Intermittent `Invalid argument` or random file moves.  

**Phase to address:** Phase 3 (audio normalization).

---

### Pitfall 4: Zombie GPU Memory

**What goes wrong:** Model stays resident across runs until process dies → RAM/VRAM starvation.  

**Why it happens:** Global singleton Whisper model reused without teardown strategy.  

**How to avoid:** LRU model handle with explicit unload or dedicated worker process lifespan.  

**Warning signs:** Windows OOM prompts after multiple long lectures.  

**Phase to address:** Phase 3.

---

### Pitfall 5: Silent Partial ZIP Exports

**What goes wrong:** ZIP published before transcripts flush → student downloads stale bundle.  

**Why it happens:** Missing exclusive lock tying export job to prerequisites.  

**How to avoid:** State machine forbids ZIP until dependents `completed`; streaming download uses temp file finalize pattern.  

**Warning signs:** `completed` timestamps misordered vs child artifacts.  

**Phase to address:** Phase 5 (packaging/export).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| SQLite single writer | simplistic | ingestion spikes block | MVP ok if queue serializes intentionally |
| No automated tests GPU path | quicker prototype | regressions unnoticed | Temporary—add smoke tests fast |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|---|---|---|---|
| O(n²) merges for PDF listing | sluggish UI listing hundred files | deterministic ordering + paging | Hundreds of uploads |

## Security Mistakes

| Mistake | Risk | Prevention |
|---|---|---|
| Trusting MIME headers only | disguised payloads | Inspect magic bytes |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---|---|---|
| No ETA on GPU backlog | Anxiety / duplicate clicks | surfaced queue estimates + disables |

## "Looks Done But Isn't" Checklist

- [ ] **Transcripts:** Verified sample audio cross-checked vs manual spot listen  
- [ ] **ZIP:** Hash manifest matches included files  

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---|---|---|
| Corrupt DB | MEDIUM | Replay metadata from filesystem + backup DB snapshot |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---|---|---|
| Event loop blockage | Phase 3 | Simulate parallel UI fetch while transcription runs |

## Sources

- SDD Sections 17 (fingerprint/job queue), 23 NFR backlog  
- Windows GPU ops tribal knowledge  

---
*Pitfalls research for: acadeMIND workstation MVP*  
*Researched: 2026-05-17*
