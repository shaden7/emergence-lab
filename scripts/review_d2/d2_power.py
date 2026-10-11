"""Power of D2-G1 under a Gaussian (delta-method) model for log Bbar(r), using the exact
per-source covariance of |B(v,r)| (d2_second_moment.moments) and assuming the S sources in a
replicate are INDEPENDENT (optimistic: Var(Bbar) >= that only if cross-source covariance >= 0;
the exact upper bound is perfect correlation, S_eff=1). No tree is sampled. Applies the frozen
D1 verdict() to each simulated curve."""
import os
import sys, math, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from emergence_lab.dimension_d1 import verdict
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d2_second_moment.py")).read().split("# 1) exhaustive")[0])
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])
rng=np.random.default_rng(424242)  # review-only seed, unrelated to D2 seed_base
T=4000
for e in (20,22):
    N=2**e; radii=[2**j for j in range(2,13)]
    mean,cov=moments(N,radii)
    mu=np.array([mean[r] for r in radii]); C=np.array([[cov[(a,b)] for b in radii] for a in radii])
    for S in (32,128,256,1024):
        Clog=C/np.outer(mu,mu)/S
        L=np.linalg.cholesky(Clog+1e-15*np.eye(len(radii)))
        res=[]
        for t in range(T):
            x=mu*np.exp(L@rng.standard_normal(len(radii))-0.5*np.diag(Clog))
            v=verdict({r:float(b) for r,b in zip(radii,x)},N)
            res.append((v["verdict"],v["d_hat"]))
        p=np.mean([a=="PLATEAU" for a,_ in res]); dh=np.array([d for a,d in res if d is not None])
        # Monte Carlo of G1 level part: 8 replicates
        print(f"N=2^{e} S={S:5d}: P(PLATEAU per replicate)={p:.3f}  P(8/8)={p**8:.3f}  d_hat mean={dh.mean():.4f} sd={dh.std():.4f}")
