"""Later-pass reviewer check of PR #39 (D2 UST, prereg v1.0-r3).

Modes (D = docs/experiments/2026-10-11-d2-ust):
  csv   D                 hashes vs both manifests; own D1 verdict (logic as in
                          d2_cay_review_independent.py, no emergence_lab import); all 24
                          verdicts/d_hat and the G2 numbers recomputed from the CSV.
  regen D i_size L reps   rebuild instances with the *library* generator (seed rule) and
                          recompute every ball count with scipy csgraph BFS (not the D1
                          shell_counts code); checks edges are torus edges, tree, sources.
                          This tests CSV/BFS consistency, not generator independence.
  ab    D L ntrees nsrc seed
                          independent generator: Aldous-Broder (vectorised first-entrance
                          random walk; a different exact UST sampler from Wilson), fresh seed.
                          Compares replicate means of B-bar(r) with the CSV replicates at the
                          same L (Welch t per r), the leaf fraction with the exact Z^2 value
                          8/pi^2 (1 - 2/pi), and the degree distribution with the library.
"""
import csv, json, math, sys, hashlib, collections, statistics, time
import numpy as np
from scipy import stats, sparse
from scipy.sparse import csgraph

D = sys.argv[2]
mode = sys.argv[1]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def verdict(bbar, N, rmin=4, eps=0.15, k=3, guard=0.125):
    rs = sorted(r for r in bbar if r >= rmin and (r & (r - 1)) == 0 and 2 * r in bbar)
    A = []
    for r in rs:
        if bbar[2 * r] <= guard * N:
            A.append(r)
        else:
            break
    if len(A) < 3:
        return {"verdict": "INSUFFICIENT_RANGE", "A": A}
    d = {r: math.log2(bbar[2 * r] / bbar[r]) for r in A}
    best = None
    for i in range(len(A)):
        for j in range(i + k - 1, len(A)):
            vals = [d[A[t]] for t in range(i, j + 1)]
            if max(vals) - min(vals) <= eps:
                key = (A[j], j - i + 1)
                if best is None or key > best[0]:
                    best = (key, i, j)
    if best is None:
        return {"verdict": "NO_PLATEAU", "A": A}
    _, i, j = best
    return {"verdict": "PLATEAU", "A": A, "d_hat": d[A[j]], "r_last": A[j], "window": (A[i], 2 * A[j])}


def load_csv():
    acc = collections.defaultdict(lambda: collections.defaultdict(dict))
    for row in csv.DictReader(open(f"{D}/ball_counts.csv")):
        acc[(int(row["size"]), int(row["rep"]))][int(row["source"])][int(row["r"])] = int(row["ball"])
    return acc


def rep_means(acc, L):
    out = []
    for rep in range(8):
        srcs = acc[(L, rep)]
        radii = sorted(next(iter(srcs.values())))
        out.append({r: statistics.fmean(s[r] for s in srcs.values()) for r in radii})
    return out


def tree_from_edges(n, us, vs):
    A = sparse.coo_matrix((np.ones(len(us)), (us, vs)), shape=(n, n)).tocsr()
    A = A + A.T
    return A


def balls(A, srcs, radii):
    res = {}
    for q in range(0, len(srcs), 16):
        dist = csgraph.shortest_path(A, unweighted=True, directed=False, indices=srcs[q:q + 16])
        for row, v in zip(dist, srcs[q:q + 16]):
            cum = np.cumsum(np.bincount(row.astype(np.int64)))
            res[int(v)] = {r: int(cum[min(r, len(cum) - 1)]) for r in radii}
    return res


def torus_ok(L, us, vs):
    ux, uy, vx, vy = us % L, us // L, vs % L, vs // L
    dx = (ux - vx) % L
    dy = (uy - vy) % L
    return bool(np.all(((dx == 0) & ((dy == 1) | (dy == L - 1))) | ((dy == 0) & ((dx == 1) | (dx == L - 1)))))


def aldous_broder(L, rng, chunk=1 << 22):
    """Parent edges of a UST of the L x L torus: each vertex's first-entrance edge."""
    n = L * L
    first = np.full(n, -1, dtype=np.int64)
    par = np.full(n, -1, dtype=np.int64)
    x, y = 0, 0
    first[0] = 0
    seen = 1
    t0 = 0
    while seen < n:
        d = rng.integers(0, 4, size=chunk)
        dx = np.where(d == 0, -1, np.where(d == 1, 1, 0))
        dy = np.where(d == 2, -1, np.where(d == 3, 1, 0))
        xs = (x + np.cumsum(dx)) % L
        ys = (y + np.cumsum(dy)) % L
        pos = ys * L + xs
        prev = np.concatenate(([y * L + x], pos[:-1]))
        uniq, idx = np.unique(pos, return_index=True)
        new = first[uniq] < 0
        u, i = uniq[new], idx[new]
        first[u] = t0 + i + 1
        par[u] = prev[i]
        seen += len(u)
        x, y = int(xs[-1]), int(ys[-1])
        t0 += chunk
    child = np.arange(n)[par >= 0]
    return child, par[child]


if mode == "csv":
    man = json.load(open(f"{D}/manifest.json"))
    man2 = json.load(open(f"{D}/manifest_repeat.json"))
    for f in ("ball_counts.csv", "result.json"):
        print(f, "sha ok:", sha(f"{D}/{f}") == man["outputs"][f] == man2["outputs"][f])
    print("manifest keys differing:", sorted(k for k in set(man) | set(man2) if man.get(k) != man2.get(k)))
    acc = load_csv()
    res = json.load(open(f"{D}/result.json"))
    byk = {(x["size"], x["i_rep"]): x for x in res["results"]}
    mism = 0
    means = {}
    for L in (256, 512, 1024):
        N = L * L
        vs = []
        for rep, bbar in enumerate(rep_means(acc, L)):
            assert len(acc[(L, rep)]) == 256
            v = verdict(bbar, N)
            x = byk[(L, rep)]
            mism += not (v["verdict"] == x["verdict"] and abs(v.get("d_hat", 0) - (x.get("d_hat") or 0)) < 1e-12)
            vs.append(v)
        xs = [v["d_hat"] for v in vs if v["verdict"] == "PLATEAU"]
        m, s = statistics.mean(xs), statistics.stdev(xs)
        h = stats.t.ppf(.975, len(xs) - 1) * s / math.sqrt(len(xs))
        means[L] = m
        print(f"L={L}: PLATEAU {len(xs)}/8 mean {m:.4f} sd {s:.4f} CI [{m-h:.3f},{m+h:.3f}] "
              f"r_last {collections.Counter(v.get('r_last') for v in vs)} max {max(xs):.3f}")
        reps = rep_means(acc, L)
        common = set.intersection(*(set(b) for b in reps))
        pool = {r: statistics.fmean(b[r] for b in reps) for r in sorted(common)}
        vp = verdict(pool, N)
        print(f"  pooled: {vp['verdict']} d_hat {vp.get('d_hat'):.4f} window {vp.get('window')}")
    print("verdict/d_hat mismatches vs result.json:", mism)
    m1024 = means[1024]
    print(f"G2: |m-1.6|={abs(m1024-1.6):.4f}<=0.15  |m512-m1024|={abs(means[512]-m1024):.4f}<=0.10")
elif mode == "regen":
    from emergence_lab import dimension_d2 as d2
    i_size, L, reps = int(sys.argv[3]), int(sys.argv[4]), [int(x) for x in sys.argv[5].split(",")]
    cfg = json.load(open("configs/dimension_d2.json"))
    acc = load_csv()
    tot = bad = 0
    degs = collections.Counter()
    for rep in reps:
        t0 = time.time()
        _, src = d2.build_instance(cfg, d2.UST, i_size, rep)
        # rebuild edges from the library parent array directly (independent of Graph internals)
        ss = np.random.SeedSequence([cfg["seed_base"], cfg["family_index_order"].index(d2.UST), i_size, rep])
        parent, _ = d2.wilson_parents_torus(L, np.random.Generator(np.random.PCG64(ss)))
        us, vs = np.arange(1, L * L), parent[1:]
        assert torus_ok(L, us, vs), "non-torus edge"
        A = tree_from_edges(L * L, us, vs)
        assert csgraph.connected_components(A, directed=False)[0] == 1
        degs.update(dict(enumerate(np.bincount(np.asarray(A.sum(axis=1)).ravel().astype(int)))))
        assert sorted(acc[(L, rep)]) == list(src), "source mismatch"
        radii = sorted(next(iter(acc[(L, rep)].values())))
        mine = balls(A, src, radii)
        for v, rr in acc[(L, rep)].items():
            for r, b in rr.items():
                tot += 1
                bad += mine[v][r] != b
        print(f"L={L} rep {rep}: torus tree ok, sources match, {time.time()-t0:.0f}s", flush=True)
    n = sum(degs.values())
    print("ball counts compared:", tot, "mismatches:", bad)
    print("library degree fractions:", {k: round(v / n, 4) for k, v in sorted(degs.items())})
elif mode == "ab":
    L, ntrees, nsrc, seed = map(int, sys.argv[3:7])
    acc = load_csv()
    lib = rep_means(acc, L)
    radii = sorted(set.intersection(*(set(b) for b in lib)))
    rng = np.random.Generator(np.random.PCG64(seed))
    mine = []
    degs = collections.Counter()
    for t in range(ntrees):
        t0 = time.time()
        us, vs = aldous_broder(L, rng)
        assert len(us) == L * L - 1 and torus_ok(L, us, vs)
        A = tree_from_edges(L * L, us, vs)
        assert csgraph.connected_components(A, directed=False)[0] == 1
        degs.update(dict(enumerate(np.bincount(np.asarray(A.sum(axis=1)).ravel().astype(int)))))
        src = np.sort(rng.choice(L * L, size=nsrc, replace=False))
        b = balls(A, src, radii)
        mine.append({r: statistics.fmean(b[v][r] for v in b) for r in radii})
        print(f"AB tree {t}: {time.time()-t0:.0f}s", flush=True)
    n = sum(degs.values())
    p1 = 8 / math.pi ** 2 * (1 - 2 / math.pi)
    print(f"AB degree fractions: { {k: round(v / n, 4) for k, v in sorted(degs.items())} }  "
          f"exact Z^2 leaf fraction {p1:.4f}; binomial se {math.sqrt(p1*(1-p1)/n):.4f}")
    ts = []
    for r in radii:
        a = [m[r] for m in mine]
        b = [m[r] for m in lib]
        if max(a + b) == min(a + b):
            print(f"r={r:5d} saturated (all {a[0]:.0f}), skipped")
            continue
        t, p = stats.ttest_ind(a, b, equal_var=False)
        ts.append((r, statistics.mean(a), statistics.mean(b), t, p))
        print(f"r={r:5d} AB mean {statistics.mean(a):12.2f}  CSV mean {statistics.mean(b):12.2f}  Welch t {t:+.2f} p {p:.3f}")
    crit = 0.01 / len(ts)
    print(f"min p {min(x[4] for x in ts):.4f}; Bonferroni alpha 0.01 over {len(ts)} radii -> per-test {crit:.5f}; "
          f"pass {all(x[4] > crit for x in ts)}")
    for k, lab in ((mine, "AB"), (lib, "CSV")):
        vv = [verdict(m, L * L) for m in k]
        print(lab, "per-tree verdicts", collections.Counter(v["verdict"] for v in vv),
              "mean d_hat", round(statistics.mean(v["d_hat"] for v in vv if "d_hat" in v), 4))
