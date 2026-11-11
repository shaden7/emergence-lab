"""Read-only independent re-analysis of an archived D2-E0 result, not a target rerun.

No emergence_lab imports. Exact law via a sliding-window DP; direct coordinate
counts through N=9; unseeded bisection on those supports; all saved support
forward residuals, moments and weighted summaries independently recomputed.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import permutations
import json
import math
from pathlib import Path
import resource
import signal
import time


def recheck(directory):
    import mpmath as mp
    mp.mp.dps = 80
    folder = Path(directory)
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    raw_gzip = (folder / 'reference.json.gz').read_bytes()
    raw = gzip.decompress(raw_gzip)
    assert manifest['outcome'] == 'REFERENCE_COMPLETE' and manifest['stage'] == 'finished'
    assert manifest['authorized'] is True and manifest['frozen'] is True
    assert manifest['cap_sys_resource'] is False and manifest['cs0_acceptance'] is False
    assert hashlib.sha256(raw_gzip).hexdigest() == manifest['reference_sha256']
    assert hashlib.sha256(raw).hexdigest() == manifest['raw_sha256']
    payload = json.loads(raw)
    assert payload['outcome'] == 'REFERENCE_COMPLETE' and payload['failures'] == []
    assert payload['config']['sizes'] == list(range(2, 33))
    f = lambda d: mp.gamma(d+1)*mp.gamma(d/2)/(2*mp.gamma(3*d/2))
    as_mp = lambda r: mp.mpf(r.numerator)/r.denominator
    fractions = [Fraction(*row['r']) for row in payload['fractions']]
    assert fractions == sorted(set(fractions))
    values = [mp.mpf(row['d_hp']) for row in payload['fractions']]
    worst_residual = mp.mpf(0)
    for r, d in zip(fractions, values):
        residual = abs(f(d)-as_mp(r))
        assert residual <= mp.mpf('1e-60') and 1 <= d < 10
        assert (r == 1 and d == 1) or f(d-mp.mpf('1e-62')) > as_mp(r) > f(d+mp.mpf('1e-62'))
        worst_residual = max(worst_residual, residual)
    assert all(a >= b for a, b in zip(values, values[1:]))
    dp = [1]
    law, enumerated, bisection_cache = {}, 0, {}
    worst_bisection = worst_summary = mp.mpf(0)
    observed_fractions = set()
    rows = []
    assert len(payload['summaries']) == len(payload['weights']) == len(payload['coverage']) == 31
    for n, w, coverage, summary in zip(range(2,33), payload['weights'], payload['coverage'], payload['summaries']):
        m = n-2
        if m >= 2:
            acc, nxt = 0, []
            for k in range(len(dp)+m-1):
                acc += dp[k] if k < len(dp) else 0
                acc -= dp[k-m] if 0 <= k-m < len(dp) else 0
                nxt.append(acc)
            dp = nxt
        law[n] = list(dp)
        assert w['N'] == coverage['N'] == summary['N'] == n
        assert w['counts'] == dp and sum(dp) == math.factorial(m)
        C, offset = math.comb(n,2), 2*n-3
        assert w['offset'] == offset and w['pairs'] == C and w['denominator'] == math.factorial(m)
        support = [Fraction(offset+k,C) for k in range(len(dp))]
        observed_fractions.update(support)
        idx = coverage['fraction_index']
        assert [fractions[i] for i in idx] == support
        mean = sum((Fraction(c,math.factorial(m))*r for c,r in zip(dp,support)),Fraction())
        var = sum((Fraction(c,math.factorial(m))*(r-mean)**2 for c,r in zip(dp,support)),Fraction())
        assert mean == Fraction(n*n+3*n-6,2*n*(n-1)) == Fraction(*summary['mean_r'])
        assert var == Fraction(m*(m-1)*(2*m+5),72*C*C) == Fraction(*summary['variance_r'])
        expected_d = mp.fsum(as_mp(Fraction(c,math.factorial(m)))*values[i] for c,i in zip(dp,idx))
        err = abs(expected_d-mp.mpf(summary['mean_dimension_hp']))
        worst_summary = max(worst_summary,err)
        assert err < mp.mpf('1e-70')
        dmean = mp.mpf(summary['dimension_of_mean_r_hp'])
        assert abs(f(dmean)-as_mp(mean)) <= mp.mpf('1e-60')
        if n <= 9:
            counts = Counter(offset+sum(p[i]<p[j] for i in range(m) for j in range(i+1,m))
                             for p in permutations(range(m)))
            enumerated += math.factorial(m)
            assert counts == Counter({offset+k:c for k,c in enumerate(dp)})
            for r,i in zip(support,idx):
                if r not in bisection_cache:
                    lo,hi = mp.mpf(1),mp.mpf(10)
                    if r == 1:
                        hi = lo
                    else:
                        while hi-lo > mp.mpf('1e-65'):
                            mid = (lo+hi)/2
                            if f(mid)>as_mp(r): lo=mid
                            else: hi=mid
                    bisection_cache[r]=(lo+hi)/2
                discrepancy=abs(values[i]-bisection_cache[r])
                worst_bisection=max(worst_bisection,discrepancy)
                assert discrepancy < mp.mpf('1e-60')
        rows.append(dict(N=n,endpoint_mean_dimension=float(expected_d),endpoint_dimension_of_mean=float(dmean)))
    assert observed_fractions == set(fractions)
    return dict(outcome='RECHECK_PASS', enumerated_permutations=enumerated,
                support_fractions=len(fractions), independent_bisections=len(bisection_cache),
                max_forward_residual=mp.nstr(worst_residual,8),
                max_bisection_discrepancy=mp.nstr(worst_bisection,8),
                max_weighted_summary_discrepancy=mp.nstr(worst_summary,8), rows=rows,
                limitation='Same-session AI-mediated independent code; not external review or formal proof.')


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    signal.alarm(60)
    parser=argparse.ArgumentParser();parser.add_argument('directory');args=parser.parse_args()
    start=time.process_time();result=recheck(args.directory)
    result['cpu_seconds']=time.process_time()-start
    print(json.dumps(result,sort_keys=True,indent=2))
