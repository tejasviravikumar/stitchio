"""Extract a normalized garment silhouette from a boolean mask."""
import numpy as np


def largest_contour(mask: np.ndarray, epsilon_ratio: float = 0.002) -> np.ndarray:
    """Return the largest contour as normalized (x, y) points."""
    import cv2

    if mask.ndim != 2:
        raise ValueError("mask must be a two-dimensional array")
    m = mask.astype(np.uint8) * 255
    contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.empty((0, 2))
    contour = max(contours, key=cv2.contourArea)
    contour = cv2.approxPolyDP(contour, epsilon_ratio * cv2.arcLength(contour, True), True)
    h, w = mask.shape
    points = contour.reshape(-1, 2).astype(float)
    points[:, 0] /= w
    points[:, 1] /= h
    return points
