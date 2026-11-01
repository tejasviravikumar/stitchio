"""Dijkstra-based live-wire path snapping to strong image edges."""
import heapq

import numpy as np


def edge_cost(gray: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(gray.astype(float))
    magnitude = np.hypot(gx, gy)
    magnitude /= magnitude.max() + 1e-9
    return 1.0 - magnitude + 0.02


def live_wire(cost: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Return the cheapest 8-connected path; coordinates are (row, column)."""
    if cost.ndim != 2:
        raise ValueError("cost must be a two-dimensional array")
    h, w = cost.shape
    for point in (start, end):
        if not (0 <= point[0] < h and 0 <= point[1] < w):
            raise ValueError("start and end must be inside the cost map")
    dist = np.full((h, w), np.inf)
    prev: dict[tuple[int, int], tuple[int, int]] = {}
    dist[start] = 0.0
    queue = [(0.0, start)]
    while queue:
        distance, (r, c) = heapq.heappop(queue)
        if (r, c) == end:
            break
        if distance > dist[r, c]:
            continue
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    step = 1.4142 if dr and dc else 1.0
                    next_distance = distance + cost[nr, nc] * step
                    if next_distance < dist[nr, nc]:
                        dist[nr, nc] = next_distance
                        prev[(nr, nc)] = (r, c)
                        heapq.heappush(queue, (next_distance, (nr, nc)))
    path = [end]
    while path[-1] != start:
        if path[-1] not in prev:
            return [start, end]
        path.append(prev[path[-1]])
    return path[::-1]
