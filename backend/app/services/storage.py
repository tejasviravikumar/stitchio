"""Local upload storage used in development."""
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings


def save_upload(data: bytes, suffix: str) -> str:
    settings = get_settings()
    settings.local_upload_dir.mkdir(parents=True, exist_ok=True)
    key = f"{uuid4().hex}{suffix}"
    (settings.local_upload_dir / key).write_bytes(data)
    return key


def delete_upload(key: str) -> None:
    path = (get_settings().local_upload_dir / Path(key).name).resolve()
    root = get_settings().local_upload_dir.resolve()
    if path.parent == root and path.exists():
        path.unlink()
