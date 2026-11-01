"""Background jobs (arq + Redis). Run with ``arq app.workers.jobs.WorkerSettings``."""
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.trace import Trace
from app.schemas.trace import TracePoint
from app.services.inference.seam_classifier import get_classifier


async def reclassify_trace(ctx: dict, trace_id: int) -> dict:
    db = SessionLocal()
    try:
        trace = db.get(Trace, trace_id)
        if trace is None or trace.confirmed_by_user:
            return {"updated": False}
        preds = get_classifier().predict([TracePoint(**point) for point in trace.points], trace.note)
        trace.label, trace.confidence = preds[0].label.value, preds[0].score
        trace.suggestions = [prediction.model_dump(mode="json") for prediction in preds]
        db.commit()
        return {"updated": True, "label": trace.label}
    finally:
        db.close()


class WorkerSettings:
    functions = [reclassify_trace]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
