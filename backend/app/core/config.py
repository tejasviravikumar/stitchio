"""Settings, read from environment variables or backend/.env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Stitch Bunny"
    environment: str = "dev"  # dev | prod

    # SQLite by default so the app runs with zero setup.
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'stitchbunny.db').as_posix()}"
    cors_origins: str = "http://localhost:5173"  # comma separated

    supabase_url: str = ""
    supabase_service_key: str = ""  # backend only, never ship to the frontend
    supabase_jwt_secret: str = ""
    supabase_bucket: str = "garment-images"

    dev_auth_bypass: bool = False
    max_upload_mb: int = 10
    local_upload_dir: Path = BACKEND_DIR / "uploads"
    redis_url: str = "redis://localhost:6379"
    model_path: str = ""  # path to an exported ONNX seam classifier (later)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()