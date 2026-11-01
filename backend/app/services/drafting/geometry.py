"""Small geometry helpers: sampling Bezier outlines into polylines."""
import numpy as np

from app.schemas.pattern import PatternPoint

XY = tuple[float, float]


def _segment(p0: XY, p1: XY, ctrl: list[XY], n: int) -> list[XY]:
    """Points along one segment, excluding p0, including p1."""
    if not ctrl:
        return [p1]
    t = np.linspace(0.0, 1.0, n + 1)[1:, None]
    a, b = np.array(p0), np.array(p1)
    if len(ctrl) == 1:
        c = np.array(ctrl[0])
        pts = (1 - t) ** 2 * a + 2 * (1 - t) * t * c + t**2 * b
    else:
        c1, c2 = np.array(ctrl[0]), np.array(ctrl[1])
        pts = (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t**2 * c2 + t**3 * b
    return [(float(x), float(y)) for x, y in pts]


def sample_outline(outline: list[PatternPoint], samples_per_curve: int = 16) -> list[XY]:
    """Flatten a closed outline (lines + Beziers) into a polygon."""
    out: list[XY] = []
    for i, cur in enumerate(outline):
        prev = outline[i - 1]
        out.extend(_segment((prev.x, prev.y), (cur.x, cur.y), cur.ctrl, samples_per_curve))
    return out


def bbox(points: list[XY]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)
