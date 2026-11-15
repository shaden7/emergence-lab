"""D3-E0/M0 implementation r1 (PROPOSED design; NOT frozen, NOT authorized).

Implements the tools required by docs/CS0_D3_E0_CONTROL_PROPOSAL.md before any
frozen pilot or target run:

* a vectorised *direct* sampler of i.i.d. uniform points in the unit-height
  D-dimensional Alexandrov diamond |t| + |x| <= 1/2, written independently of
  the existing rejection sampler ``causal_set_mm.sprinkle_diamond``;
* batched relation counting for arm A (two tips + N-2 interior points) and
  arm B (N interior points);
* the Myrheim–Meyer inverse d(r) on the bracket [1, 10] as a lookup table over
  the attainable fractions k / C(N, 2);
* a deterministic quadrature of the three-point configuration probabilities
  (mpmath, no sampling), with the literature k-chain closed form as an extra
  anchor;
* exact N=3 arm-B / N=5 arm-A laws derived from that quadrature;
* a Monte Carlo cell estimator and the D=2 positive-control comparison against
  archived exact values.

Status labels: the sampler and counting are implementation; the quadrature is a
numerical (high-precision) evaluation of exact integrals, not a proof; nothing
in this module is a D=3 result. No function here runs a target campaign.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import gammaln
from scipy.stats import norm

from .causal_set_mm import expected_ordering_fraction

GRID = (2, 3, 4, 5, 6, 8, 12, 16, 24, 32)
INVERSE_BRACKET = (1.0, 10.0)
#: Cells whose d is identically 1 (r = 1 with probability one): arm A N=2,3;
#: arm B N=2 conditional on R>0.  Classified analytically (BELOW 3 at D=3).
DETERMINISTIC_CELLS = (("A", 2), ("A", 3), ("B", 2))


# --------------------------------------------------------------------------
# Sampling
# --------------------------------------------------------------------------

def direct_sample(batch: int, n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """Array (batch, n, d) of i.i.d. uniform points in |t| + |x| <= 1/2.

    Direct (non-rejection) construction: the spatial cross-section at time t is
    a (d-1)-ball of radius u = 1/2 - |t|, so the marginal density of u on
    [0, 1/2] is proportional to u^(d-1), i.e. u = U^(1/d) / 2.  The sign of t is
    a fair coin; the spatial point is uniform in the ball (Gaussian direction,
    radius u * V^(1/(d-1)))."""
    if d < 2 or n < 1 or batch < 1:
        raise ValueError("need d >= 2, n >= 1, batch >= 1")
    u = 0.5 * rng.random((batch, n)) ** (1.0 / d)
    sign = np.where(rng.random((batch, n)) < 0.5, -1.0, 1.0)
    t = sign * (0.5 - u)
    g = rng.standard_normal((batch, n, d - 1))
    g /= np.linalg.norm(g, axis=2, keepdims=True)
    rad = u * rng.random((batch, n)) ** (1.0 / (d - 1))
    out = np.empty((batch, n, d))
    out[:, :, 0] = t
    out[:, :, 1:] = g * rad[:, :, None]
    return out


def relation_counts(points: np.ndarray) -> np.ndarray:
    """Number of causally related unordered pairs per replicate.

    points: (batch, n, d).  Pair (i, j) is related iff dt^2 > |dx|^2 (strict
    interior of the light cone, same relation as ``causal_matrix``)."""
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 3:
        raise ValueError("points must have shape (batch, n, d)")
    n = pts.shape[1]
    if n < 2:
        return np.zeros(pts.shape[0], dtype=np.int64)
    iu, ju = np.triu_indices(n, k=1)
    diff = pts[:, ju, :] - pts[:, iu, :]
    dt2 = diff[:, :, 0] ** 2
    dx2 = np.sum(diff[:, :, 1:] ** 2, axis=2)
    return np.count_nonzero(dt2 > dx2, axis=1).astype(np.int64)


def arm_counts(arm: str, n: int, d: int, batch: int,
               rng: np.random.Generator) -> np.ndarray:
    """Relation counts R for ``batch`` replicates of arm A or B at total N=n.

    Arm A: tips (+-1/2, 0) plus n-2 interior points; R = 2n-3 + R_inner exactly
    (each tip precedes/follows every interior point almost surely and the tips
    are related)."""
    if n < 2:
        raise ValueError("need n >= 2")
    if arm == "A":
        m = n - 2
        inner = relation_counts(direct_sample(batch, m, d, rng)) if m >= 2 else \
            np.zeros(batch, dtype=np.int64)
        return inner + (2 * n - 3)
    if arm == "B":
        return relation_counts(direct_sample(batch, n, d, rng))
    raise ValueError("arm must be 'A' or 'B'")


# --------------------------------------------------------------------------
# Inverse table
# --------------------------------------------------------------------------

def mm_forward(d: float) -> float:
    return expected_ordering_fraction(d)


@lru_cache(maxsize=None)
def inverse_table(n: int) -> np.ndarray:
    """d(k / C) for k = 0..C on the bracket [1, 10]; entry 0 is nan (R = 0).

    Raises if any positive fraction falls below f(10) (not invertible)."""
    c = n * (n - 1) // 2
    lo, hi = INVERSE_BRACKET
    f_hi = mm_forward(hi)
    table = np.full(c + 1, np.nan)
    for k in range(1, c + 1):
        r = k / c
        if r == 1.0:
            table[k] = 1.0
            continue
        if r <= f_hi:
            raise ValueError(f"r={k}/{c} below f(10): not invertible on [1,10]")
        table[k] = brentq(lambda x: mm_forward(x) - r, lo, hi,
                          xtol=1e-14, rtol=1e-14, maxiter=200)
    table.setflags(write=False)
    return table


# --------------------------------------------------------------------------
# Three-point quadrature (deterministic, independent of the samplers)
# --------------------------------------------------------------------------

def _mp():
    import mpmath
    return mpmath.mp


def _diamond_average(ctx, d: int, g):
    """E[g(t, rho)] for a uniform point; rho = |x|, weight rho^(d-2)."""
    def inner(t):
        top = ctx.mpf(1) / 2 - abs(t)
        return ctx.quad(lambda r: g(t, r) * r ** (d - 2), [0, top])
    half = ctx.mpf(1) / 2
    num = ctx.quad(inner, [-half, 0, half])
    den = ctx.quad(lambda t: (half - abs(t)) ** (d - 1) / (d - 1), [-half, 0, half])
    return num / den


def _tau2(ctx, t, r, future: bool):
    a = (ctx.mpf(1) / 2 - t) if future else (t + ctx.mpf(1) / 2)
    return max(a * a - r * r, ctx.mpf(0))


@lru_cache(maxsize=None)
def three_point_probabilities(d: int) -> dict:
    """Labeled-point probabilities for i.i.d. uniform diamond points (mpmath).

    The future (past) of x inside the diamond is the Alexandrov interval
    between x and the top (bottom) tip, whose volume fraction is tau_+^d
    (tau_-^d), tau the proper time to the tip (the whole diamond has proper
    height 1).  Hence, for labeled points x1, x2, x3:

      q_pair  = P(x1 < x2)            = E[tau_+^d]
      q_chain = P(x1 < x2 < x3)       = E[tau_-^d tau_+^d]
      q_down  = P(x1 < x2, x1 < x3)   = E[tau_+^(2d)]

    These are 2-D integrals evaluated by tanh-sinh quadrature at 40 digits."""
    import mpmath
    with mpmath.workdps(40):
        return _three_point(_mp(), d)


def _three_point(ctx, d: int) -> dict:
    def tp(t, r):
        return ctx.sqrt(_tau2(ctx, t, r, True))
    def tm(t, r):
        return ctx.sqrt(_tau2(ctx, t, r, False))
    q_pair = _diamond_average(ctx, d, lambda t, r: tp(t, r) ** d)
    q_chain = _diamond_average(ctx, d, lambda t, r: (tm(t, r) * tp(t, r)) ** d)
    q_down = _diamond_average(ctx, d, lambda t, r: tp(t, r) ** (2 * d))
    return {"q_pair": q_pair, "q_chain": q_chain, "q_down": q_down}


def k_chain_probability(k: int, d: int) -> float:
    """Literature closed form for P(x1 < ... < xk), k labeled uniform points.

    chi_k = (1/k) (Gamma(d+1)/2)^(k-1) Gamma(d/2) Gamma(d) /
            (Gamma(k d / 2) Gamma((k+1) d / 2))
    (Meyer 1988, as reviewed in Surya 2019, Living Rev. Relativ. 22:5; formula
    as recalled — used only as a cross-check of the quadrature, which is the
    gate).  k=2 reproduces f(d)/2."""
    if k < 2 or d < 2:
        raise ValueError("need k >= 2 and d >= 2")
    return math.exp(-math.log(k) + (k - 1) * (gammaln(d + 1) - math.log(2))
                    + gammaln(d / 2) + gammaln(d)
                    - gammaln(k * d / 2) - gammaln((k + 1) * d / 2))


def three_point_r_law(d: int) -> dict:
    """Distribution of R for 3 i.i.d. uniform points: {0,1,2,3} -> probability.

    P(R=3) = 6 q_chain; P(R=2) = 2 (3 q_down - 6 q_chain) (V and Lambda shapes,
    equal by time reversal; each chain has one common minimum, so it is
    subtracted); P(R=1) from E[R] = 3 * 2 q_pair; P(R=0) by normalisation."""
    q = three_point_probabilities(d)
    p3 = 6 * q["q_chain"]
    p2 = 2 * (3 * q["q_down"] - 6 * q["q_chain"])
    p1 = 6 * q["q_pair"] - 3 * p3 - 2 * p2
    p0 = 1 - p1 - p2 - p3
    return {0: p0, 1: p1, 2: p2, 3: p3}


def exact_three_point_cells(d: int) -> dict:
    """E[d | R>0] for arm B N=3 and E[d] for arm A N=5 from the quadrature law."""
    law = three_point_r_law(d)
    tb = inverse_table(3)
    pos = sum(law[k] for k in (1, 2, 3))
    b3 = sum(law[k] * tb[k] for k in (1, 2, 3)) / pos
    ta = inverse_table(5)
    a5 = sum(law[k] * ta[7 + k] for k in range(4))
    return {"law": {k: float(v) for k, v in law.items()},
            "B3_conditional_mean_d": float(b3), "B3_p_r0": float(law[0]),
            "A5_mean_d": float(a5)}


# --------------------------------------------------------------------------
# Monte Carlo cell estimator
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class CellEstimate:
    arm: str
    n: int
    d_input: int
    replicates: int
    positive: int
    mean_d: float
    sd_d: float
    se_d: float
    mean_r: float
    p_r0: float


def estimate_cell(arm: str, n: int, d: int, replicates: int,
                  rng: np.random.Generator, chunk: int = 4096) -> CellEstimate:
    """Mean MM dimension over R>0 replicates (arm A: all), with i.i.d. SE."""
    table = inverse_table(n)
    c = n * (n - 1) // 2
    s = s2 = 0.0
    pos = 0
    rsum = 0
    done = 0
    while done < replicates:
        b = min(chunk, replicates - done)
        r = arm_counts(arm, n, d, b, rng)
        rsum += int(r.sum())
        dv = table[r[r > 0]]
        pos += dv.size
        s += float(dv.sum())
        s2 += float(np.dot(dv, dv))
        done += b
    mean = s / pos if pos else math.nan
    var = (s2 - pos * mean * mean) / (pos - 1) if pos > 1 else math.nan
    var = max(var, 0.0) if pos > 1 else var
    sd = math.sqrt(var) if pos > 1 else math.nan
    return CellEstimate(arm, n, d, replicates, pos, mean, sd,
                        sd / math.sqrt(pos) if pos > 1 else math.nan,
                        rsum / (replicates * c), 1.0 - pos / replicates)


# --------------------------------------------------------------------------
# D=2 positive control and decision arithmetic
# --------------------------------------------------------------------------

ARCHIVED_D2 = Path(__file__).resolve().parents[2] / "docs" / "experiments" / \
    "d2-e0-v1-20261111" / "ensemble_comparison.csv"


def archived_d2_exact(path: Path = ARCHIVED_D2) -> dict:
    """{('A', N): E[d], ('B', N): E[d | R>0]} from the archived exact table."""
    out = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            n = int(row["N"])
            out[("A", n)] = float(row["endpoint_mean_dimension"])
            out[("B", n)] = float(row["no_endpoint_conditional_mean_dimension"])
    return out


def positive_control_z(est: CellEstimate, exact: float) -> float:
    """(MC - exact) / SE; the proposed gate is |z| <= 4."""
    if not est.se_d > 0:
        return 0.0 if est.mean_d == exact else math.inf
    return (est.mean_d - exact) / est.se_d


def detectable_bias(sd: float, n_eff: int, gate: float = 4.0,
                    power: float = 0.9) -> float:
    """Smallest |bias| detected by the |z|>gate rule with the stated power
    (one-sided approximation, normal SE)."""
    return (gate + norm.ppf(power)) * sd / math.sqrt(n_eff)


def bonferroni_z(alpha: float, family: int) -> float:
    return float(norm.isf(alpha / (2 * family)))


def classify(delta: float, se: float, z: float) -> str:
    if delta - z * se > 0:
        return "ABOVE"
    if delta + z * se < 0:
        return "BELOW"
    return "UNRESOLVED"
