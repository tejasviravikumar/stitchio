from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.measurement import Measurements


class PatternPoint(BaseModel):
    id: str
    x: float
    y: float
    ctrl: list[tuple[float, float]] = Field(default_factory=list, max_length=2)


class Dart(BaseModel):
    kind: str
    apex: tuple[float, float]
    legs: tuple[tuple[float, float], tuple[float, float]]
    intake_cm: float


class Grainline(BaseModel):
    start: tuple[float, float]
    end: tuple[float, float]


class Notch(BaseModel):
    x: float
    y: float
    angle_deg: float = 0.0
    label: str | None = None


class Piece(BaseModel):
    name: str
    outline: list[PatternPoint]
    cutting_line: list[tuple[float, float]] = Field(default_factory=list)
    darts: list[Dart] = Field(default_factory=list)
    notches: list[Notch] = Field(default_factory=list)
    grainline: Grainline | None = None
    fold_line: tuple[tuple[float, float], tuple[float, float]] | None = None
    cut_on_fold: bool = False
    cut_count: int = 1


class Pattern(BaseModel):
    garment: str
    pieces: list[Piece]
    meta: dict[str, Any] = Field(default_factory=dict)


class PatternGenerateRequest(BaseModel):
    garment: str = "bodice"
    measurements: Measurements | None = None
    measurements_id: int | None = None
    seam_allowance_cm: float = Field(default=1.5, ge=0, le=5)


class PatternSave(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    pattern: Pattern
    is_public: bool = False


class PatternOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    garment: str
    data: dict[str, Any]
    is_public: bool
    created_at: datetime
    updated_at: datetime
