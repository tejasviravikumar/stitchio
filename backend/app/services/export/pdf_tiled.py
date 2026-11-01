"""Tile a pattern across A4 pages at 1:1 scale for home printing."""
import io
import math

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.schemas.pattern import Pattern
from app.services.drafting.geometry import bbox, sample_outline
from app.services.export.svg import MM, layout

PAGE_W, PAGE_H = A4[0] / mm, A4[1] / mm
MARGIN = 12.0
OVERLAP = 6.0


def _cover_page(c: canvas.Canvas, rows: int, cols: int) -> None:
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN * mm, (PAGE_H - 25) * mm, "Stitch Bunny pattern: print check")
    c.setFont("Helvetica", 10)
    lines = ["1. Print this PDF at 100% / 'Actual size'. Turn OFF 'Fit to page'.",
             "2. Measure the line below with a ruler. It must be exactly 10 cm.",
             f"3. Print the remaining pages ({rows} rows x {cols} columns), trim the margins,",
             "   and tape the pages together, matching the overlap."]
    for i, text in enumerate(lines):
        c.drawString(MARGIN * mm, (PAGE_H - 40 - i * 7) * mm, text)
    y = (PAGE_H - 80) * mm
    c.setLineWidth(0.8)
    c.line(MARGIN * mm, y, (MARGIN + 100) * mm, y)
    c.line(MARGIN * mm, y - 2 * mm, MARGIN * mm, y + 2 * mm)
    c.line((MARGIN + 100) * mm, y - 2 * mm, (MARGIN + 100) * mm, y + 2 * mm)
    c.drawString((MARGIN + 38) * mm, y + 4 * mm, "10 cm")
    c.showPage()


def render_pdf(pattern: Pattern) -> bytes:
    placed = layout(pattern)
    if not placed:
        raise ValueError("A pattern must contain at least one piece")
    polylines: list[list[tuple[float, float]]] = []
    for piece, dx, dy in placed:
        polylines.append([((x + dx) * MM, (y + dy) * MM) for x, y in sample_outline(piece.outline)])
        if piece.cutting_line:
            polylines.append([((x + dx) * MM, (y + dy) * MM) for x, y in piece.cutting_line])
    flat = [point for line in polylines for point in line]
    _, _, max_x, max_y = bbox(flat)
    usable_w, usable_h = PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN
    step_w, step_h = usable_w - OVERLAP, usable_h - OVERLAP
    cols = max(1, math.ceil((max_x - OVERLAP) / step_w))
    rows = max(1, math.ceil((max_y - OVERLAP) / step_h))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _cover_page(c, rows, cols)
    for r in range(rows):
        for col in range(cols):
            ox, oy = col * step_w, r * step_h
            c.saveState()
            clip = c.beginPath()
            clip.rect(MARGIN * mm, MARGIN * mm, usable_w * mm, usable_h * mm)
            c.clipPath(clip, stroke=0, fill=0)
            c.setLineWidth(0.6)
            for line in polylines:
                pts = [((x - ox + MARGIN) * mm, (PAGE_H - (y - oy + MARGIN)) * mm) for x, y in line]
                path = c.beginPath()
                path.moveTo(*pts[0])
                for point in pts[1:]:
                    path.lineTo(*point)
                path.close()
                c.drawPath(path, stroke=1, fill=0)
            c.restoreState()
            c.setFont("Helvetica", 7)
            c.drawString(MARGIN * mm, (PAGE_H - 7) * mm, f"Stitch Bunny | page row {r + 1}, col {col + 1} of {rows}x{cols}")
            c.showPage()
    c.save()
    return buf.getvalue()
