"""D2 out-of-sample test of the frozen D1 estimator (Issue #4): implementation of prereg v1.0-r3.

Frozen design: docs/DIMENSION_D2_PREREGISTRATION.md with configs/dimension_d2.json (both pinned
below and checked at run time). New code is limited to the three generators, structural checks,
the D2-G0 CAY distributional check, the gates D2-G1...D2-G3 and the driver. The D1 code path
(`verdict`, `shell_counts`, `ball_sizes`, `mean_balls`, `required_radii`, `_seed_seq`) is reused
unchanged.

Running a family on the preregistered seed base produces gated output; per the prereg (§8) this is
done only after a later-pass review of this implementation.

Implementation choices not fixed verbatim by the prereg (flagged for review):
* Pruefer decoding: the standard linear-time decoder (pointer to the smallest leaf plus the
  "new leaf smaller than pointer" shortcut). Sequence entries are rng.integers(0, N, N - 2).
* Wilson's algorithm: root vertex 0; the processing order is rng.permutation(N); walk steps take
  a direction in {-x, +x, -y, +y} (vertex index y*L + x) from blocks of rng.integers(0, 4, 4096)
  drawn on demand from the same replicate stream. The block size affects only which stream
  values are used, not the distribution (each step is an independent uniform direction).
  Loop erasure is the "last exit" pointer form of Wilson's cycle-popping: the walk overwrites
  next[u] on each visit, and the retrace from the start vertex follows the final pointers.
* RRT: parent(i) = rng.integers(0, i) for i = 1..N-1, drawn as one vectorised call.
* Sources: S distinct vertices, src_rng.choice(N, S, replace=False), sorted (as in D1).
* D2-G0 CAY check: radii are the admissible scales of the pooled curve at each N; t uses the
  8 replicate means of B-bar(r), df = 7, two-sided Bonferroni over all (N, r) pairs at alpha 0.01.
* G1/G2 size comparison: 8/8 PLATEAU is required at the largest size only (prereg §5 text); the
  middle-size mean is over its PLATEAU replicates, as in the §5a power model (later-pass review fix;
  the first version also required 8/8 there, which is not in the prereg and would have raised the
  model's noise-only G1 failure probability from about 0.3 % to about 2.7 %).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.csgraph import connected_components

from .dimension_d1 import (PLATEAU, Graph, _from_edges, _seed_seq, git_blob_sha, mean_balls,
                           required_radii, rows_to_csv, shell_counts, verdict, ball_sizes)

PREREG_PATH = "docs/DIMENSION_D2_PREREGISTRATION.md"
CONFIG_PATH = "configs/dimension_d2.json"
# Pinned at the v1.0-r3 errata commit (no parameter change against the PR #35 merge 505ab21).
PREREG_BLOB_SHA = "8f53e1e08c11c912010479a4638ac22d2ab97644"
CONFIG_SHA256 = "a0609a6d29a6015a20344cc50af5f8ffd39045226c76657e05f5a0ee1d429d2d"

CAY, UST, RRT = "cayley_uniform_tree", "ust_2d_torus", "random_recursive_tree"
WILSON_BLOCK = 4096


# ----------------------------------------------------------------------------- generators
def prufer_decode(seq) -> tuple[np.ndarray, np.ndarray]:
    """Edges (u, v) of the labelled tree on [N], N = len(seq) + 2, with Pruefer sequence `seq`.
    Linear time. Returns int64 arrays of length N - 1."""
    seq = [int(x) for x in seq]
    n = len(seq) + 2
    deg = [1] * n
    for x in seq:
        deg[x] += 1
    us, vs = [0] * (n - 1), [0] * (n - 1)
    ptr = 0
    while deg[ptr] != 1:
        ptr += 1
    leaf = ptr
    k = 0
    for x in seq:
        us[k], vs[k] = leaf, x
        k += 1
        deg[x] -= 1
        if x < ptr and deg[x] == 1:
            leaf = x
        else:
            ptr += 1
            while deg[ptr] != 1:
                ptr += 1
            leaf = ptr
    # the two remaining vertices of degree 1: `leaf` and n - 1
    us[k], vs[k] = leaf, n - 1
    return np.asarray(us, dtype=np.int64), np.asarray(vs, dtype=np.int64)


def cayley_tree(n: int, rng: np.random.Generator) -> Graph:
    if n < 2:
        raise ValueError("need N >= 2")
    seq = rng.integers(0, n, size=n - 2)
    u, v = prufer_decode(seq)
    return _from_edges(n, u, v, {"generator": "pruefer"})


def wilson_parents_torus(L: int, rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """Parent array of a uniform spanning tree of the L x L periodic square lattice (Wilson's
    algorithm, root 0). parent[0] = -1. Returns (parent, number of walk steps)."""
    if L < 3:
        raise ValueError("need L >= 3 (simple torus graph)")
    n = L * L
    in_tree = bytearray(n)
    in_tree[0] = 1
    nxt = [0] * n
    order = rng.permutation(n).tolist()
    buf: list[int] = []
    bi = 0
    steps = 0
    for start in order:
        u = start
        while not in_tree[u]:
            if bi == len(buf):
                buf = rng.integers(0, 4, size=WILSON_BLOCK).tolist()
                bi = 0
            dirn = buf[bi]
            bi += 1
            x, y = u % L, u // L
            if dirn == 0:
                w = y * L + (x - 1) % L
            elif dirn == 1:
                w = y * L + (x + 1) % L
            elif dirn == 2:
                w = ((y - 1) % L) * L + x
            else:
                w = ((y + 1) % L) * L + x
            nxt[u] = w
            u = w
            steps += 1
        u = start
        while not in_tree[u]:
            in_tree[u] = 1
            u = nxt[u]
    parent = np.asarray(nxt, dtype=np.int64)
    parent[0] = -1
    return parent, steps


def ust_torus(L: int, rng: np.random.Generator) -> Graph:
    parent, steps = wilson_parents_torus(L, rng)
    child = np.arange(1, L * L, dtype=np.int64)
    return _from_edges(L * L, child, parent[1:], {"generator": "wilson", "L": L, "walk_steps": steps})


def rrt_parents(n: int, rng: np.random.Generator) -> np.ndarray:
    """parent[i] uniform in {0, ..., i-1} for i >= 1; parent[0] = -1."""
    parent = np.empty(n, dtype=np.int64)
    parent[0] = -1
    if n > 1:
        parent[1:] = rng.integers(0, np.arange(1, n, dtype=np.int64))
    return parent


def random_recursive_tree(n: int, rng: np.random.Generator) -> Graph:
    parent = rrt_parents(n, rng)
    g = _from_edges(n, np.arange(1, n, dtype=np.int64), parent[1:], {"generator": "rrt"})
    g.info["parent_order_ok"] = bool(np.all(parent[1:] < np.arange(1, n)))
    return g


# ----------------------------------------------------------------------------- checks
def is_connected(g: Graph) -> bool:
    a = sparse.csr_matrix((np.ones(g.indices.size, dtype=np.int8), g.indices, g.indptr),
                          shape=(g.n, g.n))
    return connected_components(a, directed=False)[0] == 1


def torus_edges_ok(g: Graph, L: int) -> bool:
    """Every edge of g joins torus nearest neighbours (vertex index y*L + x)."""
    src = np.repeat(np.arange(g.n, dtype=np.int64), g.degrees)
    dst = g.indices.astype(np.int64)
    dx = np.abs(src % L - dst % L)
    dy = np.abs(src // L - dst // L)
    dx = np.minimum(dx, L - dx)
    dy = np.minimum(dy, L - dy)
    return bool(np.all(dx + dy == 1))


def structural_checks(fam: str, g: Graph, size: int) -> dict:
    tree = g.n_edges == g.n - 1 and g.info.get("self_loops_removed") == 0 \
        and g.info.get("duplicate_edges_removed") == 0
    conn = is_connected(g)
    out = {"n": g.n, "edges": g.n_edges, "tree_edge_count": bool(tree), "connected": bool(conn)}
    ok = tree and conn
    if fam == UST:
        out["lattice_edges"] = torus_edges_ok(g, size)
        ok = ok and out["lattice_edges"]
    if fam == RRT:
        out["parent_order"] = g.info["parent_order_ok"]
        ok = ok and out["parent_order"]
    out["pass"] = bool(ok)
    return out


# ----------------------------------------------------------------------------- exact reference
def cayley_ball_mean(n: int, radii) -> dict:
    """E|B(v, r)| = sum_{k<=r} (k+1) prod_{i<=k} (1 - i/N) for the uniform labelled tree (§4)."""
    rmax = int(max(radii))
    out, cum, prod = {}, 0.0, 1.0
    want = set(int(r) for r in radii)
    for k in range(rmax + 1):
        if k > 0:
            prod *= 1.0 - k / n
        cum += (k + 1) * prod
        if k in want:
            out[k] = cum
    return out


# ----------------------------------------------------------------------------- run
def validate_frozen_files(root: Path = Path(".")) -> dict:
    prereg = (root / PREREG_PATH).read_bytes()
    cfg_raw = (root / CONFIG_PATH).read_bytes()
    if git_blob_sha(prereg) != PREREG_BLOB_SHA:
        raise ValueError("D2 preregistration differs from the pinned frozen blob")
    if hashlib.sha256(cfg_raw).hexdigest() != CONFIG_SHA256:
        raise ValueError("D2 config differs from the pinned SHA-256")
    return {"prereg_blob_sha": PREREG_BLOB_SHA, "config_sha256": CONFIG_SHA256}


def sizes(cfg: dict, fam: str) -> list[int]:
    f = cfg["families"][fam]
    return f["L"] if fam == UST else f["N"]


def build_instance(cfg: dict, fam: str, i_size: int, i_rep: int, size: int | None = None,
                   seed_base: int | None = None):
    """Return (graph, sorted sources). `size`/`seed_base` overrides are for tests only."""
    i_fam = cfg["family_index_order"].index(fam)
    size = sizes(cfg, fam)[i_size] if size is None else size
    graph_rng, src_rng = _seed_seq(cfg["seed_base"] if seed_base is None else seed_base,
                                   i_fam, i_size, i_rep)
    if fam == CAY:
        g = cayley_tree(size, graph_rng)
    elif fam == UST:
        g = ust_torus(size, graph_rng)
    elif fam == RRT:
        g = random_recursive_tree(size, graph_rng)
    else:
        raise KeyError(fam)
    S = cfg["families"][fam]["sources"]
    sources = np.sort(src_rng.choice(g.n, size=min(S, g.n), replace=False))
    return g, sources


def _est(cfg: dict) -> dict:
    e = cfg["estimator_parameters"]
    return {"r_min": e["r_min"], "eps": e["plateau_epsilon"], "min_scales": e["plateau_min_scales"]}


def analyse(bbar: dict, n: int, cfg: dict) -> dict:
    e = _est(cfg)
    sens_cfg = cfg["sensitivity_not_gated"]
    main = verdict(bbar, n, e["r_min"], e["eps"], e["min_scales"], 0.125)
    sens = {}
    for x in sens_cfg["plateau_epsilon"]:
        sens[f"eps={x}"] = verdict(bbar, n, e["r_min"], x, e["min_scales"], 0.125)["verdict"]
    for rm in sens_cfg["r_min"]:
        sens[f"r_min={rm}"] = verdict(bbar, n, rm, e["eps"], e["min_scales"], 0.125)["verdict"]
    for gf in sens_cfg["saturation_guard_fraction"]:
        sens[f"guard={gf}"] = verdict(bbar, n, e["r_min"], e["eps"], e["min_scales"], gf)["verdict"]
    main["sensitivity"] = sens
    main["bbar"] = {str(k): v for k, v in bbar.items()}
    return main


def run_replicate(cfg: dict, fam: str, i_size: int, i_rep: int, size: int | None = None,
                  seed_base: int | None = None):
    size_v = sizes(cfg, fam)[i_size] if size is None else size
    g, sources = build_instance(cfg, fam, i_size, i_rep, size, seed_base)
    chk = structural_checks(fam, g, size_v)
    shells = [shell_counts(g, int(s)) for s in sources]
    r_floor = min([_est(cfg)["r_min"]] + cfg["sensitivity_not_gated"]["r_min"])
    radii = required_radii(shells, r_floor)
    res = analyse(mean_balls(shells, radii), g.n, cfg)
    res.update(family=fam, size=size_v, i_size=i_size, i_rep=i_rep, n=g.n,
               sources=[int(s) for s in sources], structural_check=chk,
               generator_info={k: v for k, v in g.info.items()})
    rows = []
    for s, sh in zip(sources, shells):
        b = ball_sizes(sh, radii)
        rows += [{"family": fam, "size": size_v, "rep": i_rep, "source": int(s), "r": r, "ball": int(x)}
                 for r, x in zip(radii, b)]
    return res, rows, shells


def _t_crit(df: int, q: float) -> float:
    from scipy.stats import t
    return float(t.ppf(q, df))


def pooled(results: list[dict], shells_by_key: dict, cfg: dict) -> dict:
    """Pooled curve per (family, size) over all replicates and sources (reported; used by G0)."""
    out = {}
    for fam, size in sorted({(r["family"], r["size"]) for r in results}):
        sh = [s for (f, z, _), ss in shells_by_key.items() if f == fam and z == size for s in ss]
        n = next(r["n"] for r in results if r["family"] == fam and r["size"] == size)
        r_floor = min([_est(cfg)["r_min"]] + cfg["sensitivity_not_gated"]["r_min"])
        res = analyse(mean_balls(sh, required_radii(sh, r_floor)), n, cfg)
        out[f"{fam}:{size}"] = res
    return out


def cayley_g0(results: list[dict], pooled_res: dict, alpha: float = 0.01) -> dict:
    """D2-G0 CAY distributional check: replicate means of B-bar(r) vs the exact formula."""
    cay = [r for r in results if r["family"] == CAY]
    pairs = []
    for N in sorted({r["size"] for r in cay}):
        reps = [r for r in cay if r["size"] == N]
        for rad in pooled_res[f"{CAY}:{N}"]["admissible"]:
            x = np.array([r["bbar"][str(rad)] for r in reps])
            pairs.append((N, rad, x))
    m = len(pairs)
    if m == 0:
        return {"pairs": 0, "pass": False}
    out = []
    for N, rad, x in pairs:
        exact = cayley_ball_mean(N, [rad])[rad]
        se = float(np.std(x, ddof=1) / math.sqrt(len(x)))
        t = (float(np.mean(x)) - exact) / se if se > 0 else float("inf")
        out.append({"N": N, "r": rad, "mean": float(np.mean(x)), "exact": exact, "t": t, "n_rep": len(x)})
    df = min(o["n_rep"] for o in out) - 1
    crit = _t_crit(df, 1 - alpha / (2 * m))
    return {"pairs": m, "df": df, "t_crit": crit, "tests": out,
            "pass": all(abs(o["t"]) < crit for o in out)}


def _family_stats(rs: list[dict]) -> dict:
    dh = [r["d_hat"] for r in rs if r["verdict"] == PLATEAU]
    st = {"n_rep": len(rs), "n_plateau": len(dh), "verdicts": [r["verdict"] for r in rs],
          "r_last": [r["admissible"][-1] if r["admissible"] else None for r in rs]}
    if dh:
        st["mean"] = float(np.mean(dh))
    if len(dh) >= 2:
        m, s = st["mean"], float(np.std(dh, ddof=1))
        hw = _t_crit(len(dh) - 1, 0.975) * s / math.sqrt(len(dh))
        st.update(sd=s, ci95=[m - hw, m + hw])
    return st


def evaluate_gates(results: list[dict], pooled_res: dict, cfg: dict) -> dict:
    by: dict = {}
    for r in results:
        by.setdefault(r["family"], []).append(r)
    gates: dict = {}
    struct_ok = all(r["structural_check"]["pass"] for r in results)
    g0 = {"structural_pass": struct_ok, "unit_tests": "tests/test_dimension_d2.py (CI pytest)"}
    if CAY in by:
        g0["cayley"] = cayley_g0(results, pooled_res)
        g0["pass"] = struct_ok and g0["cayley"]["pass"]
    else:
        g0["pass"] = struct_ok
    gates["D2-G0"] = g0

    def two_size(fam, target, extra=None):
        # Prereg §5 (G1/G2) requires 8/8 PLATEAU only at the largest size; the middle-size
        # "replicate mean" is the mean d_hat over its PLATEAU replicates, as in the §5a power
        # model (nanmean). It is undefined, and the gate fails, if no replicate there is PLATEAU.
        zs = sizes(cfg, fam)
        stats = {str(z): _family_stats([r for r in by[fam] if r["size"] == z]) for z in zs}
        top, mid = stats[str(zs[2])], stats[str(zs[1])]
        ok = (top["n_rep"] == 8 and top["n_plateau"] == 8 and abs(top["mean"] - target) <= 0.15
              and mid["n_rep"] == 8 and "mean" in mid
              and abs(mid["mean"] - top["mean"]) <= 0.10)
        if extra is not None and ok:
            ok = extra(top)
        return {"by_size": stats, "pass": bool(ok)}

    if CAY in by:
        gates["D2-G1"] = two_size(CAY, 2.0)
        gates["D2-G1"]["note"] = ("8/8 PLATEAU is required at 2^22 only (prereg §5); the 2^20 mean is "
                                   "over its PLATEAU replicates (prereg §5a model), n_plateau reported")
    if UST in by:
        gates["D2-G2"] = two_size(UST, 1.6, extra=lambda top: top["ci95"][1] < 1.85)
        gates["D2-G2"]["note"] = ("8/8 PLATEAU is required at L=1024 only (prereg §5); the L=512 mean is "
                                   "over its PLATEAU replicates, n_plateau reported")
    if RRT in by:
        rs = by[RRT]
        counts: dict = {}
        for r in rs:
            counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
        gates["D2-G3"] = {"verdict_counts": counts, "n": len(rs),
                          "pass": len(rs) == 24 and all(r["verdict"] != PLATEAU for r in rs)}
    return gates


def run(cfg: dict, families: list[str], outdir: Path, check_frozen: bool = True) -> dict:
    t0, c0 = time.time(), time.process_time()
    frozen = validate_frozen_files() if check_frozen else {"prereg_blob_sha": None, "config_sha256": None}
    order = cfg["family_index_order"]
    families = sorted(families, key=order.index)
    results, rows, shells_by_key = [], [], {}
    for fam in families:
        for i_size, z in enumerate(sizes(cfg, fam)):
            for i_rep in range(cfg["families"][fam]["replicates"]):
                res, rr, sh = run_replicate(cfg, fam, i_size, i_rep)
                results.append(res)
                rows += rr
                shells_by_key[(fam, z, i_rep)] = sh
            print(f"{fam} size={z} done ({time.time() - t0:.0f}s)", file=sys.stderr, flush=True)
    pooled_res = pooled(results, shells_by_key, cfg)
    gates = evaluate_gates(results, pooled_res, cfg)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_bytes = rows_to_csv(rows)
    result = {"families": families, "results": results, "pooled": pooled_res, "gates": gates}
    result_bytes = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode()
    (outdir / "ball_counts.csv").write_bytes(csv_bytes)
    (outdir / "result.json").write_bytes(result_bytes)
    peak_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    manifest = {**frozen, "commit": os.getenv("GIT_SHA"), "python": platform.python_version(),
                "numpy": np.__version__, "scipy": scipy.__version__, "seed_base": cfg["seed_base"],
                "seed_rule": cfg["seed_rule"], "families": families,
                "seed_tuples": [[cfg["seed_base"], order.index(r["family"]), r["i_size"], r["i_rep"]]
                                for r in results],
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
    ap.add_argument("--families", required=True,
                    help="'all' or comma-separated family names (one invocation per family is allowed, prereg §8)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text())
    order = cfg["family_index_order"]
    fams = order if a.families == "all" else a.families.split(",")
    for f in fams:
        if f not in order:
            raise SystemExit(f"unknown family {f}")
    m = run(cfg, fams, a.output)
    print(json.dumps(m, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
