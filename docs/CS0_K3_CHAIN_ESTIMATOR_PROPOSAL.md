# K3-E0/M0 — second causal-set dimension estimator (3-chain abundance) on the D=2/D=3 endpoint/no-endpoint arms (design r1, PROPOSED, NOT frozen)

Status: **design proposal only.** Not preregistered/frozen, not authorized,
not implemented beyond a constants test, not run. No D=3 K3 data exist.
Merging this file would integrate a design for later-pass review; it is not a
result.
Author r0: Director `rd-claude-20261122T080245Z-85f98e1f` (2026-11-22).
Revision r1: Director `rd-claude-20261123T080344Z-746a46c8` (2026-11-23),
addressing [later-pass review r1 (REVISE)](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7095051265).
See "Revision r1" at the end of this file. r1 is self-authored by the reviewer
session and needs a later-pass review r2 by a different session.
Related: [Issue #37](https://github.com/shaden7/emergence-lab/issues/37),
[D3-E0/M0 proposal](CS0_D3_E0_CONTROL_PROPOSAL.md),
[D3-E0/M0 protocol](CS0_D3_E0_PROTOCOL.md),
[D3-E0/M0 v1 target archive](experiments/d3-e0-v1-target-20261120/),
constants test `tests/test_k3_design_constants.py`.

## Why this control

Issue #37 asks whether short-scale dimensional reduction is robust or an
artifact of the measurement, and its "robust" criterion requires
**≥ 2 independently calibrated estimators**. So far the causal-set track has
exactly one estimator, Myrheim–Meyer (MM, the 2-chain/relation fraction).
Integrated numerical observations for MM in a flat diamond (fixed input D,
no physical claim):

- D=2 (exact weights, archived): arm A (two interval endpoints) E[d] < 2 at
  N = 2..32; arm B (no endpoints, conditioned on R>0) E[d | R>0] > 2 at N = 4..32.
- D=3 (Monte Carlo, v1 target, merged `8cff580`): arm A BELOW 3 at every grid
  N; arm B BELOW at N = 3–5 and ABOVE at N ≥ 6.

That is, the **sign** of MM's finite-N bias depends on the point ensemble.
The open instrument-level question is whether this sign pattern belongs to the
quantity being measured (flat-diamond dimension at small N) or to the
particular estimator. A second estimator on **identical arms and geometries**
is the smallest discriminating step.

## Question (preregistration target)

Let C_3 be the number of 3-chains (x<y<z) in the sprinkled order, and
c_3 = C_3 / binom(N,3). Define the 3-chain dimension d_3 as the inverse of

    g_3(D) = 3! · χ_3(D),   χ_k(D) = (1/k) (Γ(D+1)/2)^(k-1) Γ(D/2) Γ(D) / (Γ(kD/2) Γ((k+1)D/2))

on [1,10] (g_3 is the probability that three i.i.d. uniform diamond points
form a chain in some order). **At fixed input D ∈ {2,3}, in arms A and B, is
the sign of the finite-N bias of d_3 the same as that of MM at every grid
N?** Answer per cell: CONCORDANT, DISCORDANT, or UNRESOLVED (rules below).

This is an estimator comparison in one prescribed geometry. It is not a model
comparison, does not answer Issue #37, and no outcome licenses any statement
about physical dimensional reduction.

## Honest scope of "independent"

d_3 is a **distinct statistic** (3-point abundance vs 2-point), with its own
calibration curve, exact anchors and failure modes, but it belongs to the
same chain-abundance family as MM (MM is the k=2 member) and is computed on
the same sprinkling. It is therefore expected to be **positively correlated**
with MM replicate by replicate; the design reports that correlation. A
concordant result would support only "the sign pattern is shared within the
chain-abundance family", not estimator-independence in general. Estimators
based on a different principle (midpoint/longest-chain scaling, Reid 2003;
interval abundances, Glaser–Surya 2013; spectral or d'Alembertian-based
dimensions) are excluded here because at N ≤ 32 they are either undefined or
dominated by integer discreteness; they are the natural next candidates.
Citations are as recalled by the author; not re-checked in this run.

## Arms, geometry, grid

Identical to D3-E0/M0 v1: unit-height Alexandrov diamond `|t| + |x| ≤ 1/2`,
strict interior of the future light cone, direct sampler
`d3_e0.direct_sample`.

- **Arm A (endpoints):** two tips plus m = N−2 i.i.d. interior points. Exact
  identity (each tip precedes/follows every interior point a.s.):
  C_3 = C_3,inner + 2 R_inner + m, so C_3 ≥ m > 0 for N ≥ 3 (checked
  against brute-force triple counting in the constants test).
- **Arm B (no endpoints):** N i.i.d. points; d_3 reported conditional on
  C_3 > 0; P(C_3 = 0) reported separately. Note C_3 > 0 is a **stricter**
  event than MM's R > 0 (C_3>0 implies R>0). **Primary comparison (r1):
  matched conditioning.** In arm B both estimators are evaluated on the same
  replicates with C_3 > 0; MM | R>0 is reported as a secondary, descriptive
  value and is used only by gate 3 (tie to the archive).

Counting: for a transitive order, C_3 = Σ_y |past(y)|·|future(y)|
(O(N²) given the causal matrix). Grid N ∈ {3,4,5,6,8,12,16,24,32}
(N=2 has no 3-chain). Invertibility: the smallest positive c_3 on the grid is
1/binom(32,3) ≈ 2.02e−4 ≫ g_3(10) ≈ 5.4e−9, so every positive c_3 is
invertible on [1,10]. **Boundary (r1):** c_3 = 1 (total order) is mapped to
d_3 = 1 explicitly and not by root finding. In double precision g_3(1)
evaluates to 1 − 2.2e−16, so a bracketing solver on [1,10] fails there. This
case has positive probability (arm A N=4; arm B N=3). MM's
`myrheim_meyer_dimension` already maps r = 1 to 1.

## Established identities and exact anchors (no sampling)

Checked numerically in `tests/test_k3_design_constants.py` (40-digit mpmath;
grid checks, not proofs):

- g_3(1) = 1, g_3(2) = 1/6, g_3(3) = 4/175, g_3(4) = 1/350. g_3(3) = 4/175
  equals the D3-E0 quadrature value P(R=3) at N=3 (independent of the χ_k
  formula). 2χ_2 = f (MM ordering fraction) at D = 2,3,4.
- g_3 is strictly decreasing and convex on a 91-point grid in [1,10], so
  d_3(c) is decreasing and convex there; Jensen then gives E[d_3] ≥ d_3(E[c_3]).
- Arm B: E[c_3] = g_3(D) for every N ≥ 3 (linearity), but
  E[c_3 | C_3>0] > g_3(D) whenever P(C_3=0) > 0. As for MM, the conditioning
  (lowers d) and the Jensen gap (raises d) compete; the sign is the target.
- Arm A: E[c_3] = (binom(m,3) g_3 + 2 binom(m,2) f + m)/binom(N,3) > g_3 at
  every grid N for D = 2,3, hence d_3(E[c_3]) < D; endpoint shift and Jensen
  gap compete.
- Deterministic cells: arm A N=3 (c_3 = 1) and arm B N=3 | C_3>0 (c_3 = 1)
  give d_3 = 1 exactly at both D; classified analytically BELOW.
- Arm A N=4: C_3 ∈ {2,4}, c_3 ∈ {1/2, 1}, P(c_3=1) = f(D). With
  d_3(1/2) ≈ 1.407226: E[d_3] ≈ 1.203613 (D=2), ≈ 1.314146 (D=3); both BELOW,
  identical in sign to MM's arm-A N=4 cells (1.141957 and 1.219020).
- Caveat (b) (χ_k primary text) remains open; the gates below do **not**
  depend on the closed form, because the D=3 N=3 anchor comes from the
  existing quadrature and the D=2 anchors from permutation enumeration.

## Controls

1. **D=2 exact positive control.** A D=2 diamond sprinkling is a uniformly
   random permutation (light-cone coordinates); C_3 is the number of
   increasing length-3 subsequences. Exact laws by full enumeration of S_N
   for arm B N ≤ 9 and arm A m ≤ 9 (N ≤ 11); Monte Carlo must agree within
   4 SE at those N; otherwise INVALID. D=2 cells at larger N are Monte Carlo
   cells of the target.
2. **Sampler/count gates.** C_3 by the in·out formula equals brute-force
   triple counting on fixed-seed batches; MC mean of c_3 in arm B within 4 SE
   of g_3(D) at N = 4, 8, 32 for D = 2, 3.
3. **MM re-measurement in the same replicates.** MM d is recomputed on the
   same sprinklings (arm B: conditioned on R>0, as archived); its arm/N sign must agree with the archived MM
   classification wherever that was resolved (D=2 exact; D=3 v1), else
   INVALID. This ties the comparison to integrated evidence instead of a
   second, unreviewed MM run.
4. **Negative (non-manifold) control.** Transitive percolation (random DAG on
   N=32 labelled elements, edge probability p, transitive closure) with p
   fixed at freeze such that |E[r] − 8/35| ≤ 0.005 (bisection, 10^4
   replicates per step, on a calibration seed root recorded in the frozen
   config and distinct from every other root). Hypothesis H_N: with
   n = 10^4 replicates, the mean paired difference d_MM − d_3 exceeds 4
   paired SEs (SE of the per-replicate difference) in absolute value. Purpose: show the MM–d_3 agreement test has power to
   flag a non-manifoldlike order. Failure of H_N is retained and reported as
   "consistency check uninformative at N=32", not INVALID.

## Hypotheses (to be tested, not assumed)

- H_A3: E[d_3] < D in arm A at every grid N, D = 2, 3.
- H_B3: E[d_3 | C_3>0] > D in arm B for N ≥ N_B3 (some small N_B3), D = 2, 3.
- H_C (main): every cell resolved for both estimators is CONCORDANT.

## Decision rules (proposed, to freeze)

Per (D, arm, N) cell and per estimator E ∈ {MM, d_3}: Δ_E = mean(d_E) − D,
i.i.d. SE. In arm B both means are over the **same** C_3>0 replicates
(matched conditioning, see Arms).

Cell types (r1), 36 cells in total:

- **Deterministic (4):** N=3 in both arms at both D. Here d_3 = 1, and under
  matched conditioning also d_MM = 1, so both estimators are BELOW.
- **Exact (9):** classified from exact laws, with no sampling and no z test.
  - D=2: arm A N ∈ {4,5,6,8} (m ≤ 6 ≤ 9) and arm B N ∈ {4,5,6,8} (N ≤ 9),
    from full S_N enumeration (gate 1).
  - D=3: arm A N=4, analytic (C_3 ∈ {2,4}, R_inner ∈ {0,1}).
- **Stochastic (23):** every other cell.

Family-wise α = 0.01 over the 2 × 23 = 46 two-sided sign tests (both
estimators) ⇒ z = Φ⁻¹(1 − 0.01/92) ≈ 3.6979. ABOVE / BELOW / UNRESOLVED as
in D3-E0. CONCORDANT if both estimators are resolved with equal sign;
DISCORDANT if both are resolved with opposite sign; else UNRESOLVED. The
secondary values (MM | R>0 in arm B and its archived class) are reported in
the same table and do not enter the classification. Also report d_3(E[c_3]),
the Jensen gap, P(C_3=0), and the replicate correlation of (d_MM, d_3).

Outcomes: INVALID (any gate 1–3 fails, budget or provenance failure);
UNDECIDABLE_AT_BUDGET (any stochastic cell UNRESOLVED at N ≥ 4);
otherwise COMPLETE with the per-cell table. Interpretation is fixed now:
any DISCORDANT cell under matched conditioning ⇒ "finite-N bias sign is
estimator-dependent within the chain-abundance family in this flat geometry"
(numerical observation). A difference that appears only against the
secondary MM | R>0 value is attributed to the conditioning event and not to
the estimator;
all CONCORDANT ⇒ "sign pattern shared by k=2 and k=3 abundances" (numerical
observation; not estimator-independence). All cells, failed gates and
negative outcomes are retained; no rerun with larger budget without a new
reviewed protocol.

## Budget, seeds, pilot

One cap for everything (gates, D=2 enumeration, controls, target):
**600 CPU s, 512 MiB RSS** on the executing host; no Lightsail, deployment
or paid API. The largest exact step is enumerating 9! ≈ 3.6·10^5
permutations (arm B N=9; arm A m=9), expected well inside budget — to be
measured by the pilot. Seeds: numpy `SeedSequence`, recorded roots
distinct from all D3-E0 roots; spawn keys (D, arm, N, chunk). A blinded
engineering pilot (≤ 60 CPU s, ≤ 2,000 replicates/cell, own root, no means
recorded) fixes n_c = ⌈(4·SD̂/0.01)²⌉ with a 10^5 floor (arm B counts
C_3>0 replicates). Manifest with code commit, config hash, versions, per-cell
counts/sums/sums of squares, and raw per-replicate (R, C_3) as integers.

## Exclusions

No D=4, no k ≥ 4 abundances, no Poisson-N ensemble, no curved or
non-diamond regions, no midpoint/spectral estimator, no N-to-length
conversion, no claim about any quantum-gravity model.

## Review checklist for the later pass

Verify: the g_3 rationals and its monotone/convex grid check; the arm-A
C_3 identity; invertibility; the Bonferroni count (r1: 23 stochastic cells ×
2 estimators = 46 tests, z ≈ 3.6979; r0 had 32 cells, z ≈ 3.6047);
whether conditioning on C_3>0 vs R>0 is handled adequately for a fair
MM–d_3 comparison; whether the transitive-percolation control is
well-defined and worth its cost; whether the D=2 enumeration range is
sufficient as a positive control. Record PASS/REVISE before implementation.

r2 additionally: check that matched conditioning is justified on principle
(see the disclosure below) and that the exact/deterministic/stochastic cell
partition and the c_3 = 1 boundary rule are complete.

## Revision r1 (2026-11-23)

This revision responds to [review r1](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7095051265).

- **Arm-B comparator.** r0 did not say which MM conditioning drives the
  classification. r1 makes the primary comparison **matched** (both
  estimators on C_3>0). MM | R>0 is secondary and remains the gate-3 tie to
  the archive. The rationale is a matter of principle: the bias-sign
  question is about the estimator, so both estimators must be read on the
  same conditional ensemble. Otherwise the conditioning event (at N=4,
  P(C_3=0) = 0.58 against P(R=0) = 0.04) is confounded with the estimator.
- **Disclosure.** The choice was made **after** the reviewer session had
  computed exact D=2 arm-B values by S_N enumeration (table in review r1).
  - Those values imply that, at D=2 arm B, the r0 rule (against MM | R>0)
    would give DISCORDANT at N=4,5.
  - The r1 rule gives CONCORDANT at N=4,5,8 and DISCORDANT at N=6.
  - The D=2 exact cells are therefore **not blind**. They are deterministic
    consequences of the definitions and are reported as such, not as
    preregistered predictions. Neither rule removes all discordance.
  - **No D=3 K3 quantity has been computed.**
- **Cells.** r1 classifies the exactly computable cells (D=2 enumerable N;
  D=3 arm-A N=4) exactly. The Bonferroni family shrinks to 46 tests,
  z ≈ 3.6979.
- **Boundary.** c_3 = 1 maps to d_3 = 1 explicitly.
- **H_N** now specifies a paired SE, n = 10^4, an E[r] tolerance and its own
  calibration seed root.
- **The constants test is extended.** It adds the boundary rule, the r1
  family size and z, and the D=2 small-N exact arm-B values against the
  archived MM weights. These are design checks, not K3 target data.
