from __future__ import annotations

import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setattr("app.core.paths.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("app.core.config.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("app.core.config.DEFAULTS_PATH", tmp_path / "config.defaults.yaml")
    monkeypatch.setattr("app.core.config.USER_CONFIG_PATH", tmp_path / "config.yaml")
    shutil.copy(REPO_ROOT / "config.defaults.yaml", tmp_path / "config.defaults.yaml")
    with TestClient(create_app()) as c:
        yield c
