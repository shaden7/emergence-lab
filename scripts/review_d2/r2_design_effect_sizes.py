"""Check of D2 prereg r1 (session rd-claude-20261011T125558Z-220239), NOT a D2 result: does the within-tree design effect depend on r/sqrt(N) only?
Independent implementation: networkx Pruefer decode, scipy BFS; exact per-source variance from
the review's moments(). Sizes 2^14 and 2^17 (not D2 grid sizes), seed 727272. No d_eff computed."""
import math, sys, os, time, numpy as np, networkx as nx
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from scipy import stats
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])
S=32
SIZES=((14,600),(17,150))  # fresh rng(727272) per size, as run by the check
for e,T in SIZES:
    rng=np.random.default_rng(727272); N=2**e; sq=math.sqrt(N); qs=[1/16,1/8,1/4,1/2]; radii=[int(round(q*sq)) for q in qs]
    mean,cov=moments(N,radii); Bb=[]; t0=time.time()
    for t in range(T):
        G=nx.from_prufer_sequence(rng.integers(0,N,size=N-2).tolist())
        A=nx.to_scipy_sparse_array(G,format="csr")
        D=shortest_path(A,unweighted=True,indices=rng.choice(N,size=S,replace=False))
        Bb.append([(D<=r).sum(axis=1).mean() for r in radii])
    Bb=np.array(Bb)
    for i,(q,r) in enumerate(zip(qs,radii)):
        v=Bb[:,i].var(ddof=1); de=v/(cov[(r,r)]/S); k=T-1
        z=(Bb[:,i].mean()-mean[r])/math.sqrt(v/T)
        print(f"N=2^{e} r={r} r/sqrtN={q:.4f} DE={de:.2f} 90%CI[{de*k/stats.chi2.ppf(.95,k):.2f},{de*k/stats.chi2.ppf(.05,k):.2f}] mean z={z:+.2f}")
    print(f"  {T} trees {time.time()-t0:.0f}s",flush=True)
