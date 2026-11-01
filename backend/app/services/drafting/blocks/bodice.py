"""Simplified educational front bodice block, drafted from measurements."""
from app.schemas.measurement import Measurements
from app.schemas.pattern import Pattern, PatternPoint, Piece
from app.services.drafting.darts import split_suppression, waist_dart
from app.services.drafting.geometry import sample_outline
from app.services.drafting.seam_allowance import offset_outline
from app.services.drafting.symbols import make_grainline, make_notch

WAIST_EASE_CM = 4.0
SHOULDER_DROP_CM = 4.0


def draft_front_bodice(m: Measurements, seam_allowance_cm: float = 1.5) -> Pattern:
    half_w = (m.bust_cm + m.ease_cm) / 4
    waist_edge = (m.waist_cm + WAIST_EASE_CM) / 4
    length = m.waist_length_cm + 1.0
    neck_w = m.bust_cm / 16 + 1.5
    neck_d = neck_w + 1.0
    shoulder_x = m.shoulder_width_cm / 2
    armhole_d = m.bust_cm / 6 + 8.0
    if armhole_d + 5 > length:
        raise ValueError("These measurements look inconsistent: the armhole is deeper than the bodice.")
    if not (neck_w + 2 < shoulder_x < half_w):
        raise ValueError("The shoulder width does not fit this bust measurement. Please re-measure.")
    intake, side_shaping = split_suppression(half_w, waist_edge)
    waist_side_x = half_w - side_shaping if half_w > waist_edge else waist_edge
    apex_x, apex_y = m.bust_point_distance_cm / 2, armhole_d
    outline = [
        PatternPoint(id="cf_neck", x=0, y=neck_d),
        PatternPoint(id="hps", x=neck_w, y=0, ctrl=[(neck_w * 0.5, neck_d), (neck_w, neck_d * 0.45)]),
        PatternPoint(id="shoulder_tip", x=shoulder_x, y=SHOULDER_DROP_CM),
        PatternPoint(id="underarm", x=half_w, y=armhole_d,
                     ctrl=[(shoulder_x - 1.5, SHOULDER_DROP_CM + (armhole_d - SHOULDER_DROP_CM) * 0.4),
                           (half_w - 3.0, armhole_d - 1.5)]),
        PatternPoint(id="waist_side", x=waist_side_x, y=length),
        PatternPoint(id="cf_waist", x=0, y=length),
    ]
    cutting = offset_outline(sample_outline(outline), seam_allowance_cm, fold_x=0.0) if seam_allowance_cm > 0 else []
    dart = waist_dart(apex_x, apex_y, length, intake)
    piece = Piece(
        name="front_bodice", outline=outline, cutting_line=cutting,
        darts=[dart] if dart else [],
        notches=[make_notch(half_w, armhole_d, 0, "underarm"),
                 make_notch(waist_side_x, length, 0, "waist"),
                 make_notch((neck_w + shoulder_x) / 2, SHOULDER_DROP_CM / 2, -90, "shoulder")],
        grainline=make_grainline(half_w * 0.55, neck_d + 6, length - 4),
        fold_line=((0.0, neck_d), (0.0, length)), cut_on_fold=True, cut_count=1,
    )
    return Pattern(garment="bodice", pieces=[piece], meta={
        "block": "simplified_front_bodice_v1", "seam_allowance_cm": seam_allowance_cm,
        "dart_intake_cm": round(intake, 2), "half_width_cm": round(half_w, 2), "warnings": m.warnings(),
    })
