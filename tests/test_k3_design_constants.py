"""Checks of the constants quoted in docs/CS0_K3_CHAIN_ESTIMATOR_PROPOSAL.md.

Design-level identities and deterministic small checks only.  No target cell is
sampled; no K3 result is computed here."""

from fractions import Fraction

import math

import mpmath as mp
import numpy as np
import pytest
from scipy.stats import norm

from emergence_lab.causal_set_mm import expected_ordering_fraction as f
from emergence_lab.d3_e0 import direct_sample, k_chain_probability

GRID_K3 = (3, 4, 5, 6, 8, 12, 16, 24, 32)
# All mpmath work runs under ``mp.workdps(40)`` (no global precision change).


def g3(d):
    """Probability that 3 i.i.d. uniform diamond points form a chain (any order)."""
    d = mp.mpf(d)
    chi3 = ((mp.gamma(d + 1) / 2) ** 2 * mp.gamma(d / 2) * mp.gamma(d)
            / (3 * mp.gamma(3 * d / 2) * mp.gamma(2 * d)))
    return 6 * chi3


def d3_inverse(c):
    with mp.workdps(40):
        return mp.findroot(lambda x: g3(x) - c, (1, 10), solver="bisect")


@pytest.fixture(autouse=True)
def _precision():
    with mp.workdps(40):
        yield


def causal(points):
    """(batch, n, n) boolean strict-precedence matrix (row precedes column)."""
    dif = points[:, None, :, :] - points[:, :, None, :]
    dt = dif[..., 0]
    dx2 = np.sum(dif[..., 1:] ** 2, axis=-1)
    return (dt > 0) & (dt ** 2 > dx2)


def three_chains(prec):
    """C_3 = sum_y |past(y)| * |future(y)| (valid because the order is transitive)."""
    return np.sum(prec.sum(axis=1) * prec.sum(axis=2), axis=1)


@pytest.mark.parametrize("d,expected", [(1, Fraction(1)), (2, Fraction(1, 6)),
                                        (3, Fraction(4, 175)), (4, Fraction(1, 350))])
def test_g3_rational_values(d, expected):
    assert abs(g3(d) - mp.mpf(expected.numerator) / expected.denominator) < mp.mpf(10) ** -30


@pytest.mark.parametrize("d", [2, 3, 4])
def test_g3_matches_existing_k_chain_closed_form(d):
    assert float(g3(d)) == pytest.approx(6 * k_chain_probability(3, d), rel=1e-12)
    # k=2 consistency of the same closed form with the MM ordering fraction.
    assert 2 * k_chain_probability(2, d) == pytest.approx(f(d), rel=1e-12)


def test_g3_decreasing_and_convex_on_bracket():
    xs = [1 + 9 * i / 90 for i in range(91)]
    vals = [g3(x) for x in xs]
    assert all(a > b for a, b in zip(vals, vals[1:]))
    for x in xs[1:-1]:
        assert mp.diff(g3, x) < 0
        assert mp.diff(g3, x, 2) > 0


def test_grid_positive_fractions_invertible():
    assert g3(10) < mp.mpf("6e-9")
    for n in GRID_K3:
        assert mp.mpf(1) / math.comb(n, 3) > g3(10)


def test_arm_a_n4_exact_values():
    d_half = d3_inverse(mp.mpf(1) / 2)
    assert float(d_half) == pytest.approx(1.407226187, abs=1e-9)
    for d, p, expected in [(2, 0.5, 1.203613093), (3, 8 / 35, 1.314145915)]:
        assert float((1 - p) * d_half + p) == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize("d", [2, 3])
def test_arm_a_mean_c3_exceeds_g3(d):
    g = g3(d)
    for n in GRID_K3:
        m = n - 2
        mean_c3 = (math.comb(m, 3) * g + 2 * math.comb(m, 2) * f(d) + m) / math.comb(n, 3)
        assert mean_c3 > g
        assert d3_inverse(mean_c3) < d


def test_bonferroni_z_for_32_stochastic_cells():
    # 2 dimensions x 2 arms x 9 N, minus the 4 cells with d3 = 1 identically.
    assert 2 * 2 * len(GRID_K3) - 4 == 32
    assert norm.ppf(1 - 0.01 / 64) == pytest.approx(3.6047, abs=1e-4)


def test_three_chain_count_formula_and_arm_a_identity():
    rng = np.random.default_rng(20261122)
    for d in (2, 3):
        pts = direct_sample(200, 7, d, rng)
        prec = causal(pts)
        # brute-force triple count
        brute = np.zeros(pts.shape[0], dtype=np.int64)
        n = pts.shape[1]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    brute += prec[:, i, j] & prec[:, j, k]
        assert np.array_equal(brute, three_chains(prec))
        # arm A: tips (-1/2, 0) and (+1/2, 0) added to m = 7 interior points
        tips = np.zeros((pts.shape[0], 2, d))
        tips[:, 0, 0], tips[:, 1, 0] = -0.5, 0.5
        full = np.concatenate([tips[:, :1], pts, tips[:, 1:]], axis=1)
        r_inner = prec.sum(axis=(1, 2))
        assert np.array_equal(three_chains(causal(full)),
                              three_chains(prec) + 2 * r_inner + n)
