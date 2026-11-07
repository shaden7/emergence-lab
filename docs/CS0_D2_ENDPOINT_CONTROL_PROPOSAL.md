# D2-E0 — endpoint-conditioned finite-occupancy MM control (design, NOT frozen)

**Status:** proposal for later-pass review; **no experiment authorized or executed**.
Related: [D2-M0 protocol](CS0_D2_M0_PROTOCOL.md), [D2-M0 observed reference](experiments/2026-11-07-d2-m0-run.md), [Issue #37](https://github.com/shaden7/emergence-lab/issues/37).
This is an exact estimator-control at fixed **input D=2**, not a model comparison, physical discovery, or full-CS0 authorization.

## Question and discriminating comparison

Does the small-N apparent MM dimension shift found in D2-M0 persist when two
causally ordered interval endpoints are included by construction, removing
the undefined R=0 selection event? Compare D2-E0 against the **same total N**
from D2-M0; report the different point-generation conventions prominently.
A difference between curves is a finite-occupancy / endpoint-convention
effect, **not** evidence of dynamical dimension change. Do not interpret
a positive or negative shift as a universal claim.

## Model and exact distribution (analytical derivation)

Take an ideal D=2 Minkowski Alexandrov diamond with its minimal and maximal
events included deterministically, and m=N-2 independent continuous uniform
interior events (N>=2). In null coordinates the inner events induce a uniform
permutation of size m. Let I_m be its inversion count, K_m=m(m-1)/2, and
R_inner=K_m-I_m. Every endpoint is related to all other points, and the
endpoints to each other, contributing (N-1)+(N-2)=2N-3 ordered pairs.
Therefore

    R = 2N-3 + R_inner = 2N-3 + K_m-I_m,
    C = N(N-1)/2,  r=R/C.

The exact multiplicity at R=2N-3+k is the Mahonian coefficient
M(m,k) (symmetry of the inversion distribution), k=0,...,K_m;
the sum of all weights is m!. For m=0 or 1 there is one weight.
The **exact** rational controls are

    min R=2N-3, max R=C;  P(R=0)=0;
    E[R]=2N-3 + (N-2)(N-3)/4;
    E[r]=(N^2+3N-6)/(2N(N-1))
        =1/2+(2N-3)/(N(N-1));
    Var(r) = Var(I_m)/C^2
           = m(m-1)(2m+5)/(72*C^2),  m>=0.

The inversion variance formula also covers m=0,1 by zero factors.
For every finite N, E[r]>1/2, so monotonicity of the usual
Myrheim-Meyer D2 relation implies d(E[r])<2. At N=2 and N=3,
r=1 deterministically, hence d(r)=1; there is no undefined estimate.
Unlike D2-M0, E[d(r)] is **unconditional** and always defined.

## Required proposed observables and controls

For each integer N=2,...,32 report full exact weights, m!, min/max R,
E[r], Var(r), d(E[r]), E[d(r)], and Jensen/nonlinearity gap
E[d(r)]-d(E[r]). Compare d(E[r]) and E[d(r)] with D2-M0's
d(E[r|R>0]) and E[d(r)|R>0], respectively, explicitly identifying
the **different ensembles**. No finite-N claim may be extrapolated to
the continuum or another dimension.

Exact controls: enumeration of all m! permutations for m<=7;
weight symmetry, integer sum, range, rational mean/variance for
every N; N=2,3 both dimensions exactly 1. For numerical checks,
compute an independent 80-digit inversion from exact rational r
(no binary64 intermediate), and check every N's mean-inverse and
full weighted dimension means at N=2,3,4,8,32. Record all
binary64/high-precision discrepancies, including negative outcomes.
The D2-M0 gamma relation, monotonicity and inverse domain must be
rechecked against endpoint fractions before freezing a runner.

## Proposed resources and decision rule (not authorization)

Deterministic, no RNG or sampling error. Proposed limits:
30 CPU seconds, 60 wall seconds, 512 MiB total observed memory,
1,000,000 bytes retained outputs; include controller/finalization cost
and manifest, environment, exact code/config SHA, complete results,
error checks, and SHA-256 digests. Require explicit child containment;
if budget/provenance fails record INCOMPLETE, not a selectively rerun
curve. Outcome vocabulary: REFERENCE_COMPLETE, NUMERICAL_CHECK_FAILED,
INCOMPLETE; never CS0 PASS.

**Freeze gate:** later-pass reviewer verifies the combinatorial law,
variance, inversion range, numerical precision, endpoint ensemble,
proposed tests and enforceable budget. Only then freeze the protocol,
implement a bounded runner in a separate reviewed code change, and
authorize at most one pinned diagnostic. No Lightsail deployment.
