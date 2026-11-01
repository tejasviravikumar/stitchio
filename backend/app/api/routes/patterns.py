from fastapi import APIRouter, HTTPException, Response

from app.api.deps import DbSession, User
from app.models.measurement import MeasurementRow
from app.models.pattern import PatternRow
from app.schemas.measurement import Measurements
from app.schemas.pattern import Pattern, PatternGenerateRequest, PatternOut, PatternSave
from app.services.drafting import draft_pattern
from app.services.export.pdf_tiled import render_pdf
from app.services.export.svg import render_svg

router = APIRouter(prefix="/patterns", tags=["patterns"])


def _readable(db, pattern_id: int, user_id: str) -> PatternRow:
    row = db.get(PatternRow, pattern_id)
    if row is None or (row.user_id != user_id and not row.is_public):
        raise HTTPException(404, "Pattern not found")
    return row


def _owned(db, pattern_id: int, user_id: str) -> PatternRow:
    row = _readable(db, pattern_id, user_id)
    if row.user_id != user_id:
        raise HTTPException(403, "You can only change your own patterns")
    return row


@router.post("/generate", response_model=Pattern)
def generate(body: PatternGenerateRequest, db: DbSession, user: User):
    if body.measurements is not None:
        m = body.measurements
    elif body.measurements_id is not None:
        row = db.get(MeasurementRow, body.measurements_id)
        if row is None or row.user_id != user.id:
            raise HTTPException(404, "Measurements not found")
        m = Measurements(**row.data)
    else:
        raise HTTPException(422, "Provide either measurements or measurements_id")
    try:
        return draft_pattern(body.garment, m, body.seam_allowance_cm)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("", response_model=PatternOut, status_code=201)
def save(body: PatternSave, db: DbSession, user: User):
    row = PatternRow(user_id=user.id, name=body.name, garment=body.pattern.garment,
                     data=body.pattern.model_dump(mode="json"), is_public=body.is_public)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[PatternOut])
def list_mine(db: DbSession, user: User):
    return db.query(PatternRow).filter(PatternRow.user_id == user.id).order_by(PatternRow.id.desc()).all()


@router.get("/{pattern_id}", response_model=PatternOut)
def get_one(pattern_id: int, db: DbSession, user: User):
    return _readable(db, pattern_id, user.id)


@router.put("/{pattern_id}", response_model=PatternOut)
def update(pattern_id: int, body: PatternSave, db: DbSession, user: User):
    row = _owned(db, pattern_id, user.id)
    row.name, row.garment, row.is_public = body.name, body.pattern.garment, body.is_public
    row.data = body.pattern.model_dump(mode="json")
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{pattern_id}", status_code=204)
def delete(pattern_id: int, db: DbSession, user: User):
    db.delete(_owned(db, pattern_id, user.id))
    db.commit()
    return Response(status_code=204)


@router.get("/{pattern_id}/svg")
def export_svg(pattern_id: int, db: DbSession, user: User):
    row = _readable(db, pattern_id, user.id)
    return Response(render_svg(Pattern.model_validate(row.data)), media_type="image/svg+xml")


@router.get("/{pattern_id}/pdf")
def export_pdf(pattern_id: int, db: DbSession, user: User):
    row = _readable(db, pattern_id, user.id)
    return Response(render_pdf(Pattern.model_validate(row.data)), media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="pattern-{pattern_id}.pdf"'})
