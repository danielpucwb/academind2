"""Database session + engine lifecycle."""

from __future__ import annotations

from sqlalchemy import Engine, event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi import Request


def engine_from_sqlite(url: str) -> Engine:
    """Create SQLite engine enabling WAL pragma + foreign keys."""

    kwargs: dict[str, object] = {"future": True}
    if ":memory:" in url:
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = StaticPool
    else:
        kwargs["connect_args"] = {"check_same_thread": False}
    eng = create_engine(url, **kwargs)

    @event.listens_for(eng, "connect")
    def _sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    return eng


def make_engine_from_settings(sqlite_absolute_path) -> Engine:
    from pathlib import Path

    p = Path(sqlite_absolute_path)
    url = f"sqlite+pysqlite:///{p.as_posix()}"
    return engine_from_sqlite(url)


def make_memory_engine():
    """Shared-cache in-memory SQLite for tests."""
    return engine_from_sqlite("sqlite+pysqlite:///:memory:?cache=shared")


def init_db(engine: Engine) -> None:
    # Register all SQLModel tables on metadata before create_all.
    import app.models.catalogue as _catalogue  # noqa: F401
    import app.models.hierarchy as _hierarchy  # noqa: F401
    import app.models.jobs as _jobs  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session(request: Request):
    engine: Engine = request.app.state.engine
    with Session(engine, expire_on_commit=False) as session:
        yield session
