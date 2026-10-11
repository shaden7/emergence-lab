"""D2 preregistration §4: exact Cayley-tree reference (no sampling).

1. Exhaustive check: for N = 5, 6, 7 every labelled tree is decoded from its Pruefer
   sequence and the distance profile of vertex 0 is averaged in exact rationals; it must
   equal E #{u: d(v,u)=k} = (k+1) * prod_{i<=k} (1 - i/N).
2. The frozen D1 verdict function is applied to the exact mean curve E|B(v,r)| at the
   gated sizes N = 2^18, 2^20, 2^22 (reproduces the table in the preregistration).
Run from the repository root: python scripts/d2_cayley_reference.py
"""
import itertools, math, sys
from fractions import Fraction
sys.path.insert(0,"src")
def shell_exact(N,k):
    p=Fraction(k+1)
    for i in range(1,k+1): p*=Fraction(N-i,N)
    return p
def prufer_to_edges(seq,N):
    deg=[1]*N
    for x in seq: deg[x]+=1
    edges=[]; import heapq
    leaves=[i for i in range(N) if deg[i]==1]; heapq.heapify(leaves)
    for x in seq:
        l=heapq.heappop(leaves); edges.append((l,x)); deg[x]-=1
        if deg[x]==1: heapq.heappush(leaves,x)
    a=heapq.heappop(leaves); b=heapq.heappop(leaves); edges.append((a,b)); return edges
# exhaustive verification (exact enumeration, not sampling) for N = 5, 6, 7, vertex 0
for N in (5,6,7):
    tot=[0]*N; cnt=0
    for seq in itertools.product(range(N),repeat=N-2):
        adj=[[] for _ in range(N)]
        for a,b in prufer_to_edges(seq,N): adj[a].append(b); adj[b].append(a)
        dist=[-1]*N; dist[0]=0; q=[0]
        for x in q:
            for y in adj[x]:
                if dist[y]<0: dist[y]=dist[x]+1; q.append(y)
        for d in dist: tot[d]+=1
        cnt+=1
    assert cnt==N**(N-2)
    ok=all(Fraction(tot[k],cnt)==shell_exact(N,k) for k in range(N))
    print("N",N,"trees",cnt,"formula exact:",ok)
import numpy as np
from emergence_lab.dimension_d1 import verdict
def ball(N,r):
    s=0.0; p=1.0
    for k in range(r+1):
        if k>0: p*=(1-k/N)
        s+=(k+1)*p
    return s
for e in (18,20,22):
    N=2**e
    radii=[2**j for j in range(1,14)]
    bb={r:ball(N,r) for r in radii}
    row=[(r, round(bb[r],1), round(math.log2(bb[2*r]/bb[r]),6)) for r in radii[:-1] if 8*bb[2*r]<=N]
    print("N=2^%d"%e, row)
    print("  verdict on analytic mean:", verdict(bb,N))
