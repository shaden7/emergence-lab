# Post-hoc, exploratory: degree post-stratified annealed window slopes on the archived S1 pilot CSV.
# Usage: python -I docs/experiments/s1_pilot_degree_poststrat.py docs/experiments/2026-10-17-s1-pilot/s1_pilot_numeric.csv
# Class weights: CAY 1+Poisson(1) limit (classes 1,2,3,>=4); UST: the pooled empirical degree shares of both sizes
# (no exact reference used for classes 2-4). SE: delete-one-tree jackknife per size. No emergence_lab imports.
import csv, sys, math, collections
import numpy as np
rows = list(csv.DictReader(open(sys.argv[1])))
times = [1 << k for k in range(13)]
def cls(d): return min(int(d), 4)
def load(fam, size):
    d = collections.defaultdict(list)
    for r in rows:
        if r["family"] == fam and r["size"] == size:
            d[int(r["i_rep"])].append((cls(r["degree"]), np.array([float(r[f"q_t{t}"]) for t in times])))
    return [d[k] for k in sorted(d)]
def qbar(trees, w):
    allrec = [x for t in trees for x in t]
    if w is None:
        return np.mean([q for _, q in allrec], axis=0)
    out = np.zeros(len(times))
    for k, wk in w.items():
        qs = [q for c, q in allrec if c == k]
        if not qs: return None
        out += wk * np.mean(qs, axis=0)
    return out
def slope(Q, lo, hi):
    a, b = times.index(lo), times.index(hi)
    return -2 * (math.log(Q[b]) - math.log(Q[a])) / math.log(hi / lo)
def jk(trees, w, lo, hi):
    full = slope(qbar(trees, w), lo, hi); n = len(trees)
    loo = [slope(qbar(trees[:i] + trees[i + 1:], w), lo, hi) for i in range(n)]
    return full, math.sqrt((n - 1) / n * sum((x - np.mean(loo)) ** 2 for x in loo))
e = math.e
pois = {1: 1 / e, 2: 1 / e, 3: 1 / (2 * e)}; pois[4] = 1 - sum(pois.values())
for fam, s, l in [("cayley_uniform_tree", "65536", "262144"), ("ust_2d_torus", "128", "256")]:
    Ts, Tl = load(fam, s), load(fam, l)
    if fam.startswith("ust"):
        c = collections.Counter(x[0] for t in Ts + Tl for x in t); n = sum(c.values())
        w = {k: c[k] / n for k in (1, 2, 3, 4)}
    else:
        w = pois
    print(fam, "weights", {k: round(v, 4) for k, v in w.items()})
    for lo, hi in [(8, 64), (32, 256), (128, 1024), (256, 2048), (512, 4096)]:
        for lab, ww in (("raw", None), ("poststrat", w)):
            a, sa = jk(Ts, ww, lo, hi); b, sb = jk(Tl, ww, lo, hi); se = math.hypot(sa, sb)
            print(f"  W={lo}-{hi} {lab:9s} small {a:.3f}±{sa:.3f} large {b:.3f}±{sb:.3f} diff {b - a:+.3f}±{se:.3f}")
