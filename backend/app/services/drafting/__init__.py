from collections.abc import Callable

from app.schemas.measurement import Measurements
from app.schemas.pattern import Pattern
from app.services.drafting.blocks.bodice import draft_front_bodice

DRAFTERS: dict[str, Callable[[Measurements, float], Pattern]] = {"bodice": draft_front_bodice}


def draft_pattern(garment: str, m: Measurements, seam_allowance_cm: float = 1.5) -> Pattern:
    if garment not in DRAFTERS:
        raise ValueError(f"Unknown garment '{garment}'. Available: {', '.join(DRAFTERS)}")
    return DRAFTERS[garment](m, seam_allowance_cm)
