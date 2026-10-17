# Independent recomputation of S1 pilot P5 from the numeric CSV (no emergence_lab imports).
import csv, math, sys, collections
import numpy as np
rows = list(csv.DictReader(open(sys.argv[1])))
times = [1 << k for k in range(13)]
def Q(fam, size):
    d = collections.defaultdict(list)
    for r in rows:
        if r["family"] == fam and r["size"] == size and r["status"] == "OK":
            d[int(r["i_rep"])].append([float(r[f"q_t{t}"]) for t in times])
    return np.array([np.mean(d[k], axis=0) for k in sorted(d)])  # trees x times
def slope_infl(Qm, lo, hi):
    a, b = times.index(lo), times.index(hi); m = Qm.mean(0); c = -2 / math.log(hi / lo)
    return c * (math.log(m[b]) - math.log(m[a])), c * ((Qm[:, b] - m[b]) / m[b] - (Qm[:, a] - m[a]) / m[a])
out = {}
for fam, s, l in [("cayley_uniform_tree", "65536", "262144"), ("ust_2d_torus", "128", "256")]:
    Qs, Ql = Q(fam, s), Q(fam, l); n_pass_z = 0; tested = 0; mx = None
    for lo in times[3:]:
        for hi in times[times.index(lo) + 3:]:
            ds, ps = slope_infl(Qs, lo, hi); dl, pl = slope_infl(Ql, lo, hi)
            se = math.sqrt(ps.var(ddof=1) / len(ps) + pl.var(ddof=1) / len(pl)); diff = dl - ds
            ci = (diff - 1.645 * se, diff + 1.645 * se); tested += 1
            n_pass_z += (-0.03 <= ci[0] and ci[1] <= 0.03)
            if (lo, hi) == (128, 1024): mx = (round(diff, 6), round(se, 6))
    print(fam, Qs.shape, Ql.shape, "windows", tested, "pass with normal z (narrower than Welch):", n_pass_z, "128-1024 diff,se:", mx)
