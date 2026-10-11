"""Tests for the D1 volume-growth estimator (prereg v1.0, D-G0 implementation exactness).

Random-graph tests use small sizes and test-only seeds (never the preregistered seed base) and
check generator properties only; no gated D1 verdict on a preregistered random graph is computed.
"""
import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import dimension_d1 as d1

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / d1.CONFIG_PATH).read_text())
TEST_SEED = 424242  # not the preregistered seed base


def rng(i=0):
    return np.random.default_rng([TEST_SEED, i])


# --------------------------------------------------------------- frozen files
def test_frozen_prereg_and_config_pinned():
    out = d1.validate_frozen_files(ROOT)
    assert out["prereg_blob_sha"] == d1.PREREG_BLOB_SHA
    assert CFG["seed_base"] == 2035101101 and CFG["version"] == "1.0"


# --------------------------------------------------------------- closed form vs BFS
@pytest.mark.parametrize("d", [1, 2, 3])
def test_closed_form_small_values(d):
    # direct enumeration on Z^d for small r
    for r in range(0, 7):
        rng_ = range(-r, r + 1)
        if d == 1:
            cnt = sum(1 for x in rng_ if abs(x) <= r)
        elif d == 2:
            cnt = sum(1 for x in rng_ for y in rng_ if abs(x) + abs(y) <= r)
        else:
            cnt = sum(1 for x in rng_ for y in rng_ for z in rng_ if abs(x) + abs(y) + abs(z) <= r)
        assert d1.lattice_ball_exact(d, r) == cnt


@pytest.mark.parametrize("d,L", [(1, 64), (2, 40), (3, 24)])
def test_bfs_ball_equals_closed_form_below_wrap(d, L):
    g = d1.torus_lattice(d, L)
    assert np.all(g.degrees == 2 * d) and g.n_edges == d * L ** d
    shells = d1.bfs_shell_counts(g, 0)
    assert shells.sum() == g.n
    for r in range(L // 2):  # torus ball = lattice ball while r < L/2
        assert int(d1.ball_sizes(shells, [r])[0]) == d1.lattice_ball_exact(d, r)
    # vertex-transitivity spot check: another source gives identical shells
    assert np.array_equal(d1.bfs_shell_counts(g, g.n // 3), shells)


def test_prereg_section4_table_values():
    table = {1: [9, 17, 33, 65, 129], 2: [41, 145, 545, 2113, 8321],
             3: [129, 833, 6017, 45825, 357889]}
    for d, vals in table.items():
        assert [d1.lattice_ball_exact(d, r) for r in (4, 8, 16, 32, 64)] == vals


def test_expected_verdict_table_matches_prereg():
    e = d1.expected_lattice_verdicts()
    want = {("lattice_Z1", 1024): ([4, 32], 0.977974), ("lattice_Z1", 4096): ([4, 128], 0.994397),
            ("lattice_Z1", 16384): ([4, 512], 0.998593), ("lattice_Z2", 256): ([4, 32], 1.954965),
            ("lattice_Z2", 512): ([8, 64], 1.977464), ("lattice_Z2", 1024): ([8, 128], 1.988730),
            ("lattice_Z3", 144): ([8, 64], 2.965305), ("lattice_Z3", 168): ([8, 64], 2.965305),
            ("lattice_Z3", 192): ([8, 64], 2.965305)}
    assert set(e) == set(want)
    for k, (win, dh) in want.items():
        assert e[k]["verdict"] == d1.PLATEAU and e[k]["window"] == win
        assert abs(e[k]["d_hat"] - dh) < 5e-7
    assert e[("lattice_Z1", 1024)]["admissible"] == [4, 8, 16]
    assert e[("lattice_Z2", 512)]["admissible"] == [4, 8, 16, 32]


@pytest.mark.parametrize("fam,i_size", [("lattice_Z1", 0), ("lattice_Z1", 1), ("lattice_Z2", 0)])
def test_dg0_full_size_small_lattices(fam, i_size):
    res, rows = d1.run_lattice(CFG, fam, i_size)
    e = d1.expected_lattice_verdicts()[(fam, res["size"])]
    assert res["dg0_ball_pass"] and res["generator_check"]["pass"]
    assert res["verdict"] == e["verdict"] and res["window"] == e["window"]
    assert abs(res["d_hat"] - e["d_hat"]) <= 1e-12
    assert rows and all(r["ball"] >= 1 for r in rows)


# --------------------------------------------------------------- verdict rule
def _bbar_from_deff(deffs, r_min=4, b0=10.0, n_scale=1e12):
    """Build B̄ with given d_eff at r_min, 2 r_min, ... ; afterwards saturate at N."""
    bb, r, b = {r_min: b0}, r_min, b0
    for d in deffs:
        b = b * 2 ** d
        r *= 2
        bb[r] = b
    n = 8 * b  # last listed scale is exactly admissible (8*B(2r) = N)
    bb[2 * r] = n
    bb[4 * r] = n
    return bb, n


def test_verdict_insufficient_and_no_plateau():
    bb, n = _bbar_from_deff([2.0, 2.0])
    v = d1.verdict(bb, n)
    assert v["verdict"] == d1.INSUFFICIENT and v["admissible"] == [4, 8]
    bb, n = _bbar_from_deff([1.0, 1.3, 1.6, 1.9, 2.2])  # steps 0.3 > eps
    v = d1.verdict(bb, n)
    assert v["verdict"] == d1.NO_PLATEAU and len(v["admissible"]) == 5


def test_verdict_selection_largest_rlast_then_longest_and_drift():
    # values at r=4..128 (6 scales): run [4,8,16] valid; [32,64,128] valid; choose the later one
    bb, n = _bbar_from_deff([1.0, 1.05, 1.1, 2.0, 2.05, 2.1])
    v = d1.verdict(bb, n)
    assert v["verdict"] == d1.PLATEAU and v["window"] == [32, 256]
    assert math.isclose(v["d_hat"], 2.1) and v["post_window_drift"] is None
    # trailing excursion: best run ends before last admissible scale -> drift reported
    bb, n = _bbar_from_deff([2.0, 2.02, 2.04, 2.06, 3.0])
    v = d1.verdict(bb, n)
    assert v["window"] == [4, 64] and math.isclose(v["d_hat"], 2.06)
    assert math.isclose(v["post_window_drift"], 3.0)
    # epsilon boundary is inclusive (max - min <= eps)
    bb, n = _bbar_from_deff([2.0, 2.075, 2.125])
    assert d1.verdict(bb, n, eps=0.125 + 1e-12)["verdict"] == d1.PLATEAU
    assert d1.verdict(bb, n, eps=0.12)["verdict"] == d1.NO_PLATEAU


def test_verdict_requires_radii():
    with pytest.raises(ValueError):
        d1.verdict({4: 10.0}, 1000)


def test_guard_uses_giant_component_size_and_fraction():
    bb, n = _bbar_from_deff([2.0, 2.0, 2.0])
    assert d1.verdict(bb, n)["verdict"] == d1.PLATEAU
    assert d1.verdict(bb, n, guard_fraction=0.0625)["verdict"] == d1.INSUFFICIENT


# --------------------------------------------------------------- generators
def test_from_edges_drops_loops_and_collapses_duplicates():
    g = d1._from_edges(4, np.array([0, 1, 1, 2, 3, 0]), np.array([1, 0, 1, 3, 2, 1]))
    assert g.n_edges == 2
    assert g.info["self_loops_removed"] == 1 and g.info["duplicate_edges_removed"] == 3
    assert sorted(g.indices[g.indptr[0]:g.indptr[1]].tolist()) == [1]


def test_subdivided_tree_structure_and_shells():
    h, ell = 5, 4
    g = d1.subdivided_binary_tree(h, ell)
    n_tree = 2 ** (h + 1) - 1
    assert g.n == n_tree + 3 * (n_tree - 1) and g.n_edges == 4 * (n_tree - 1)
    _, ncomp = d1.giant_component(g)
    assert ncomp == 1
    shells = d1.bfs_shell_counts(g, 0)
    # from the root: distance 4j -> 2^j tree nodes (j>=0); 4j+t (t=1..3) -> 2^(j+1) path vertices
    want = [1] + [2 ** (j + 1) for j in range(h) for _ in range(ell)]
    assert shells.tolist() == want
    deg = np.bincount(g.degrees).tolist()
    assert deg[1] == 2 ** h and deg[3] == n_tree - 1 - 2 ** h  # leaves; internal non-root tree nodes


def test_erased_configuration_model():
    n = 2000
    g = d1.random_regular_erased(n, 4, rng(1))
    assert g.degrees.max() <= 4
    assert g.n_edges + g.info["self_loops_removed"] + g.info["duplicate_edges_removed"] == 2 * n
    # simple graph: no self-loops, no duplicate neighbours
    rows = np.repeat(np.arange(n), g.degrees)
    assert not np.any(rows == g.indices)
    assert np.unique(rows.astype(np.int64) * n + g.indices).size == g.indices.size
    # symmetric adjacency
    a = set(zip(rows.tolist(), g.indices.tolist()))
    assert all((v, u) in a for u, v in a)
    # deterministic given the stream
    g2 = d1.random_regular_erased(n, 4, rng(1))
    assert np.array_equal(g.indices, g2.indices)


def test_rgg_matches_bruteforce_and_mean_degree():
    n, k = 600, 12
    r = rng(2)
    g = d1.rgg_2d_torus(n, k, r)
    pts = rng(2).random((n, 2))
    rho = math.sqrt(k / (math.pi * n))
    dx = np.abs(pts[:, None, :] - pts[None, :, :])
    dx = np.minimum(dx, 1 - dx)
    adj = (np.hypot(dx[..., 0], dx[..., 1]) < rho) & ~np.eye(n, dtype=bool)
    assert g.n_edges == adj.sum() // 2
    rows = np.repeat(np.arange(n), g.degrees)
    assert np.all(adj[rows, g.indices])
    # wrap-around edges exist (periodic boundary)
    assert np.any(np.abs(pts[rows, 0] - pts[g.indices, 0]) > 0.5)
    info = {"n_generated": n, "edges_generated": g.n_edges}
    chk = d1.generator_checks("rgg_2d_torus", n, info, CFG)
    assert chk["pass"]


def test_newman_watts_zero_p_is_torus_and_accounting():
    g0 = d1.newman_watts_2d(20, 0.0, rng(3))
    t = d1.torus_lattice(2, 20)
    assert np.array_equal(g0.indptr, t.indptr)
    assert np.array_equal(np.sort(g0.indices), np.sort(t.indices))
    g = d1.newman_watts_2d(20, 0.2, rng(3))
    info = {**g.info, "edges_generated": g.n_edges}
    assert d1.generator_checks("newman_watts_2d", 0.2, info, {"families": {"newman_watts_2d": {"L": 20}}})["pass"]
    assert g.info["shortcuts_drawn"] > 0 and g.n_edges > t.n_edges


def test_giant_component_relabels():
    # path 0-1-2 plus edge 3-4
    g = d1._from_edges(5, np.array([0, 1, 3]), np.array([1, 2, 4]))
    gc, ncomp = d1.giant_component(g)
    assert ncomp == 2 and gc.n == 3 and gc.n_edges == 2
    assert d1.bfs_shell_counts(g, 3).tolist() == [1, 1]


# --------------------------------------------------------------- end-to-end determinism (tiny config)
def _tiny_cfg():
    c = copy.deepcopy(CFG)
    c["seed_base"] = TEST_SEED
    c["families"]["rgg_2d_torus"].update(N=[4096, 8192, 16384], replicates=2)
    c["families"]["random_4_regular"].update(N=[2048, 4096, 8192], replicates=2)
    c["families"]["subdivided_binary_tree"].update(depth=[6, 7, 8], source_draws=2)
    c["families"]["newman_watts_2d"].update(L=40, replicates=2)
    return c


def test_run_random_families_tiny_deterministic(tmp_path):
    cfg = _tiny_cfg()
    fams = ["rgg_2d_torus", "random_4_regular", "subdivided_binary_tree", "newman_watts_2d"]
    m1 = d1.run(cfg, fams, tmp_path / "a", check_frozen=False)
    m2 = d1.run(cfg, fams, tmp_path / "b", check_frozen=False)
    assert m1["outputs"] == m2["outputs"]
    for f in ("ball_counts.csv", "result.json"):
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes()
    res = json.loads((tmp_path / "a" / "result.json").read_text())
    assert all(r["generator_check"]["pass"] for r in res["results"])
    assert all(len(r["sources"]) == 32 == len(set(r["sources"])) for r in res["results"])
    # different replicate index -> different graph stream
    s = [r["sources"] for r in res["results"] if r["family"] == "rgg_2d_torus" and r["size"] == 4096]
    assert s[0] != s[1]


def test_cli_lattice_subset(tmp_path):
    assert d1.main(["--output", str(tmp_path), "--families", "lattice_Z1"]) == 0
    m = json.loads((tmp_path / "manifest.json").read_text())
    assert m["prereg_blob_sha"] == d1.PREREG_BLOB_SHA and m["gates_pass"]["D-G0"] is True


# --------------------------------------------------------------- production BFS vs reference BFS
@pytest.mark.parametrize("make", [
    lambda: d1.torus_lattice(3, 11),
    lambda: d1.torus_lattice(1, 37),
    lambda: d1.subdivided_binary_tree(6, 4),
    lambda: d1.random_regular_erased(3000, 4, rng(5)),
    lambda: d1.rgg_2d_torus(5000, 12, rng(6)),
    lambda: d1.newman_watts_2d(30, 0.05, rng(7)),
    lambda: d1._from_edges(6, np.array([0, 1, 3, 4]), np.array([1, 2, 4, 5])),
])
def test_production_bfs_equals_reference(make):
    g = make()
    for s in np.random.default_rng([TEST_SEED, 99]).choice(g.n, size=5, replace=False):
        assert np.array_equal(d1.shell_counts(g, int(s)), d1.bfs_shell_counts(g, int(s)))


# --------------------------------------------------------------- full-grid workflow (later-pass review r1)
def test_full_grid_workflow_dispatch_only_main_twice_and_uploaded():
    text = (ROOT / ".github/workflows/d1-full-grid.yml").read_text()
    on_block = text.split("\non:", 1)[1].split("\npermissions:", 1)[0]
    assert "workflow_dispatch" in on_block
    for trigger in ("push", "pull_request", "schedule"):
        assert trigger not in on_block, trigger
    assert "github.ref == 'refs/heads/main'" in text and "contents: read" in text
    # D-G5: two invocations, byte-compared, outputs uploaded even on failure
    assert text.count("python -m emergence_lab.dimension_d1 --families all") == 2
    assert "cmp results/d1_full/ball_counts.csv results/d1_full_repeat/ball_counts.csv" in text
    assert "cmp results/d1_full/result.json results/d1_full_repeat/result.json" in text
    assert "actions/upload-artifact" in text and "if: always()" in text
    # ci.yml must not run the full grid (a main dispatch there also reruns the Phase-0 gates)
    assert "--families all" not in (ROOT / ".github/workflows/ci.yml").read_text()
