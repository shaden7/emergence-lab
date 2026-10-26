"""S1 spectral feasibility/power pilot: kernel, exact references, P0 gates, statistics.

Preregistration: docs/SPECTRAL_S1_PREREGISTRATION.md v0.2 (config
configs/spectral_s1_pilot.json). This module is the *implementation* stage (prereg §0,
order of work step 2). It must be reviewed before any pilot seed (seed_base 2036101301)
is drawn. Tests and the P0 gates in this module use the separate engineering seed base
TEST_SEED_BASE, never the pilot or a future S2 base.

Nothing here classifies a spectral dimension or makes a physical claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy import stats

from emergence_lab.dimension_d1 import Graph, _from_edges, _seed_seq, torus_lattice
from emergence_lab.dimension_d2 import (
    CAY, RRT, UST, cayley_tree, prufer_decode, random_recursive_tree, structural_checks,
    ust_torus,
)
from emergence_lab.spectral_dimension import graph_even_returns, torus_even_return_fourier

PREREG_PATH = Path("docs/SPECTRAL_S1_PREREGISTRATION.md")
CONFIG_PATH = Path("configs/spectral_s1_pilot.json")
PILOT_SEED_BASE = 2036101301
# S1b authorization is enabled only by the separately reviewed activation commit.
# Real seed use still requires S1B_ALLOW_SEEDS=1, supplied by the once-only workflow
# after its release marker; the contained entry also requires an invocation proof.
S1B_SEED_BASE = 2036101701
S1B_RUN_AUTHORIZED = True
BOOTSTRAP_SEED = 2036101499
# SE audit (docs/SPECTRAL_SE_AUDIT_PREREGISTRATION.md). LOCKED: flipping this flag
# requires a separately reviewed run-authorization change; real seed use additionally
# requires SE_AUDIT_ALLOW_SEEDS=1 in the environment.
SE_AUDIT_SEED_BASE = 2036101901
SE_AUDIT_RUN_AUTHORIZED = False
# Engineering-only seed base for P0b/P0d and unit tests. Disjoint from the pilot base,
# the bootstrap seed and the D2 base 2036101101 (grep at the implementation commit).
TEST_SEED_BASE = 2036101397
FAMILY_ORDER = (CAY, UST, RRT)
ETA = 1e-4
R_START = 64
EDGE_STEP_CAP = 2_000_000_000
IDENTITY_TOL = 1e-12


# ----------------------------------------------------------------------------- kernel
def ball(graph: Graph, source: int, radius: int) -> np.ndarray:
    """Vertices of the graph-distance ball B(source, radius), in BFS order (source first)."""
    if radius < 0:
        raise ValueError("radius must be >= 0")
    seen = np.zeros(graph.n, dtype=bool)
    seen[source] = True
    layers = [np.array([source], dtype=np.int64)]
    frontier = layers[0]
    indptr, indices = graph.indptr, graph.indices
    for _ in range(radius):
        if frontier.size == 0:
            break
        starts, ends = indptr[frontier], indptr[frontier + 1]
        lengths = ends - starts
        if lengths.sum() == 0:
            break
        offs = np.repeat(starts - np.cumsum(np.concatenate([[0], lengths[:-1]])), lengths)
        nbr = indices[np.arange(lengths.sum()) + offs].astype(np.int64)
        nbr = np.unique(nbr[~seen[nbr]])
        seen[nbr] = True
        layers.append(nbr)
        frontier = nbr
    return np.concatenate(layers)


@dataclass
class KilledBallResult:
    """Return probabilities of the walk killed on leaving B(v, R).

    q_lower[t-1] = [P_R^(2t)]_vv for t = 1..T (lower bound of [P^(2t)]_vv);
    killed[t-1] = killed mass m_R(2t) (upper bracket q_lower + killed);
    identity[t] = reversibility value deg(v) sum_x P_R^t(v,x)^2/deg(x) at the requested t.
    """
    source: int
    degree: int
    R: int
    T: int
    ball_size: int
    nnz: int
    q_lower: np.ndarray
    killed: np.ndarray
    identity: dict = field(default_factory=dict)
    status: str = "OK"

    @property
    def edge_steps(self) -> int:
        return 2 * self.T * self.nnz

    def relative_bracket(self) -> float:
        return float(self.killed[-1] / self.q_lower[-1])


def killed_ball_returns(graph: Graph, source: int, T: int, R: int, *,
                        identity_times=(), edge_step_cap: int = EDGE_STEP_CAP) -> KilledBallResult:
    """Iterate the killed sub-stochastic kernel 2T steps from delta_v (prereg §3).

    Degrees are those of the full graph G, so P_R is P restricted to the ball. The
    killed mass is accumulated as the exact outflow through boundary vertices (no
    1 - sum cancellation). If 2T*nnz exceeds the cap nothing is iterated and the result
    has status OVER_CAP (callers must record it, never drop it).
    """
    if not isinstance(T, (int, np.integer)) or T < 1:
        raise ValueError("T must be a positive integer")
    if not 0 <= source < graph.n:
        raise ValueError("invalid source")
    deg_g = graph.degrees
    if np.any(deg_g <= 0):
        raise ValueError("isolated vertex")
    verts = ball(graph, int(source), int(R))
    local = np.full(graph.n, -1, dtype=np.int64)
    local[verts] = np.arange(verts.size)
    starts, ends = graph.indptr[verts], graph.indptr[verts + 1]
    lengths = ends - starts
    offs = np.repeat(starts - np.cumsum(np.concatenate([[0], lengths[:-1]])), lengths)
    nbr = local[graph.indices[np.arange(lengths.sum()) + offs]]
    rows = np.repeat(np.arange(verts.size), lengths)
    keep = nbr >= 0
    deg_in = np.bincount(rows[keep], minlength=verts.size)
    indptr_b = np.concatenate([[0], np.cumsum(deg_in)])
    # rows are already grouped (vertex order), so this is valid CSR without a COO pass
    a = sparse.csr_matrix((np.ones(int(keep.sum())), nbr[keep], indptr_b),
                          shape=(verts.size, verts.size))
    deg = deg_g[verts].astype(np.float64)
    leak = (deg - deg_in) / deg  # fraction of a vertex's mass that leaves the ball per step
    res = KilledBallResult(int(source), int(deg_g[source]), int(R), int(T), int(verts.size),
                           int(a.nnz), np.zeros(T), np.zeros(T))
    if 2 * T * a.nnz > edge_step_cap:
        res.status = "OVER_CAP"
        res.q_lower[:] = np.nan
        res.killed[:] = np.nan
        return res
    inv_deg = 1.0 / deg
    want_id = set(int(t) for t in identity_times)
    p = np.zeros(verts.size)
    p[0] = 1.0
    killed = 0.0
    for s in range(1, 2 * T + 1):
        killed += float(np.dot(p, leak))
        p = a @ (p * inv_deg)
        if s % 2 == 0:
            res.q_lower[s // 2 - 1] = p[0]
            res.killed[s // 2 - 1] = killed
        if s in want_id and s <= T:
            res.identity[s] = float(deg[0] * np.dot(p * p, inv_deg))
    if not np.all(np.isfinite(res.q_lower)) or np.any(res.q_lower <= 0):
        raise ArithmeticError("invalid killed-ball return probability")
    return res


def certified_returns(graph: Graph, source: int, T: int, *, eta: float = ETA,
                      r_start: int = R_START, identity_times=(),
                      edge_step_cap: int = EDGE_STEP_CAP) -> KilledBallResult:
    """Radius rule of prereg §3: R = r_start, doubled until m_R(2T) <= eta*q_R(2T) or R >= 2T."""
    R = int(r_start)
    while True:
        res = killed_ball_returns(graph, source, T, R, identity_times=identity_times,
                                  edge_step_cap=edge_step_cap)
        if res.status != "OK":
            return res
        if res.killed[-1] <= eta * res.q_lower[-1] or R >= 2 * T:
            return res
        R *= 2


def dyadic_half_times(T: int) -> list[int]:
    out, t = [], 1
    while t <= T:
        out.append(t)
        t *= 2
    return out


def even_time_monotone(q: np.ndarray, rel_tol: float = 1e-12) -> bool:
    """q(t+1) <= q(t)(1 + rel_tol): known property of even-time returns of a reversible walk."""
    q = np.asarray(q, dtype=float)
    return bool(np.all(q[1:] <= q[:-1] * (1 + rel_tol)))


# ----------------------------------------------------------------------------- exact (P0a)
def all_labelled_trees(n: int):
    """Every labelled tree on [n] via all Pruefer sequences (Cayley: n^(n-2) of them)."""
    if n < 3:
        raise ValueError("n >= 3 required")
    for seq in product(range(n), repeat=n - 2):
        yield prufer_decode(seq)


def exact_annealed_cayley(n: int, half_times) -> dict[int, Fraction]:
    """Exact annealed q(t) over all labelled trees and all vertices on [n] (integer arithmetic).

    B = diag(M/deg) A with M = lcm(1..n-1) is an integer matrix and P = B/M, so
    [P^(2t)]_vv = [B^(2t)]_vv / M^(2t). Entries of B^s are <= M^s, kept below 2^62.
    Independent of the float kernels; only the Pruefer decoder is shared.
    """
    M = math.lcm(*range(1, n))
    tmax = 2 * max(half_times)
    if M ** tmax >= 2 ** 62:
        raise OverflowError("integer range exceeded")
    mats = []
    seen = set()
    for u, v in all_labelled_trees(n):
        a = np.zeros((n, n), dtype=np.int64)
        a[u, v] = 1
        a[v, u] = 1
        deg = a.sum(axis=1)
        mats.append(a * (M // deg)[:, None])
        seen.add(frozenset(zip(np.minimum(u, v).tolist(), np.maximum(u, v).tolist())))
    if len(seen) != n ** (n - 2) or len(mats) != n ** (n - 2):
        raise AssertionError("Pruefer enumeration is not a bijection")
    b = np.stack(mats)
    power = np.broadcast_to(np.eye(n, dtype=np.int64), b.shape).copy()
    sums = {}
    for s in range(1, tmax + 1):
        power = np.matmul(power, b)
        if s % 2 == 0 and s // 2 in set(half_times):
            diag_total = sum(int(x) for x in np.einsum("kii->k", power))
            sums[s // 2] = Fraction(diag_total, len(mats) * n * M ** s)
    return sums


def pipeline_annealed_cayley(n: int, half_times) -> dict[int, float]:
    """Same annealed mean through the float killed-ball pipeline (all trees, all sources)."""
    T = max(half_times)
    total = np.zeros(T)
    count = 0
    for u, v in all_labelled_trees(n):
        g = _from_edges(n, u, v)
        for s in range(n):
            total += certified_returns(g, s, T).q_lower
            count += 1
    return {t: float(total[t - 1] / count) for t in half_times}


# ----------------------------------------------------------------------------- instances
def build_instance(fam: str, size: int, i_size: int, i_rep: int, n_sources: int,
                   seed_base: int):
    """(graph, sorted sources) with the D2 seed rule; caller supplies the seed base."""
    if seed_base == S1B_SEED_BASE:
        if not S1B_RUN_AUTHORIZED or os.environ.get("S1B_ALLOW_SEEDS") != "1":
            raise PermissionError("S1b seeds locked: reviewed implementation and activation required")
    if seed_base == SE_AUDIT_SEED_BASE:
        if not SE_AUDIT_RUN_AUTHORIZED or os.environ.get("SE_AUDIT_ALLOW_SEEDS") != "1":
            raise PermissionError("SE-audit seeds locked: reviewed run authorization required")
    if seed_base == PILOT_SEED_BASE and os.environ.get("S1_ALLOW_PILOT_SEEDS") != "1":
        raise PermissionError("pilot seeds are locked until the implementation is reviewed")
    graph_rng, src_rng = _seed_seq(seed_base, FAMILY_ORDER.index(fam), i_size, i_rep)
    if fam == CAY:
        g = cayley_tree(size, graph_rng)
    elif fam == UST:
        g = ust_torus(size, graph_rng)
    elif fam == RRT:
        g = random_recursive_tree(size, graph_rng)
    else:
        raise KeyError(fam)
    check = structural_checks(fam, g, size)
    if not check["pass"]:
        raise AssertionError(f"structural check failed: {check}")
    sources = np.sort(src_rng.choice(g.n, size=min(n_sources, g.n), replace=False))
    return g, sources


# ----------------------------------------------------------------------------- P0 gates
def p0a(ns=(5, 6, 7), half_times=(1, 2, 3, 4), tol: float = IDENTITY_TOL) -> dict:
    out = {}
    for n in ns:
        exact = exact_annealed_cayley(n, half_times)
        pipe = pipeline_annealed_cayley(n, half_times)
        err = max(abs(pipe[t] - float(exact[t])) for t in half_times)
        out[str(n)] = {"exact": {str(t): f"{exact[t].numerator}/{exact[t].denominator}"
                                 for t in half_times},
                       "pipeline": {str(t): pipe[t] for t in half_times},
                       "max_abs_error": err, "pass": bool(err <= tol)}
    return {"cases": out, "pass": all(c["pass"] for c in out.values())}


def p0b(seed_base: int = TEST_SEED_BASE, T: int = 256, sources_per_instance: int = 4,
        small_radii=(2, 4, 8, 16), tol: float = IDENTITY_TOL) -> dict:
    """Killed ball with R >= 2T vs S0 full-graph kernel; forced small R brackets the exact."""
    sizes = {CAY: 4096, UST: 64, RRT: 4096}
    times = dyadic_half_times(T)
    cases = []
    for fam in FAMILY_ORDER:
        for rep in range(3):
            g, srcs = build_instance(fam, sizes[fam], 0, rep, sources_per_instance, seed_base)
            for v in srcs.tolist():
                exact = graph_even_returns(g, v, times)
                full = killed_ball_returns(g, v, T, 2 * T, identity_times=times)
                agree = max(abs(full.q_lower[t - 1] - exact[t]) for t in times)
                ident = max(abs(full.identity[t] - full.q_lower[t - 1]) for t in times)
                brackets = []
                for R in small_radii:
                    kb = killed_ball_returns(g, v, T, R)
                    ok = all(kb.q_lower[t - 1] <= exact[t] + tol and
                             exact[t] <= kb.q_lower[t - 1] + kb.killed[t - 1] + tol
                             for t in times)
                    brackets.append({"R": R, "contains": bool(ok),
                                     "rel_width_T": float(kb.killed[-1] / kb.q_lower[-1])})
                cases.append({"family": fam, "rep": rep, "source": v,
                              "max_abs_vs_s0": agree, "max_abs_identity": ident,
                              "killed_at_2T": float(full.killed[-1]),
                              "monotone": even_time_monotone(full.q_lower),
                              "brackets": brackets,
                              "pass": bool(agree <= tol and ident <= tol and full.killed[-1] == 0
                                           and even_time_monotone(full.q_lower)
                                           and all(b["contains"] for b in brackets))})
    return {"seed_base": seed_base, "T": T, "cases": cases,
            "pass": all(c["pass"] for c in cases)}


def p0c(L: int = 64, T: int = 256, n_sources: int = 32, eta: float = ETA,
        tol: float = IDENTITY_TOL) -> dict:
    """Z^2 torus positive control against the S0 Fourier value (vertex-transitive graph).

    Sources are fixed and deterministic (evenly spaced vertex indices); no RNG.
    The float tolerance `tol` is added to both bracket ends.
    """
    g = torus_lattice(2, L)
    times = dyadic_half_times(T)
    ref = {t: torus_even_return_fourier(2, L, t) for t in times}
    srcs = [int(k * g.n // n_sources) for k in range(n_sources)]
    cases = []
    for v in srcs:
        res = certified_returns(g, v, T, eta=eta, identity_times=times)
        inside = all(res.q_lower[t - 1] - tol <= ref[t] <= res.q_lower[t - 1] + res.killed[t - 1] + tol
                     for t in times)
        width_ok = bool(res.killed[-1] <= eta * res.q_lower[-1])
        ident = max(abs(res.identity[t] - res.q_lower[t - 1]) for t in times)
        cases.append({"source": v, "R": res.R, "ball_size": res.ball_size,
                      "max_abs_vs_fourier": max(abs(res.q_lower[t - 1] - ref[t]) for t in times),
                      "rel_bracket_T": res.relative_bracket(), "max_abs_identity": ident,
                      "pass": bool(inside and width_ok and ident <= tol)})
    return {"L": L, "T": T, "cases": cases, "pass": all(c["pass"] for c in cases)}


# ----------------------------------------------------------------------------- CSV / manifest
CSV_HEADER = ["family", "size", "i_size", "i_rep", "source", "degree", "status", "R",
              "ball_size", "nnz", "edge_steps", "killed_2T"]


def rows_csv(results: list[tuple[str, int, int, int, KilledBallResult]], T: int) -> bytes:
    times = dyadic_half_times(T)
    buf = io.StringIO()
    buf.write(",".join(CSV_HEADER + [f"q_t{t}" for t in times]) + "\n")
    for fam, size, i_size, i_rep, r in results:
        vals = [fam, size, i_size, i_rep, r.source, r.degree, r.status, r.R, r.ball_size, r.nnz,
                r.edge_steps, repr(float(r.killed[-1]))]
        vals += [repr(float(r.q_lower[t - 1])) for t in times]
        buf.write(",".join(str(x) for x in vals) + "\n")
    return buf.getvalue().encode()


def manifest(root: Path = Path("."), seeds: list | None = None) -> dict:
    import scipy
    commit = os.environ.get("GIT_SHA")
    if not commit:
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                             text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unknown"
    return {
        "commit": commit,
        "prereg_sha256": hashlib.sha256((root / PREREG_PATH).read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256((root / CONFIG_PATH).read_bytes()).hexdigest(),
        "python": platform.python_version(), "numpy": np.__version__,
        "scipy": scipy.__version__, "seeds": seeds or [],
    }


def p0d_tree_csv(seed_base: int = TEST_SEED_BASE, n: int = 4096, T: int = 256,
                 n_sources: int = 8) -> bytes:
    """Numeric CSV of one CAY engineering tree (no wall time, no paths)."""
    g, srcs = build_instance(CAY, n, 0, 0, n_sources, seed_base)
    res = [(CAY, n, 0, 0, certified_returns(g, v, T)) for v in srcs.tolist()]
    return rows_csv(res, T)


def p0d(root: Path = Path(".")) -> dict:
    """Byte identity of the numeric CSV across two separate interpreter processes."""
    code = ("import sys,hashlib;from emergence_lab.spectral_s1 import p0d_tree_csv;"
            "sys.stdout.write(hashlib.sha256(p0d_tree_csv()).hexdigest())")
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    digests = [subprocess.check_output([sys.executable, "-c", code], cwd=root, env=env,
                                       text=True).strip() for _ in range(2)]
    m = manifest(root, seeds=[[TEST_SEED_BASE, 0, 0, 0]])
    ok = digests[0] == digests[1] and len(digests[0]) == 64
    return {"csv_sha256": digests, "manifest": m, "pass": bool(ok)}


# ----------------------------------------------------------------------------- statistics (P3, P5, §7)
def annealed_window_slope(Q: np.ndarray, lo: int, hi: int, times: list[int]) -> float:
    """d_W = -2 [ln Qbar(hi) - ln Qbar(lo)] / ln(hi/lo); Q is trees x times (per-tree source means)."""
    qbar = np.asarray(Q, dtype=float).mean(axis=0)
    i, j = times.index(lo), times.index(hi)
    if qbar[i] <= 0 or qbar[j] <= 0:
        return float("nan")
    return float(-2.0 * (math.log(qbar[j]) - math.log(qbar[i])) / math.log(hi / lo))


def tree_influences(Q: np.ndarray, lo: int, hi: int, times: list[int]) -> np.ndarray:
    """Delta-method influences psi_i of the annealed window slope, one per tree (prereg §5 P3)."""
    Q = np.asarray(Q, dtype=float)
    qbar = Q.mean(axis=0)
    i, j = times.index(lo), times.index(hi)
    c = -2.0 / math.log(hi / lo)
    return c * ((Q[:, j] - qbar[j]) / qbar[j] - (Q[:, i] - qbar[i]) / qbar[i])


def power_projection(psi: np.ndarray, n_primes, multiplier: float = 1.0) -> dict:
    """Approximate 95% upper variance limit U and projected half-width h(n') (S fixed)."""
    psi = np.asarray(psi, dtype=float)
    n = psi.size
    s2 = float(psi.var(ddof=1))
    U = multiplier * (n - 1) * s2 / float(stats.chi2.ppf(0.05, n - 1))
    h = {int(m): float(stats.t.ppf(0.975, m - 1) * math.sqrt(U / m)) for m in n_primes}
    return {"n": n, "s2_psi": s2, "U": U, "multiplier": multiplier, "h": h}


def projection_reliability(psi: np.ndarray, qbar_values, skew_max: float = 1.5,
                           share_max: float = 0.5) -> dict:
    """Frozen reliability screen (prereg §5 P3); any failure => UNRELIABLE (no GO)."""
    psi = np.asarray(psi, dtype=float)
    s2 = float(psi.var(ddof=1)) if psi.size > 1 else 0.0
    centred = psi - psi.mean()
    m2 = float(np.mean(centred ** 2))
    g1 = float(np.mean(centred ** 3) / m2 ** 1.5) if m2 > 0 else float("nan")
    sq = psi ** 2
    share = float(sq.max() / sq.sum()) if sq.sum() > 0 else float("nan")
    reasons = []
    if not (s2 > 0):
        reasons.append("zero_variance")
    if any(not (q > 0) for q in qbar_values):
        reasons.append("nonpositive_mean")
    if not (abs(g1) <= skew_max):
        reasons.append("skewness")
    if not (share <= share_max):
        reasons.append("influence_share")
    return {"g1": g1, "max_share": share, "s2_psi": s2, "reasons": reasons,
            "reliable": not reasons}


def bootstrap_slopes(Q: np.ndarray, lo: int, hi: int, times: list[int],
                     n_boot: int = 4096, seed: int = BOOTSTRAP_SEED) -> dict:
    """Whole-tree bootstrap of the annealed window slope; descriptive percentile interval."""
    Q = np.asarray(Q, dtype=float)
    rng = np.random.Generator(np.random.PCG64(seed))
    idx = rng.integers(0, Q.shape[0], size=(n_boot, Q.shape[0]))
    i, j = times.index(lo), times.index(hi)
    means_lo = Q[idx, i].mean(axis=1)
    means_hi = Q[idx, j].mean(axis=1)
    d = -2.0 * (np.log(means_hi) - np.log(means_lo)) / math.log(hi / lo)
    return {"n_boot": n_boot, "seed": seed, "sd": float(d.std(ddof=1)),
            "p2_5": float(np.quantile(d, 0.025)), "p97_5": float(np.quantile(d, 0.975))}


def size_equivalence(Q_small: np.ndarray, Q_large: np.ndarray, lo: int, hi: int,
                     times: list[int], margin: float = 0.03, level: float = 0.90) -> dict:
    """P5: large-minus-small annealed slope difference with a two-sided `level` CI.

    Standard errors are tree-level delta-method (s_psi/sqrt(n)) per size; independent sizes.
    Implementation choice (flagged for review, not fixed by the prereg text): Welch t
    quantile with Satterthwaite df, which is wider than the normal quantile for n = 8.
    Equivalent only if the CI lies entirely inside [-margin, margin].
    """
    d_s = annealed_window_slope(Q_small, lo, hi, times)
    d_l = annealed_window_slope(Q_large, lo, hi, times)
    ps, pl = tree_influences(Q_small, lo, hi, times), tree_influences(Q_large, lo, hi, times)
    vs, vl = ps.var(ddof=1) / ps.size, pl.var(ddof=1) / pl.size
    se = math.sqrt(vs + vl)
    df = (vs + vl) ** 2 / (vs ** 2 / (ps.size - 1) + vl ** 2 / (pl.size - 1)) if se > 0 else float("nan")
    q = float(stats.t.ppf(0.5 + level / 2, df)) if se > 0 else float("nan")
    diff = d_l - d_s
    ci = (diff - q * se, diff + q * se)
    ok = bool(se > 0 and -margin <= ci[0] and ci[1] <= margin)
    return {"diff": diff, "se": se, "df": df, "ci": ci, "level": level, "margin": margin,
            "equivalent": ok}


def candidate_windows(T: int, t_lo_min: int = 8, min_slopes: int = 3) -> list[tuple[int, int]]:
    """Dyadic windows (lo, hi) with >= min_slopes consecutive dyadic slopes and lo >= t_lo_min."""
    times = dyadic_half_times(T)
    out = []
    for a, lo in enumerate(times):
        if lo < t_lo_min:
            continue
        for b in range(a + min_slopes, len(times)):
            out.append((lo, times[b]))
    return out


def adjacent_slopes_ok(qbar: np.ndarray, times: list[int], lo: int, hi: int,
                       max_diff: float = 0.10) -> bool:
    """§7: |difference of any two adjacent dyadic slopes within the window| <= max_diff."""
    i, j = times.index(lo), times.index(hi)
    slopes = [-2.0 * math.log2(qbar[k + 1] / qbar[k]) for k in range(i, j)]
    return all(abs(slopes[k + 1] - slopes[k]) <= max_diff for k in range(len(slopes) - 1))


def headroom_min(q_hi: np.ndarray, degrees: np.ndarray, n: int) -> float:
    """min over sampled sources of q_v(t_hi) / [deg(v)/(N-1)] (bipartite even-time floor)."""
    return float(np.min(np.asarray(q_hi) / (np.asarray(degrees, dtype=float) / (n - 1))))


# ----------------------------------------------------------------------------- CLI
def run_p0(root: Path = Path(".")) -> dict:
    report = {"manifest": manifest(root, seeds=[[TEST_SEED_BASE, "family", 0, "rep"]]),
              "P0a": p0a(), "P0b": p0b(), "P0c": p0c(), "P0d": p0d(root)}
    report["pass"] = all(report[k]["pass"] for k in ("P0a", "P0b", "P0c", "P0d"))
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S1 P0 engineering gates (no pilot seeds)")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    report = run_p0()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=1, default=str))
    print(json.dumps({k: report[k]["pass"] for k in ("P0a", "P0b", "P0c", "P0d")}))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
