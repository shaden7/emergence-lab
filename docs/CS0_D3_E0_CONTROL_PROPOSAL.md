# D3-E0/M0 — fixed-input D=3 endpoint vs no-endpoint MM finite-occupancy control (design r0, PROPOSED, NOT frozen)

Status: **design proposal only.** Not preregistered/frozen, not authorized, not
run. No new D=3 data exist. Merging this file would integrate a design to be
reviewed, implemented and pilot-checked; it is not an experimental result.
Related: [D2-E0 v1 protocol](CS0_D2_E0_PROTOCOL.md),
[D2-E0 result](experiments/2026-11-11-d2-e0-run.md),
[D2-M0 result](experiments/2026-11-07-d2-m0-run.md),
[Issue #37](https://github.com/shaden7/emergence-lab/issues/37)
(design candidate in the 2026-11-12 07:35 UTC audit comment).

## Question

At D=2 the archived exact references show that the sign of the finite-N
Myrheim–Meyer (MM) bias relative to the input dimension depends on the point
ensemble: with two mandatory interval endpoints E[d(r)]<2 at N=2..32, without
endpoints and conditioning on R>0 E[d(r)|R>0]>2 at N=4..32 (numerical
observation, exact weights). **Does the same ensemble-dependent sign appear at
fixed input D=3?** This is an estimator/measurement-instrument control in one
prescribed geometry. It is not a model comparison, does not answer Issue #37,
and no outcome licenses a statement about physical dimensional reduction.

## Arms (same total N, different ensembles — always disclosed)

Geometry: the unit-height D=3 Minkowski Alexandrov diamond
`|t| + |x| <= 1/2`, x in R^2, as in `causal_set_mm.sprinkle_diamond`.
Relation: strict interior of the future light cone (`causal_matrix`).

- **Arm A (E0, endpoints):** the bottom and top tips plus m=N-2 i.i.d.
  uniform interior points. R = 2N-3 + R_inner. R>0 always.
- **Arm B (M0, no endpoints):** N i.i.d. uniform points. The MM estimate is
  reported conditional on R>0 (as in D2-M0); P(R=0) is reported separately.

C = N(N-1)/2, r = R/C, d(r) = inverse of
f(d) = Gamma(d+1) Gamma(d/2) / (2 Gamma(3d/2)) on [1,10] (as in D2-E0 v1),
d(1)=1 exactly. f(3) = 8/35.

Proposed grid: N in {2,3,4,5,6,8,12,16,24,32}. N<=32 keeps the grid inside
the archived D=2 exact range (positive control) and guarantees that every
positive fraction is invertible: min positive r = 1/C >= 1/496 > f(10)
≈ 4.995e-4. Hence in arm B "R>0" and "d defined" coincide, and arm A is
always defined. N>=64 would add an OUT_OF_RANGE category and is excluded.

## Established identities and exact controls (model-level, no sampling)

Pair-relation probability for two i.i.d. uniform diamond points is f(D)
(Myrheim 1978; Meyer 1988; Surya 2019 review). Hence, exactly:

- Arm B: E[r] = 8/35 for every N>=2 (unconditioned); E[r | R>0] =
  (8/35)/P(R>0) > 8/35, so d(E[r|R>0]) < 3 whenever P(R=0)>0.
  N=2: P(R=0) = 27/35, and conditional on R>0, r=1, d=1 exactly.
- Arm A: E[R] = 2N-3 + (8/35)(N-2)(N-3)/2 and
  E[r] = 8/35 + (27/35)(2N-3)/C > 8/35; since f is decreasing,
  d(E[r]) < 3 at every finite N. Rational values: N=4 61/70,
  N=8 115/196, N=16 83/200, N=32 1123/3472.
  N=2,3: r=1, d=1 exactly. N=4: R_inner ~ Bernoulli(8/35), r in {5/6, 1},
  E[d(r)] = (27/35) d(5/6) + 8/35 ≈ 1.219020 (d(5/6) ≈ 1.283914, the same
  inverse value that enters the archived D2-E0 N=4 entry 1.141957).
- Exact arm-A N=5 and arm-B N=3 laws need the D=3 three-point configuration
  probabilities (chain, V, Λ, single relation, antichain). These must be
  computed by a deterministic quadrature written independently of the
  sampler and then compared with Monte Carlo; they are **not** asserted here.
- Var(r) at D=3 is not claimed in closed form; it is estimated empirically.

Numerical design observation (finite-difference at r = 0.1, 0.2286, 0.4,
0.6; not a proof): d(r) is convex there. Later-pass check (2026-11-13,
40-digit mpmath, 901-point grid on d in [1,10]): f'<0 and f''>0 at every
grid point, so d''(r) = -f''(d)/f'(d)^3 > 0 on the whole invertible support
(still a grid check, not a proof). Given convexity on the support, Jensen gives E[d(r)] >= d(E[r]), so in arm A
the endpoint shift (d(E[r])<3) and the Jensen gap (>=0) compete; in arm B
the R>0 conditioning (lower d) and the Jensen gap (higher d) compete. The
sign of E[d(r)]-3 in either arm is therefore **not** settled by identities
and is the target quantity. Arm-A d(E[r]) is far below 3 on the grid
(≈1.784 at N=8, 2.565 at N=32), so H_A below is expected but unverified.

## Hypotheses (to be tested, not assumed)

- H_A: E[d(r)] < 3 in arm A at every grid N.
- H_B: E[d(r) | R>0] > 3 in arm B at grid N >= N_B for some small N_B.
- Sign reversal at N := arm A BELOW and arm B ABOVE (rules below) at that N.

## Sampling, implementation requirements, independence

Unlike D=2 (Mahonian weights), the D=3 relation-count law has no known
closed form here; estimation is Monte Carlo with i.i.d. replicate sprinklings,
so there is no Markov-chain autocorrelation. Requirements before any target:

1. Two independent samplers: (i) existing rejection sampler; (ii) direct
   sampler — t with density ∝ (1/2-|t|)^2, then uniform in the disc of radius
   1/2-|t|. Agreement gates: pair probability vs 8/35 within 4 SE for each;
   R-distribution chi-square/permutation test between samplers at N=3,4,8.
2. Deterministic quadrature for the D=3 three-point probabilities; Monte
   Carlo N=3 arm-B and N=5 arm-A laws must agree within 4 SE.
3. **D=2 positive control through the same Monte Carlo pipeline**: run arms
   A/B at input D=2 on the grid and require |MC − archived exact| <= 4 SE for
   E[d] (A) and E[d|R>0] (B) at every N (archived values in
   `docs/experiments/d2-e0-v1-20261111/ensemble_comparison.csv` and
   `docs/experiments/d2-m0-run-20261107/curve.csv`). Failure ⇒ INVALID, no
   D=3 conclusion.
4. Seeds: numpy `SeedSequence` with a fixed, recorded root; spawn keys
   (arm, D, N, chunk). Pilot and target roots differ. Manifest with code
   commit, config hash, versions, per-cell counts, sums, sums of squares,
   R=0 count, and raw per-replicate R in compact integer form.

## Pilot (engineering only) and freezing

A bounded pilot with its own seed root measures per-cell Var(d), P(R=0),
CPU s per replicate and archive size. It is used **only** to choose
replicate counts and confirm the budget; pilot estimates are never reported
as results or pooled into target estimates. Proposed pilot ceiling: 60 CPU s,
512 MiB, 2,000 replicates per cell.

Freeze then fixes: grid, replicates per cell n_c (proposed target: the
smallest n_c making the 4-SE half-width <= 0.01 in dimension units in every
D=3 cell, capped so total CPU <= 600 s and RSS <= 512 MiB on the executing
host), seed root, thresholds below and the archive layout. If the cap binds
before 0.01 is reached, the cell is reported with its achieved half-width.

## Decision rules (proposed, to freeze)

Per (arm, N) cell at D=3, estimator Δ = mean(d) − 3 (arm B: over R>0
replicates), standard error from i.i.d. replicates. Family of 20 cells,
Bonferroni family-wise α=0.01 ⇒ two-sided per-cell z = 3.48.
ABOVE if Δ − z·SE > 0; BELOW if Δ + z·SE < 0; else UNRESOLVED.
Also report d(E[r]) (arm A: exact rational; arm B: d((8/35)/P̂(R>0))) and the
Jensen gap E[d]−d(E[r]) with SEs; never substitute one for the other.
Outcomes: INVALID (any implementation/positive-control gate fails, or
budget/provenance failure); UNDECIDABLE_AT_BUDGET (any cell UNRESOLVED at
N >= 4); otherwise COMPLETE with the per-cell classification table.
All cells, failed gates and negative outcomes are retained; no rerun with
larger budget without a new reviewed protocol.

## Exclusions and limits

No D=4, no other estimator (midpoint, chain-length), no k-order null, no
Poisson-N ensemble, no N-to-length conversion, no full-CS0 claim. A D=3
sign pattern mirroring D=2 would show only that this estimator's finite-N
bias sign is ensemble-dependent in two prescribed flat geometries; it
cannot show that any model's reported dimensional reduction is (or is not)
an artifact. No Lightsail, deployment or paid API.

## Review checklist for the later pass

Verify the identities above (and the constants test
`tests/test_d3_e0_design_constants.py`), the grid's invertibility argument,
the Bonferroni arithmetic, whether D=2 MC-vs-exact at 4 SE is adequately
powered as a positive control, and whether 0.01 is a sensible precision
target given the pilot. Record PASS/REVISE before any implementation PR.

## Later-pass review r0 → findings to resolve at freeze (2026-11-13)

Review by Director `rd-claude-20261113T080316Z-7d3fd7a3` (separate session
from the author; same-model AI, not external peer review). Decision: **PASS
for integration as a design proposal only.** Verified: f(3)=8/35 (exact Gamma
arithmetic and 40-digit check); arm-A identity R = 2N-3 + R_inner and
C(N,2)-C(N-2,2) = 2N-3; the four quoted rationals; arm-A N=4 E[d]≈1.219020;
arm-B N=2 law; grid invertibility (1/496 > f(10) = 1/2002); Bonferroni
z = 3.4808; direct-sampler t-density ∝ (1/2-|t|)^2. 88 tests pass locally.

The following are **mandatory freeze items** (the protocol may not be frozen
until each is resolved in text and, where applicable, by a test):

1. **D=2 positive-control power.** Fix the D=2 replicates per cell (proposed:
   same n_c as the matching D=3 cell) and state the minimum MC-vs-exact bias
   the 4-SE gate detects with stated power. A gate with unspecified n can
   pass a biased pipeline.
2. **Budget scope.** State whether the 600 CPU s / 512 MiB cap covers the
   D=2 control, sampler-agreement and quadrature gates, or only D=3 cells.
   Engineering-only feasibility probe in review (scratch, not a pilot, not
   archived; no D=3 sign or mean recorded): SD(d) per cell ≈0.2–0.8, so
   O(10^5) R>0-replicates per cell meet the 0.01 target at ≈20–75 µs per
   replicate (vectorised direct sampler), i.e. O(10^2) CPU s in total. The
   frozen pilot must re-measure this on the executing host.
3. **Precision vs decision threshold.** n_c is set by a 4-SE half-width but
   classification uses z = 3.48; keep both but say so explicitly. In arm B
   n_c must count R>0 replicates (P(R>0) ≈ 0.47 at D=3, N=3).
4. **Deterministic cells.** Arm A N=2,3 and arm B N=2 have d = 1 exactly
   (SE = 0). Classify them analytically and state whether they stay in the
   Bonferroni family (20 is conservative; 17 is exact).
5. **Additional exact anchor.** Literature closed forms for expected k-chain
   counts in a flat diamond (Meyer 1988, as reviewed in Surya 2019) give the
   3-chain probability exactly; verify the reference and use it as an extra
   check of the three-point quadrature.

Not issues: the identities above; claims are correctly bounded (H_A, H_B are
hypotheses; no D=3 data; no Issue #37 or physical inference).

## Implementation r1 and proposed freeze-item resolutions (2026-11-14, PROPOSED)

Director `rd-claude-20261114T080252Z-e5ca9465`. Code:
`src/emergence_lab/d3_e0.py`, tests `tests/test_d3_e0_impl.py`. Still **not
frozen, not authorized, no pilot and no target run**. No D=3 target-cell
Monte Carlo mean or SD was computed or looked at; the D=3 engineering probe
printed CPU time only.

Implemented: (i) a vectorised direct sampler (u = 1/2−|t| with density ∝
u^(D−1), uniform ball cross-section), written independently of the existing
rejection sampler; (ii) batched relation counting (strict light-cone
interior) and arms A/B (arm A uses R = 2N−3 + R_inner); (iii) the inverse
d(k/C) on [1,10] as a lookup table for every grid N (all finite, < 10);
(iv) a deterministic mpmath (40-digit tanh-sinh) quadrature of the labeled
three-point probabilities, using that the future/past of x inside the
diamond is an Alexandrov interval of volume fraction τ±^D:
q_pair = E[τ+^D], q_chain = E[τ−^D τ+^D], q_down = E[τ+^(2D)]; (v) the
N=3 relation-count law P(3)=6q_chain, P(2)=2(3q_down−6q_chain), P(1) from
E[R], P(0) by normalisation; (vi) a Monte Carlo cell estimator with i.i.d.
SE and the D=2 positive-control comparison against the archived exact table.

Gate checks run in tests (engineering sizes, fixed seed root 20261114, not the
pilot or target roots):

- Quadrature vs exact values (numerical agreement, not a proof): D=2
  q_chain = 1/36, q_down = 1/9 (light-cone coordinates) to 1e−14; q_pair =
  f(D)/2 at D=2,3 to 1e−12; q_chain equals the literature k-chain closed form
  χ_3 at D=2 (1/36) and D=3 (2/525) to 1e−12 (freeze item 5: formula as
  recalled from Meyer 1988 / Surya 2019; primary-source text not re-checked
  in this run). D=3 q_down agrees with 1/30 to 1e−13.
- **Quadrature → archived D=2 exact:** the quadrature law reproduces the
  archived exact arm-B N=3 E[d|R>0] = 1.853650366338 and arm-A N=5 E[d] =
  1.260177663638 to 1e−12. This checks the law construction, the inverse
  table and the arm-A offset against an independent (Mahonian) computation.
- Sampler agreement: pair probability within 4 SE of f(D) for both samplers
  at D=2,3 (40,000 pairs each); D=3 R-distribution chi-square between
  samplers at N=3,4,8 (6,000 replicates each) p > 1e−3; MC D=3 N=3 law within
  4 SE of the quadrature law in every R class (200,000 replicates).
- D=2 MC positive control (20,000 replicates; arm A N=4,8; arm B N=4,8,16):
  |z| ≤ 4 against the archived exact values.

Exact D=3 three-point cells implied by the quadrature (numerical evaluation
of exact integrals; the rationals are matched to ~1e−13, not proved here):
N=3 law P(R=0,1,2,3) = 18/35, 54/175, 27/175, 4/175; hence arm-B N=3
E[d|R>0] ≈ 2.163007 and P(R=0) = 18/35 (P(R>0) ≈ 0.486); arm-A N=5 E[d] ≈
1.408768. Both are below 3 (classification-free statement about two
small-N cells; H_B concerns N ≥ N_B and is untested).

Proposed resolutions (to be confirmed by a later-pass review, then frozen):

1. **D=2 control power.** D=2 replicates per cell = the matching D=3 cell's
   n_c (R>0 count in arm B), at least 10^5. With D=2 SD(d) ≤ 0.68 per cell
   (engineering probe, 8,192 replicates/cell; arm B N=4 largest), the
   |z| > 4 gate detects a pipeline bias |b| ≥ (4+1.2816)·SD/√n ≈ 0.011 with
   power ≥ 0.9 per cell. Family-wise false-INVALID probability under a
   correct pipeline ≈ 17·6.3e−5 ≈ 1e−3.
2. **Budget scope.** One cap covers everything: D=3 cells, D=2 control,
   sampler-agreement and quadrature gates: 600 CPU s and 512 MiB RSS total.
   Engineering timing (this sandbox, 2 vCPU, numpy 2.5.3, scipy 1.18.1):
   ≈123 µs per replicate summed over the 17 stochastic D=3 cells, ≈55 µs for
   D=2; quadrature ≈10 s for D=2 and D=3 together. 10^5 replicates/cell ⇒
   ≈20 s total; the cap is not expected to bind but the pilot must re-measure
   on the executing host.
3. **Precision vs decision.** n_c is chosen by the 4-SE half-width ≤ 0.01
   (n_c = ⌈(4·SD̂/0.01)²⌉ from pilot SD̂); classification uses the Bonferroni
   z below. These are deliberately different: precision targets the
   reported interval, z controls the family-wise error. In arm B n_c counts
   R>0 replicates; the total drawn is ⌈n_c / P̂(R>0)⌉ (P(R>0) = 17/35 at N=3
   exactly).
4. **Deterministic cells.** Arm A N=2,3 and arm B N=2 have d ≡ 1 (verified in
   tests: SD = 0). They are classified analytically BELOW and removed from
   the Bonferroni family, which becomes the 17 stochastic cells: per-cell
   two-sided z = Φ^(−1)(1 − 0.01/34) ≈ 3.4370. Arm-B N=3 and arm-A N=5 stay
   in the Monte Carlo family; their quadrature values above serve as an
   additional exact gate (|MC − quadrature| ≤ 4 SE).
5. **Additional anchor.** Done as above (χ_3 closed form vs quadrature at
   D=2,3). Before freezing, the cited formula should be checked against the
   primary text; the quadrature itself does not depend on it.

Next: later-pass review of this implementation (separate session); then a
frozen protocol with seed roots, pilot (≤60 CPU s, ≤2,000 replicates/cell)
and target n_c rule. No deployment, Lightsail/EatSleepFeel or paid API.
