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


# --- design r1 additions (review r1 of PR #86) ---------------------------------

def d3_of_c(c):
    """r1 boundary rule: c_3 = 1 (total order) maps to d_3 = 1 explicitly."""
    if c == 1:
        return mp.mpf(1)
    return d3_inverse(c)


def test_r1_boundary_rule_total_order():
    assert d3_of_c(1) == 1
    # double-precision g_3(1) is not exactly 1, which is why the rule is explicit
    assert float(g3(1)) == pytest.approx(1.0, abs=1e-12)


def test_r1_cell_partition_and_bonferroni():
    deterministic = {(d, arm, 3) for d in (2, 3) for arm in "AB"}
    exact = ({(2, "A", n) for n in GRID_K3 if 4 <= n and n - 2 <= 9}
             | {(2, "B", n) for n in GRID_K3 if 4 <= n <= 9}
             | {(3, "A", 4)})
    assert len(deterministic) == 4 and len(exact) == 9
    stochastic = 2 * 2 * len(GRID_K3) - len(deterministic) - len(exact)
    assert stochastic == 23
    tests = 2 * stochastic
    assert norm.ppf(1 - 0.01 / (2 * tests)) == pytest.approx(3.6979, abs=1e-4)


def _d2_arm_b_exact(n):
    """Exact D=2 arm-B means by S_n enumeration (permutation <-> light-cone order)."""
    import itertools
    from emergence_lab.causal_set_mm import myrheim_meyer_dimension as mm
    b2, b3 = math.comb(n, 2), math.comb(n, 3)
    mm_r, mm_c, k3, n_r, n_c = 0.0, 0.0, mp.mpf(0), 0, 0
    upper = np.triu(np.ones((n, n), bool), 1)
    for perm in itertools.permutations(range(n)):
        a = np.array(perm)
        lt = (a[None, :] > a[:, None]) & upper
        r, c3 = int(lt.sum()), int((lt.sum(0) * lt.sum(1)).sum())
        if r > 0:
            mm_r += mm(r / b2); n_r += 1
        if c3 > 0:
            mm_c += mm(r / b2); k3 += d3_of_c(mp.mpf(c3) / b3); n_c += 1
    return mm_r / n_r, mm_c / n_c, float(k3 / n_c)


@pytest.mark.parametrize("n,mm_r_archived,mm_matched,d3_matched", [
    (4, 2.0731669723898114, 1.52795, 1.59389),
    (5, 2.102161560251244, 1.78605, 1.88108),
    (6, 2.0861912679526076, 1.92107, 2.02906),
])
def test_r1_d2_arm_b_exact_small_n(n, mm_r_archived, mm_matched, d3_matched):
    # MM | R>0 reproduces docs/experiments/d2-m0-run-20261107/curve.csv
    mm_r, mm_c, k3 = _d2_arm_b_exact(n)
    assert mm_r == pytest.approx(mm_r_archived, abs=1e-9)
    assert mm_c == pytest.approx(mm_matched, abs=1e-5)
    assert k3 == pytest.approx(d3_matched, abs=1e-5)


# --- design r2 additions (review r2 of PR #86) ---------------------------------

def _d2_exact_cached(n, arm):
    """Exact D=2 means for arm A (tips + n-2 interior) or arm B (matched C_3>0).

    Same permutation <-> light-cone-order correspondence as above; d_3 and MM
    inverses are cached per distinct count so N=8 stays fast."""
    import itertools
    from emergence_lab.causal_set_mm import myrheim_meyer_dimension as mm
    b2, b3 = math.comb(n, 2), math.comb(n, 3)
    m = n - 2 if arm == "A" else n
    cache_mm, cache_k3 = {}, {}
    s_mm = s_k3 = 0.0
    count = 0
    upper = np.triu(np.ones((m, m), bool), 1)
    for perm in itertools.permutations(range(m)):
        a = np.array(perm)
        lt = (a[None, :] > a[:, None]) & upper
        r, c3 = int(lt.sum()), int((lt.sum(0) * lt.sum(1)).sum())
        if arm == "A":
            r, c3 = r + 2 * m + 1, c3 + 2 * r + m  # tips: identity C_3 = C_3,in + 2R_in + m
        if c3 == 0:
            continue
        if r not in cache_mm:
            cache_mm[r] = mm(r / b2)
        if c3 not in cache_k3:
            cache_k3[c3] = float(d3_of_c(mp.mpf(c3) / b3))
        s_mm += cache_mm[r]
        s_k3 += cache_k3[c3]
        count += 1
    return s_mm / count, s_k3 / count


@pytest.mark.parametrize("n,arm,mm_exact,d3_exact", [
    (8, "B", 2.02070, 2.11941),
    (4, "A", 1.141957, 1.203613),
    (5, "A", 1.260178, 1.321927),
    (6, "A", 1.352235, 1.404288),
    (8, "A", 1.482809, 1.516029),
])
def test_r2_d2_exact_cells(n, arm, mm_exact, d3_exact):
    mm_v, k3_v = _d2_exact_cached(n, arm)
    assert mm_v == pytest.approx(mm_exact, abs=1e-5)
    assert k3_v == pytest.approx(d3_exact, abs=1e-5)


def sign_pattern(labels):
    """r2 rule. labels: list over the grid in N order, each 'A', 'B' or 'U'.

    Returns (terminal, changes) or None if UNDETERMINED. changes is a tuple of
    (from, to) pairs; crossover brackets are not part of the comparison."""
    if labels[-1] == "U":
        return None
    resolved = [(i, s) for i, s in enumerate(labels) if s != "U"]
    for (i, a), (j, b) in zip(resolved, resolved[1:]):
        if a == b and j - i > 1:  # an UNRESOLVED gap between equal signs may hide two changes
            return None
    changes = tuple((a, b) for (_, a), (_, b) in zip(resolved, resolved[1:]) if a != b)
    return labels[-1], changes


def compare_patterns(mm_labels, k3_labels):
    p, q = sign_pattern(mm_labels), sign_pattern(k3_labels)
    if p is None or q is None:
        return "UNDETERMINED"
    return "PATTERN-CONSISTENT" if p == q else "PATTERN-DIFFERENT"


def test_r2_pattern_rule_cases():
    # crossover shift only: consistent despite a DISCORDANT cell
    assert compare_patterns(list("BBBBAAAAA"), list("BBBAAAAAA")) == "PATTERN-CONSISTENT"
    # different terminal sign
    assert compare_patterns(list("BBBBAAAAA"), list("BBBBBBBBB")) == "PATTERN-DIFFERENT"
    # same terminal sign, different number of changes
    assert compare_patterns(list("BBBBBBBBB"), list("BBAABBBBB")) == "PATTERN-DIFFERENT"
    # UNRESOLVED next to a crossover is harmless
    assert compare_patterns(list("BBBUAAAAA"), list("BBUAAAAAA")) == "PATTERN-CONSISTENT"
    # UNRESOLVED between equal signs, or at N=32, is UNDETERMINED
    assert compare_patterns(list("BBUBAAAAA"), list("BBBBAAAAA")) == "UNDETERMINED"
    assert compare_patterns(list("BBBBAAAAU"), list("BBBBAAAAA")) == "UNDETERMINED"


def test_r2_known_d2_cells_are_crossover_shift_not_pattern_difference():
    # exact D=2 labels at N = 3, 4, 5, 6, 8 (N=3 deterministic B); N >= 12 is blind
    mm_b = ["B"] + ["A" if v > 2 else "B" for v in (1.52795, 1.78605, 1.92107, 2.02070)]
    k3_b = ["B"] + ["A" if v > 2 else "B" for v in (1.59389, 1.88108, 2.02906, 2.11941)]
    assert mm_b == list("BBBBA") and k3_b == list("BBBAA")
    assert [a != b for a, b in zip(mm_b, k3_b)] == [False, False, False, True, False]
    # on the known prefix the change signatures agree (one B->A each)
    assert sign_pattern(mm_b)[1] == sign_pattern(k3_b)[1] == (("B", "A"),)
