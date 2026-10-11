"""Later-pass review of D2 prereg (PR #35): exact second moments of |B(v,r)| for a fixed
vertex v of a uniform labelled tree, from Moon's forest formula (no sampling).
P(tree contains a given labelled subtree on s vertices) = s * N^(1-s).
Ordered pairs (u,w) with d(v,u)=a, d(v,w)=b sharing j edges span a subtree with s=a+b-j+1
vertices; there are (N-1)_(s-1) labellings, so E#=f(s)=s*prod_{i<s}(1-i/N)."""
import os
import itertools, heapq, math, sys
from fractions import Fraction
import numpy as np

def prufer_edges(seq, N):
    deg=[1]*N
    for x in seq: deg[x]+=1
    leaves=[i for i in range(N) if deg[i]==1]; heapq.heapify(leaves); E=[]
    for x in seq:
        l=heapq.heappop(leaves); E.append((l,x)); deg[x]-=1
        if deg[x]==1: heapq.heappush(leaves,x)
    E.append((heapq.heappop(leaves),heapq.heappop(leaves))); return E

def f_exact(N,s):
    p=Fraction(s)
    for i in range(1,s): p*=Fraction(N-i,N)
    return p

def second_exact(N,r1,r2):
    return sum(f_exact(N,a+b-j+1) for a in range(r1+1) for b in range(r2+1) for j in range(min(a,b)+1))

# 1) exhaustive check of E[|B(0,r1)| |B(0,r2)|] for N=6,7
for N in (6,7):
    acc={}; cnt=0
    for seq in itertools.product(range(N),repeat=N-2):
        adj=[[] for _ in range(N)]
        for a,b in prufer_edges(seq,N): adj[a].append(b); adj[b].append(a)
        d=[-1]*N; d[0]=0; q=[0]
        for x in q:
            for y in adj[x]:
                if d[y]<0: d[y]=d[x]+1; q.append(y)
        for r1 in range(N):
            for r2 in range(N):
                b1=sum(1 for t in d if t<=r1); b2=sum(1 for t in d if t<=r2)
                acc[(r1,r2)]=acc.get((r1,r2),0)+b1*b2
        cnt+=1
    ok=all(Fraction(acc[k],cnt)==second_exact(N,*k) for k in acc)
    print(f"N={N}: exhaustive E[B(r1)B(r2)] == formula for all r1,r2: {ok}")

# 2) moments at gated sizes (float)
def moments(N, radii):
    smax=2*max(radii)+2
    s=np.arange(smax+1,dtype=float)
    logp=np.concatenate([[0.0],np.cumsum(np.log1p(-np.arange(1,smax+1)/N))])  # logp[s-1]=sum_{i<s}
    f=np.zeros(smax+2); f[1:smax+2]=np.arange(1,smax+2)*np.exp(logp[:smax+1])
    F=np.concatenate([[0.0],np.cumsum(f)])  # F[n]=sum_{s<n} f(s)
    mean={r:F[r+2]-F[1] for r in radii}     # sum_{k<=r} f(k+1)
    M={}
    for r1 in radii:
        a=np.arange(r1+1)[:,None]
        for r2 in radii:
            if r2<r1: continue
            b=np.arange(r2+1)[None,:]
            m=np.minimum(a,b)
            tot=(F[a+b+2]-F[a+b-m+1]).sum()  # sum_{j=0}^{m} f(a+b-j+1)
            M[(r1,r2)]=M[(r2,r1)]=tot
    cov={k:M[k]-mean[k[0]]*mean[k[1]] for k in M}
    return mean,cov

z=1/math.log(2)
for e in (18,20,22):
    N=2**e
    radii=[2**j for j in range(2,12)]
    mean,cov=moments(N,radii)
    print(f"\nN=2^{e}  guard N/8={N//8}")
    print(" r    E|B(r)|    CV(S=1)   sd d_eff(r) S=1   S=32 indep   corr(d_eff(r),d_eff(2r)) S=1")
    rs=[r for r in radii if 2*r in mean and mean[2*r]*8<=N*1.0]
    sds={}
    for r in rs:
        R=2*r
        v=z*z*(cov[(R,R)]/mean[R]**2+cov[(r,r)]/mean[r]**2-2*cov[(r,R)]/(mean[r]*mean[R]))
        sds[r]=v
    for r in rs:
        R=2*r; RR=4*r
        c="" 
        if r*2 in sds and RR in mean:
            # cov(log B(2r)-log B(r), log B(4r)-log B(2r))
            g=lambda x,y: cov[(x,y)]/(mean[x]*mean[y])
            cc=z*z*(g(R,RR)-g(R,R)-g(r,RR)+g(r,R))
            c=f"{cc/math.sqrt(sds[r]*sds[2*r]):+.3f}"
        print(f"{r:4d} {mean[r]:11.1f} {math.sqrt(cov[(r,r)])/mean[r]:9.3f} {math.sqrt(sds[r]):12.4f} {math.sqrt(sds[r]/32):12.4f}   {c}")
    print(f" E|B(2*r_last)|/(N/8) at r_last={rs[-1]}: {mean[2*rs[-1]]/(N/8):.3f}; next scale {2*rs[-1]}: {mean[4*rs[-1]]/(N/8):.3f}")
