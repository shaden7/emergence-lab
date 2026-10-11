"""Tests for the D2 implementation (prereg v1.0-r3). None of these tests uses the preregistered
seed base 2036101101 or a grid size; they cannot produce a D2 result."""
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import chi2

from emergence_lab import dimension_d1 as d1
from emergence_lab import dimension_d2 as d2

CFG = json.loads(Path("configs/dimension_d2.json").read_text())
TEST_SEED = 515000  # not the D2 seed base


def _key(u, v):
    return tuple(sorted((min(a, b), max(a, b)) for a, b in zip(u.tolist(), v.tolist())))


def _adj(n, u, v):
    adj = [[] for _ in range(n)]
    for a, b in zip(u.tolist(), v.tolist()):
        adj[a].append(b)
        adj[b].append(a)
    return adj


def _profile(adj, s):
    dist = {s: 0}
    q = [s]
    for x in q:
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return Counter(dist.values())


def test_frozen_files_pinned():
    out = d2.validate_frozen_files()
    assert out["prereg_blob_sha"] == d2.PREREG_BLOB_SHA
    assert CFG["seed_base"] == 2036101101
    assert CFG["estimator_parameters"] == {"r_min": 4, "saturation_guard": "8 * Bbar(2r) <= N",
                                           "plateau_epsilon": 0.15, "plateau_min_scales": 3,
                                           "sources": 256}


@pytest.mark.parametrize("n", [3, 4, 5, 6, 7])
def test_prufer_bijection_and_exact_shell_mean(n):
    """All n^(n-2) sequences decode to distinct spanning trees of K_n; the mean distance profile
    of vertex 0 equals (k+1) prod_{i<=k}(1 - i/n) exactly (prereg §4)."""
    trees = set()
    tot = Counter()
    for seq in itertools.product(range(n), repeat=n - 2):
        u, v = d2.prufer_decode(seq)
        assert len(u) == n - 1
        k = _key(u, v)
        trees.add(k)
        g = d1._from_edges(n, u, v)
        assert g.n_edges == n - 1 and d2.is_connected(g)
        tot.update(_profile(_adj(n, u, v), 0))
    assert len(trees) == n ** (n - 2)
    T = n ** (n - 2)
    for k in range(n):
        exact = Fraction(k + 1)
        for i in range(1, k + 1):
            exact *= Fraction(n - i, n)
        assert Fraction(tot.get(k, 0), T) == exact


def test_prufer_known_example():
    # classic example: sequence (3, 3, 3, 4) on 6 vertices (1-based 4,4,4,5)
    u, v = d2.prufer_decode([3, 3, 3, 4])
    assert _key(u, v) == ((0, 3), (1, 3), (2, 3), (3, 4), (4, 5))


def test_cayley_ball_mean_matches_formula_and_d2_table():
    # mean-curve d_hat at 2^18 from the prereg §4 table
    n = 2 ** 18
    radii = [2 ** j for j in range(1, 13)]
    b = d2.cayley_ball_mean(n, radii)
    v = d1.verdict(b, n)
    assert v["verdict"] == d1.PLATEAU and round(v["d_hat"], 4) == 1.9162


def _torus_spanning_tree_count(L):
    n = L * L
    lap = np.zeros((n, n))
    for y in range(L):
        for x in range(L):
            u = y * L + x
            for w in (y * L + (x + 1) % L, ((y + 1) % L) * L + x):
                lap[u, u] += 1; lap[w, w] += 1; lap[u, w] -= 1; lap[w, u] -= 1
    return round(np.linalg.det(lap[1:, 1:]))


def test_wilson_uniform_on_3x3_torus():
    """D2-G0: >= 3e5 draws on the 3x3 torus see every one of the 11664 spanning trees and a
    chi-square uniformity test does not reject at alpha = 1e-3."""
    tau = _torus_spanning_tree_count(3)
    assert tau == 11664
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([TEST_SEED, 3])))
    draws = 300_000
    cnt = Counter()
    for _ in range(draws):
        parent, _ = d2.wilson_parents_torus(3, rng)
        cnt[tuple(parent.tolist())] += 1  # rooted at 0: parent array <-> spanning tree
    assert len(cnt) == tau
    exp = draws / tau
    stat = sum((c - exp) ** 2 / exp for c in cnt.values())
    assert chi2.sf(stat, tau - 1) > 1e-3


def test_ust_structure_and_lattice_edges():
    rng = np.random.default_rng(TEST_SEED)
    for L in (3, 4, 16, 33):
        g = d2.ust_torus(L, rng)
        chk = d2.structural_checks(d2.UST, g, L)
        assert chk["pass"], chk
    # negative control: a non-lattice edge is detected
    g = d1._from_edges(16, np.arange(1, 16), np.zeros(15, dtype=np.int64))  # star
    assert not d2.torus_edges_ok(g, 4)


def test_rrt_parent_order_and_structure():
    rng = np.random.default_rng(TEST_SEED)
    p = d2.rrt_parents(5000, rng)
    assert p[0] == -1 and np.all(p[1:] < np.arange(1, 5000)) and np.all(p[1:] >= 0)
    g = d2.random_recursive_tree(5000, rng)
    assert d2.structural_checks(d2.RRT, g, 5000)["pass"]
    # parent of vertex 1 is always 0; parent of vertex 2 is uniform on {0, 1}
    ps = [d2.rrt_parents(3, np.random.default_rng(s))[2] for s in range(4000)]
    assert abs(np.mean(ps) - 0.5) < 0.05


def test_cayley_structure_and_small_n_ball_means():
    """Generator + BFS against the exact formula on small N (non-preregistered seed)."""
    n, T, S = 4096, 64, 16
    rng = np.random.default_rng(TEST_SEED)
    radii = [4, 8, 16, 32]
    bb = []
    for _ in range(T):
        g = d2.cayley_tree(n, rng)
        assert d2.structural_checks(d2.CAY, g, n)["pass"]
        src = rng.choice(n, S, replace=False)
        bb.append([np.mean([d1.ball_sizes(d1.shell_counts(g, int(s)), [r])[0] for s in src]) for r in radii])
    bb = np.array(bb)
    exact = d2.cayley_ball_mean(n, radii)
    for i, r in enumerate(radii):
        t = (bb[:, i].mean() - exact[r]) / (bb[:, i].std(ddof=1) / math.sqrt(T))
        assert abs(t) < 4.5, (r, t)


def test_shell_counts_match_reference_bfs_on_trees():
    rng = np.random.default_rng(TEST_SEED + 1)
    for g in (d2.cayley_tree(3000, rng), d2.ust_torus(40, rng), d2.random_recursive_tree(3000, rng)):
        for s in rng.choice(g.n, 5, replace=False):
            assert np.array_equal(d1.shell_counts(g, int(s)), d1.bfs_shell_counts(g, int(s)))


def test_seed_rule_determinism_and_override():
    a, sa = d2.build_instance(CFG, d2.UST, 0, 1, size=12, seed_base=TEST_SEED)
    b, sb = d2.build_instance(CFG, d2.UST, 0, 1, size=12, seed_base=TEST_SEED)
    c, _ = d2.build_instance(CFG, d2.UST, 0, 2, size=12, seed_base=TEST_SEED)
    assert np.array_equal(a.indices, b.indices) and np.array_equal(sa, sb)
    assert not np.array_equal(a.indices, c.indices)
    assert len(sa) == 144 and np.all(np.diff(sa) > 0)  # S capped at n for tiny tests


def _fake(fam, size, rep, verdict, d_hat, adm=(4, 8, 16), bbar=None):
    return {"family": fam, "size": size, "i_rep": rep, "verdict": verdict, "d_hat": d_hat,
            "admissible": list(adm), "structural_check": {"pass": True}, "n": size,
            "bbar": bbar or {}}


def test_gate_logic_synthetic():
    N = d2.sizes(CFG, d2.CAY)
    Ls = d2.sizes(CFG, d2.UST)
    res = []
    for z in N:
        res += [_fake(d2.CAY, z, i, d1.PLATEAU, 1.93 + 0.01 * (i % 2)) for i in range(8)]
        res += [_fake(d2.RRT, z, i, d1.INSUFFICIENT, None) for i in range(8)]
    for z in Ls:
        res += [_fake(d2.UST, z, i, d1.PLATEAU, 1.62 + 0.01 * (i % 2)) for i in range(8)]
    g = d2.evaluate_gates([r for r in res if r["family"] != d2.CAY], {}, CFG)
    assert g["D2-G2"]["pass"] and g["D2-G3"]["pass"]
    # G1 with CAY: build gates without the CAY G0 dependency on pooled curves
    by = d2.evaluate_gates([r for r in res if r["family"] == d2.CAY],
                           {f"{d2.CAY}:{z}": {"admissible": []} for z in N}, CFG)
    assert by["D2-G1"]["pass"]
    # one non-PLATEAU replicate at the top size fails G1
    bad = [dict(r) for r in res if r["family"] == d2.CAY]
    bad[-1].update(verdict=d1.NO_PLATEAU, d_hat=None)
    assert not d2.evaluate_gates(bad, {f"{d2.CAY}:{z}": {"admissible": []} for z in N}, CFG)["D2-G1"]["pass"]
    # UST: level within 0.15 of 1.6 but the 95 % upper end >= 1.85 fails G2 (separation only)
    wide = [dict(r, d_hat=1.60 if r["i_rep"] % 2 else 1.88) for r in res if r["family"] == d2.UST]
    gg = d2.evaluate_gates(wide, {}, CFG)["D2-G2"]
    top = gg["by_size"][str(Ls[2])]
    assert abs(top["mean"] - 1.6) <= 0.15 and top["ci95"][1] >= 1.85 and not gg["pass"]
    # an RRT PLATEAU fails G3
    rr = [dict(r) for r in res if r["family"] == d2.RRT]
    rr[0].update(verdict=d1.PLATEAU, d_hat=1.0)
    assert not d2.evaluate_gates(rr, {}, CFG)["D2-G3"]["pass"]


def test_cayley_g0_detects_wrong_generator():
    """The G0 t-check accepts exact-mean replicates and rejects a biased generator."""
    N = 2 ** 12
    exact = d2.cayley_ball_mean(N, [4, 8, 16])
    rng = np.random.default_rng(1)
    good = [_fake(d2.CAY, N, i, d1.PLATEAU, 1.9,
                  bbar={str(r): exact[r] * (1 + 0.02 * rng.standard_normal()) for r in exact}) for i in range(8)]
    pooled = {f"{d2.CAY}:{N}": {"admissible": [4, 8, 16]}}
    assert d2.cayley_g0(good, pooled)["pass"]
    biased = [dict(r, bbar={k: v * 1.10 for k, v in r["bbar"].items()}) for r in good]
    assert not d2.cayley_g0(biased, pooled)["pass"]


def test_run_end_to_end_tiny(tmp_path):
    """Driver on a shrunken copy of the config (tiny sizes, test seed): outputs and determinism."""
    cfg = json.loads(json.dumps(CFG))
    cfg["seed_base"] = TEST_SEED
    cfg["families"][d2.CAY]["N"] = [512, 1024, 2048]
    cfg["families"][d2.RRT]["N"] = [512, 1024, 2048]
    cfg["families"][d2.UST]["L"] = [16, 24, 32]
    for f in cfg["families"].values():
        f["replicates"], f["sources"] = 8, 8
    m1 = d2.run(cfg, list(cfg["family_index_order"]), tmp_path / "a", check_frozen=False)
    m2 = d2.run(cfg, list(cfg["family_index_order"]), tmp_path / "b", check_frozen=False)
    assert m1["outputs"] == m2["outputs"]
    for f in ("ball_counts.csv", "result.json"):
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes()
    res = json.loads((tmp_path / "a" / "result.json").read_text())
    assert set(res["gates"]) == {"D2-G0", "D2-G1", "D2-G2", "D2-G3"}
    assert res["gates"]["D2-G0"]["structural_pass"]
    assert len(m1["seed_tuples"]) == 72
