from fastapi import APIRouter, HTTPException, Response

from app.api.deps import DbSession, User
from app.models.measurement import MeasurementRow
from app.schemas.measurement import MeasurementCreate, MeasurementOut, Measurements

router = APIRouter(prefix="/measurements", tags=["measurements"])


def _out(row: MeasurementRow) -> MeasurementOut:
    m = Measurements(**row.data)
    return MeasurementOut(id=row.id, name=row.name, measurements=m, warnings=m.warnings(), created_at=row.created_at)


@router.post("/check")
def check(body: Measurements):
    return {"warnings": body.warnings()}


@router.post("", response_model=MeasurementOut, status_code=201)
def create(body: MeasurementCreate, db: DbSession, user: User):
    row = MeasurementRow(user_id=user.id, name=body.name, data=body.measurements.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _out(row)


@router.get("", response_model=list[MeasurementOut])
def list_all(db: DbSession, user: User):
    rows = db.query(MeasurementRow).filter(MeasurementRow.user_id == user.id).order_by(MeasurementRow.id).all()
    return [_out(row) for row in rows]


@router.get("/{measurement_id}", response_model=MeasurementOut)
def get_one(measurement_id: int, db: DbSession, user: User):
    row = db.get(MeasurementRow, measurement_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Measurements not found")
    return _out(row)


@router.delete("/{measurement_id}", status_code=204)
def delete(measurement_id: int, db: DbSession, user: User):
    row = db.get(MeasurementRow, measurement_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Measurements not found")
    db.delete(row)
    db.commit()
    return Response(status_code=204)
