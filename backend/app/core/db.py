"""SQLAlchemy engine and session for local SQLite and PostgreSQL deployments."""
from collections.abc import Iterator

from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_url = _normalize(get_settings().database_url)
IS_SQLITE = _url.startswith("sqlite")
JsonType = JSON().with_variant(JSONB(), "postgresql")

if IS_SQLITE:
    engine = create_engine(_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
else:
    engine = create_engine(_url, pool_pre_ping=True, pool_size=5, max_overflow=5, pool_recycle=1800)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create development tables on SQLite; manage PostgreSQL schema with Alembic."""
    if not IS_SQLITE:
        return
    from app import models  # noqa: F401  (registers the tables)

    Base.metadata.create_all(bind=engine)
