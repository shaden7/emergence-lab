"""Later-pass reviewer check of PR #41 (D2 RRT, prereg v1.0-r3). No emergence_lab import.

Modes (D = docs/experiments/2026-10-12-d2-rrt):
  csv   D                  hashes vs both manifests; own D1 verdict (same logic as the UST/CAY
                           review scripts, re-typed); all 24 verdicts, admissible sets and the
                           r_min = 2 sensitivity recomputed from the CSV; B-bar(32)/N per size.
  regen D i_size rep nsrc  rebuild one instance from the seed rule (SeedSequence + PCG64, same
                           rng call as the library, re-typed) and recompute the first nsrc
                           sources' ball counts with an own level-synchronous numpy BFS.
                           Tests CSV/BFS consistency, not generator independence.
  indep D N ntrees nsrc seed
                           independent generator: parent(i) = floor(U_i * i) from Generator.random
                           (a different algorithm and stream from rng.integers), fresh seed, own
                           BFS. Compares replicate means of B-bar(r) with the CSV replicates at
                           the same N (Welch t per r, Bonferroni over r), and reports own verdicts.
"""
import csv, json, math, sys, hashlib, collections, statistics, time
import numpy as np
from scipy import stats

mode, D = sys.argv[1], sys.argv[2]
SEED_BASE, I_FAM = 2036101101, 2
SIZES = [2 ** 18, 2 ** 20, 2 ** 22]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def verdict(bbar, N, rmin=4, eps=0.15, k=3, guard=0.125):
    A, r = [], rmin
    while r in bbar and 2 * r in bbar:
        if bbar[2 * r] > guard * N:
            break
        A.append(r)
        r *= 2
    else:
        raise ValueError("missing radius")
    if len(A) < k:
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
        return {"verdict": "NO_PLATEAU", "A": A, "d": d}
    _, i, j = best
    return {"verdict": "PLATEAU", "A": A, "d_hat": d[A[j]]}


def load_csv():
    acc = collections.defaultdict(lambda: collections.defaultdict(dict))
    for row in csv.DictReader(open(f"{D}/ball_counts.csv")):
        acc[(int(row["size"]), int(row["rep"]))][int(row["source"])][int(row["r"])] = int(row["ball"])
    return acc


def rep_bbar(srcs):
    radii = set.intersection(*[set(b) for b in srcs.values()])
    return {r: statistics.fmean(b[r] for b in srcs.values()) for r in radii}


def csr(parent):
    n = parent.size
    a = np.concatenate([np.arange(1, n), parent[1:]])
    b = np.concatenate([parent[1:], np.arange(1, n)])
    o = np.argsort(a, kind="stable")
    indptr = np.zeros(n + 1, np.int64)
    np.add.at(indptr, a + 1, 1)
    return np.cumsum(indptr), b[o]


def shells(indptr, ind, s):
    """Level-synchronous BFS; returns counts at distance 0, 1, 2, ..."""
    n = indptr.size - 1
    seen = np.zeros(n, bool)
    seen[s] = True
    front, out = np.array([s]), [1]
    while front.size:
        st, en = indptr[front], indptr[front + 1]
        lens = en - st
        idx = np.repeat(st - np.cumsum(lens) + lens, lens) + np.arange(lens.sum())
        nb = np.unique(ind[idx])
        nb = nb[~seen[nb]]
        seen[nb] = True
        if nb.size:
            out.append(nb.size)
        front = nb
    return np.array(out)


def balls(sh, radii):
    c = np.cumsum(sh)
    return {r: int(c[min(r, c.size - 1)]) for r in radii}


RADII = [1, 2, 4, 8, 16, 32, 64, 128]

if mode == "csv":
    m1, m2 = (json.load(open(f"{D}/{f}")) for f in ("manifest.json", "manifest_repeat.json"))
    for f in ("ball_counts.csv", "result.json"):
        h = sha(f"{D}/{f}")
        print(f, h[:12], "manifest", h == m1["outputs"][f], "repeat", h == m2["outputs"][f])
    res = {(r["size"], r["i_rep"]): r for r in json.load(open(f"{D}/result.json"))["results"]}
    acc = load_csv()
    mism, cnt, sens2, ratio = 0, collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for (N, rep), srcs in sorted(acc.items()):
        assert len(srcs) == 256
        bb = rep_bbar(srcs)
        v = verdict(bb, N)
        lib = res[(N, rep)]
        mism += (v["verdict"] != lib["verdict"]) or (v["A"] != lib["admissible"])
        cnt[(N, v["verdict"])] += 1
        sens2[(N, verdict(bb, N, rmin=2)["verdict"])] += 1
        ratio[N].append(bb[32] / N)
    print("replicates", len(acc), "verdict/admissible mismatches vs result.json:", mism)
    print("main verdicts:", dict(cnt))
    print("r_min=2:", dict(sens2))
    for N in SIZES:
        pool = statistics.fmean(ratio[N])
        print(f"N={N}: mean over reps of Bbar(32)/N = {pool:.3f} (range {min(ratio[N]):.3f}-{max(ratio[N]):.3f})")
    print("G3:", "PASS" if not any(k[1] == "PLATEAU" for k in cnt) else "FAIL")

elif mode == "regen":
    i_size, rep, nsrc = map(int, sys.argv[3:6])
    N = SIZES[i_size]
    ss = np.random.SeedSequence([SEED_BASE, I_FAM, i_size, rep])
    g = np.random.Generator(np.random.PCG64(ss))
    sr = np.random.Generator(np.random.PCG64(ss.spawn(1)[0]))
    parent = np.empty(N, np.int64)
    parent[0] = -1
    parent[1:] = g.integers(0, np.arange(1, N, dtype=np.int64))
    src = np.sort(sr.choice(N, size=256, replace=False))
    acc = load_csv()[(N, rep)]
    assert sorted(acc) == [int(s) for s in src], "source set differs"
    indptr, ind = csr(parent)
    t, comp, bad = time.time(), 0, 0
    for s in src[:nsrc]:
        b = balls(shells(indptr, ind, int(s)), list(acc[int(s)]))
        for r, x in acc[int(s)].items():
            comp += 1
            bad += b[r] != x
    print(f"N={N} rep={rep}: {comp} ball counts compared over {nsrc} sources, mismatches {bad} ({time.time()-t:.0f}s)")

elif mode == "indep":
    N, ntrees, nsrc, seed = map(int, sys.argv[3:7])
    rng = np.random.Generator(np.random.PCG64(seed))
    mine = collections.defaultdict(list)
    vc = collections.Counter()
    for t in range(ntrees):
        parent = np.empty(N, np.int64)
        parent[0] = -1
        i = np.arange(1, N)
        parent[1:] = np.floor(rng.random(N - 1) * i).astype(np.int64)
        assert np.all(parent[1:] < i) and np.all(parent[1:] >= 0)
        indptr, ind = csr(parent)
        src = rng.choice(N, size=nsrc, replace=False)
        bl = [balls(shells(indptr, ind, int(s)), RADII + [256]) for s in src]
        bb = {r: statistics.fmean(b[r] for b in bl) for r in RADII + [256]}
        for r in RADII:
            mine[r].append(bb[r])
        vc[verdict(bb, N)["verdict"]] += 1
    acc = load_csv()
    theirs = collections.defaultdict(list)
    for (n, rep), srcs in acc.items():
        if n == N:
            bb = rep_bbar(srcs)
            for r in RADII:
                if r in bb:
                    theirs[r].append(bb[r])
    print(f"N={N}: own {ntrees} trees x {nsrc} sources (seed {seed}); own verdicts {dict(vc)}")
    tested = [r for r in RADII if len(theirs[r]) >= 2 and len(mine[r]) >= 2
              and len(set(mine[r] + theirs[r])) > 1]  # skip radii saturated at N in every tree
    pmin = 1
    for r in tested:
        tt = stats.ttest_ind(mine[r], theirs[r], equal_var=False)
        pmin = min(pmin, tt.pvalue)
        print(f"  r={r:3d}: own {statistics.fmean(mine[r]):12.2f}  csv {statistics.fmean(theirs[r]):12.2f}"
              f"  ratio {statistics.fmean(mine[r])/statistics.fmean(theirs[r]):.4f}  p={tt.pvalue:.3f}")
    print(f"  smallest p {pmin:.3f}; Bonferroni threshold 0.05/{len(tested)} = {0.05/len(tested):.4f}"
          f" -> {'no rejection' if pmin > 0.05/len(tested) else 'REJECT'}")
