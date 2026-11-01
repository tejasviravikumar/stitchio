from fastapi import APIRouter
from sqlalchemy import inspect, text

from app.api.deps import DbSession

router = APIRouter(tags=["health"])
REQUIRED_TABLES = {"images", "traces", "patterns", "measurements"}


@router.get("/health")
def health():
    return {"status": "ok", "app": "Stitch Bunny"}


@router.get("/health/ready")
def ready(db: DbSession):
    db.execute(text("SELECT 1"))
    tables = set(inspect(db.get_bind()).get_table_names())
    return {"status": "ready", "database": "ok", "tables_ready": REQUIRED_TABLES <= tables}
