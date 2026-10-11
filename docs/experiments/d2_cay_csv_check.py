"""Producer check: recompute every replicate verdict / d_hat from ball_counts.csv with the frozen
D1 verdict, and recompute G1 numbers independently of dimension_d2.evaluate_gates."""
import csv, json, sys, collections, statistics, math
from scipy import stats
from emergence_lab.dimension_d1 import verdict
d = sys.argv[1]
res = json.load(open(f"{d}/result.json"))
acc = collections.defaultdict(lambda: collections.defaultdict(list))
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    acc[(int(row["size"]), int(row["rep"]))][int(row["r"])].append(int(row["ball"]))
mism = 0; dh = collections.defaultdict(list); verds = collections.defaultdict(list)
byk = {(x["size"], x["i_rep"]): x for x in res["results"]}
for (n, rep), m in sorted(acc.items()):
    assert all(len(v) == 256 for v in m.values())
    bbar = {r: sum(v) / len(v) for r, v in m.items()}
    v = verdict(bbar, n, 4, 0.15, 3, 0.125)
    x = byk[(n, rep)]
    if v["verdict"] != x["verdict"] or abs(v["d_hat"] - x["d_hat"]) > 1e-12: mism += 1
    verds[n].append(v["verdict"]); dh[n].append(v["d_hat"])
print("replicates", len(acc), "mismatches", mism)
for n in sorted(dh):
    xs = dh[n]; m = statistics.mean(xs); s = statistics.stdev(xs); h = stats.t.ppf(0.975, 7) * s / math.sqrt(8)
    print(n, verds[n].count("PLATEAU"), "/8 PLATEAU mean %.4f sd %.4f ci [%.4f, %.4f]" % (m, s, m - h, m + h))
m20, m22 = statistics.mean(dh[1048576]), statistics.mean(dh[4194304])
print("G1: |m22-2| = %.4f (<=0.15), |m20-m22| = %.4f (<=0.10), 8/8 at 2^22: %s" % (abs(m22 - 2), abs(m20 - m22), verds[4194304].count("PLATEAU") == 8))
