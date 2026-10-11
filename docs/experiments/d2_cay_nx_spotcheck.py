"""Spot check: rebuild CAY instances (size index 0, reps 0 and 7) and compare CSV ball counts for
8 sources each with an independent networkx BFS."""
import csv, json, sys, collections
import networkx as nx, numpy as np
from emergence_lab.dimension_d2 import build_instance
d = sys.argv[1]
cfg = json.load(open("configs/dimension_d2.json"))
want = collections.defaultdict(dict)
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    if row["size"] == "262144" and row["rep"] in ("0", "7"):
        want[(int(row["rep"]), int(row["source"]))][int(row["r"])] = int(row["ball"])
bad = 0; n_cmp = 0
for rep in (0, 7):
    g, sources = build_instance(cfg, "cayley_uniform_tree", 0, rep)
    G = nx.Graph(); G.add_nodes_from(range(g.n))
    ip, ix = g.indptr, g.indices
    for u in range(g.n):
        for v in ix[ip[u]:ip[u + 1]]:
            if u < v: G.add_edge(u, int(v))
    assert nx.is_tree(G)
    for s in list(sources)[:8]:
        dist = np.fromiter(nx.single_source_shortest_path_length(G, int(s)).values(), int)
        for r, b in want[(rep, int(s))].items():
            n_cmp += 1; bad += int((dist <= r).sum() != b)
print("compared", n_cmp, "ball counts, mismatches", bad)
