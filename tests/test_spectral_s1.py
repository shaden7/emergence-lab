"""S1 implementation tests (prereg docs/SPECTRAL_S1_PREREGISTRATION.md v0.2).

Engineering seeds only (TEST_SEED_BASE); the pilot seed base is never drawn here.
"""
import math
from fractions import Fraction

import numpy as np
import pytest

from emergence_lab.dimension_d1 import _from_edges, torus_lattice
from emergence_lab.dimension_d2 import CAY
from emergence_lab.spectral_dimension import graph_even_returns, torus_even_return_fourier
from emergence_lab import spectral_s1 as s1


def _graph(n, edges):
    u, v = zip(*edges)
    return _from_edges(n, np.array(u), np.array(v))


def test_seed_bases_are_distinct_and_pilot_locked(monkeypatch):
    import json
    cfg = json.loads(open("configs/spectral_s1_pilot.json").read())
    assert cfg["seed_base"] == s1.PILOT_SEED_BASE
    assert cfg["statistics"]["bootstrap_seed"] == s1.BOOTSTRAP_SEED
    assert len({s1.TEST_SEED_BASE, s1.PILOT_SEED_BASE, s1.BOOTSTRAP_SEED, 2036101101}) == 4
    monkeypatch.delenv("S1_ALLOW_PILOT_SEEDS", raising=False)
    with pytest.raises(PermissionError):
        s1.build_instance(CAY, 64, 0, 0, 4, s1.PILOT_SEED_BASE)


def test_config_constants_match_module():
    import json
    cfg = json.loads(open("configs/spectral_s1_pilot.json").read())
    assert cfg["kernel"]["eta"] == s1.ETA
    assert cfg["kernel"]["R_start"] == s1.R_START
    assert cfg["kernel"]["per_source_edge_step_cap"] == s1.EDGE_STEP_CAP


def test_ball_on_path():
    g = _graph(7, [(i, i + 1) for i in range(6)])
    assert sorted(s1.ball(g, 3, 0).tolist()) == [3]
    assert sorted(s1.ball(g, 3, 2).tolist()) == [1, 2, 3, 4, 5]
    assert sorted(s1.ball(g, 0, 10).tolist()) == list(range(7))


def test_hand_computed_returns_star_and_k2():
    # K2: walk alternates, [P^(2t)]_00 = 1.
    g = _graph(2, [(0, 1)])
    r = s1.killed_ball_returns(g, 0, 4, 8)
    assert np.allclose(r.q_lower, 1.0) and r.killed[-1] == 0
    # Star K_{1,4}, centre 0: every 2 steps returns to the centre with probability 1.
    star = _graph(5, [(0, k) for k in range(1, 5)])
    assert np.allclose(s1.killed_ball_returns(star, 0, 3, 6).q_lower, 1.0)
    # From a leaf: P^2_ll = 1/4 and P^(2t)_ll = 1/4 for all t >= 1.
    assert np.allclose(s1.killed_ball_returns(star, 1, 3, 6).q_lower, 0.25)


@pytest.mark.parametrize("graph", [
    torus_lattice(1, 8), torus_lattice(2, 6),
    _graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)]),
    _graph(9, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (5, 6), (6, 7), (6, 8)]),
])
def test_unkilled_ball_equals_dense_powers(graph):
    P = graph.csr().toarray() / graph.degrees[:, None]
    T = 6
    for v in range(graph.n):
        r = s1.killed_ball_returns(graph, v, T, 2 * T, identity_times=range(1, T + 1))
        for t in range(1, T + 1):
            direct = np.linalg.matrix_power(P, 2 * t)[v, v]
            assert abs(r.q_lower[t - 1] - direct) <= 1e-12
            assert abs(r.identity[t] - direct) <= 1e-12
        assert r.killed[-1] == 0.0


def test_bracket_on_long_path_with_small_radius():
    g = _graph(101, [(i, i + 1) for i in range(100)])
    T = 40
    exact = graph_even_returns(g, 50, range(1, T + 1))
    for R in (1, 3, 7, 15, 31):
        r = s1.killed_ball_returns(g, 50, T, R)
        for t in range(1, T + 1):
            assert r.q_lower[t - 1] <= exact[t] + 1e-15
            assert exact[t] <= r.q_lower[t - 1] + r.killed[t - 1] + 1e-15
        assert np.all(np.diff(r.killed) >= -1e-15)  # killed mass non-decreasing


def test_radius_rule_doubles_until_certified():
    g = torus_lattice(2, 256)  # killing is active at R = 64 for T = 256
    T = 256
    r = s1.certified_returns(g, 0, T, r_start=16)
    assert r.R >= 16 and (r.killed[-1] <= s1.ETA * r.q_lower[-1] or r.R >= 2 * T)
    for t in (16, 64, 256):
        ref = torus_even_return_fourier(2, 256, t)
        assert r.q_lower[t - 1] - 1e-12 <= ref <= r.q_lower[t - 1] + r.killed[t - 1] + 1e-12
    first = s1.killed_ball_returns(g, 0, T, 16)
    assert first.killed[-1] > s1.ETA * first.q_lower[-1]  # the rule had to act


def test_over_cap_is_recorded_not_dropped():
    g = torus_lattice(2, 32)
    r = s1.certified_returns(g, 0, 64, edge_step_cap=10)
    assert r.status == "OVER_CAP" and np.isnan(r.q_lower).all()
    csv = s1.rows_csv([(CAY, 32, 0, 0, r)], 64).decode()
    assert "OVER_CAP" in csv


def test_even_time_monotonicity_on_trees():
    g, srcs = s1.build_instance(CAY, 2048, 0, 0, 4, s1.TEST_SEED_BASE)
    for v in srcs.tolist():
        assert s1.even_time_monotone(s1.certified_returns(g, v, 128).q_lower)
    assert not s1.even_time_monotone(np.array([0.5, 0.4, 0.41]))


def test_exact_enumeration_small_cases():
    # N=3: only paths. Centre: q=1 always; leaves: 1/2. Annealed = (1 + 1/2 + 1/2)/3 = 2/3.
    ex = s1.exact_annealed_cayley(3, (1, 2))
    assert ex[1] == Fraction(2, 3) and ex[2] == Fraction(2, 3)
    # N=4: 4 stars and 12 paths. Star: centre 1, leaves 1/3 -> 2/4 per star.
    # Path a-b-c-d: q1(a)=1/2, q1(b)=3/4 -> mean 5/8. Annealed = (4*1/2 + 12*5/8)/16.
    assert s1.exact_annealed_cayley(4, (1,))[1] == (4 * Fraction(1, 2) + 12 * Fraction(5, 8)) / 16


@pytest.mark.parametrize("n", [5, 6])
def test_p0a_pipeline_matches_exact(n):
    rep = s1.p0a(ns=(n,))
    assert rep["pass"], rep


def test_p0b_and_p0c_pass():
    assert s1.p0b(sources_per_instance=2)["pass"]
    assert s1.p0c(n_sources=8)["pass"]


def test_p0d_csv_is_deterministic_in_process():
    assert s1.p0d_tree_csv(n=1024, T=64, n_sources=4) == s1.p0d_tree_csv(n=1024, T=64, n_sources=4)


# ----------------------------------------------------------------------------- statistics
TIMES = [1, 2, 4, 8, 16, 32, 64]


def _synthetic(n_trees, ds, rng, noise=0.05):
    """Per-tree Q(t) = a_i t^(-ds/2) with lognormal tree prefactors (known annealed slope ds)."""
    a = np.exp(rng.normal(0, noise, size=(n_trees, 1)))
    return a * np.power(np.array(TIMES, float), -ds / 2)[None, :]


def test_annealed_slope_recovers_pure_power_law():
    Q = _synthetic(8, 4 / 3, np.random.default_rng(1))
    assert abs(s1.annealed_window_slope(Q, 8, 64, TIMES) - 4 / 3) < 1e-12
    psi = s1.tree_influences(Q, 8, 64, TIMES)
    assert np.allclose(psi, 0, atol=1e-12)  # common shape: no slope variation across trees


def test_influence_matches_numerical_derivative():
    rng = np.random.default_rng(2)
    Q = np.exp(rng.normal(0, 0.2, size=(8, len(TIMES)))) * np.power(np.array(TIMES, float), -0.7)
    psi = s1.tree_influences(Q, 8, 64, TIMES)
    base = s1.annealed_window_slope(Q, 8, 64, TIMES)
    eps = 1e-6
    for i in range(8):
        w = np.ones(8)
        w[i] += eps
        Qw = Q * (w[:, None] / w.mean())  # reweighting tree i
        num = (s1.annealed_window_slope(Qw, 8, 64, TIMES) - base) / eps
        # d/d(eps) of the weighted annealed slope at eps = 0 is psi_i / n
        assert abs(num - psi[i] / 8) < 1e-5


def test_power_projection_formula():
    psi = np.array([0.1, -0.1, 0.05, -0.05, 0.2, -0.2, 0.0, 0.0])
    pr = s1.power_projection(psi, [8, 32])
    from scipy import stats
    U = 7 * psi.var(ddof=1) / stats.chi2.ppf(0.05, 7)
    assert math.isclose(pr["U"], U)
    assert math.isclose(pr["h"][32], stats.t.ppf(0.975, 31) * math.sqrt(U / 32))
    assert s1.power_projection(psi, [32], multiplier=3)["h"][32] > pr["h"][32]


def test_reliability_screen():
    ok = s1.projection_reliability(np.array([0.1, -0.1, 0.05, -0.05, 0.2, -0.2, 0.01, -0.01]), [1e-3, 1e-4])
    assert ok["reliable"]
    one_dominant = s1.projection_reliability(np.array([1.0, 0, 0, 0, 0, 0, 0, -0.01]), [1, 1])
    assert not one_dominant["reliable"] and "influence_share" in one_dominant["reasons"]
    assert "zero_variance" in s1.projection_reliability(np.zeros(8), [1])["reasons"]
    assert "nonpositive_mean" in s1.projection_reliability(np.array([1., -1, 1, -1, 1, -1, 1, -1]), [0])["reasons"]


def test_size_equivalence_tost_like():
    rng = np.random.default_rng(3)
    same = s1.size_equivalence(_synthetic(8, 1.3, rng, 0.001), _synthetic(8, 1.3, rng, 0.001), 8, 64, TIMES)
    assert same["equivalent"]
    shifted = s1.size_equivalence(_synthetic(8, 1.3, rng, 0.001), _synthetic(8, 1.4, rng, 0.001), 8, 64, TIMES)
    assert not shifted["equivalent"]
    # wide noise: CI contains 0 but is not within the margin -> not equivalent
    noisy = s1.size_equivalence(_synthetic(8, 1.3, rng, 0.0) * np.exp(rng.normal(0, 0.3, (8, 7))),
                                _synthetic(8, 1.3, rng, 0.0) * np.exp(rng.normal(0, 0.3, (8, 7))), 8, 64, TIMES)
    assert not noisy["equivalent"]


def test_bootstrap_is_seeded():
    Q = np.exp(np.random.default_rng(4).normal(0, 0.1, (8, 7))) * np.power(np.array(TIMES, float), -0.6)
    a = s1.bootstrap_slopes(Q, 8, 64, TIMES, n_boot=256)
    b = s1.bootstrap_slopes(Q, 8, 64, TIMES, n_boot=256)
    assert a == b and a["seed"] == s1.BOOTSTRAP_SEED


def test_windows_and_adjacent_slopes():
    w = s1.candidate_windows(4096)
    assert (8, 64) in w and (4, 32) not in w and (8, 32) not in w and (512, 4096) in w
    assert all(hi // lo >= 8 and lo >= 8 for lo, hi in w)
    qbar = np.power(np.array(TIMES, float), -0.65)
    assert s1.adjacent_slopes_ok(qbar, TIMES, 8, 64)
    bent = qbar.copy()
    bent[-1] *= 0.8
    assert not s1.adjacent_slopes_ok(bent, TIMES, 8, 64)


def test_headroom_uses_vertex_specific_floor():
    # floors deg/(N-1): 0.01 and 0.04 -> ratios 1.0 and 0.5
    assert math.isclose(s1.headroom_min(np.array([0.01, 0.02]), np.array([1, 4]), 101), 0.5)
