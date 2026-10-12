"""Producer check (UST): recompute every replicate verdict / d_hat from ball_counts.csv with the
frozen D1 verdict, and recompute the D2-G2 numbers independently of dimension_d2.evaluate_gates.
N = L*L is the vertex count passed to the verdict (saturation guard), as in the driver."""
import csv, json, sys, collections, statistics, math
from scipy import stats
from emergence_lab.dimension_d1 import verdict
d = sys.argv[1]
res = json.load(open(f"{d}/result.json"))
acc = collections.defaultdict(lambda: collections.defaultdict(list))
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    if row["family"] != "ust_2d_torus":
        continue
    acc[(int(row["size"]), int(row["rep"]))][int(row["r"])].append(int(row["ball"]))
mism = 0; dh = collections.defaultdict(list); verds = collections.defaultdict(list)
byk = {(x["size"], x["i_rep"]): x for x in res["results"] if x["family"] == "ust_2d_torus"}
for (L, rep), m in sorted(acc.items()):
    assert all(len(v) == 256 for v in m.values())
    bbar = {r: sum(v) / len(v) for r, v in m.items()}
    v = verdict(bbar, L * L, 4, 0.15, 3, 0.125)
    x = byk[(L, rep)]
    same_d = (v["d_hat"] is None and x["d_hat"] is None) or (
        v["d_hat"] is not None and x["d_hat"] is not None and abs(v["d_hat"] - x["d_hat"]) <= 1e-12)
    if v["verdict"] != x["verdict"] or not same_d:
        mism += 1
    verds[L].append(v["verdict"])
    if v["verdict"] == "PLATEAU":
        dh[L].append(v["d_hat"])
print("replicates", len(acc), "mismatches", mism)
for L in sorted(verds):
    xs = dh[L]
    if len(xs) >= 2:
        m = statistics.mean(xs); s = statistics.stdev(xs); h = stats.t.ppf(0.975, len(xs) - 1) * s / math.sqrt(len(xs))
        print(L, verds[L].count("PLATEAU"), "/8 PLATEAU mean %.4f sd %.4f ci [%.4f, %.4f]" % (m, s, m - h, m + h))
    else:
        print(L, verds[L].count("PLATEAU"), "/8 PLATEAU", collections.Counter(verds[L]))
if len(dh[1024]) >= 2 and dh[512]:
    m5, m10 = statistics.mean(dh[512]), statistics.mean(dh[1024])
    s = statistics.stdev(dh[1024]); up = m10 + stats.t.ppf(0.975, len(dh[1024]) - 1) * s / math.sqrt(len(dh[1024]))
    print("G2: 8/8 at L=1024: %s, |m1024-1.6| = %.4f (<=0.15), upper CI %.4f (<1.85), |m512-m1024| = %.4f (<=0.10)"
          % (verds[1024].count("PLATEAU") == 8, abs(m10 - 1.6), up, abs(m5 - m10)))
