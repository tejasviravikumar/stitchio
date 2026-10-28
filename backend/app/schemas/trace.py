from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.taxonomy import SeamLabel


class TracePoint(BaseModel):
    """Normalized image coordinates: (0,0) top-left, (1,1) bottom-right."""

    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class LabelScore(BaseModel):
    label: SeamLabel
    score: float = Field(ge=0.0, le=1.0)


class TraceCreate(BaseModel):
    image_id: int
    points: list[TracePoint] = Field(min_length=2, max_length=2000)
    note: str | None = Field(default=None, max_length=500)
    label: SeamLabel | None = None  # set when the user already knows the label


class TraceConfirm(BaseModel):
    label: SeamLabel
    note: str | None = Field(default=None, max_length=500)


class TraceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    points: list[TracePoint]
    label: SeamLabel
    confidence: float
    suggestions: list[LabelScore]
    note: str | None
    confirmed_by_user: bool
    created_at: datetime


class ClassifyRequest(BaseModel):
    points: list[TracePoint] = Field(min_length=2, max_length=2000)
    note: str | None = Field(default=None, max_length=500)


class ClassifyResponse(BaseModel):
    suggestions: list[LabelScore]
    needs_confirmation: bool  # True when the model is unsure: ask the user