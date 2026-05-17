from __future__ import annotations

from pathlib import Path

# Repository root (parent of `app/`), not the `app` package dir.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def discipline_tree_root(course_slug: str, discipline_slug: str, storage_root: Path) -> Path:
    """storage_root + course_slug + discipline_slug."""
    root = Path(storage_root)
    safe_course = sanitize_segment(course_slug)
    safe_disc = sanitize_segment(discipline_slug)
    return (root / safe_course / safe_disc).resolve()


def ensure_discipline_paths(course_slug: str, discipline_slug: str, storage_root: Path) -> Path:
    """
    Ensure SDD folder scaffolding under discipline root.
    Returns resolved discipline root path.
    """
    base = discipline_tree_root(course_slug, discipline_slug, storage_root)
    dirs = [
        base / "originais" / "documentos",
        base / "originais" / "videos",
        base / "originais" / "audios",
        base / "originais" / "web",
        base / "processados" / "transcricoes",
        base / "processados" / "pdfs",
        base / "processados" / "exports",
        base / "metadata",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    return base


def sanitize_segment(seg: str) -> str:
    if not seg or not seg.strip():
        raise ValueError("empty slug segment")
    # slugify already normalized in service layer; forbid traversal
    p = Path(seg)
    if p.name != seg or seg in (".", ".."):
        raise ValueError("invalid path segment")
    return seg


def course_dir(course_slug: str, storage_root: Path) -> Path:
    safe = sanitize_segment(course_slug)
    path = (Path(storage_root).resolve() / safe).resolve()
    root_resolved = Path(storage_root).resolve()
    try:
        path.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("path escapes storage_root") from exc
    return path


def mkdir_course(course_slug: str, storage_root: Path) -> Path:
    """Create filesystem anchor for course (directories for future discipline children)."""
    d = course_dir(course_slug, storage_root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def rm_tree_safe(path: Path) -> None:
    import shutil

    if path.exists():
        shutil.rmtree(path, ignore_errors=False)


def assert_resolved_under_anchor(path: Path, anchor: Path) -> None:
    """Raise ValueError when path resolves outside anchor (filesystem traversal guard)."""
    rp = path.resolve()
    ra = anchor.resolve()
    try:
        rp.relative_to(ra)
    except ValueError as exc:
        raise ValueError(f"Resolved path escapes anchor: {path}") from exc


def directory_has_files(path: Path) -> bool:
    """True if subtree contains any file (not merely empty dirs)."""
    if not path.exists():
        return False
    return any(p.is_file() for p in path.rglob("*"))
