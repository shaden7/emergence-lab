"""Spot check (UST): rebuild UST instances at L = 256 (size index 0, reps 0 and 7) from the seed
rule, check independently that the graph is a spanning tree of the L x L torus (every edge a
lattice edge), and compare the CSV ball counts of 8 sources each with an independent networkx BFS."""
import csv, json, sys, collections
import networkx as nx, numpy as np
from emergence_lab.dimension_d2 import build_instance
d = sys.argv[1]
L = 256
cfg = json.load(open("configs/dimension_d2.json"))
want = collections.defaultdict(dict)
for row in csv.DictReader(open(f"{d}/ball_counts.csv")):
    if row["family"] == "ust_2d_torus" and row["size"] == str(L) and row["rep"] in ("0", "7"):
        want[(int(row["rep"]), int(row["source"]))][int(row["r"])] = int(row["ball"])
bad = 0; n_cmp = 0; bad_edges = 0
for rep in (0, 7):
    g, sources = build_instance(cfg, "ust_2d_torus", 0, rep)
    G = nx.Graph(); G.add_nodes_from(range(g.n))
    ip, ix = g.indptr, g.indices
    for u in range(g.n):
        for v in ix[ip[u]:ip[u + 1]]:
            v = int(v)
            if u < v:
                G.add_edge(u, v)
                dx = abs(u % L - v % L); dy = abs(u // L - v // L)
                dx, dy = min(dx, L - dx), min(dy, L - dy)
                bad_edges += int(dx + dy != 1)
    assert G.number_of_nodes() == L * L and nx.is_tree(G)
    for s in list(sources)[:8]:
        dist = np.fromiter(nx.single_source_shortest_path_length(G, int(s)).values(), int)
        for r, b in want[(rep, int(s))].items():
            n_cmp += 1; bad += int((dist <= r).sum() != b)
print("non-lattice edges", bad_edges, "| compared", n_cmp, "ball counts, mismatches", bad)
