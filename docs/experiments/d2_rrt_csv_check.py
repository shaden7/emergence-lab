"""Producer check (RRT): recompute every replicate verdict / d_hat from ball_counts.csv with the
frozen D1 verdict, independently of dimension_d2.evaluate_gates, and recompute the D2-G3 count.
Also reports, per replicate, which mechanism decided a non-PLATEAU verdict (prereg §4 asks the
result note to state whether the saturation guard or the plateau criterion decided the null).
N is the vertex count passed to the verdict (saturation guard), as in the driver."""
import csv, json, sys, collections
from emergence_lab.dimension_d1 import verdict

FAM = "random_recursive_tree"
d = sys.argv[1]
res = json.load(open(f"{d}/result.json"))
acc = collections.defaultdict(lambda: collections.defaultdict(list))
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    if row["family"] != FAM:
        continue
    acc[(int(row["size"]), int(row["rep"]))][int(row["r"])].append(int(row["ball"]))
byk = {(x["size"], x["i_rep"]): x for x in res["results"] if x["family"] == FAM}
mism = 0
verds = collections.defaultdict(list)
for (n, rep), m in sorted(acc.items()):
    assert all(len(v) == 256 for v in m.values()), (n, rep)
    bbar = {r: sum(v) / len(v) for r, v in m.items()}
    v = verdict(bbar, n, 4, 0.15, 3, 0.125)
    x = byk[(n, rep)]
    same_d = (v["d_hat"] is None and x["d_hat"] is None) or (
        v["d_hat"] is not None and x["d_hat"] is not None and abs(v["d_hat"] - x["d_hat"]) <= 1e-12)
    if v["verdict"] != x["verdict"] or not same_d:
        mism += 1
    verds[n].append(v["verdict"])
    print(n, rep, v["verdict"], "admissible", v["admissible"],
          "B(r)/N:", " ".join(f"{r}:{bbar[r] / n:.3g}" for r in sorted(bbar)))
print("replicates", len(acc), "mismatches", mism, "result.json entries", len(byk))
allv = [v for vs in verds.values() for v in vs]
for n in sorted(verds):
    print(n, dict(collections.Counter(verds[n])))
print("G3: n=%d, PLATEAU=%d -> %s" % (len(allv), allv.count("PLATEAU"),
                                      "PASS" if len(allv) == 24 and "PLATEAU" not in allv else "FAIL"))
print("driver gate:", json.dumps(res["gates"].get("D2-G3")))
