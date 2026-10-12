"""Spot check (RRT), producer session, not independent.
(a) Rebuild RRT instances at N = 2^18 (size index 0, reps 0 and 7) from the seed rule; check with
    networkx that each is a tree on N vertices, and compare the CSV ball counts of 8 sources each
    with an independent networkx BFS.
(b) Exact-mathematics check of the r = 2 ball: for any tree, sum_v |B(v,2)| = N + sum_u deg(u)^2,
    so the mean over a uniform source is 1 + mean(deg^2). For a random recursive tree the
    out-degree of a uniform vertex is asymptotically Geometric(1/2) on {0,1,...} (mean 1,
    variance 2), so E deg^2 -> E(D+1)^2 = 6 and E|B(v,2)| -> 7. Compare the sampled mean of
    |B(v,2)| over all 2048 sources per size with 7 (z-score from the per-replicate means), and
    with the instance-exact value 1 + mean(deg^2) for the two rebuilt instances."""
import csv, json, sys, collections, math, statistics
import networkx as nx, numpy as np
from emergence_lab.dimension_d2 import build_instance

FAM = "random_recursive_tree"
d = sys.argv[1]
N0 = 2 ** 18
cfg = json.load(open("configs/dimension_d2.json"))
want = collections.defaultdict(dict)
b2 = collections.defaultdict(lambda: collections.defaultdict(list))
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    if row["family"] != FAM:
        continue
    if row["r"] == "2":
        b2[int(row["size"])][int(row["rep"])].append(int(row["ball"]))
    if row["size"] == str(N0) and row["rep"] in ("0", "7"):
        want[(int(row["rep"]), int(row["source"]))][int(row["r"])] = int(row["ball"])
bad = n_cmp = 0
for rep in (0, 7):
    g, sources = build_instance(cfg, FAM, 0, rep)
    G = nx.Graph(); G.add_nodes_from(range(g.n))
    ip, ix = g.indptr, g.indices
    G.add_edges_from((u, int(v)) for u in range(g.n) for v in ix[ip[u]:ip[u + 1]] if u < v)
    assert G.number_of_nodes() == N0 and nx.is_tree(G)
    deg = np.array([G.degree(u) for u in range(N0)], dtype=float)
    srcs = [int(s) for s in sources]
    exact_b2 = 1 + float((deg ** 2).mean())
    samp_b2 = statistics.mean(want[(rep, s)][2] for s in srcs)
    print(f"rep {rep}: instance-exact mean |B(v,2)| = {exact_b2:.4f}, 256-source sample mean = {samp_b2:.4f}")
    for s in srcs[:8]:
        dist = np.fromiter(nx.single_source_shortest_path_length(G, s).values(), int)
        for r, b in want[(rep, s)].items():
            n_cmp += 1; bad += int((dist <= r).sum() != b)
print("networkx BFS: compared", n_cmp, "ball counts, mismatches", bad)
for n in sorted(b2):
    reps = [statistics.mean(v) for _, v in sorted(b2[n].items())]
    m = statistics.mean(reps); se = statistics.stdev(reps) / math.sqrt(len(reps))
    print(f"N={n}: mean |B(v,2)| over 8x256 sources = {m:.4f}, se(8 reps) = {se:.4f}, z vs 7 = {(m - 7) / se:+.2f}")
