"""Later-pass review checks of PR #36 (not D2 output; review seed 818181, non-grid sizes)."""
import sys, itertools, time
import numpy as np, networkx as nx
from scipy.stats import chi2, chi2_contingency
from emergence_lab import dimension_d2 as d2

SEED = 818181
rng = np.random.default_rng(SEED)
# (b) Pruefer vs networkx (independent decoder; nx uses 0-based labels, same convention)
bad = 0
for n in list(range(3, 40)) + [100, 1000, 5000]:
    for _ in range(50 if n < 1000 else 5):
        seq = rng.integers(0, n, n - 2)
        u, v = d2.prufer_decode(seq)
        mine = sorted(tuple(sorted(e)) for e in zip(u.tolist(), v.tolist()))
        ref = sorted(tuple(sorted(e)) for e in nx.from_prufer_sequence(seq.tolist()).edges())
        bad += mine != ref
        # inverse direction: encode our tree with networkx and recover the sequence
        T = nx.Graph(); T.add_nodes_from(range(n)); T.add_edges_from(mine)
        bad += nx.to_prufer_sequence(T) != seq.tolist()
print("pruefer vs networkx mismatches:", bad)

# (c1) Wilson on L=5 torus vs transfer-current theorem (exact single- and two-edge marginals)
L = 5; n = L * L
edges = []
for y in range(L):
    for x in range(L):
        u = y * L + x
        edges.append((u, y * L + (x + 1) % L)); edges.append((u, ((y + 1) % L) * L + x))
lap = np.zeros((n, n))
for a, b in edges:
    lap[a, a] += 1; lap[b, b] += 1; lap[a, b] -= 1; lap[b, a] -= 1
G = np.linalg.pinv(lap)
def Y(e, f):  # transfer current through f for unit current along e
    (a, b), (c, d) = e, f
    return G[a, c] - G[a, d] - G[b, c] + G[b, d]
eA = (0, 1); eB = (1, 2); eC = (0, 5); eD = (0, 6 % n)  # eD not an edge; use pairs below
pairs = {"h-h collinear (0-1,1-2)": ((0, 1), (1, 2)), "h-v at vertex 0 (0-1,0-5)": ((0, 1), (0, 5)),
         "h-h parallel (0-1,5-6)": ((0, 1), (5, 6)), "h-h far (0-1,12-13)": ((0, 1), (12, 13))}
exact1 = Y((0, 1), (0, 1))
exactp = {k: Y(e, e) * Y(f, f) - Y(e, f) * Y(f, e) for k, (e, f) in pairs.items()}
draws = 200_000
r2 = np.random.Generator(np.random.PCG64(np.random.SeedSequence([SEED, 5])))
c1 = 0; cp = {k: 0 for k in pairs}; t0 = time.time()
for _ in range(draws):
    p, _s = d2.wilson_parents_torus(L, r2)
    E = {tuple(sorted((i, int(p[i])))) for i in range(1, n)}
    c1 += (0, 1) in E
    for k, (e, f) in pairs.items():
        cp[k] += (tuple(sorted(e)) in E) and (tuple(sorted(f)) in E)
def z(c, pr):
    return (c / draws - pr) / np.sqrt(pr * (1 - pr) / draws)
print(f"L=5 Wilson {draws} draws ({time.time()-t0:.0f}s): P(edge)={c1/draws:.4f} exact={exact1:.4f} (=(n-1)/|E|={(n-1)/len(edges):.4f}) z={z(c1, exact1):+.2f}")
for k in pairs:
    print(f"  {k}: freq={cp[k]/draws:.4f} exact={exactp[k]:.4f} z={z(cp[k], exactp[k]):+.2f}")

# (c2) Wilson vs independent Aldous-Broder on the 4x4 torus: two-sample chi2 on joint
# (degree of vertex 0, tree distance 0 -> (2,2), tree diameter)
def ab_torus(L, rng):
    n = L * L; seen = np.zeros(n, bool); u = int(rng.integers(n)); seen[u] = True; k = 1; E = []
    while k < n:
        x, y = u % L, u // L; d = int(rng.integers(4))
        w = [y * L + (x - 1) % L, y * L + (x + 1) % L, ((y - 1) % L) * L + x, ((y + 1) % L) * L + x][d]
        if not seen[w]:
            seen[w] = True; k += 1; E.append((u, w))
        u = w
    return E
def stats(L, E):
    T = nx.Graph(); T.add_edges_from(E)
    return (T.degree(0), nx.shortest_path_length(T, 0, 2 * L + 2), nx.diameter(T))
L = 4; m = 40_000
r3 = np.random.default_rng([SEED, 4])
sw = [stats(L, [(i, int(p)) for i, p in enumerate(d2.wilson_parents_torus(L, r3)[0]) if i]) for _ in range(m)]
sa = [stats(L, ab_torus(L, r3)) for _ in range(m)]
for name, idx in (("deg0", 0), ("dist0-(2,2)", 1), ("diameter", 2)):
    keys = sorted(set(s[idx] for s in sw + sa))
    tab = np.array([[sum(s[idx] == k for s in sw) for k in keys], [sum(s[idx] == k for s in sa) for k in keys]])
    tab = tab[:, tab.sum(0) >= 10]
    st, pv, dof, _ = chi2_contingency(tab)
    print(f"L=4 Wilson vs Aldous-Broder, {name}: chi2={st:.1f} dof={dof} p={pv:.3f}; means W={np.mean([s[idx] for s in sw]):.4f} AB={np.mean([s[idx] for s in sa]):.4f}")
