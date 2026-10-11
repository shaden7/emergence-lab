"""Later-pass review of PR #36: per-edge marginals of Wilson on the 5x5 torus vs (n-1)/|E| = 0.48,
1e6 draws, review seed [818181, 55]. Not a D2 result."""
import numpy as np, time
from emergence_lab import dimension_d2 as d2
L = 5; n = 25; draws = 1_000_000
rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([818181, 55])))
cnt = {}
for _ in range(draws):
    p, _ = d2.wilson_parents_torus(L, rng)
    for i in range(1, n):
        e = (min(i, int(p[i])), max(i, int(p[i])))
        cnt[e] = cnt.get(e, 0) + 1
pr = 24 / 50; sd = np.sqrt(pr * (1 - pr) / draws)
zs = {e: (c / draws - pr) / sd for e, c in cnt.items()}
root = [z for e, z in zs.items() if 0 in e]
print("edges seen", len(cnt), "root-incident z:", np.round(root, 2))
oth = np.array([z for e, z in zs.items() if 0 not in e])
print("non-root z: mean %.2f sd %.2f max|z| %.2f" % (oth.mean(), oth.std(), abs(oth).max()))
