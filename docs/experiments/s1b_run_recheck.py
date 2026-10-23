"""Independent recheck of the archived S1b run (release s1b-run-v1): reads only numeric.csv,
no emergence_lab import. Usage: python -I s1b_run_recheck.py <path/to/numeric.csv>.
Recomputes per-size annealed W=128-1024 slopes, tree-level delta-method SEs, jackknife
ratios, Welch 90% CIs and the frozen prereg section-4 classification."""
import sys, csv, math, collections
import numpy as np
from scipy import stats
rows=list(csv.DictReader(open(sys.argv[1])))
print("rows",len(rows), collections.Counter(r['status'] for r in rows))
by=collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows: by[(r['family'],int(r['size']))][int(r['i_rep'])].append((float(r['q_t128']),float(r['q_t1024']),int(r['degree']),int(r['source'])))
L=math.log(8.0); res={}
for k in sorted(by):
    reps=by[k]; n=len(reps); cnt=collections.Counter(len(v) for v in reps.values())
    dup=any(len(set(s for *_ ,s in v))!=len(v) for v in reps.values())
    m=np.array([[np.mean([a for a,*_ in v]),np.mean([b for _,b,*_ in v])] for _,v in sorted(reps.items())])
    ql,qh=m[:,0].mean(),m[:,1].mean()
    d=-2*(math.log(qh)-math.log(ql))/L
    psi=-2/L*((m[:,1]-qh)/qh-(m[:,0]-ql)/ql)
    v=psi.var(ddof=1)/n
    # jackknife
    jk=[]
    for i in range(n):
        mm=np.delete(m,i,0); jk.append(-2*(math.log(mm[:,1].mean())-math.log(mm[:,0].mean()))/L)
    jk=np.array(jk); jse=math.sqrt((n-1)/n*((jk-jk.mean())**2).sum())
    res[k]=(d,v,n)
    print(k,"trees",n,"src/tree",dict(cnt),"dupsrc",dup,"d=%.6f se=%.6f jk/se=%.4f"%(d,math.sqrt(v),jse/math.sqrt(v)))
def contrast(a,b):
    da,va,na=res[a]; db,vb,nb=res[b]; D=db-da; se=math.sqrt(va+vb)
    df=(va+vb)**2/(va**2/(na-1)+vb**2/(nb-1)); t=stats.t.ppf(0.95,df)
    lo,hi=D-t*se,D+t*se; m=.03
    cls="MATERIAL-POSITIVE" if lo>m else "MATERIAL-NEGATIVE" if hi<-m else "EQUIVALENT" if lo>-m and hi<m else "INCONCLUSIVE"
    print(a,"->",b,"D=%.6f se=%.6f df=%.3f CI=[%.6f, %.6f]"%(D,se,df,lo,hi),cls)
contrast(('cayley_uniform_tree',65536),('cayley_uniform_tree',262144))
contrast(('cayley_uniform_tree',16384),('cayley_uniform_tree',65536))
contrast(('cayley_uniform_tree',16384),('cayley_uniform_tree',262144))
contrast(('ust_2d_torus',128),('ust_2d_torus',256))
