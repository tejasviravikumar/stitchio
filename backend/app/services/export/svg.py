"""Render a pattern to SVG at true scale (1 SVG unit = 1 mm)."""
import math
from xml.sax.saxutils import escape

from app.schemas.pattern import Pattern, Piece
from app.services.drafting.geometry import bbox, sample_outline
from app.services.drafting.symbols import dart_outline

MM = 10.0
MARGIN_MM = 15.0
GAP_CM = 5.0
INK, ACCENT = "#4A1026", "#B8325B"


def piece_points(piece: Piece) -> list[tuple[float, float]]:
    return piece.cutting_line or sample_outline(piece.outline)


def layout(pattern: Pattern) -> list[tuple[Piece, float, float]]:
    """Place pattern pieces left to right and return their centimetre offsets."""
    placed, cursor = [], 0.0
    for piece in pattern.pieces:
        x0, y0, x1, _ = bbox(piece_points(piece))
        placed.append((piece, cursor - x0, -y0))
        cursor += (x1 - x0) + GAP_CM
    return placed


def _path(piece: Piece, dx: float, dy: float) -> str:
    def f(x: float, y: float) -> str:
        return f"{(x + dx) * MM:.2f} {(y + dy) * MM:.2f}"

    pts = piece.outline
    d = [f"M {f(pts[0].x, pts[0].y)}"]
    for p in pts[1:] + [pts[0]]:
        if len(p.ctrl) == 2:
            d.append(f"C {f(*p.ctrl[0])} {f(*p.ctrl[1])} {f(p.x, p.y)}")
        elif len(p.ctrl) == 1:
            d.append(f"Q {f(*p.ctrl[0])} {f(p.x, p.y)}")
        else:
            d.append(f"L {f(p.x, p.y)}")
    return " ".join(d) + " Z"


def _arrow(x: float, y: float, angle: float, size: float = 3.0) -> str:
    pts = []
    for a in (angle, angle + 150, angle - 150):
        r = math.radians(a)
        pts.append(f"{x + math.cos(r) * size:.2f},{y + math.sin(r) * size:.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{INK}"/>'


def render_svg(pattern: Pattern) -> str:
    placed = layout(pattern)
    if not placed:
        raise ValueError("A pattern must contain at least one piece")
    all_pts = [(x + dx, y + dy) for pc, dx, dy in placed for x, y in piece_points(pc)]
    _, _, x1, y1 = bbox(all_pts)
    width, height = x1 * MM + 2 * MARGIN_MM, y1 * MM + 2 * MARGIN_MM + 12
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}mm" height="{height:.1f}mm" viewBox="0 0 {width:.1f} {height:.1f}">',
        f'<g transform="translate({MARGIN_MM},{MARGIN_MM})" fill="none" stroke="{INK}" stroke-width="0.6" font-family="sans-serif">',
    ]
    for piece, dx, dy in placed:
        def P(x: float, y: float) -> tuple[float, float]:
            return (x + dx) * MM, (y + dy) * MM

        if piece.cutting_line:
            pts = " ".join(f"{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}" for x, y in piece.cutting_line)
            out.append(f'<polygon points="{pts}" stroke-dasharray="4 3" stroke-width="0.5"/>')
        out.append(f'<path d="{_path(piece, dx, dy)}" stroke-width="0.9"/>')
        for dart in piece.darts:
            pts = " ".join(f"{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}" for x, y in dart_outline(dart))
            out.append(f'<polygon points="{pts}" stroke="{ACCENT}" stroke-width="0.9"/>')
        for notch in piece.notches:
            x, y = P(notch.x, notch.y)
            r = math.radians(notch.angle_deg)
            out.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{x + math.cos(r) * 6:.2f}" y2="{y + math.sin(r) * 6:.2f}" stroke-width="1.1"/>')
        if piece.grainline:
            (sx, sy), (ex, ey) = P(*piece.grainline.start), P(*piece.grainline.end)
            ang = math.degrees(math.atan2(ey - sy, ex - sx))
            out.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}"/>')
            out.extend((_arrow(ex, ey, ang), _arrow(sx, sy, ang + 180)))
        if piece.fold_line:
            (sx, sy), (ex, ey) = P(*piece.fold_line[0]), P(*piece.fold_line[1])
            out.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="{ACCENT}" stroke-width="2.2"/>')
            out.append(f'<text x="{sx + 4:.2f}" y="{(sy + ey) / 2:.2f}" fill="{ACCENT}" stroke="none" font-size="5" transform="rotate(-90 {sx + 4:.2f} {(sy + ey) / 2:.2f})" text-anchor="middle">PLACE ON FOLD</text>')
        label = f"{piece.name.replace('_', ' ').upper()}  CUT {piece.cut_count}" + (" ON FOLD" if piece.cut_on_fold else "")
        points = piece_points(piece)
        cx = sum(P(x, y)[0] for x, y in points) / len(points)
        out.append(f'<text x="{cx:.2f}" y="{y1 * MM + 22:.2f}" fill="{INK}" stroke="none" font-size="5" text-anchor="middle">{escape(label)}</text>')
    out.append("</g></svg>")
    return "\n".join(out)
