"""D1 volume-growth dimension estimator (Issue #4): implementation of preregistration v1.0.

Frozen design: docs/DIMENSION_ESTIMATOR_PREREGISTRATION.md (merged via PR #32) with
configs/dimension_d1.json. This module provides the graph generators, exact BFS ball counts,
the dyadic d_eff verdict rule, the gate evaluation D-G0...D-G5 and the provenance manifest.

Running the preregistered random-graph grid (``--families all``) produces gated output; per the
D1 handoff it is executed only after a later-pass review of this implementation.

Implementation choices not fixed verbatim by the prereg (flagged for review):
* Configuration model: "self-loops and multi-edges dropped" is implemented as the *erased*
  configuration model: self-loops removed, each multi-edge collapsed to one simple edge. The
  number of removed self-loop stubs and of removed duplicate edge copies is reported.
* Newman-Watts shortcuts: the number of shortcuts is drawn as Binomial(2N, p) and the endpoints
  uniformly and independently; this is the same distribution as one Bernoulli(p) trial per
  lattice edge. Shortcut self-loops are dropped and duplicates collapsed (both counted).
* RGG edges are found with an exact cell list using the strict rule distance < rho.
* Distances: scipy breadth_first_order + pointer jumping (production) and an independent numpy
  frontier BFS (reference); tests require identical shell counts.
* Seed streams: graph RNG = PCG64(SeedSequence([seed_base, i_family, i_size, i_rep])); the
  source RNG is PCG64 of the first spawned child of that same SeedSequence.
* Lattice sources: vertex 0. Subdivided-tree sources are drawn from all vertices (original and
  subdivision vertices), 32 distinct per draw, i_rep = draw index.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import platform
import resource
import sys
import time
from math import comb
from pathlib import Path

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.csgraph import breadth_first_order, connected_components

PREREG_PATH = "docs/DIMENSION_ESTIMATOR_PREREGISTRATION.md"
CONFIG_PATH = "configs/dimension_d1.json"
# Pinned at the frozen versions on main 6dc714e (PR #32 merge).
PREREG_BLOB_SHA = "aaf542d40cbd8a343b7cf98b8b44a295ad829c83"
CONFIG_SHA256 = "148bf001adb0521e3119c18d8e1be99b3f00f9791bf6590829d6df4a4fac2cb5"

PLATEAU, NO_PLATEAU, INSUFFICIENT = "PLATEAU", "NO_PLATEAU", "INSUFFICIENT_RANGE"
LATTICE_DIM = {"lattice_Z1": 1, "lattice_Z2": 2, "lattice_Z3": 3}


# ----------------------------------------------------------------------------- graphs
class Graph:
    """Undirected simple graph in CSR form (int32 indices; no data array is kept)."""

    def __init__(self, indptr: np.ndarray, indices: np.ndarray, info: dict | None = None):
        self.indptr = np.ascontiguousarray(indptr, dtype=np.int64)
        self.indices = np.ascontiguousarray(indices, dtype=np.int32)
        self.n = len(self.indptr) - 1
        self.info = info or {}

    @property
    def degrees(self) -> np.ndarray:
        return np.diff(self.indptr)

    @property
    def n_edges(self) -> int:
        return int(self.indices.size // 2)

    def csr(self) -> sparse.csr_matrix:
        """float64/int32 CSR as expected by scipy.sparse.csgraph (built once, so csgraph does
        not copy it on every call)."""
        if getattr(self, "_csr", None) is None:
            self._csr = sparse.csr_matrix(
                (np.ones(self.indices.size), self.indices, self.indptr.astype(np.int32)),
                shape=(self.n, self.n))
        return self._csr


def _from_edges(n: int, u: np.ndarray, v: np.ndarray, info: dict | None = None) -> Graph:
    """Simple undirected graph from an edge list; drops self-loops and collapses duplicates.
    Returns the graph with info['self_loops_removed'] and info['duplicate_edges_removed'].
    Rows are sorted; neighbour order within a row is deterministic (distances do not depend on it)."""
    u = np.asarray(u)
    v = np.asarray(v)
    loops = u == v
    n_loops = int(loops.sum())
    if n_loops:
        u, v = u[~loops], v[~loops]
    del loops
    key = np.minimum(u, v).astype(np.int64) * n + np.maximum(u, v)
    m_in = key.size
    del u, v
    key.sort()
    if key.size:
        key = key[np.concatenate([[True], key[1:] != key[:-1]])]
    n_dup = int(m_in - key.size)
    lo, hi = (key // n).astype(np.int32), (key % n).astype(np.int32)
    del key
    src = np.concatenate([lo, hi])
    dst = np.concatenate([hi, lo])
    del lo, hi
    order = np.argsort(src, kind="stable")
    dst = dst[order]
    del order
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(np.bincount(src, minlength=n), out=indptr[1:])
    del src
    info = dict(info or {})
    info.update(self_loops_removed=n_loops, duplicate_edges_removed=n_dup)
    return Graph(indptr, dst, info)


def torus_lattice(d: int, L: int) -> Graph:
    """Nearest-neighbour Z^d torus with side L (row-major vertex index), built directly in CSR.
    Neighbour order per vertex: for each axis, (-1, +1). Requires L >= 3 (simple graph)."""
    if L < 3 or d < 1:
        raise ValueError("need d >= 1 and L >= 3")
    n = L ** d
    deg = 2 * d
    idx = np.arange(n, dtype=np.int32)
    indices = np.empty(n * deg, dtype=np.int32)
    stride = 1
    for axis in reversed(range(d)):  # last axis has stride 1
        coord = (idx // stride) % L
        base = idx - coord * stride
        k = 2 * (d - 1 - axis)
        indices[k::deg] = base + ((coord - 1) % L) * stride
        indices[k + 1::deg] = base + ((coord + 1) % L) * stride
        del coord, base
        stride *= L
    del idx
    indptr = np.arange(0, n * deg + 1, deg, dtype=np.int64)
    return Graph(indptr, indices, {"family": f"Z{d}", "L": L})


def rgg_2d_torus(n: int, mean_degree: float, rng: np.random.Generator) -> Graph:
    """N uniform points on the unit 2-torus; edge iff torus Euclidean distance < rho,
    rho = sqrt(k/(pi N)). Exact cell-list search (cell side >= rho, so every edge joins the same
    or one of the 8 neighbouring cells); memory is bounded by processing points in chunks."""
    rho = math.sqrt(mean_degree / (math.pi * n))
    pts = rng.random((n, 2))
    M = int(math.floor(1.0 / rho))
    if M < 3:
        raise ValueError("rho too large for the cell list (need at least 3 cells per side)")
    cx = np.minimum((pts[:, 0] * M).astype(np.int64), M - 1)
    cy = np.minimum((pts[:, 1] * M).astype(np.int64), M - 1)
    cell = cx * M + cy
    order = np.argsort(cell, kind="stable")
    cell_s, x, y = cell[order], pts[order, 0], pts[order, 1]
    del cx, cy, cell, pts
    cnt = np.bincount(cell_s, minlength=M * M)
    start = np.zeros(M * M + 1, dtype=np.int64)
    np.cumsum(cnt, out=start[1:])
    rho2 = rho * rho
    us, vs = [], []
    # same cell (j > i) plus 4 of the 8 neighbour offsets (each unordered cell pair once; M >= 3)
    offsets = [(0, 0), (1, -1), (1, 0), (1, 1), (0, 1)]
    chunk = 1 << 18
    for a0 in range(0, n, chunk):
        ii = np.arange(a0, min(n, a0 + chunk), dtype=np.int64)
        ci = cell_s[ii]
        cix, ciy = ci // M, ci % M
        for ox, oy in offsets:
            cb = ((cix + ox) % M) * M + (ciy + oy) % M
            k = cnt[cb]
            tot = int(k.sum())
            if tot == 0:
                continue
            i_rep = np.repeat(ii, k)
            j = np.repeat(start[cb] - np.concatenate([[0], np.cumsum(k)[:-1]]), k) + np.arange(tot)
            if (ox, oy) == (0, 0):
                keep = j > i_rep
                i_rep, j = i_rep[keep], j[keep]
            dx = np.abs(x[i_rep] - x[j])
            dx = np.minimum(dx, 1.0 - dx)
            dy = np.abs(y[i_rep] - y[j])
            dy = np.minimum(dy, 1.0 - dy)
            keep = dx * dx + dy * dy < rho2
            us.append(order[i_rep[keep]].astype(np.int32))
            vs.append(order[j[keep]].astype(np.int32))
    del x, y, cell_s
    u, v = np.concatenate(us), np.concatenate(vs)
    del us, vs
    return _from_edges(n, u, v, {"family": "RGG2D", "rho": rho, "cells_per_side": M})


def random_regular_erased(n: int, k: int, rng: np.random.Generator) -> Graph:
    if (n * k) % 2:
        raise ValueError("n*k must be even")
    stubs = rng.permutation(np.repeat(np.arange(n, dtype=np.int64), k))
    g = _from_edges(n, stubs[0::2], stubs[1::2], {"family": f"erased_config_{k}_regular"})
    return g


def subdivided_binary_tree(depth: int, ell: int) -> Graph:
    """Complete binary tree with levels 0..depth (2^(depth+1)-1 nodes, heap order), each edge
    replaced by a path of `ell` edges (ell-1 new interior vertices per edge)."""
    n_tree = 2 ** (depth + 1) - 1
    child = np.arange(1, n_tree, dtype=np.int64)
    parent = (child - 1) // 2
    m = child.size
    n = n_tree + (ell - 1) * m
    # interior vertices of edge j: n_tree + j*(ell-1) + t, t = 0..ell-2, from parent to child
    chain = np.empty((m, ell + 1), dtype=np.int64)
    chain[:, 0] = parent
    chain[:, -1] = child
    if ell > 1:
        chain[:, 1:-1] = n_tree + np.arange(m)[:, None] * (ell - 1) + np.arange(ell - 1)[None, :]
    u = chain[:, :-1].ravel()
    v = chain[:, 1:].ravel()
    return _from_edges(n, u, v, {"family": "subdivided_binary_tree", "depth": depth, "ell": ell,
                                 "n_tree_nodes": n_tree})


def newman_watts_2d(L: int, p: float, rng: np.random.Generator) -> Graph:
    base = torus_lattice(2, L)
    n = base.n
    rows = np.repeat(np.arange(n, dtype=np.int64), np.diff(base.indptr))
    lat_mask = rows < base.indices
    lu, lv = rows[lat_mask], base.indices[lat_mask].astype(np.int64)
    del rows, lat_mask
    n_lattice_edges = lu.size  # = 2N
    m = int(rng.binomial(n_lattice_edges, p))
    ends = rng.integers(0, n, size=(m, 2), dtype=np.int64)
    g = _from_edges(n, np.concatenate([lu, ends[:, 0]]), np.concatenate([lv, ends[:, 1]]),
                    {"family": "NW2D", "L": L, "p": p, "shortcuts_drawn": m})
    return g


def giant_component(g: Graph) -> tuple[Graph, int]:
    """Return the largest connected component (relabelled, order preserved) and #components."""
    a = sparse.csr_matrix((np.ones(g.indices.size, dtype=np.int8), g.indices, g.indptr),
                          shape=(g.n, g.n))
    ncomp, labels = connected_components(a, directed=False)
    del a
    if ncomp == 1:
        return g, 1
    big = np.argmax(np.bincount(labels))
    keep = labels == big
    newid = np.full(g.n, -1, dtype=np.int64)
    newid[keep] = np.arange(int(keep.sum()))
    deg = np.diff(g.indptr)
    entry_keep = np.repeat(keep, deg)  # a kept vertex's neighbours are in the same component
    indptr = np.zeros(int(keep.sum()) + 1, dtype=np.int64)
    np.cumsum(deg[keep], out=indptr[1:])
    sub = Graph(indptr, newid[g.indices[entry_keep]].astype(np.int32), dict(g.info))
    return sub, int(ncomp)


# ----------------------------------------------------------------------------- BFS
def shell_counts(g: Graph, source: int) -> np.ndarray:
    """Exact number of vertices at graph distance 0, 1, 2, ... from `source` (production path).

    BFS tree from scipy's C breadth_first_order; depths by vectorised pointer jumping (list
    ranking) along the predecessor array. Cross-checked against `bfs_shell_counts` in tests."""
    order, pred = breadth_first_order(g.csr(), source, directed=True, return_predecessors=True)
    p = np.arange(g.n, dtype=np.int32)
    reached = order[1:]
    p[reached] = pred[reached]
    d = np.zeros(g.n, dtype=np.int32)
    d[reached] = 1
    while True:
        pp = p[p]
        if np.array_equal(pp, p):
            break
        d += d[p]
        p = pp
    return np.bincount(d[order]).astype(np.int64)


def bfs_shell_counts(g: Graph, source: int) -> np.ndarray:
    """Reference implementation: frontier-by-frontier numpy BFS (independent of scipy)."""
    seen = np.zeros(g.n, dtype=bool)
    seen[source] = True
    frontier = np.array([source], dtype=np.int64)
    counts = [1]
    indptr, indices = g.indptr, g.indices
    while True:
        starts = indptr[frontier]
        lens = indptr[frontier + 1] - starts
        tot = int(lens.sum())
        if tot == 0:
            break
        offs = np.repeat(starts - np.concatenate([[0], np.cumsum(lens)[:-1]]), lens)
        nb = indices[offs + np.arange(tot)]
        nb = nb[~seen[nb]]
        if nb.size == 0:
            break
        nb = np.unique(nb)
        seen[nb] = True
        counts.append(int(nb.size))
        frontier = nb.astype(np.int64)
    return np.asarray(counts, dtype=np.int64)


def ball_sizes(shells: np.ndarray, radii) -> np.ndarray:
    cum = np.cumsum(shells)
    r = np.minimum(np.asarray(radii, dtype=np.int64), cum.size - 1)
    return cum[r]


def lattice_ball_exact(d: int, r: int) -> int:
    """|B(r)| on Z^d with the L1 metric: sum_k 2^k C(d,k) C(r,k)."""
    return sum(2 ** k * comb(d, k) * comb(r, k) for k in range(d + 1))


# ----------------------------------------------------------------------------- verdict
def dyadic_scales(r_min: int, r_cap: int) -> list[int]:
    out, r = [], r_min
    while r <= r_cap:
        out.append(r)
        r *= 2
    return out


def verdict(bbar: dict, n: int, r_min: int = 4, eps: float = 0.15, min_scales: int = 3,
            guard_fraction: float = 0.125) -> dict:
    """Prereg §2 verdict. `bbar` maps radius -> mean ball size and must contain r and 2r for every
    candidate scale r = r_min * 2^k up to the first inadmissible one (B̄ is monotone in r, so the
    admissible set is a prefix of the dyadic scales)."""
    adm, deff = [], {}
    r = r_min
    while True:
        if r not in bbar or 2 * r not in bbar:
            raise ValueError(f"ball sizes at r={r} and {2 * r} are needed to decide admissibility")
        if bbar[2 * r] > guard_fraction * n:
            break
        adm.append(r)
        deff[r] = math.log2(bbar[2 * r] / bbar[r])
        r *= 2
    out = {"admissible": adm, "d_eff": {str(k): v for k, v in deff.items()}, "n": n}
    if len(adm) < min_scales:
        out.update(verdict=INSUFFICIENT, d_hat=None, window=None, post_window_drift=None)
        return out
    best = None  # (r_last, length, i, j)
    for i in range(len(adm)):
        for j in range(i + min_scales - 1, len(adm)):
            vals = [deff[adm[t]] for t in range(i, j + 1)]
            if max(vals) - min(vals) <= eps:
                cand = (adm[j], j - i + 1, i, j)
                if best is None or cand[:2] > best[:2]:
                    best = cand
    if best is None:
        out.update(verdict=NO_PLATEAU, d_hat=None, window=None, post_window_drift=None)
        return out
    _, _, i, j = best
    out.update(verdict=PLATEAU, d_hat=deff[adm[j]], window=[adm[i], 2 * adm[j]],
               post_window_drift=deff[adm[j + 1]] if j + 1 < len(adm) else None)
    return out


def required_radii(shell_list: list[np.ndarray], r_min: int) -> list[int]:
    """All dyadic radii r_min*2^k (and their doubles) up to the maximal eccentricity, plus one
    more doubling so that the first inadmissible scale is always decidable."""
    ecc = max(s.size - 1 for s in shell_list)
    rs, r = [], r_min
    while True:
        rs += [r, 2 * r]
        if r > ecc:
            break
        r *= 2
    return sorted(set(rs))


def mean_balls(shell_list: list[np.ndarray], radii: list[int]) -> dict:
    mat = np.stack([ball_sizes(s, radii) for s in shell_list])
    return {r: float(m) for r, m in zip(radii, mat.mean(axis=0))}


# ----------------------------------------------------------------------------- run
def _seed_seq(seed_base: int, i_family: int, i_size: int, i_rep: int):
    ss = np.random.SeedSequence([seed_base, i_family, i_size, i_rep])
    graph_rng = np.random.Generator(np.random.PCG64(ss))
    src_rng = np.random.Generator(np.random.PCG64(ss.spawn(1)[0]))
    return graph_rng, src_rng


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def validate_frozen_files(root: Path = Path(".")) -> dict:
    prereg = (root / PREREG_PATH).read_bytes()
    cfg_raw = (root / CONFIG_PATH).read_bytes()
    if git_blob_sha(prereg) != PREREG_BLOB_SHA:
        raise ValueError("D1 preregistration differs from the pinned frozen blob")
    if hashlib.sha256(cfg_raw).hexdigest() != CONFIG_SHA256:
        raise ValueError("D1 config differs from the pinned SHA-256")
    return {"prereg_blob_sha": PREREG_BLOB_SHA, "config_sha256": CONFIG_SHA256}


def _sizes(cfg: dict, fam: str) -> list:
    f = cfg["families"][fam]
    return {"lattice_Z1": f.get("L"), "lattice_Z2": f.get("L"), "lattice_Z3": f.get("L"),
            "rgg_2d_torus": f.get("N"), "random_4_regular": f.get("N"),
            "subdivided_binary_tree": f.get("depth"), "newman_watts_2d": f.get("p")}[fam]


def build_instance(cfg: dict, fam: str, i_size: int, i_rep: int):
    """Return (graph restricted to giant component, sources, generator info)."""
    i_fam = cfg["family_index_order"].index(fam)
    size = _sizes(cfg, fam)[i_size]
    graph_rng, src_rng = _seed_seq(cfg["seed_base"], i_fam, i_size, i_rep)
    S = cfg["estimator"]["sources_random_graphs"]
    if fam in LATTICE_DIM:
        g = torus_lattice(LATTICE_DIM[fam], size)
        return g, np.array([0]), {"n_components": 1, **g.info}
    if fam == "rgg_2d_torus":
        g = rgg_2d_torus(size, cfg["families"][fam]["mean_degree"], graph_rng)
    elif fam == "random_4_regular":
        g = random_regular_erased(size, 4, graph_rng)
    elif fam == "subdivided_binary_tree":
        g = subdivided_binary_tree(size, cfg["families"][fam]["subdivision"])
    elif fam == "newman_watts_2d":
        g = newman_watts_2d(cfg["families"][fam]["L"], size, graph_rng)
    else:
        raise KeyError(fam)
    n_before, e_before = g.n, g.n_edges
    deg_hist = np.bincount(g.degrees).tolist()
    g, ncomp = giant_component(g)
    sources = np.sort(src_rng.choice(g.n, size=S, replace=False))
    info = {**g.info, "n_generated": n_before, "edges_generated": e_before,
            "degree_histogram_generated": deg_hist, "n_components": ncomp}
    return g, sources, info


def generator_checks(fam: str, size, g_info: dict, cfg: dict) -> dict:
    """D-G0 generator checks on the generated (pre-giant-component) graph."""
    if fam in LATTICE_DIM:
        raise ValueError("lattice generator checks are done in run_lattice")
    if fam == "rgg_2d_torus":
        n, k = g_info["n_generated"], cfg["families"][fam]["mean_degree"]
        q = k / n  # pi rho^2
        mean_deg = 2 * g_info["edges_generated"] / n
        expect = (n - 1) * q
        # On the torus edge indicators are pairwise independent, so Var(#edges) = C(n,2) q(1-q).
        se = 2 * math.sqrt(comb(n, 2) * q * (1 - q)) / n
        z = (mean_deg - expect) / se
        return {"mean_degree": mean_deg, "expected": expect, "se": se, "z": z, "pass": abs(z) <= 3}
    if fam == "random_4_regular":
        n = g_info["n_generated"]
        ok = (g_info["edges_generated"] + g_info["duplicate_edges_removed"]
              + g_info["self_loops_removed"] == 2 * n)
        return {"self_loops_removed": g_info["self_loops_removed"],
                "duplicate_edges_removed": g_info["duplicate_edges_removed"],
                "stub_accounting_pass": ok, "pass": ok}
    if fam == "subdivided_binary_tree":
        n_tree = 2 ** (size + 1) - 1
        ell = cfg["families"][fam]["subdivision"]
        n_exp = n_tree + (ell - 1) * (n_tree - 1)
        ok = (g_info["n_generated"] == n_exp and g_info["edges_generated"] == ell * (n_tree - 1)
              and g_info["n_components"] == 1)
        return {"n_expected": n_exp, "pass": ok}
    if fam == "newman_watts_2d":
        L = cfg["families"][fam]["L"]
        n = L * L
        ok = (g_info["edges_generated"] + g_info["self_loops_removed"]
              + g_info["duplicate_edges_removed"] == 2 * n + g_info["shortcuts_drawn"])
        return {"shortcuts_drawn": g_info["shortcuts_drawn"],
                "self_loops_removed": g_info["self_loops_removed"],
                "duplicate_edges_removed": g_info["duplicate_edges_removed"], "pass": ok}
    raise KeyError(fam)


def analyse(shell_list: list[np.ndarray], n: int, cfg: dict) -> dict:
    est = cfg["estimator"]
    radii = required_radii(shell_list, min([est["r_min"]] + cfg["sensitivity_not_gated"]["r_min"]))
    bbar = mean_balls(shell_list, radii)
    main = verdict(bbar, n, est["r_min"], est["plateau_epsilon"], est["plateau_min_scales"], 0.125)
    sens = {}
    for e in cfg["sensitivity_not_gated"]["plateau_epsilon"]:
        sens[f"eps={e}"] = verdict(bbar, n, est["r_min"], e, est["plateau_min_scales"], 0.125)["verdict"]
    for rm in cfg["sensitivity_not_gated"]["r_min"]:
        sens[f"r_min={rm}"] = verdict(bbar, n, rm, est["plateau_epsilon"], est["plateau_min_scales"], 0.125)["verdict"]
    for gf in cfg["sensitivity_not_gated"]["saturation_guard_fraction"]:
        sens[f"guard={gf}"] = verdict(bbar, n, est["r_min"], est["plateau_epsilon"], est["plateau_min_scales"], gf)["verdict"]
    main["sensitivity"] = sens
    main["bbar"] = {str(k): v for k, v in bbar.items()}
    return main


def run_lattice(cfg: dict, fam: str, i_size: int) -> tuple[dict, list[dict]]:
    d = LATTICE_DIM[fam]
    L = _sizes(cfg, fam)[i_size]
    g = torus_lattice(d, L)
    deg = g.degrees
    shells = shell_counts(g, 0)
    res = analyse([shells], g.n, cfg)
    radii = [int(r) for r in res["bbar"]]
    # Exactness checked at every radius used by the verdict (admissible r and 2r).
    used = sorted({r for a in res["admissible"] for r in (a, 2 * a)})
    exact_used = {str(r): [int(ball_sizes(shells, [r])[0]), lattice_ball_exact(d, r)] for r in used}
    exact_ok = all(a == b for a, b in exact_used.values())
    gen_ok = bool(np.all(deg == 2 * d)) and g.n_edges == d * g.n
    res.update(family=fam, size=L, i_size=i_size, i_rep=0, n=g.n, sources=[0],
               dg0_ball_exact=exact_used, dg0_ball_pass=exact_ok,
               generator_check={"degree_all_2d": bool(np.all(deg == 2 * d)),
                                "edges": g.n_edges, "pass": gen_ok})
    rows = [{"family": fam, "size": L, "rep": 0, "source": 0, "r": r,
             "ball": int(ball_sizes(shells, [r])[0])} for r in radii]
    return res, rows


def run_random(cfg: dict, fam: str, i_size: int, i_rep: int) -> tuple[dict, list[dict]]:
    size = _sizes(cfg, fam)[i_size]
    g, sources, info = build_instance(cfg, fam, i_size, i_rep)
    chk = generator_checks(fam, size, info, cfg)
    shell_list = [shell_counts(g, int(s)) for s in sources]
    res = analyse(shell_list, g.n, cfg)
    radii = [int(r) for r in res["bbar"]]
    res.update(family=fam, size=size, i_size=i_size, i_rep=i_rep, n=g.n,
               sources=[int(s) for s in sources], generator_check=chk,
               generator_info={k: v for k, v in info.items() if k != "degree_histogram_generated"},
               degree_histogram_generated=info["degree_histogram_generated"])
    rows = []
    for s, sh in zip(sources, shell_list):
        b = ball_sizes(sh, radii)
        rows += [{"family": fam, "size": size, "rep": i_rep, "source": int(s), "r": r, "ball": int(x)}
                 for r, x in zip(radii, b)]
    return res, rows


def _t975(df: int) -> float:
    from scipy.stats import t
    return float(t.ppf(0.975, df))


def evaluate_gates(results: list[dict], cfg: dict) -> dict:
    by = {}
    for r in results:
        by.setdefault(r["family"], []).append(r)
    gates = {}
    # D-G0
    lat = [r for f in LATTICE_DIM for r in by.get(f, [])]
    gen_all = [r["generator_check"]["pass"] for r in results]
    expected = expected_lattice_verdicts()
    lat_match = []
    for r in lat:
        e = expected[(r["family"], r["size"])]
        ok = (r["verdict"] == e["verdict"] and r["window"] == e["window"]
              and abs(r["d_hat"] - e["d_hat"]) <= 1e-12)
        lat_match.append(ok)
    gates["D-G0"] = {"lattices_checked": len(lat), "ball_exact": all(r["dg0_ball_pass"] for r in lat),
                     "verdicts_match_table": all(lat_match), "generators_pass": all(gen_all),
                     "pass": bool(lat) and all(r["dg0_ball_pass"] for r in lat) and all(lat_match) and all(gen_all)}
    # D-G1
    if lat:
        gates["D-G1"] = {"pass": len(lat) == 9 and all(
            r["verdict"] == PLATEAU and abs(r["d_hat"] - LATTICE_DIM[r["family"]]) <= 0.10 for r in lat)}
    # D-G2
    nulls = by.get("random_4_regular", []) + by.get("subdivided_binary_tree", [])
    if nulls:
        counts = {}
        for r in nulls:
            counts.setdefault(r["family"], {}).setdefault(r["verdict"], 0)
            counts[r["family"]][r["verdict"]] += 1
        gates["D-G2"] = {"verdict_counts": counts, "n": len(nulls),
                         "pass": len(nulls) == 48 and all(r["verdict"] != PLATEAU for r in nulls)}
    # D-G3
    rgg = by.get("rgg_2d_torus", [])
    if rgg:
        Ns = _sizes(cfg, "rgg_2d_torus")
        stats = {}
        for N in Ns:
            rs = [r for r in rgg if r["size"] == N]
            dh = [r["d_hat"] for r in rs if r["verdict"] == PLATEAU]
            st = {"n_rep": len(rs), "n_plateau": len(dh)}
            if len(dh) >= 2:
                m, s = float(np.mean(dh)), float(np.std(dh, ddof=1))
                hw = _t975(len(dh) - 1) * s / math.sqrt(len(dh))
                st.update(mean=m, sd=s, ci95=[m - hw, m + hw])
            stats[str(N)] = st
        top, mid = stats[str(Ns[2])], stats[str(Ns[1])]
        ok = (top["n_rep"] == 8 and top["n_plateau"] == 8 and abs(top["mean"] - 2) <= 0.15
              and "mean" in mid and mid["n_plateau"] == mid["n_rep"] and abs(mid["mean"] - top["mean"]) <= 0.10)
        gates["D-G3"] = {"by_N": stats, "pass": bool(ok),
                         "note": "Student-t 95% over replicate d_hat; mean at 2^19 uses PLATEAU replicates "
                                 "and requires all 8 to be PLATEAU for the comparison to be defined"}
    # D-G4
    nw = by.get("newman_watts_2d", [])
    if nw:
        hi = [r for r in nw if r["size"] == 1e-2]
        bad = [r for r in hi if r["verdict"] == PLATEAU and r["window"][1] > 32]
        gates["D-G4"] = {"p=1e-2_verdicts": [r["verdict"] for r in hi], "violations": len(bad),
                         "pass": len(hi) == 8 and not bad}
    return gates


def expected_lattice_verdicts() -> dict:
    """Prereg §4 expected-verdict table, recomputed from the closed form (no BFS)."""
    out = {}
    for fam, d in LATTICE_DIM.items():
        Ls = {1: [1024, 4096, 16384], 2: [256, 512, 1024], 3: [144, 168, 192]}[d]
        for L in Ls:
            n = L ** d
            radii = dyadic_scales(4, L)
            radii = sorted(set(radii + [2 * r for r in radii]))
            bb = {r: float(lattice_ball_exact(d, r)) for r in radii}
            out[(fam, L)] = verdict(bb, n)
    return out


def rows_to_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=["family", "size", "rep", "source", "r", "ball"],
                       lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def run(cfg: dict, families: list[str], outdir: Path, check_frozen: bool = True) -> dict:
    t0, c0 = time.time(), time.process_time()
    frozen = validate_frozen_files() if check_frozen else {"prereg_blob_sha": None, "config_sha256": None}
    results, rows = [], []
    for fam in families:
        sizes = _sizes(cfg, fam)
        for i_size in range(len(sizes)):
            if fam in LATTICE_DIM:
                res, rr = run_lattice(cfg, fam, i_size)
                results.append(res); rows += rr
                continue
            reps = cfg["families"][fam].get("replicates", cfg["families"][fam].get("source_draws"))
            for i_rep in range(reps):
                res, rr = run_random(cfg, fam, i_size, i_rep)
                results.append(res); rows += rr
            print(f"{fam} size={sizes[i_size]} done ({time.time() - t0:.0f}s)", file=sys.stderr)
    gates = evaluate_gates(results, cfg)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_bytes = rows_to_csv(rows)
    result = {"families": families, "results": results, "gates": gates}
    result_bytes = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode()
    (outdir / "ball_counts.csv").write_bytes(csv_bytes)
    (outdir / "result.json").write_bytes(result_bytes)
    peak_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    manifest = {**frozen, "commit": os.getenv("GIT_SHA"), "python": platform.python_version(),
                "numpy": np.__version__, "scipy": scipy.__version__, "seed_base": cfg["seed_base"],
                "seed_rule": cfg["seed_rule"], "families": families,
                "seed_tuples": [[cfg["seed_base"], cfg["family_index_order"].index(r["family"]),
                                 r["i_size"], r["i_rep"]] for r in results if r["family"] not in LATTICE_DIM],
                "wall_seconds": round(time.time() - t0, 1), "cpu_seconds": round(time.process_time() - c0, 1),
                "peak_rss_mib": round(peak_kib / 1024, 1),
                "outputs": {"ball_counts.csv": hashlib.sha256(csv_bytes).hexdigest(),
                            "result.json": hashlib.sha256(result_bytes).hexdigest()},
                "gates_pass": {k: v["pass"] for k, v in gates.items()},
                "output_bytes": len(csv_bytes) + len(result_bytes)}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=CONFIG_PATH)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--families", default="lattices",
                    help="'lattices' (deterministic D-G0/D-G1 only), 'all', or comma-separated names")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text())
    order = cfg["family_index_order"]
    fams = (list(LATTICE_DIM) if a.families == "lattices" else order if a.families == "all"
            else a.families.split(","))
    m = run(cfg, fams, a.output)
    print(json.dumps(m, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
