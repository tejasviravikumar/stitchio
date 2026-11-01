"""Seam allowance: offset the stitching line outward with Shapely."""
from shapely.geometry import Polygon, box

XY = tuple[float, float]


def offset_outline(points: list[XY], allowance_cm: float, fold_x: float | None = None) -> list[XY]:
    """Grow a polygon by ``allowance_cm``; preserve an edge placed on a fold."""
    if len(points) < 3:
        raise ValueError("An outline needs at least three points")
    poly = Polygon(points)
    if not poly.is_valid:
        poly = poly.buffer(0)
    if poly.is_empty:
        raise ValueError("Cannot offset an invalid or empty outline")
    grown = poly.buffer(allowance_cm, join_style="mitre", mitre_limit=2.0)
    if fold_x is not None:
        grown = grown.intersection(box(fold_x, -1e4, 1e4, 1e4))
    if grown.geom_type != "Polygon":
        if not grown.geoms:
            raise ValueError("Seam allowance produced an empty outline")
        grown = max(grown.geoms, key=lambda g: g.area)
    return [(round(x, 3), round(y, 3)) for x, y in list(grown.exterior.coords)[:-1]]
