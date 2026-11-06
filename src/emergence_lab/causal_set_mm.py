"""Myrheim–Meyer ordering-fraction reference tools (CS0, proposed calibration).

Status: development/reference library for the *proposed* CS0 preregistration
(docs/CAUSAL_SET_CS0_PREREGISTRATION.md). It contains no gated experiment and
makes no physical claim. Sprinkling points into a *given* Minkowski interval is
a positive control for the estimator: the dimension is put in by construction.

Definitions (all exact, model-level statements):

* A finite partial order on N elements is represented by a boolean "strictly
  precedes" matrix ``prec[i, j]`` (i < j in the order). It must be irreflexive,
  antisymmetric and transitive.
* Number of related (comparable) unordered pairs R = sum(prec).
  Ordering fraction r = R / C(N, 2).
* For N points drawn i.i.d. uniformly from the volume of an Alexandrov interval
  (causal diamond) in D-dimensional Minkowski space (D counts the time
  dimension), the probability that two points are causally related is
  exactly  r_D = Gamma(D+1) Gamma(D/2) / (2 Gamma(3D/2))
  (Myrheim 1978; Meyer 1988; see Surya 2019, Living Rev. Relativ. 22:5).
  Hence E[r] = r_D for every N >= 2 under this fixed-N i.i.d. sampling;
  r_2 = 1/2, r_3 = 8/35, r_4 = 1/10.  The Myrheim–Meyer dimension estimate is
  the inverse d_MM = r_D^{-1}(r).  Because the inverse is nonlinear, d_MM is
  *not* unbiased at finite N even though r is.
* A random k-order (intersection of k independent uniform linear orders) has
  pair-relation probability exactly 2^(1-k). For k = 2 it is distributionally
  identical to the D = 2 diamond (light-cone coordinates). For k >= 3 it is
  not Minkowski-like, yet still yields a finite, non-integer d_MM: it is the
  adversarial null for "an impressive but unphysical number".
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq
from scipy.special import gammaln

D_MIN = 1.0
D_MAX = 64.0


def expected_ordering_fraction(d: float) -> float:
    """Exact pair-relation probability r_D for the D-dimensional causal diamond.

    Defined here for real d >= 1 by the same Gamma-function expression
    (d = 1 gives 1, the total order)."""
    d = float(d)
    if not math.isfinite(d) or d < D_MIN:
        raise ValueError("dimension must be a finite real >= 1")
    return math.exp(
        gammaln(d + 1.0) + gammaln(d / 2.0) - math.log(2.0) - gammaln(1.5 * d)
    )


def myrheim_meyer_dimension(r: float) -> float:
    """Invert r_D. Returns nan outside the invertible range.

    r == 1 maps to 1 (total order). r <= r_D(D_MAX) (including the antichain,
    r = 0) is reported as nan: no finite dimension is supported, and it must be
    classified as OUT_OF_RANGE rather than "very high dimension"."""
    r = float(r)
    if not math.isfinite(r) or r > 1.0 or r < 0.0:
        return math.nan
    if r == 1.0:
        return 1.0
    lo_r = expected_ordering_fraction(D_MAX)
    if r <= lo_r:
        return math.nan
    return brentq(lambda d: expected_ordering_fraction(d) - r, D_MIN, D_MAX,
                  xtol=1e-13, rtol=1e-13, maxiter=200)


def ordering_fraction(prec: np.ndarray) -> float:
    prec = np.asarray(prec, dtype=bool)
    n = prec.shape[0]
    if prec.shape != (n, n) or n < 2:
        raise ValueError("need a square relation matrix with N >= 2")
    return float(np.count_nonzero(prec)) / (n * (n - 1) / 2.0)


def check_partial_order(prec: np.ndarray) -> None:
    """Raise ValueError unless prec is a strict partial order (exact check)."""
    prec = np.asarray(prec, dtype=bool)
    n = prec.shape[0]
    if prec.shape != (n, n):
        raise ValueError("relation matrix must be square")
    if np.any(np.diag(prec)):
        raise ValueError("not irreflexive")
    if np.any(prec & prec.T):
        raise ValueError("not antisymmetric")
    # float64 BLAS product: path counts <= n are exact for n < 2**53.
    p = prec.astype(np.float64)
    if np.any(((p @ p) > 0.5) & ~prec):
        raise ValueError("not transitive")


def sprinkle_diamond(n: int, d: int, rng: np.random.Generator,
                     batch: int = 4096) -> np.ndarray:
    """N i.i.d. uniform points in the unit-height causal diamond |t| + |x| <= 1/2.

    Coordinates (t, x_1..x_{d-1}). Rejection sampling from the bounding box;
    exact in distribution. This is fixed-N (conditioned) sampling, not an
    unconditioned Poisson process."""
    if d < 2 or n < 1:
        raise ValueError("need d >= 2 and n >= 1")
    out = np.empty((0, d))
    while out.shape[0] < n:
        cand = rng.uniform(-0.5, 0.5, size=(batch, d))
        rad = np.sqrt(np.sum(cand[:, 1:] ** 2, axis=1))
        out = np.vstack([out, cand[np.abs(cand[:, 0]) + rad <= 0.5]])
    return out[:n]


def causal_matrix(points: np.ndarray) -> np.ndarray:
    """prec[i, j] = True iff j lies strictly inside the future light cone of i."""
    pts = np.asarray(points, dtype=float)
    dt = pts[None, :, 0] - pts[:, None, 0]
    dx2 = np.sum((pts[None, :, 1:] - pts[:, None, 1:]) ** 2, axis=2)
    return (dt > 0) & (dt * dt > dx2)


def random_k_order(n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    """Intersection of k independent uniformly random linear orders."""
    if k < 1 or n < 1:
        raise ValueError("need k >= 1 and n >= 1")
    ranks = np.stack([rng.permutation(n) for _ in range(k)], axis=1)
    prec = np.ones((n, n), dtype=bool)
    for c in range(k):
        prec &= ranks[:, None, c] < ranks[None, :, c]
    return prec


def chain(n: int) -> np.ndarray:
    return np.triu(np.ones((n, n), dtype=bool), k=1)


def antichain(n: int) -> np.ndarray:
    return np.zeros((n, n), dtype=bool)


def two_layer_order(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Bottom layer floor(n/2), top layer the rest; each bottom<top link with prob p.

    Height-2, so automatically transitive. Exact E[r] = p*a*b / C(n,2)."""
    a = n // 2
    prec = np.zeros((n, n), dtype=bool)
    prec[:a, a:] = rng.random((a, n - a)) < p
    return prec


def two_layer_expected_r(n: int, p: float) -> float:
    a = n // 2
    return p * a * (n - a) / (n * (n - 1) / 2.0)


@dataclass(frozen=True)
class MMResult:
    n: int
    related_pairs: int
    r: float
    d_mm: float
    classification: str  # IN_RANGE | TOTAL_ORDER | OUT_OF_RANGE


def measure(prec: np.ndarray) -> MMResult:
    prec = np.asarray(prec, dtype=bool)
    r = ordering_fraction(prec)
    d = myrheim_meyer_dimension(r)
    if r == 1.0:
        cls = "TOTAL_ORDER"
    elif math.isnan(d):
        cls = "OUT_OF_RANGE"
    else:
        cls = "IN_RANGE"
    return MMResult(prec.shape[0], int(np.count_nonzero(prec)), r, d, cls)
