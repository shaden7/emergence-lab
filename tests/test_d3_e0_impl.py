"""Implementation gates for D3-E0/M0 r1 (proposed design, not frozen).

Gates exercised here at small engineering sizes: sampler agreement, quadrature
vs literature closed form, quadrature-derived laws vs archived D=2 exact values
and vs Monte Carlo, D=2 Monte Carlo positive control. No D=3 target campaign."""

import math

import numpy as np
import pytest
from scipy.stats import chi2_contingency

from emergence_lab import d3_e0 as m
from emergence_lab.causal_set_mm import causal_matrix, sprinkle_diamond


def rng(*key):
    return np.random.default_rng(np.random.SeedSequence(20261114, spawn_key=key))


def test_direct_sample_in_diamond_and_marginal():
    pts = m.direct_sample(20000, 1, 3, rng(1)).reshape(-1, 3)
    assert np.all(np.abs(pts[:, 0]) + np.linalg.norm(pts[:, 1:], axis=1) <= 0.5 + 1e-15)
    # E|t| for density (1/2-|t|)^2 on [0,1/2]: 1/8.
    se = np.std(np.abs(pts[:, 0])) / math.sqrt(len(pts))
    assert abs(np.mean(np.abs(pts[:, 0])) - 0.125) < 4 * se


def test_relation_counts_match_causal_matrix():
    pts = m.direct_sample(50, 7, 3, rng(2))
    got = m.relation_counts(pts)
    ref = [int(causal_matrix(p).sum()) for p in pts]
    assert got.tolist() == ref


@pytest.mark.parametrize("d", [2, 3])
def test_pair_probability_both_samplers(d):
    f = m.mm_forward(d)
    n_rep = 40000
    direct = m.relation_counts(m.direct_sample(n_rep, 2, d, rng(3, d)))
    g = rng(4, d)
    rej = np.array([int(causal_matrix(sprinkle_diamond(2, d, g, batch=16)).sum())
                    for _ in range(n_rep)])
    se = math.sqrt(f * (1 - f) / n_rep)
    assert abs(direct.mean() - f) < 4 * se
    assert abs(rej.mean() - f) < 4 * se


@pytest.mark.parametrize("n", [3, 4, 8])
def test_r_distribution_samplers_agree(n):
    n_rep = 6000
    a = m.relation_counts(m.direct_sample(n_rep, n, 3, rng(5, n)))
    g = rng(6, n)
    b = np.array([int(causal_matrix(sprinkle_diamond(n, 3, g, batch=64)).sum())
                  for _ in range(n_rep)])
    c = n * (n - 1) // 2
    ca = np.bincount(a, minlength=c + 1)
    cb = np.bincount(b, minlength=c + 1)
    keep = (ca + cb) > 0
    p = chi2_contingency(np.vstack([ca[keep], cb[keep]]))[1]
    assert p > 1e-3


def test_arm_a_identity():
    r = m.arm_counts("A", 6, 3, 200, rng(7))
    assert r.min() >= 2 * 6 - 3 and r.max() <= 15


@pytest.mark.parametrize("n", m.GRID)
def test_inverse_table_defined_on_grid(n):
    t = m.inverse_table(n)
    assert math.isnan(t[0]) and t[-1] == 1.0
    assert np.all(np.isfinite(t[1:])) and np.all(np.diff(t[1:]) < 0)
    assert np.nanmax(t) < 10.0


@pytest.mark.parametrize("d", [2, 3])
def test_quadrature_matches_closed_forms(d):
    q = m.three_point_probabilities(d)
    assert float(q["q_pair"]) == pytest.approx(m.mm_forward(d) / 2, rel=1e-12)
    assert float(q["q_pair"]) == pytest.approx(m.k_chain_probability(2, d), rel=1e-12)
    assert float(q["q_chain"]) == pytest.approx(m.k_chain_probability(3, d), rel=1e-12)


def test_quadrature_d2_exact_light_cone_values():
    q = m.three_point_probabilities(2)
    assert float(q["q_chain"]) == pytest.approx(1 / 36, rel=1e-14)
    assert float(q["q_down"]) == pytest.approx(1 / 9, rel=1e-14)


def test_quadrature_d3_rationals():
    q = m.three_point_probabilities(3)
    assert float(q["q_chain"]) == pytest.approx(2 / 525, rel=1e-13)
    assert float(q["q_down"]) == pytest.approx(1 / 30, rel=1e-13)


def test_quadrature_cells_reproduce_archived_d2_exact():
    ex = m.archived_d2_exact()
    cells = m.exact_three_point_cells(2)
    assert cells["B3_conditional_mean_d"] == pytest.approx(ex[("B", 3)], abs=1e-12)
    assert cells["A5_mean_d"] == pytest.approx(ex[("A", 5)], abs=1e-12)


def test_mc_three_point_law_matches_quadrature_d3():
    law = m.three_point_r_law(3)
    n_rep = 200000
    r = m.relation_counts(m.direct_sample(n_rep, 3, 3, rng(8)))
    counts = np.bincount(r, minlength=4)
    for k in range(4):
        p = float(law[k])
        se = math.sqrt(p * (1 - p) / n_rep)
        assert abs(counts[k] / n_rep - p) < 4 * se


@pytest.mark.parametrize("arm,n", [("A", 4), ("B", 4), ("A", 8), ("B", 8), ("B", 16)])
def test_d2_positive_control_small(arm, n):
    ex = m.archived_d2_exact()[(arm, n)]
    est = m.estimate_cell(arm, n, 2, 20000, rng(9, ord(arm), n))
    assert abs(m.positive_control_z(est, ex)) <= 4.0


def test_deterministic_cells():
    for arm, n in m.DETERMINISTIC_CELLS:
        est = m.estimate_cell(arm, n, 3, 500, rng(10, ord(arm), n))
        assert est.mean_d == 1.0 and est.sd_d == 0.0


def test_decision_arithmetic():
    assert m.bonferroni_z(0.01, 20) == pytest.approx(3.4808, abs=1e-4)
    assert m.bonferroni_z(0.01, 17) == pytest.approx(3.4370, abs=1e-4)
    assert m.classify(0.1, 0.01, 3.48) == "ABOVE"
    assert m.classify(-0.1, 0.01, 3.48) == "BELOW"
    assert m.classify(0.01, 0.01, 3.48) == "UNRESOLVED"
    # (4 + 1.2816) * 0.5 / sqrt(1e5) ~ 0.00835
    assert m.detectable_bias(0.5, 100000) == pytest.approx(0.008352, abs=2e-5)
