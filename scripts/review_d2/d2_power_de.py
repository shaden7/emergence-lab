"""Power of D2-G1 with the pilot design effect DE(r/sqrt N) (interpolated in log r/sqrt N from
the N=2^16 review pilot; DE=1 below r/sqrtN=1/64; correlations kept from the exact per-source
matrix). Review-only seed 434343. Model-based, not a D2 result."""
import os
import sys, math, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from emergence_lab.dimension_d1 import verdict
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])
x=np.log2(np.array([4,8,16,32,64,128,256])/256.0); de=np.array([0.98,1.03,1.05,1.29,1.45,2.49,6.48])
DE=lambda q: float(np.interp(math.log2(q),x,de,left=1.0,right=de[-1]))
rng=np.random.default_rng(434343); T=4000
for e in (20,22):
    N=2**e; radii=[2**j for j in range(2,13)]
    mean,cov=moments(N,radii)
    mu=np.array([mean[r] for r in radii]); C=np.array([[cov[(a,b)] for b in radii] for a in radii])
    g=np.sqrt(np.array([DE(r/math.sqrt(N)) for r in radii]))
    for S in (32,256,1024):
        Clog=C/np.outer(mu,mu)/S*np.outer(g,g)
        L=np.linalg.cholesky(Clog+1e-15*np.eye(len(radii)))
        res=[verdict({r:float(b) for r,b in zip(radii,mu*np.exp(L@rng.standard_normal(len(radii))-0.5*np.diag(Clog)))},N) for _ in range(T)]
        p=np.mean([v["verdict"]=="PLATEAU" for v in res]); dh=np.array([v["d_hat"] for v in res if v["d_hat"] is not None])
        rl=np.mean([v["window"][1]//2==max(v["admissible"]) for v in res if v["window"]])
        print(f"N=2^{e} S={S:5d}: P(PLATEAU)={p:.3f}  P(8/8)={p**8:.3f}  d_hat mean={dh.mean():.4f} sd={dh.std():.4f}  P(|mean8-2|<=0.15)~{np.mean([abs(rng.choice(dh,8).mean()-2)<=0.15 for _ in range(2000)]):.3f}")
