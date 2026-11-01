"""Dart maths. A dart removes a wedge so flat cloth fits a curved body."""
from app.schemas.pattern import Dart

MAX_DART_INTAKE_CM = 6.0
MIN_DART_INTAKE_CM = 0.5
DART_STOP_BELOW_APEX_CM = 3.0


def split_suppression(half_width_at_bust: float, waist_edge: float) -> tuple[float, float]:
    suppression = max(0.0, half_width_at_bust - waist_edge)
    intake = min(suppression, MAX_DART_INTAKE_CM)
    return intake, suppression - intake


def waist_dart(apex_x: float, apex_y: float, waist_y: float, intake_cm: float) -> Dart | None:
    if intake_cm < MIN_DART_INTAKE_CM:
        return None
    half = intake_cm / 2
    return Dart(kind="waist", apex=(apex_x, apex_y + DART_STOP_BELOW_APEX_CM),
                legs=((apex_x - half, waist_y), (apex_x + half, waist_y)), intake_cm=round(intake_cm, 2))
