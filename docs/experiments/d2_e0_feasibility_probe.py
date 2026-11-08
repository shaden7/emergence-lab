"""D2-E0 feasibility probe (NOT the D2-E0 diagnostic; no frozen protocol).

Measures, for the proposed endpoint ensemble N=2..32:
  * per-N support rows vs distinct reduced fractions,
  * CPU for a seeded 80-digit Newton inverse with bracket certification,
  * binary64 brentq discrepancy vs the 80-digit value,
  * serialized byte sizes of candidate output layouts.
Standard library + mpmath 1.3.0 + scipy. Run with: python3 -I e0_probe.py
"""
import gzip, hashlib, json, math, sys, time
from fractions import Fraction

import mpmath
from scipy.optimize import brentq

T0 = time.process_time()
mp = mpmath.mp.clone(); mp.dps = 80


def mahonian(m):
    w = [1]
    for j in range(1, m + 1):  # multiply by 1+q+...+q^(j-1)
        new = [0] * (len(w) + j - 1)
        for i, a in enumerate(w):
            for s in range(j):
                new[i + s] += a
        w = new
    return w


def f64(d):
    return math.gamma(d + 1) * math.gamma(d / 2) / (2 * math.gamma(1.5 * d))


def fmp(d):
    return mp.gamma(d + 1) * mp.gamma(d / 2) / (2 * mp.gamma(3 * d / 2))


def inv64(r):
    if r == 1.0:
        return 1.0
    return brentq(lambda d: f64(d) - r, 1.0, 10.0, xtol=1e-15, rtol=8.9e-16, maxiter=200)


def invhp(r: Fraction, seed: float):
    """Newton from binary64 seed; certify by sign change on [d-δ, d+δ]."""
    if r == 1:
        return mp.mpf(1), mp.mpf(0), 0
    t = mp.mpf(r.numerator) / mp.mpf(r.denominator)
    d = mp.mpf(seed)
    it = 0
    for it in range(1, 40):
        fd = fmp(d) - t
        # derivative of f: f * (psi(d+1) + psi(d/2)/2 - 1.5 psi(1.5d))
        der = fmp(d) * (mp.digamma(d + 1) + mp.digamma(d / 2) / 2 - 1.5 * mp.digamma(1.5 * d))
        step = fd / der
        d -= step
        if abs(step) < mp.mpf('1e-75'):
            break
    delta = mp.mpf('1e-62')
    lo, hi = fmp(d - delta) - t, fmp(d + delta) - t
    if not (lo > 0 > hi):  # f decreasing: bracket certification
        raise RuntimeError(f'certification failed r={r}')
    return d, abs(fmp(d) - t), it


rows, distinct, perN = [], {}, {}
for N in range(2, 33):
    m, C = N - 2, N * (N - 1) // 2
    w = mahonian(m)
    assert sum(w) == math.factorial(m) and w == w[::-1]
    perN[N] = w
    for k, wk in enumerate(w):
        r = Fraction(2 * N - 3 + k, C)
        rows.append((N, k, r))
        distinct.setdefault(r, 0)
        distinct[r] += 1
t_enum = time.process_time() - T0

t1 = time.process_time()
sol, maxres, maxdisc, maxit = {}, mp.mpf(0), 0.0, 0
for r in distinct:
    seed = inv64(float(r))
    d, res, it = invhp(r, seed)
    sol[r] = (d, seed)
    maxres = max(maxres, res); maxit = max(maxit, it)
    maxdisc = max(maxdisc, float(abs(mp.mpf(seed) - d)))
t_inv = time.process_time() - t1

# monotonicity across each N's support (r increasing in k => d nonincreasing)
mono = all(sol[rows[i][2]][0] >= sol[rows[i + 1][2]][0]
           for i in range(len(rows) - 1) if rows[i][0] == rows[i + 1][0])

# weighted summaries, binary64 vs 80-digit
t2 = time.process_time()
summ, maxsumdisc = [], 0.0
for N, w in perN.items():
    C, tot = N * (N - 1) // 2, sum(w)
    Er = sum(Fraction(wk * (2 * N - 3 + k), C) for k, wk in enumerate(w)) / tot
    assert Er == Fraction(N * N + 3 * N - 6, 2 * N * (N - 1))
    Ed_hp = mp.fsum(mp.mpf(wk) * sol[Fraction(2 * N - 3 + k, C)][0] for k, wk in enumerate(w)) / tot
    Ed_64 = math.fsum(wk * sol[Fraction(2 * N - 3 + k, C)][1] for k, wk in enumerate(w)) / tot
    dEr_64 = inv64(float(Er))
    dEr_hp, _, _ = invhp(Er, dEr_64)
    maxsumdisc = max(maxsumdisc, abs(float(Ed_hp) - Ed_64), abs(float(dEr_hp) - dEr_64))
    summ.append(dict(N=N, Er=[Er.numerator, Er.denominator], dEr=mp.nstr(dEr_hp, 80, strip_zeros=False),
                     Ed=mp.nstr(Ed_hp, 80, strip_zeros=False), dEr64=repr(dEr_64), Ed64=repr(Ed_64)))
t_sum = time.process_time() - t2

# serialization layouts
weights_canon = json.dumps({str(N): w for N, w in perN.items()}, separators=(',', ':')).encode()
dist_tab = [[r.numerator, r.denominator, mp.nstr(sol[r][0], 80, strip_zeros=False), repr(sol[r][1])]
            for r in sorted(distinct)]
cover = {str(N): len(w) for N, w in perN.items()}
A = json.dumps(dict(distinct=dist_tab, coverage=cover, summaries=summ,
                    weights_sha256=hashlib.sha256(weights_canon).hexdigest()), separators=(',', ':')).encode()
B = json.dumps(dict(distinct=dist_tab, coverage=cover, summaries=summ, weights=json.loads(weights_canon)),
               separators=(',', ':')).encode()
out = dict(
    support_rows=len(rows), distinct_fractions=len(distinct),
    max_newton_iterations=maxit, max_hp_residual=mp.nstr(maxres, 5),
    max_binary64_discrepancy_support=maxdisc, max_binary64_discrepancy_summaries=maxsumdisc,
    monotone_nonincreasing=mono,
    cpu_s=dict(enumerate=round(t_enum, 3), inverse=round(t_inv, 3), summaries=round(t_sum, 3),
               total=round(time.process_time() - T0, 3)),
    bytes=dict(weights_json=len(weights_canon), weights_gzip9=len(gzip.compress(weights_canon, 9, mtime=0)),
               A_distinct_no_weights=len(A), A_gzip9=len(gzip.compress(A, 9, mtime=0)),
               B_distinct_with_weights=len(B), B_gzip9=len(gzip.compress(B, 9, mtime=0))),
    probe_points=dict(N32_min=mp.nstr(sol[Fraction(61, 496)][0], 20)),
    versions=dict(python=sys.version.split()[0], mpmath=mpmath.__version__),
)
print(json.dumps(out, indent=1))
