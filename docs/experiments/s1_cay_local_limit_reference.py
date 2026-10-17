# Independent check of the CAY local-limit value E[P(X_2=v)] = 2(e-1)/e^2 with a separate
# Pruefer decoder (heapq), exhaustive vertex average per tree. Seed 20261017 is a throwaway
# check seed, not a project seed base.
import heapq, math, numpy as np
def prufer_edges(seq, n):
    deg=[1]*n
    for x in seq: deg[x]+=1
    leaves=[i for i in range(n) if deg[i]==1]; heapq.heapify(leaves); E=[]
    for x in seq:
        l=heapq.heappop(leaves); E.append((l,x)); deg[x]-=1
        if deg[x]==1: heapq.heappush(leaves,x)
    E.append((heapq.heappop(leaves),heapq.heappop(leaves))); return E
rng=np.random.default_rng(20261017); n=20000; vals=[]; p1=[]
for _ in range(40):
    E=prufer_edges(rng.integers(0,n,n-2).tolist(),n); d=np.zeros(n)
    for a,b in E: d[a]+=1; d[b]+=1
    vals.append(2/n*sum(1/(d[a]*d[b]) for a,b in E)); p1.append(np.mean(d==1))
v=np.array(vals); print("q_t1 mean %.5f se %.5f  P(deg1) %.5f   ref %.5f / %.5f"%(v.mean(),v.std(ddof=1)/math.sqrt(len(v)),np.mean(p1),2*(math.e-1)/math.e**2,1/math.e))
