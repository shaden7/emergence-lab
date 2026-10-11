"""Check of D2 prereg r1 (session rd-claude-20261011T125558Z-220239), model-based, NOT a D2 result.
(1) Per-replicate non-PLATEAU rate of the r1 G1 power model (scripts/d2_g1_power.py) at S = 256
    with a large pool (T = 40000), because r1's joint estimate resamples a 4000-replicate pool:
    with 0 failures in that pool the joint P(G1) cannot fall below 1.
(2) Sensitivity of the joint G1 pass probability at S = 256 to the design-effect input.
Seed 939393 (unrelated to the D2 seed_base). No tree is sampled."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from emergence_lab.dimension_d1 import verdict  # noqa: E402

src = open(os.path.join(HERE, "d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])  # defines moments(N, radii)

x = np.log2(np.array([4, 8, 16, 32, 64, 128, 256]) / 256.0)
DE0 = np.array([0.98, 1.03, 1.05, 1.29, 1.45, 2.49, 6.48])  # review pilot, N = 2^16 (as r1)
RADII = [2 ** j for j in range(2, 13)]
PRE = {e: moments(2 ** e, RADII) for e in (20, 22)}


def sim(e, S, T, rng, de):
    N = 2 ** e
    mean, cov = PRE[e]
    mu = np.array([mean[r] for r in RADII])
    C = np.array([[cov[(a, b)] for b in RADII] for a in RADII])
    g = np.sqrt(np.array([float(np.interp(math.log2(r / math.sqrt(N)), x, de, left=1.0, right=de[-1]))
                          for r in RADII]))
    Cl = C / np.outer(mu, mu) / S * np.outer(g, g)
    L = np.linalg.cholesky(Cl + 1e-15 * np.eye(len(RADII)))
    return [verdict({r: float(v) for r, v in zip(RADII, mu * np.exp(L @ rng.standard_normal(len(RADII))
                                                                   - 0.5 * np.diag(Cl)))}, N)
            for _ in range(T)]


def joint(v20, v22, rng, trials=10000):
    ok = np.array([v["verdict"] == "PLATEAU" for v in v22])
    d22 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v22])
    d20 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v20])
    p = 0
    for _ in range(trials):
        i = rng.integers(0, len(v22), 8)
        j = rng.integers(0, len(v20), 8)
        p += bool(ok[i].all() and abs(np.nanmean(d22[i]) - 2) <= 0.15
                  and abs(np.nanmean(d20[j]) - np.nanmean(d22[i])) <= 0.10)
    return ok, d22, p / trials


def main():
    rng = np.random.default_rng(939393)
    v22 = sim(22, 256, 40000, rng, DE0)
    k = sum(v["verdict"] != "PLATEAU" for v in v22)
    print(f"(1) S=256, 2^22: non-PLATEAU {k}/40000 = {k / 40000:.2e}; P(8/8 PLATEAU) = {(1 - k / 40000) ** 8:.4f}")
    for lab, de in (("r1 DE", DE0), ("DE x1.5", DE0 * 1.5), ("DE x2", DE0 * 2), ("DE x3", DE0 * 3)):
        ok, d22, p = joint(sim(20, 256, 3000, rng, de), sim(22, 256, 3000, rng, de), rng)
        print(f"(2) {lab:8s}: P(PLATEAU, 2^22) = {ok.mean():.4f}; P(G1 joint) = {p:.4f}; sd d_hat(2^22) = {np.nanstd(d22):.4f}")


if __name__ == "__main__":
    main()
