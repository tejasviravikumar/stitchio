from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Measurements(BaseModel):
    height_cm: float = Field(gt=0, le=300)
    bust_cm: float = Field(gt=0, le=250)
    waist_cm: float = Field(gt=0, le=250)
    hip_cm: float = Field(gt=0, le=250)
    waist_length_cm: float = Field(default=42.0, gt=0, le=100)
    shoulder_width_cm: float = Field(default=38.0, gt=0, le=100)
    bust_point_distance_cm: float = Field(default=19.0, gt=0, le=60)
    ease_cm: float = Field(default=6.0, ge=0, le=30)

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.waist_cm >= self.bust_cm:
            warnings.append("Waist larger than bust is rare; please double-check both measurements.")
        if self.waist_cm >= self.hip_cm:
            warnings.append("Your waist measurement is as large as or larger than your hip; please double-check both measurements.")
        if self.waist_length_cm > self.height_cm * 0.4:
            warnings.append("Your waist length seems long for your height; please double-check it.")
        return warnings


class MeasurementCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    measurements: Measurements


class MeasurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    measurements: Measurements
    warnings: list[str]
    created_at: datetime
