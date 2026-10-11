"""Review-only pilot (NOT a D2 result): design effect of using S=32 sources in ONE uniform
labelled tree, i.e. Var_trees(Bbar_32(r)) / (Var_exact(|B(v,r)|)/32), at a size NOT in the
D2 grid (N=2^16), review seed 515151 (unrelated to D2 seed_base 2036101101).
Also checks the sampled mean against the exact formula (generator sanity)."""
import os
import sys, math, numpy as np, heapq, time
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "d2_second_moment.py")).read()
exec(src[src.index("def moments"):src.index("z=1/math.log(2)")])
def prufer_decode(seq,N):
    deg=np.ones(N,dtype=np.int64); np.add.at(deg,seq,1); deg=deg.tolist()
    leaves=[i for i in range(N) if deg[i]==1]; heapq.heapify(leaves); a=[];b=[]
    for x in seq.tolist():
        l=heapq.heappop(leaves); a.append(l); b.append(x); deg[x]-=1
        if deg[x]==1: heapq.heappush(leaves,x)
    a.append(heapq.heappop(leaves)); b.append(heapq.heappop(leaves)); return np.array(a),np.array(b)
N=2**16; S=32; TREES=int(sys.argv[1]) if len(sys.argv)>1 else 300
radii=[4,8,16,32,64,128,256]
rng=np.random.default_rng(515151)
mean,cov=moments(N,radii)
Bb=[]; t0=time.time()
for t in range(TREES):
    seq=rng.integers(0,N,size=N-2); a,b=prufer_decode(seq,N)
    A=csr_matrix((np.ones(2*(N-1)),(np.r_[a,b],np.r_[b,a])),shape=(N,N))
    srcs=rng.choice(N,size=S,replace=False)
    D=shortest_path(A,unweighted=True,indices=srcs)
    Bb.append([ (D<=r).sum(axis=1).mean() for r in radii])
Bb=np.array(Bb); print(f"{TREES} trees, {time.time()-t0:.0f}s")
print(" r   exact E|B|  sampled mean (z)   design effect Var(Bbar)/(Var(B)/32)  [90% CI]")
from scipy import stats
for i,r in enumerate(radii):
    v=Bb[:,i].var(ddof=1); ve=cov[(r,r)]/S; de=v/ve; k=TREES-1
    lo,hi=de*k/stats.chi2.ppf(0.95,k), de*k/stats.chi2.ppf(0.05,k)
    zz=(Bb[:,i].mean()-mean[r])/math.sqrt(v/TREES)
    print(f"{r:4d} {mean[r]:10.1f} {Bb[:,i].mean():10.1f} ({zz:+.2f})   {de:6.2f}  [{lo:.2f}, {hi:.2f}]   guard ok: {8*mean[2*r]<=N if 2*r in mean else '-'}")
