"""Explicit Poisson sprinkling into a finite flat 2+1 Minkowski slab.

The region is a project-defined rectangular patch, not a reconstruction of the
underspecified finite patch used in the published ESV numerical examples.
Coordinates are (t, x, y), with t in [0, T), x in [-Lx/2, Lx/2), and
y in [-Ly/2, Ly/2). The homogeneous Poisson count is drawn once; no fixed-N
conditioning, truncation, or resampling is performed.
"""
from __future__ import annotations

import math
from collections.abc import Iterable
from fractions import Fraction

import numpy as np

from .causal_set_spatial import (
    MAX_REFERENCE_ELEMENTS,
    minimum_common_future_witnesses,
    minimal_antichain,
    validate_initial_antichain,
)

MAX_SLAB_ELEMENTS = MAX_REFERENCE_ELEMENTS


class PoissonDrawExceedsLimit(RuntimeError):
    """A valid Poisson count exceeded the explicit allocation guard."""

    def __init__(
        self, *, sampled_count: int, max_elements: int, expected_count: float
    ) -> None:
        self.sampled_count = int(sampled_count)
        self.max_elements = int(max_elements)
        self.expected_count = float(expected_count)
        super().__init__(
            f"Poisson draw N={self.sampled_count} exceeds max_elements="
            f"{self.max_elements}; no truncation or resampling was performed"
        )


def _positive_finite(name: str, value: float) -> float:
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, float, np.integer, np.floating))
    ):
        raise ValueError(f"{name} must be a finite positive number")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")
    return result


def minkowski_slab_volume(
    *, time_extent: float, x_extent: float, y_extent: float
) -> float:
    """Exact spacetime volume T * Lx * Ly of the rectangular slab."""
    t = _positive_finite("time_extent", time_extent)
    lx = _positive_finite("x_extent", x_extent)
    ly = _positive_finite("y_extent", y_extent)
    exact_volume = (
        Fraction.from_float(t)
        * Fraction.from_float(lx)
        * Fraction.from_float(ly)
    )
    try:
        volume = float(exact_volume)
    except OverflowError:
        raise ValueError("slab volume must be finite and positive") from None
    if not math.isfinite(volume) or volume <= 0.0:
        raise ValueError("slab volume must be finite and positive")
    return volume


def expected_poisson_count(
    *, density: float, time_extent: float, x_extent: float, y_extent: float
) -> float:
    """Return rho * Vol(M), the Poisson mean for the specified slab."""
    rho = _positive_finite("density", density)
    mean = rho * minkowski_slab_volume(
        time_extent=time_extent, x_extent=x_extent, y_extent=y_extent
    )
    if (
        not math.isfinite(mean)
        or mean <= 0.0
        or mean > np.iinfo(np.int64).max / 4
    ):
        raise ValueError("Poisson mean must be positive, finite and safe")
    return mean


def poisson_sprinkle_minkowski_slab(
    rng: np.random.Generator,
    *,
    density: float,
    time_extent: float,
    x_extent: float,
    y_extent: float,
    max_elements: int = MAX_SLAB_ELEMENTS,
) -> np.ndarray:
    """Draw an unconditioned homogeneous Poisson sprinkling into a flat slab.

    First draw N ~ Poisson(rho * T * Lx * Ly), then draw N iid uniform
    coordinates in the half-open rectangular region. The default 256-element
    guard matches the dense exact spatial-geometry oracle. If the realized
    count exceeds the guard, raise PoissonDrawExceedsLimit after the single
    count draw; do not truncate the sample, redraw N, or allocate coordinates.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be a numpy.random.Generator")
    if (
        not isinstance(max_elements, (int, np.integer))
        or isinstance(max_elements, (bool, np.bool_))
        or max_elements < 0
        or max_elements > MAX_SLAB_ELEMENTS
    ):
        raise ValueError(
            f"max_elements must be a nonnegative integer no greater than "
            f"{MAX_SLAB_ELEMENTS}"
        )

    t = _positive_finite("time_extent", time_extent)
    lx = _positive_finite("x_extent", x_extent)
    ly = _positive_finite("y_extent", y_extent)
    half_x = lx / 2.0
    half_y = ly / 2.0
    if half_x == 0.0 or half_y == 0.0:
        raise ValueError("x_extent and y_extent must have representable positive half-extents")
    if np.nextafter(t, 0.0) == 0.0:
        raise ValueError("time_extent must have a representable positive coordinate below its upper bound")
    rho = _positive_finite("density", density)
    mean = expected_poisson_count(
        density=rho, time_extent=t, x_extent=lx, y_extent=ly
    )
    count = int(rng.poisson(mean))
    if count > int(max_elements):
        raise PoissonDrawExceedsLimit(
            sampled_count=count,
            max_elements=int(max_elements),
            expected_count=mean,
        )

    unit = rng.random((count, 3), dtype=np.float64)
    scale = np.array([t, lx, ly], dtype=np.float64)
    offset = np.array([0.0, -half_x, -half_y], dtype=np.float64)
    coordinates = unit * scale + offset
    # Keep the represented sample inside the half-open region even if a
    # floating-point multiplication rounds a value to an excluded upper edge.
    coordinates[:, 0] = np.minimum(coordinates[:, 0], np.nextafter(t, 0.0))
    coordinates[:, 1] = np.minimum(
        coordinates[:, 1], np.nextafter(half_x, -np.inf)
    )
    coordinates[:, 2] = np.minimum(
        coordinates[:, 2], np.nextafter(half_y, -np.inf)
    )
    return coordinates


def minkowski_slab_causal_relation(points: np.ndarray) -> np.ndarray:
    """Return the strict 2+1 Minkowski order for binary64 (t, x, y) points.

    The exact rational values represented by the input float64 coordinates are
    compared pairwise. This avoids overflow in coordinate differences/squares
    and avoids rounding a near-null pair across the light cone. The dense
    relation is bounded by the same 256-element cap as the spatial oracle.
    Sized inputs are rejected before conversion when they already exceed the
    cap, avoiding an unnecessary large temporary array for list-like inputs.
    """
    if isinstance(points, np.ndarray):
        if points.ndim == 2 and points.shape[0] > MAX_SLAB_ELEMENTS:
            raise ValueError(
                f"exact slab relation is limited to N <= {MAX_SLAB_ELEMENTS}"
            )
    else:
        try:
            input_length = len(points)
        except (TypeError, AttributeError):
            input_length = None
        if input_length is not None and input_length > MAX_SLAB_ELEMENTS:
            raise ValueError(
                f"exact slab relation is limited to N <= {MAX_SLAB_ELEMENTS}"
            )
    coordinates = np.asarray(points, dtype=np.float64)
    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError("points must have shape (N, 3) in (t, x, y) order")
    if not np.all(np.isfinite(coordinates)):
        raise ValueError("points must contain only finite coordinates")
    n = coordinates.shape[0]
    if n > MAX_SLAB_ELEMENTS:
        raise ValueError(
            f"exact slab relation is limited to N <= {MAX_SLAB_ELEMENTS}"
        )

    times = [Fraction.from_float(float(value)) for value in coordinates[:, 0]]
    xs = [Fraction.from_float(float(value)) for value in coordinates[:, 1]]
    ys = [Fraction.from_float(float(value)) for value in coordinates[:, 2]]
    relation = np.zeros((n, n), dtype=np.bool_)

    # Every unordered pair has at most one future direction. Fractions preserve
    # the exact binary64 input values, including differences outside float64's
    # finite range and strict exclusion of exactly null-related pairs.
    for i in range(n):
        for j in range(i + 1, n):
            dt = times[j] - times[i]
            if dt == 0:
                continue
            if dt > 0:
                source, target = i, j
            else:
                source, target = j, i
                dt = -dt
            dx = xs[j] - xs[i]
            dy = ys[j] - ys[i]
            if dt * dt > dx * dx + dy * dy:
                relation[source, target] = True
    return relation



def side_boundary_censor_mask(
    points: np.ndarray,
    prec: np.ndarray,
    antichain: Iterable[int] | None = None,
    *,
    time_extent: float,
    x_extent: float,
    y_extent: float,
) -> np.ndarray:
    """Return pair-level side-boundary validity for a project-defined Minkowski slab.

    The returned boolean matrix is indexed by the sorted initial antichain.
    Its diagonal is true; a distinct pair is true exactly when at least one
    *global minimum-volume common-future witness* has its entire past cone down
    to t=0 inside the spatial rectangle:

        min(x + Lx/2, Lx/2 - x, y + Ly/2, Ly/2 - y) >= t.

    All tied global minimizers are considered. A pair is retained when any
    minimizer is side-safe, because then the minimum over side-safe witnesses
    equals the unrestricted minimum. If every global minimizer is unsafe, a
    safe but higher-volume candidate does not rescue the pair: the observed
    minimum could have been lowered by a clipped candidate, so the pair is
    censored. This avoids arbitrary index-based tie-breaking.

    This is only a side-boundary censor for the stated flat rectangular slab.
    It does not correct the stochastic minimal-antichain layer, the future
    boundary, continuum discretization error, or finite-size effects. The
    supplied relation must exactly match the strict Minkowski order of points.
    """
    if isinstance(points, np.ndarray):
        if points.ndim == 2 and points.shape[0] > MAX_SLAB_ELEMENTS:
            raise ValueError(
                f"exact slab censor is limited to N <= {MAX_SLAB_ELEMENTS}"
            )
    else:
        try:
            input_length = len(points)
        except (TypeError, AttributeError):
            input_length = None
        if input_length is not None and input_length > MAX_SLAB_ELEMENTS:
            raise ValueError(
                f"exact slab censor is limited to N <= {MAX_SLAB_ELEMENTS}"
            )

    coordinates = np.asarray(points, dtype=np.float64)
    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError("points must have shape (N, 3) in (t, x, y) order")
    if not np.all(np.isfinite(coordinates)):
        raise ValueError("points must contain only finite coordinates")

    relation = np.asarray(prec)
    if relation.dtype != np.bool_:
        raise TypeError("prec must be a boolean strict-order matrix")
    if relation.shape != (coordinates.shape[0], coordinates.shape[0]):
        raise ValueError("prec must match the number of embedded points")

    t_bound = Fraction.from_float(_positive_finite("time_extent", time_extent))
    x_bound = Fraction.from_float(_positive_finite("x_extent", x_extent)) / 2
    y_bound = Fraction.from_float(_positive_finite("y_extent", y_extent)) / 2
    exact_points = [
        tuple(Fraction.from_float(float(value)) for value in row)
        for row in coordinates
    ]
    for t, x, y in exact_points:
        if not (
            0 <= t < t_bound
            and -x_bound <= x < x_bound
            and -y_bound <= y < y_bound
        ):
            raise ValueError("points must lie within the declared half-open slab")

    expected_relation = minkowski_slab_causal_relation(coordinates)
    if not np.array_equal(relation, expected_relation):
        raise ValueError(
            "prec must equal the strict Minkowski relation of the supplied points"
        )

    if antichain is None:
        a = minimal_antichain(relation)
    else:
        try:
            requested_antichain = list(antichain)
        except TypeError as exc:
            raise ValueError("antichain must be an iterable of indices") from exc
        a = validate_initial_antichain(relation, requested_antichain)

    witnesses = minimum_common_future_witnesses(relation, a)
    mask = np.eye(a.size, dtype=np.bool_)
    for i in range(a.size):
        for j in range(i + 1, a.size):
            pair = (int(a[i]), int(a[j]))
            for witness in witnesses[pair]:
                t, x, y = exact_points[witness]
                margin = min(
                    x + x_bound,
                    x_bound - x,
                    y + y_bound,
                    y_bound - y,
                )
                if margin >= t:
                    mask[i, j] = mask[j, i] = True
                    break
    return mask
