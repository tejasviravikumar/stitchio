"""Fit template parameters to a traced outline with CMA-ES."""
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import cma
import numpy as np
from scipy.spatial import cKDTree

from app.schemas.measurement import Measurements
from app.services.drafting.blocks.bodice import draft_front_bodice
from app.services.drafting.geometry import sample_outline

PARAM_BOUNDS: dict[str, tuple[float, float]] = {
    "shoulder_width_cm": (30.0, 50.0),
    "waist_length_cm": (32.0, 52.0),
    "ease_cm": (0.0, 16.0),
}


def chamfer(a: np.ndarray, b: np.ndarray) -> float:
    """Symmetric mean nearest-neighbour distance between two point sets."""
    return float(cKDTree(b).query(a)[0].mean() + cKDTree(a).query(b)[0].mean()) / 2


@dataclass
class FitResult:
    params: dict[str, float]
    loss: float
    evaluations: int


def fit_parameters(objective: Callable[[np.ndarray], float], x0: np.ndarray,
                   sigma0: float = 0.25, max_evals: int = 400,
                   seed: int = 0) -> tuple[np.ndarray, float, int]:
    """Minimize an objective over the unit cube."""
    es = cma.CMAEvolutionStrategy(x0.tolist(), sigma0,
                                  {"bounds": [0, 1], "maxfevals": max_evals,
                                   "seed": seed, "verbose": -9})
    es.optimize(objective)
    best = es.result
    return np.clip(np.array(best.xbest), 0, 1), float(best.fbest), int(best.evaluations)


def fit_bodice_to_outline(target_cm: np.ndarray, base: Measurements,
                          free: Sequence[str] = tuple(PARAM_BOUNDS),
                          max_evals: int = 400, seed: int = 0) -> FitResult:
    names = list(free)
    if not names or any(name not in PARAM_BOUNDS for name in names):
        raise ValueError("free must contain known bodice parameter names")
    target = np.asarray(target_cm, dtype=float)
    if target.ndim != 2 or target.shape[1] != 2 or len(target) < 2:
        raise ValueError("target_cm must be an (N, 2) array with at least two points")
    lo = np.array([PARAM_BOUNDS[name][0] for name in names])
    hi = np.array([PARAM_BOUNDS[name][1] for name in names])

    def to_measurements(z: np.ndarray) -> Measurements:
        values = lo + np.clip(z, 0, 1) * (hi - lo)
        return base.model_copy(update=dict(zip(names, values.tolist())))

    def objective(z: np.ndarray) -> float:
        try:
            pattern = draft_front_bodice(to_measurements(z), seam_allowance_cm=0)
        except ValueError:
            return 1e3
        pts = np.array(sample_outline(pattern.pieces[0].outline, 24))
        return chamfer(pts, target)

    x0 = np.clip((np.array([getattr(base, name) for name in names]) - lo) / (hi - lo), 0, 1)
    z, loss, evals = fit_parameters(objective, x0, max_evals=max_evals, seed=seed)
    return FitResult(params=dict(zip(names, (lo + z * (hi - lo)).tolist())), loss=loss, evaluations=evals)
