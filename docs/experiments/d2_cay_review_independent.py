"""Later-pass reviewer check of PR #38 (D2 CAY). Written without using emergence_lab code:
own D1 verdict (from D1 prereg §2 text), own exact CAY mean (D2 prereg §4), own Pruefer decoder
(heap algorithm) and scipy csgraph BFS for regeneration. Only the seed rule (SeedSequence +
PCG64, spawn(1) for sources; rng.integers(0,N,N-2); src.choice(N,256,replace=False)) is copied."""
import csv, json, math, sys, heapq, hashlib, collections, statistics, time
import numpy as np
from scipy import stats, sparse
from scipy.sparse import csgraph

D = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "csv"

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def verdict(bbar, N, rmin=4, eps=0.15, k=3, guard=0.125):
    rs = sorted(r for r in bbar if r >= rmin and (r & (r - 1)) == 0 and 2 * r in bbar)
    A = []
    for r in rs:
        if bbar[2 * r] <= guard * N: A.append(r)
        else: break
    # A must be consecutive dyadic from rmin; stop at first inadmissible (balls monotone)
    if len(A) < 3: return {"verdict": "INSUFFICIENT_RANGE", "A": A}
    d = {r: math.log2(bbar[2 * r] / bbar[r]) for r in A}
    best = None
    for i in range(len(A)):
        for j in range(i + k - 1, len(A)):
            vals = [d[A[t]] for t in range(i, j + 1)]
            if max(vals) - min(vals) <= eps:
                key = (A[j], j - i + 1)
                if best is None or key > best[0]: best = (key, i, j)
    if best is None: return {"verdict": "NO_PLATEAU", "A": A}
    _, i, j = best
    return {"verdict": "PLATEAU", "A": A, "d_hat": d[A[j]], "r_last": A[j], "window": (A[i], 2 * A[j])}

def exact_mean(N, r):
    s, p = 0.0, 1.0
    for kk in range(r + 1):
        if kk > 0: p *= (1 - kk / N)
        s += (kk + 1) * p
    return s

def load_csv():
    acc = collections.defaultdict(lambda: collections.defaultdict(dict))
    for row in csv.DictReader(open(f"{D}/ball_counts.csv")):
        acc[(int(row["size"]), int(row["rep"]))][int(row["source"])][int(row["r"])] = int(row["ball"])
    return acc

if mode == "csv":
    man = json.load(open(f"{D}/manifest.json")); man2 = json.load(open(f"{D}/manifest_repeat.json"))
    for f in ("ball_counts.csv", "result.json"):
        print(f, "sha ok:", sha(f"{D}/{f}") == man["outputs"][f] == man2["outputs"][f])
    diff = {k for k in set(man) | set(man2) if man.get(k) != man2.get(k)}
    print("manifest keys differing between runs:", sorted(diff))
    acc = load_csv(); res = json.load(open(f"{D}/result.json"))
    byk = {(x["size"], x["i_rep"]): x for x in res["results"]}
    dh = collections.defaultdict(list); mism = 0; perrep = {}
    for (N, rep), srcs in sorted(acc.items()):
        assert len(srcs) == 256
        radii = sorted(next(iter(srcs.values())))
        bbar = {r: statistics.fmean(s[r] for s in srcs.values()) for r in radii}
        v = verdict(bbar, N); perrep[(N, rep)] = bbar
        x = byk[(N, rep)]
        ok = v["verdict"] == x["verdict"] and abs(v.get("d_hat", 0) - (x.get("d_hat") or 0)) < 1e-12
        mism += not ok
        dh[N].append((v["verdict"], v.get("d_hat"), v.get("r_last")))
        # sources sorted, distinct, in range
        ss = sorted(srcs); assert len(set(ss)) == 256 and ss[0] >= 0 and ss[-1] < N
        assert all(s[0] == 1 for s in srcs.values()) if 0 in radii else True
    print("replicate verdict/d_hat mismatches vs result.json:", mism)
    means = {}
    for N in sorted(dh):
        xs = [t[1] for t in dh[N] if t[0] == "PLATEAU"]
        m, s = statistics.mean(xs), statistics.stdev(xs); h = stats.t.ppf(.975, 7) * s / math.sqrt(8)
        means[N] = m
        print(f"N={N}: PLATEAU {len(xs)}/8 mean {m:.4f} sd {s:.4f} CI [{m-h:.3f},{m+h:.3f}] r_last {collections.Counter(t[2] for t in dh[N])}")
    print(f"G1: |m22-2|={abs(means[4194304]-2):.4f}  |m20-m22|={abs(means[1048576]-means[4194304]):.4f}")
    # G0: admissible r of pooled curve, t vs exact
    pairs = []
    for N in sorted(dh):
        reps = [perrep[(N, r)] for r in range(8)]
        pool = {r: statistics.fmean(b[r] for b in reps) for r in reps[0]}
        vp = verdict(pool, N)
        print(f"pooled N={N}: {vp['verdict']} d_hat {vp.get('d_hat'):.4f} window {vp.get('window')} A={vp['A']}")
        for r in vp["A"]:
            x = np.array([b[r] for b in reps]); e = exact_mean(N, r)
            pairs.append((N, r, (x.mean() - e) / (x.std(ddof=1) / math.sqrt(8))))
    crit = stats.t.ppf(1 - 0.01 / (2 * len(pairs)), 7)
    worst = max(pairs, key=lambda p: abs(p[2]))
    print(f"G0: pairs {len(pairs)} crit {crit:.3f} max|t| {abs(worst[2]):.3f} at {worst[:2]} pass {all(abs(p[2])<crit for p in pairs)}")
    # also t over all radii incl. 2r (not only admissible), descriptive
    allp = [(N, r, (np.mean(x) - exact_mean(N, r)) / (np.std(x, ddof=1) / math.sqrt(8)))
            for N in sorted(dh) for r in perrep[(N, 0)] if r >= 1
            for x in [[perrep[(N, q)][r] for q in range(8)]]]
    w = max(allp, key=lambda p: abs(p[2])); print(f"descriptive all radii: {len(allp)} pairs, max|t| {abs(w[2]):.3f} at {w[:2]}")
else:
    # regenerate: mode "regen", args: i_size N reps nsrc
    i_size, N, reps, nsrc = int(sys.argv[3]), int(sys.argv[4]), [int(x) for x in sys.argv[5].split(",")], int(sys.argv[6])
    acc = load_csv(); total = 0; bad = 0
    for rep in reps:
        t0 = time.time()
        ss = np.random.SeedSequence([2036101101, 0, i_size, rep])
        g = np.random.Generator(np.random.PCG64(ss)); s = np.random.Generator(np.random.PCG64(ss.spawn(1)[0]))
        seq = g.integers(0, N, size=N - 2).tolist()
        deg = [1] * N
        for x in seq: deg[x] += 1
        heap = [v for v in range(N) if deg[v] == 1]; heapq.heapify(heap)
        us, vs = [], []
        for x in seq:
            leaf = heapq.heappop(heap); us.append(leaf); vs.append(x)
            deg[x] -= 1
            if deg[x] == 1: heapq.heappush(heap, x)
        a, b = heapq.heappop(heap), heapq.heappop(heap); us.append(a); vs.append(b)
        A = sparse.coo_matrix((np.ones(N - 1), (us, vs)), shape=(N, N)).tocsr(); A = A + A.T
        assert csgraph.connected_components(A, directed=False)[0] == 1 and A.nnz == 2 * (N - 1)
        src = np.sort(s.choice(N, size=256, replace=False))
        csv_src = sorted(acc[(N, rep)])
        assert list(src) == csv_src, "source mismatch"
        pick = src[np.linspace(0, 255, nsrc).astype(int)] if nsrc < 256 else src
        for q in range(0, len(pick), 16):
            dist = csgraph.shortest_path(A, unweighted=True, directed=False, indices=pick[q:q+16])
            for row, v in zip(dist, pick[q:q+16]):
                hist = np.bincount(row.astype(np.int64)); cum = np.cumsum(hist)
                for r, ball in acc[(N, rep)][int(v)].items():
                    mine = int(cum[min(r, len(cum) - 1)]); total += 1; bad += mine != ball
        print(f"N={N} rep {rep}: sources match, {len(pick)} sources checked, {time.time()-t0:.0f}s", flush=True)
    print("ball counts compared:", total, "mismatches:", bad)
