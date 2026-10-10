"""Independent minimal cross-check of finite-size gate 5 exponents from the released raw .npz.

Deliberately does not import emergence_lab: chain-bootstrap (2000 reps, seed 20261010),
unweighted OLS of ln<|m|> and ln(N<m^2>/T) vs ln L over the primary window L = 12..48.
Usage: python -I scripts/fss_gate_independent_crosscheck.py finite_size_gate.npz
"""
import sys, numpy as np
z = np.load(sys.argv[1]); T = 2.269185
Ls = [12, 16, 24, 32, 48]
rng = np.random.default_rng(20261010)
def stats(L, idx):
    M = z[f"main_L{L}_magnetization_sum"][idx].astype(float) / (L*L)
    am = np.abs(M).mean(); m2 = (M**2).mean()
    return np.log(am), np.log(L*L*m2/T)
def slope(y): return np.polyfit(np.log(Ls), y, 1)[0]
full = np.array([stats(L, slice(None)) for L in Ls])
bs = []
for _ in range(2000):
    v = np.array([stats(L, rng.integers(0, 16, 16)) for L in Ls]); bs.append([-slope(v[:,0]), slope(v[:,1])])
bs = np.array(bs)
print("beta/nu  %.4f +- %.4f   (exact 0.125)" % (-slope(full[:,0]), bs[:,0].std(ddof=1)))
print("gamma/nu %.4f +- %.4f   (exact 1.75)" % (slope(full[:,1]), bs[:,1].std(ddof=1)))
