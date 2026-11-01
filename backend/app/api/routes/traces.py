from fastapi import APIRouter, HTTPException, Query, Response

from app.api.deps import DbSession, User
from app.models.image import ImageRow
from app.models.trace import Trace
from app.schemas.taxonomy import LABEL_INFO, LABELS
from app.schemas.trace import (ClassifyRequest, ClassifyResponse, LabelScore, TraceConfirm,
                               TraceCreate, TraceOut)
from app.services.inference.seam_classifier import get_classifier

router = APIRouter(prefix="/traces", tags=["traces"])


def _scores(points, note):
    return get_classifier().predict(points, note)


@router.get("/labels")
def labels():
    return [{"label": label.value, "help": LABEL_INFO[label]} for label in LABELS]


@router.post("/classify", response_model=ClassifyResponse)
def classify(body: ClassifyRequest):
    suggestions = _scores(body.points, body.note)
    return ClassifyResponse(suggestions=suggestions,
                            needs_confirmation=suggestions[0].score < 0.75)


@router.post("", response_model=TraceOut, status_code=201)
def create(body: TraceCreate, db: DbSession, user: User):
    image = db.get(ImageRow, body.image_id)
    if image is None or image.user_id != user.id:
        raise HTTPException(404, "Image not found")
    suggestions = [LabelScore(label=body.label, score=1.0)] if body.label else _scores(body.points, body.note)
    chosen = suggestions[0]
    row = Trace(image_id=image.id, user_id=user.id,
                points=[point.model_dump(mode="json") for point in body.points],
                label=chosen.label.value, confidence=chosen.score,
                suggestions=[item.model_dump(mode="json") for item in suggestions],
                note=body.note, confirmed_by_user=body.label is not None)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[TraceOut])
def list_traces(db: DbSession, user: User, image_id: int | None = Query(default=None)):
    query = db.query(Trace).filter(Trace.user_id == user.id)
    if image_id is not None:
        query = query.filter(Trace.image_id == image_id)
    return query.order_by(Trace.id).all()


@router.patch("/{trace_id}", response_model=TraceOut)
def confirm(trace_id: int, body: TraceConfirm, db: DbSession, user: User):
    row = db.get(Trace, trace_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Trace not found")
    row.label = body.label.value
    row.confidence = 1.0
    row.suggestions = [LabelScore(label=body.label, score=1.0).model_dump(mode="json")]
    row.note = body.note if body.note is not None else row.note
    row.confirmed_by_user = True
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{trace_id}", status_code=204)
def delete(trace_id: int, db: DbSession, user: User):
    row = db.get(Trace, trace_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Trace not found")
    db.delete(row)
    db.commit()
    return Response(status_code=204)
