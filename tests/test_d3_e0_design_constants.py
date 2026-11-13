"""Checks of the exact constants quoted in docs/CS0_D3_E0_CONTROL_PROPOSAL.md.

Design-level identities only (no sampling, no D=3 result)."""

from fractions import Fraction

import math

import numpy as np
import pytest

from emergence_lab.causal_set_mm import (
    expected_ordering_fraction as f,
    myrheim_meyer_dimension as d_mm,
    sprinkle_diamond,
    causal_matrix,
)

GRID = (2, 3, 4, 5, 6, 8, 12, 16, 24, 32)
P3 = Fraction(8, 35)


def arm_a_mean_r(n: int) -> Fraction:
    c = Fraction(n * (n - 1), 2)
    m = n - 2
    return (2 * n - 3 + P3 * Fraction(m * (m - 1), 2)) / c


def test_f3_is_8_over_35():
    assert f(3) == pytest.approx(float(P3), abs=1e-15)


@pytest.mark.parametrize("n,expected", [(4, Fraction(61, 70)), (8, Fraction(115, 196)),
                                        (16, Fraction(83, 200)), (32, Fraction(1123, 3472))])
def test_arm_a_mean_r_values(n, expected):
    assert arm_a_mean_r(n) == expected


@pytest.mark.parametrize("n", range(2, 65))
def test_arm_a_closed_form_and_below_three(n):
    c = Fraction(n * (n - 1), 2)
    assert arm_a_mean_r(n) == P3 + Fraction(27, 35) * (2 * n - 3) / c
    assert arm_a_mean_r(n) > P3
    assert d_mm(float(arm_a_mean_r(n))) < 3.0


def test_arm_a_n4_exact_expected_dimension():
    d56 = d_mm(5 / 6)
    assert d56 == pytest.approx(1.283914, abs=1e-6)
    e = (27 / 35) * d56 + 8 / 35
    assert e == pytest.approx(1.219020, abs=1e-6)
    # Same inverse value reproduces the archived D2-E0 N=4 entry.
    assert 0.5 * d56 + 0.5 == pytest.approx(1.141957, abs=1e-6)


def test_grid_positive_fractions_are_invertible():
    assert f(10) == pytest.approx(4.995e-4, rel=1e-3)
    for n in GRID:
        c = n * (n - 1) // 2
        assert 1 / c > f(10)
        assert math.isfinite(d_mm(1 / c))


def test_bonferroni_threshold():
    from scipy.stats import norm
    z = norm.ppf(1 - 0.01 / 20 / 2)
    assert z == pytest.approx(3.48, abs=0.005)


def test_inverse_convex_at_design_points():
    h = 1e-4
    for r in (0.1, 0.2286, 0.4, 0.6):
        assert d_mm(r + h) - 2 * d_mm(r) + d_mm(r - h) > 0


def test_existing_sampler_pair_probability_d3_smoke():
    rng = np.random.default_rng(20261112)
    trials = 20000
    pts = sprinkle_diamond(2 * trials, 3, rng)
    a, b = pts[:trials], pts[trials:]
    dt = b[:, 0] - a[:, 0]
    dx2 = np.sum((b[:, 1:] - a[:, 1:]) ** 2, axis=1)
    p = float(np.mean(dt * dt > dx2))
    # Cross-check the vectorised pair test against causal_matrix on a few pairs.
    for i in range(50):
        prec = causal_matrix(np.stack([a[i], b[i]]))
        assert bool(prec[0, 1] or prec[1, 0]) == bool(dt[i] ** 2 > dx2[i])
    se = math.sqrt(float(P3) * (1 - float(P3)) / trials)
    assert abs(p - float(P3)) < 5 * se
