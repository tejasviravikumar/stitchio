"""Pattern symbols and plain-language help for beginners."""
from app.schemas.pattern import Dart, Grainline, Notch

SYMBOL_HELP: dict[str, dict[str, str]] = {
    "dart": {"meaning": "A folded wedge that shapes flat fabric around the body.", "how_to": "Fold along the centre of the wedge, matching the legs, then stitch from the wide end to the point."},
    "notch": {"meaning": "A small tick on the edge that tells you where pieces match up.", "how_to": "Snip a tiny cut (less than the seam allowance) and line the notches up when pinning."},
    "grainline": {"meaning": "An arrow showing which way the fabric threads should run.", "how_to": "Keep the arrow parallel to the selvage (the finished edge of the fabric)."},
    "fold_line": {"meaning": "An edge placed on a folded fabric edge so you cut one piece that opens out symmetrical.", "how_to": "Fold the fabric, put this edge exactly on the fold, and do not add a seam allowance there."},
}


def dart_outline(d: Dart) -> list[tuple[float, float]]:
    return [d.legs[0], d.apex, d.legs[1]]


def make_grainline(x: float, y_top: float, y_bottom: float) -> Grainline:
    return Grainline(start=(x, y_top), end=(x, y_bottom))


def make_notch(x: float, y: float, angle_deg: float = 0.0, label: str | None = None) -> Notch:
    return Notch(x=x, y=y, angle_deg=angle_deg, label=label)
