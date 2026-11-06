"""Development checks for the proposed CS0 Myrheim–Meyer reference library.

Exact/analytic identities are tested exactly. The few stochastic checks are
fixed-seed *development* sanity checks with deliberately loose tolerances; they
are not CS0 gate evaluations and produce no reported result.
"""

import math
from fractions import Fraction

import numpy as np
import pytest

from emergence_lab import causal_set_mm as mm


@pytest.mark.parametrize("d,exact", [(1, Fraction(1)), (2, Fraction(1, 2)),
                                      (3, Fraction(8, 35)), (4, Fraction(1, 10))])
def test_closed_form_values(d, exact):
    assert mm.expected_ordering_fraction(d) == pytest.approx(float(exact), rel=1e-13)


def test_closed_form_monotone_and_inverse_round_trip():
    ds = np.linspace(1.0, 20.0, 200)
    rs = [mm.expected_ordering_fraction(d) for d in ds]
    assert all(a > b for a, b in zip(rs, rs[1:]))
    for d in [1.25, 2.0, 2.5, 3.0, 4.0, 7.3]:
        assert mm.myrheim_meyer_dimension(mm.expected_ordering_fraction(d)) == pytest.approx(d, abs=1e-9)


def test_inverse_out_of_range_is_nan_not_large_dimension():
    assert math.isnan(mm.myrheim_meyer_dimension(0.0))
    assert math.isnan(mm.myrheim_meyer_dimension(-0.1))
    assert math.isnan(mm.myrheim_meyer_dimension(1.1))
    assert mm.myrheim_meyer_dimension(1.0) == 1.0
    with pytest.raises(ValueError):
        mm.expected_ordering_fraction(0.5)


def test_exact_nulls():
    c = mm.measure(mm.chain(50))
    assert (c.r, c.d_mm, c.classification) == (1.0, 1.0, "TOTAL_ORDER")
    a = mm.measure(mm.antichain(50))
    assert a.r == 0.0 and math.isnan(a.d_mm) and a.classification == "OUT_OF_RANGE"
    mm.check_partial_order(mm.chain(20))
    mm.check_partial_order(mm.antichain(20))


def test_partial_order_checker_rejects_violations():
    bad = np.zeros((3, 3), dtype=bool)
    bad[0, 1] = bad[1, 2] = True  # missing 0<2
    with pytest.raises(ValueError, match="transitive"):
        mm.check_partial_order(bad)
    loop = np.eye(2, dtype=bool)
    with pytest.raises(ValueError, match="irreflexive"):
        mm.check_partial_order(loop)
    sym = np.array([[False, True], [True, False]])
    with pytest.raises(ValueError, match="antisymmetric"):
        mm.check_partial_order(sym)


def test_sprinkling_geometry_and_order_validity():
    rng = np.random.default_rng(20261106)
    for d in (2, 3, 4):
        pts = mm.sprinkle_diamond(200, d, rng)
        assert pts.shape == (200, d)
        rad = np.sqrt(np.sum(pts[:, 1:] ** 2, axis=1))
        assert np.all(np.abs(pts[:, 0]) + rad <= 0.5)
        mm.check_partial_order(mm.causal_matrix(pts))


def test_causal_matrix_small_exact_case():
    pts = np.array([[0.0, 0.0], [0.3, 0.1], [0.3, 0.4], [-0.3, 0.0]])
    prec = mm.causal_matrix(pts)
    expected = np.zeros((4, 4), dtype=bool)
    expected[0, 1] = True          # dt=.3 > |dx|=.1; 0 vs 2 spacelike (.3 < .4)
    expected[3, 0] = expected[3, 1] = True
    expected[3, 2] = True          # dt=.6 > |dx|=.4
    assert np.array_equal(prec, expected)


def test_seed_determinism():
    a = mm.causal_matrix(mm.sprinkle_diamond(64, 3, np.random.default_rng(7)))
    b = mm.causal_matrix(mm.sprinkle_diamond(64, 3, np.random.default_rng(7)))
    assert np.array_equal(a, b)


def test_k_order_and_two_layer_are_partial_orders():
    rng = np.random.default_rng(11)
    for k in (1, 2, 3, 4):
        mm.check_partial_order(mm.random_k_order(60, k, rng))
    assert mm.ordering_fraction(mm.random_k_order(40, 1, rng)) == 1.0
    mm.check_partial_order(mm.two_layer_order(60, 0.5, rng))
    assert mm.two_layer_expected_r(10, 1.0) == pytest.approx(25 / 45)


def test_development_sanity_means():
    """Loose fixed-seed sanity only (not a gate): averages land near exact means."""
    rng = np.random.default_rng(20261106)
    for d in (2, 4):
        rs = [mm.ordering_fraction(mm.causal_matrix(mm.sprinkle_diamond(128, d, rng)))
              for _ in range(20)]
        assert abs(np.mean(rs) - mm.expected_ordering_fraction(d)) < 0.05
    rs3 = [mm.ordering_fraction(mm.random_k_order(128, 3, rng)) for _ in range(20)]
    assert abs(np.mean(rs3) - 0.25) < 0.05
