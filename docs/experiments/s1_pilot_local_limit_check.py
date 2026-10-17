# Post-hoc diagnostic of the archived S1 pilot CSV (no emergence_lab imports, no new seeds).
# Usage: python -I docs/experiments/s1_pilot_local_limit_check.py docs/experiments/2026-10-17-s1-pilot/s1_pilot_numeric.csv
# Exploratory only: informs the S1b design; nothing here is gated.
import csv, math, sys, collections
import numpy as np
rows=list(csv.DictReader(open(sys.argv[1])))
times=[1<<k for k in range(13)]
def grp(fam,size):
    d=collections.defaultdict(list)
    for r in rows:
        if r["family"]==fam and r["size"]==size:
            d[int(r["i_rep"])].append(r)
    return [d[k] for k in sorted(d)]
def cluster(vals):  # list per tree of per-source values -> mean of tree means, se
    tm=np.array([np.mean(v) for v in vals]); return tm.mean(), tm.std(ddof=1)/math.sqrt(len(tm)), len(tm)
e=math.e
ref_q1=2*(e-1)/e**2
for fam,size in [("cayley_uniform_tree","65536"),("cayley_uniform_tree","262144"),("ust_2d_torus","128"),("ust_2d_torus","256"),("random_recursive_tree","65536")]:
    g=grp(fam,size)
    m,se,n=cluster([[float(r["q_t1"]) for r in t] for t in g])
    p1,sp1,_=cluster([[r["degree"]=="1" for r in t] for t in g])
    md,smd,_=cluster([[int(r["degree"]) for r in t] for t in g])
    print(f"{fam} {size}: trees={n} q_t1={m:.4f}±{se:.4f}  P(deg1)={p1:.4f}±{sp1:.4f} meandeg={md:.3f}±{smd:.3f}")
print("ref CAY local limit q_t1=2(e-1)/e^2=%.5f  P(deg1)=1/e=%.5f"%(ref_q1,1/e))
print("ref UST Z2 P(deg1)=8/pi^2(1-2/pi)=%.5f"%(8/math.pi**2*(1-2/math.pi)))
# size differences of annealed log q at each t and of short-window slopes
def Q(fam,size):
    return np.array([np.mean([[float(r[f"q_t{t}"]) for t in times] for r in tr],axis=0) for tr in grp(fam,size)])
for fam,s,l in [("cayley_uniform_tree","65536","262144"),("ust_2d_torus","128","256")]:
    Qs,Ql=Q(fam,s),Q(fam,l)
    print(fam,"log(mean q_large/mean q_small) per t with delta-method se:")
    for i,t in enumerate(times):
        ms,ml=Qs[:,i].mean(),Ql[:,i].mean()
        se=math.sqrt(Qs[:,i].var(ddof=1)/len(Qs)/ms**2+Ql[:,i].var(ddof=1)/len(Ql)/ml**2)
        print(f"  t={t:5d} ratio_log={math.log(ml/ms):+.4f} se={se:.4f} z={math.log(ml/ms)/se:+.2f}")
