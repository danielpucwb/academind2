"""Load merged YAML defaults + optional workspace config."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import BaseModel, Field, computed_field, field_validator

from app.core.paths import PROJECT_ROOT


def _abs_under_project(path: Path) -> Path:
    if path.is_absolute():
        resolved = path.resolve()
    else:
        resolved = (PROJECT_ROOT / path).resolve()
    try:
        resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Configured path escapes project root: {path}") from exc
    return resolved


def _before_path_convert(v: Any) -> Path:
    return Path(v)


PathField = Annotated[Path, _before_path_convert]


class SettingsModel(BaseModel):
    sqlite_path: PathField
    storage_root: PathField
    ffmpeg_path: str = Field(default="ffmpeg")
    whisper_model: str = Field(default="large-v3")
    max_parallel_jobs: int = Field(default=2, ge=1)
    logging_dir: PathField | None = None
    max_upload_bytes: int = Field(default=536_870_912, ge=1_048_576)
    upload_chunk_bytes: int = Field(default=1_048_576, ge=4_096, le=16_777_216)
    allowed_extensions: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}

    @field_validator("allowed_extensions")
    @classmethod
    def _non_empty_extensions(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("`allowed_extensions` must be non-empty.")
        norm = sorted({str(x).lstrip(".").lower() for x in v})
        if not norm:
            raise ValueError("`allowed_extensions` invalid after normalization.")
        return norm

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlite_path_abs(self) -> Path:
        return _abs_under_project(self.sqlite_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def storage_root_abs(self) -> Path:
        return _abs_under_project(self.storage_root)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def logging_dir_abs(self) -> Path | None:
        if self.logging_dir is None:
            return None
        return _abs_under_project(self.logging_dir)


DEFAULTS_PATH = PROJECT_ROOT / "config.defaults.yaml"
USER_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
        return dict(data or {})


def load_settings(defaults_path: Path | None = None, user_path: Path | None = None) -> SettingsModel:
    defaults_path = defaults_path or DEFAULTS_PATH
    user_path = user_path or USER_CONFIG_PATH
    if not defaults_path.exists():
        raise FileNotFoundError(f"Missing bundled defaults YAML: {defaults_path}")
    merged = _load_yaml(defaults_path)
    if user_path.exists():
        merged = _deep_merge(merged, _load_yaml(user_path))
    sm = SettingsModel.model_validate(merged)
    sm.sqlite_path_abs.parent.mkdir(parents=True, exist_ok=True)
    sm.storage_root_abs.mkdir(parents=True, exist_ok=True)
    if sm.logging_dir_abs:
        sm.logging_dir_abs.mkdir(parents=True, exist_ok=True)
    return sm
