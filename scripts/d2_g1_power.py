"""D2 v1.0-r1: noise-only pass probability of the whole D2-G1 gate for the CAY family, for a
correct instrument on exactly dimension-2 uniform labelled trees. Model (not a D2 result):
log Bbar_S(r) Gaussian with the EXACT per-source covariance of |B(v,r)| (Moon forest formula,
scripts/review_d2/d2_second_moment.py) divided by S and inflated by the review pilot's design
effect DE(r/sqrt N) (scripts/review_d2/d2_design_effect.py, N=2^16, not a grid size). Each
simulated replicate curve goes through the frozen D1 verdict(). G1 = 8/8 PLATEAU at 2^22 AND
|mean d_hat(2^22) - 2| <= 0.15 AND |mean(2^20) - mean(2^22)| <= 0.10. Seed 616161 is
producer-only and unrelated to the D2 seed_base; no tree is sampled."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from emergence_lab.dimension_d1 import verdict  # noqa: E402

src = open(os.path.join(HERE, "review_d2", "d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])  # defines moments(N, radii)

x = np.log2(np.array([4, 8, 16, 32, 64, 128, 256]) / 256.0)
de = np.array([0.98, 1.03, 1.05, 1.29, 1.45, 2.49, 6.48])  # review pilot, N = 2^16


def DE(q):
    return float(np.interp(math.log2(q), x, de, left=1.0, right=de[-1]))


def simulate(e, S, T, rng):
    N = 2 ** e
    radii = [2 ** j for j in range(2, 13)]
    mean, cov = moments(N, radii)
    mu = np.array([mean[r] for r in radii])
    C = np.array([[cov[(a, b)] for b in radii] for a in radii])
    g = np.sqrt(np.array([DE(r / math.sqrt(N)) for r in radii]))
    Clog = C / np.outer(mu, mu) / S * np.outer(g, g)
    L = np.linalg.cholesky(Clog + 1e-15 * np.eye(len(radii)))
    out = []
    for _ in range(T):
        b = mu * np.exp(L @ rng.standard_normal(len(radii)) - 0.5 * np.diag(Clog))
        out.append(verdict({r: float(v) for r, v in zip(radii, b)}, N))
    return out


def main(T=4000, reps=8, trials=20000):
    rng = np.random.default_rng(616161)
    for S in (32, 128, 256):
        v20, v22 = simulate(20, S, T, rng), simulate(22, S, T, rng)
        ok20 = np.array([v["verdict"] == "PLATEAU" for v in v20])
        ok22 = np.array([v["verdict"] == "PLATEAU" for v in v22])
        d20 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v20])
        d22 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v22])
        rlast = np.array([max(v["admissible"]) if v["admissible"] else 0 for v in v22])
        passes = 0
        for _ in range(trials):
            i = rng.integers(0, T, reps)
            j = rng.integers(0, T, reps)
            m22 = np.nanmean(d22[i]) if np.isfinite(d22[i]).any() else np.nan
            m20 = np.nanmean(d20[j]) if np.isfinite(d20[j]).any() else np.nan
            passes += bool(ok22[i].all() and abs(m22 - 2) <= 0.15 and abs(m20 - m22) <= 0.10)
        print(f"S={S:4d}: P(PLATEAU) 2^20={ok20.mean():.3f} 2^22={ok22.mean():.3f}; "
              f"P(G1 pass, joint)={passes / trials:.3f}; d_hat(2^22) mean={np.nanmean(d22):.4f} "
              f"sd={np.nanstd(d22):.4f}; max admissible scale at 2^22: "
              f"256 in {np.mean(rlast == 256):.2f}, 512 in {np.mean(rlast == 512):.2f}; "
              f"d_hat | 256: {np.nanmean(d22[rlast == 256]):.4f}, | 512: {np.nanmean(d22[rlast == 512]):.4f}")


if __name__ == "__main__":
    main()
