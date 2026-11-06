# D2-M0 — deterministic finite-occupancy MM reference (proposed)

Status: **reviewed/frozen; evaluation recorded separately**. Accepted in the
[PR #71 review](https://github.com/shaden7/emergence-lab/pull/71#issuecomment-6686226940)
at df77fc87711aaa93b640d95b33df62c34fdc1d63, merged as
7dd34c3f4d1dc282a0e220ee6f764f2ee30c93dd. No curve had been evaluated at freeze.
This is a separate follow-up to the exact D2 combinatorial reference, not CS0
study execution or run authorization. Review the numerical implementation and
runner before evaluation; pin the exact code, config and runtime in its record.
No RNG, seed entropy, Monte Carlo samples or physical data enter this diagnostic.

## Question, model and discriminator

At fixed ambient dimension D=2, how much apparent dimension dependence can
selection of finite estimates and nonlinear averaging produce at finite N?
Use the ideal i.i.d. continuously uniform fixed diamond, equivalently a uniform
random 2-order, **without mandatory interval endpoints**. No model search or fit
is performed. Every integer N=2,...,32 is included, with exact integer Mahonian
weights for every R=0,...,C(N,2). No point on the curve may be dropped.

Compare three observables: dimension of the unconditioned mean fraction,
dimension of the explicitly positive-R conditioned mean fraction, and mean of
finite individual MM dimensions. Their differences separate selection from
nonlinear averaging in a model whose input dimension stays exactly 2. This is
an estimator-control calculation, not evidence for dimensional reduction.

## Fixed outputs and exact controls

For every N record the exact rational P(R=0), P(R=C), E[r], E[r|R>0], and numeric
d(E[r]), d(E[r|R>0]), E[d(r)|R>0], plus the nonlinear averaging gap
E[d(r)|R>0]-d(E[r|R>0]). Keep exact weights, conditioning probability and excluded
mass alongside every reported dimension. The unconditioned E[d] is **undefined**
because R=0 has positive probability; do not substitute zero or silently filter.

Required exact controls, justified by docs/CS0_D2_EXACT_REFERENCE.md:

- Total integer weight N!, symmetry and endpoint weights 1.
- P(R=0)=P(R=C)=1/N! and E[r]=1/2.
- E[r|R>0]=1/[2(1-1/N!)] and Var(r)=(2N+5)/(18N(N-1)).
- d(E[r])=2 at every N.
- At N=2 both positive-conditioned dimension observables equal 1.

For all admitted positive fractions, r>=1/496>r_10=1/2002; invert in [1,10].
Strict d(E[r|R>0])<2 is an analytic consequence, not a binary64 sign gate:
the deviation at large N can round away. Preserve high-precision decimal strings
for that observable rather than mistaking a rounded value for zero selection.
Construct every high-precision fraction directly from its exact integer
numerator and denominator, never through a binary64 value. Retain at least
70 significant digits for high-precision conditioned dimensions.

## Independent numerical checks and outcomes

Use the existing binary64 reference inverse for the main numeric curve.
Independently evaluate the gamma expression with 80-digit arithmetic and
bisection on [1,10] until bracket width <=1e-65 (handle exact endpoint r=1
as dimension 1) for:

- every conditioned-mean inverse at N=2,...,32;
- the complete weighted dimension means at N=2,3,4,8;
- fractions 1, 1/2, 1/3, 2/3, 1/496 and 495/496.

Require absolute agreement <=1e-10 between binary64 and independent results.
The exact integer/rational controls must hold exactly. Record errors and all
negative outcomes; numerical agreement is not a formal floating-point proof.

Outcomes: REFERENCE_COMPLETE if all controls/checks pass;
NUMERICAL_CHECK_FAILED for a failed exact/numeric control; INCOMPLETE for a
resource/provenance stop. Never output CS0 PASS or accept the guiding question.

## Budget, provenance and limits

Budget: 30 CPU seconds, 60 wall seconds, 512 MiB and 1 MB total retained output.
The run must have explicit enforced child limits and documented controller cost;
if total observed cost or output exceeds the budget, preserve INCOMPLETE.
No automatic retry or selective rerun. Save code/config pin, software versions,
exact weights, complete CSV, numeric-check results and artifact SHA-256 digests.

This does not calibrate CS0 t-reference family-wise coverage, validate the PRNG,
extend the exact D2 law to D=3/4 or endpoint-conditioned intervals, or establish
physics. A later scale-dependent model comparison needs its own reviewed design,
occupancy accounting, alternative estimators and matched finite-size controls.
