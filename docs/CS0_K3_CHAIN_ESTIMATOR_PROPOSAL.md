# K3-E0/M0 — second causal-set dimension estimator (3-chain abundance) on the D=2/D=3 endpoint/no-endpoint arms (design r3, PROPOSED, NOT frozen)

Status: **design proposal only.** Not preregistered/frozen, not authorized,
not implemented beyond a constants test, not run. No D=3 K3 data exist.
Merging this file would integrate a design for later-pass review; it is not a
result.
Author r0: Director `rd-claude-20261122T080245Z-85f98e1f` (2026-11-22).
Revision r1: Director `rd-claude-20261123T080344Z-746a46c8` (2026-11-23),
addressing [later-pass review r1 (REVISE)](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7095051265).
See "Revision r1" at the end of this file.
Revision r2: Director `rd-claude-20261124T080327Z-99323fda` (2026-11-24),
addressing [later-pass review r2 (REVISE)](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7125763242).
See "Revision r2" at the end of this file.
Revision r3: Director `rd-claude-20261125T080251Z-6b4ea485` (2026-11-25),
addressing [later-pass review r3 (REVISE)](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7156580424).
See "Revision r3" at the end of this file. r3 is self-authored by the r3
reviewer session and needs a later-pass review r4 by a different session.
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
form a chain in some order). **Primary question (r2): at fixed input
D ∈ {2,3}, in arms A and B, does d_3 have the same finite-N bias-sign
*pattern* over the grid as MM?** Here the pattern is (i) the sign at the
largest grid N and (ii) the number and direction of sign changes over N. The
answer per (D, arm) is PATTERN-CONSISTENT, PATTERN-DIFFERENT or UNDETERMINED
(rules below). Per-cell CONCORDANT / DISCORDANT / UNRESOLVED is reported as a
descriptive table.

The r0/r1 per-cell form ("same sign at **every** grid N?") is already
answered **no** by exact, non-blind D=2 cells: arm B N=6 is DISCORDANT (see
Revision r2). It is therefore not a preregistration target.

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
- A 91-point numerical grid in [1,10] shows sampled values of g_3 decreasing
  and convex. This is a finite-grid observation, not a proof or interval
  certificate on the continuum. No global convexity claim is made here.
  The Jensen inequality E[d_3(c_3)] ≥ d_3(E[c_3]) is valid only if d_3 is
  convex on the support of c_3; that condition has not been proved or
  interval-certified. The Jensen gap is therefore exploratory/descriptive
  only and is not used by any gate or sign classification.
- Arm B: E[c_3] = g_3(D) for every N ≥ 3 (linearity), but
  E[c_3 | C_3>0] > g_3(D) whenever P(C_3=0) > 0. Conditioning changes the
  ensemble; any additional Jensen-gap interpretation is conditional on the
  unproved convexity above. The sign remains the target.
- Arm A: E[c_3] = (binom(m,3) g_3 + 2 binom(m,2) f + m)/binom(N,3) > g_3 at
  every grid N for D = 2,3. This is an exact mean-abundance identity; it does
  not by itself determine E[d_3] − D. No global monotonicity or convexity
  claim, inverse-mean sign inference, or Jensen bound is used by the gates.
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
   INVALID. **r2:** the re-measured cell is classified with the same z. Only
   a resolved **opposite** sign is INVALID. An UNRESOLVED re-measurement is
   reported and is not INVALID. The smallest archived D=3 margin is cell B5,
   at about 15.6 SE with n = 10^5. This ties the comparison to integrated evidence instead of a
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
- ~~H_C: every cell resolved for both estimators is CONCORDANT.~~ Already
  refuted, exactly and not blind, at D=2 arm B N=6 (Revision r2). Retained
  only as a record.
- H_P (main, r2): PATTERN-CONSISTENT in every (D, arm) at D=3. D=2 is
  reported the same way, but its N ≤ 8 cells are not blind.

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

**Sign pattern (r2, primary).** For each (D, arm, estimator), take the
per-cell labels over the grid N = 3, …, 32 in order. Deterministic and exact
cells contribute their exact labels. Let s be the subsequence of resolved
labels, with UNRESOLVED removed. Define:

- (i) the terminal sign: the label at N = 32;
- (ii) the change signature: the ordered list of sign changes in s (for
  example "B→A once"), each with its **crossover bracket**, i.e. the two
  adjacent resolved grid N between which the change occurs.

Per (D, arm):

- **UNDETERMINED** if, for either estimator, the N = 32 cell is UNRESOLVED,
  or (r3) for two consecutive resolved labels a, b at grid positions i < j:
  a = b and j − i ≥ 2 (one or more UNRESOLVED cells between equal signs), or
  a ≠ b and j − i ≥ 3 (two or more UNRESOLVED cells between opposite signs).
  Either gap could hide a pair of sign changes. A single UNRESOLVED cell
  between opposite signs hides none (exactly one change) and is allowed.
- Otherwise **PATTERN-CONSISTENT** if both estimators have the same terminal
  sign and the same change signature, counted and directed, with the
  brackets allowed to differ.
- Otherwise **PATTERN-DIFFERENT**.

The pattern is a function of the 46 per-cell sign tests and the exact
labels, so the family-wise α = 0.01 bound carries over and there is no extra
multiplicity. DISCORDANT cells that lie strictly between the two estimators'
crossover brackets are reported as a **crossover shift**, not as a pattern
difference.

Outcomes:

- INVALID: any gate 1–3 fails, or a budget or provenance failure.
- UNDECIDABLE_AT_BUDGET (r2): any (D, arm) is UNDETERMINED. A single
  UNRESOLVED cell next to a crossover does not by itself make the run
  undecidable.
- Otherwise COMPLETE, with the per-(D, arm) pattern table and the per-cell
  table.

Interpretation is fixed now:

- Any PATTERN-DIFFERENT (D, arm) ⇒ "the finite-N bias-sign pattern is
  estimator-dependent within the chain-abundance family in this flat
  geometry" (numerical observation).
- All PATTERN-CONSISTENT ⇒ "the sign pattern is shared by the k=2 and k=3
  abundances; crossover positions as reported" (numerical observation, not
  estimator-independence).
- A difference that appears only against the secondary MM | R>0 value is
  attributed to the conditioning event, not to the estimator.
- Because the D=2 N ≤ 8 cells are not blind, the blind content of the
  verdict is D=3, plus the D=2 cells at N ≥ 12.

All cells, failed gates and negative outcomes are retained; no rerun with
larger budget without a new reviewed protocol.

## Budget, seeds, pilot

One cap for everything (exact enumeration, gate 1, pilot, negative control
and target): **600 CPU s and 512 MiB RSS** on the executing host. The
engineering pilot is included in that cap and has a **60 CPU s sub-cap**.
No Lightsail, deployment or paid API. The largest exact step is enumerating
9! ≈ 3.6·10^5 permutations (arm B N=9; arm A m=9); its CPU time is measured
and charged to the same cap. Seeds use numpy `SeedSequence`, with recorded
roots distinct from all D3-E0 roots and spawn keys (D, arm, N, chunk).

The blinded engineering pilot uses its own seed root and at most **2,000
total draws per non-deterministic target cell** (not 2,000 accepted positives),
within 60 CPU s. Its separate output contains only, for each (D, arm, N):
`SD_MM`, `SD_d3`, total draws, accepted `C_3>0` draws, and CPU seconds.
It contains no means, sums, per-replicate values, sign labels or target
outcomes. In arm A all draws are accepted. In arm B, both SDs are calculated
on the **same matched `C_3>0` subset** used for the primary MM–d_3
comparison; MM conditioned only on `R>0` remains secondary and does not
enter sizing. If a cell has too few accepted draws to estimate both SDs, or
its one-sided 97.5% Clopper–Pearson lower bound `p_L` for `P(C_3>0)` is zero, sizing
fails and no target run starts.

For each non-deterministic cell, the shared target is
`n_c = max(10^5, ceil((4·max(SD_MM, SD_d3)/0.01)^2))` **accepted
replicates**. This is a pilot-based planning target for a four-SE
half-width of 0.01 for both estimators, not a confidence bound on the unknown
target SD. The realized target SDs and SEs are computed from the target sample
and used in the frozen classification. Arm A requires `n_c` total
draws. For arm B, let `k` be the pilot's accepted count out of `n_p` total
draws. Set `p_L = Beta^{-1}(0.025; k, n_p-k+1)` (and `p_L=0` if `k=0`),
the exact one-sided 97.5% Clopper–Pearson lower bound for the acceptance
probability. The planned total-draw limit `N_total` is the smallest integer
`n` for which `Pr[Binomial(n, p_L) >= n_c] >= 0.975`. This allows for
both uncertainty in the pilot acceptance estimate and binomial variation
in the target draws: by a union bound, the probability that `p_L <= p`
and that `N_total` draws yield at least `n_c` accepts is at least 95%,
assuming independent pilot/target draws with a stable acceptance
probability.
The runner stops when `n_c` accepted draws are obtained or `N_total` total
draws are reached. If the accepted count is still short at that limit, the
cell is INVALID and no target verdict is issued. Both attempted and accepted
counts are reported. The pilot's SDs and acceptance estimate are used only
for sizing, never for the target sign classification.

**Gate 1 count convention.** The D=2 positive-control Monte Carlo uses
`10^4 total draws per (arm, N) cell`, not `10^4` accepted positives.
For arm B, `d_MM` (primary) and `d_3` means and their SEs use only the
matched accepted `C_3>0` subset; `P(C_3=0)` uses all total draws, and
secondary MM `| R>0` is reported separately. For arm A, all total draws
are accepted. Gate-1 counts are never mixed into target data.

Gate 1 now covers **every non-deterministic N for which exact permutation
enumeration is feasible in each arm**: arm B N = 4, 5, 6, 7, 8, 9; arm A
N = 4, …, 11. The ranges differ because arm B enumerates N points, whereas
arm A enumerates m = N−2 interior points. The larger arm-A range is therefore
not a selective omission; all off-grid enumerable cells are included. These
are D=2 controls only and do not enter the target classification.

Before target execution, the runner projects target CPU time from each cell's
pilot seconds per total draw and its planned total-draw count. It measures
exact enumeration, gate 1, pilot and negative-control time separately, then
requires `measured_pre_target_CPU + 1.25 × projected_target_CPU ≤ 600 s`.
If this preflight fails, no target starts and the outcome is INVALID (budget
gate failed). The runner also stops at the hard 600 CPU s / 512 MiB limits,
retains partial outputs, and reports INVALID rather than silently dropping
cells. The target manifest records code commit, config hash, versions,
per-cell counts/sums/sums of squares and raw per-replicate (R, C_3) integers;
the blinded pilot artifact remains separate and restricted as specified
above.

## Exclusions

No D=4, no k ≥ 4 abundances, no Poisson-N ensemble, no curved or
non-diamond regions, no midpoint/spectral estimator, no N-to-length
conversion, no claim about any quantum-gravity model.

## Review checklist for the later pass

Verify: the g_3 rationals and the scope of its finite-grid monotone/convex
check (do not infer a continuum theorem); the arm-A C_3 identity; invertibility;
the Bonferroni count (r1: 23 stochastic cells × 2 estimators = 46 tests,
z ≈ 3.6979; r0 had 32 cells, z ≈ 3.6047);
whether conditioning on C_3>0 vs R>0 is handled adequately for a fair
MM–d_3 comparison; whether the transitive-percolation control is
well-defined and worth its cost; whether the D=2 enumeration range is
sufficient as a positive control. Record PASS/REVISE before implementation.

r2 additionally: check that matched conditioning is justified on principle
(see the disclosure below) and that the exact/deterministic/stochastic cell
partition and the c_3 = 1 boundary rule are complete. (Done in review r2:
both pass.)

r3 additionally: check that the r2 sign-pattern rule (terminal sign, change
signature, UNDETERMINED cases) is well-defined, not tuned to the known D=2
cells beyond what is disclosed, and that the UNDECIDABLE rule cannot be
gamed by budget choice. (Done in review r3: the UNDETERMINED rule was
incomplete and is fixed in r3. Tuning and budget gaming pass.)

r4 additionally: check that the r3 UNDETERMINED rule is complete (every
labelling it accepts has a unique change signature over all fillings of its
UNRESOLVED cells), and that the gate-1 MC set and pilot schema are adequate.

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

## Revision r2 (2026-11-24)

This revision responds to [review r2](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7125763242).

- **The headline was predetermined.** The exact D=2 arm-B values under
  matched conditioning (independently re-derived in review r2) are:

  | N | E[d_MM \| C_3>0] | E[d_3 \| C_3>0] | cell |
  |---|---|---|---|
  | 4 | 1.52795 (B) | 1.59389 (B) | CONCORDANT |
  | 5 | 1.78605 (B) | 1.88108 (B) | CONCORDANT |
  | 6 | 1.92107 (B) | 2.02906 (A) | DISCORDANT |
  | 8 | 2.02070 (A) | 2.11941 (A) | CONCORDANT |

  The N=6 cell alone refutes the r1 per-cell H_C and triggers its fixed
  interpretation before any D=3 data exist, so the r1 rule could not change
  its own headline. One-cell discordance between two crossovers is also
  generic. Here MM crosses in (6, 8) and d_3 in (5, 6).
- **Primary target changed to the sign pattern per (D, arm).** The pattern
  is the terminal sign at N=32 plus the change signature. Per-cell
  concordance is now descriptive. On the known D=2 cells the two estimators
  have the same change signature so far (MM B,B,B,A; d_3 B,B,A,A at
  N = 4, 5, 6, 8; arm A all B for both at N = 3–8). The verdict therefore
  still depends on blind cells (D=3 and D=2 N ≥ 12).
- **Disclosure.** This rule was chosen with the D=2 N ≤ 8 exact cells
  known, as in r1. The "terminal sign + change signature" form was chosen
  because it is the coarsest description that separates "crossover shift"
  from "different pattern". It was not fitted to make D=2 come out
  consistent: D=2 at N ≥ 12 is still blind for d_3 and for matched MM.
  **No D=3 K3 quantity has been computed.**
- **Gate 3:** only a resolved opposite sign is INVALID; an UNRESOLVED
  re-measurement is reported.
- **UNDECIDABLE_AT_BUDGET** now depends on whether the pattern can be
  determined, not on every cell.
- **The constants test is extended** with the D=2 arm-B N=8 and arm-A
  N = 4, 5, 6, 8 exact values and the sign-pattern rule applied to the
  exact D=2 cells. These are design checks, not K3 target data.

## Revision r3 (2026-11-25)

This revision responds to [review r3](https://github.com/shaden7/emergence-lab/pull/86#issuecomment-7156580424).

- **UNDETERMINED rule completed.** The r2 rule did not cover two or more
  consecutive UNRESOLVED cells between opposite signs. The r2 test function
  returned PATTERN-CONSISTENT for MM `BBBUUAAAA` vs d_3 `BBBBBAAAA`. But
  `BBBABAAAA` is a compatible MM truth with three changes, so the correct
  answer is UNDETERMINED. The rule now reads as above. The fix only adds
  UNDETERMINED cases. It does not change any verdict on fully resolved
  sequences or on the known D=2 cells (no D=2 exact cell is UNRESOLVED).
- **Gate 1 MC set (clarification).** Exact cells are classified from the
  exact laws only. Gate 1 additionally draws Monte Carlo at every
  enumerated N (arm B N = 4, 5, 6, 8, 9; arm A N = 4, …, 11), with
  n = 10^4 replicates per N on the gate seed root, and compares the MC mean
  of d_MM, the MC mean of d_3 and P(C_3=0) with the exact values within 4 SE.
  These draws never enter the target classification.
- **Pilot blinding (requirement for the implementation PR).** The pilot
  output schema is restricted, in code, to per-cell SDs, counts and timings.
  It writes no means or labels.
- **No D=3 K3 quantity has been computed.**


## Revision r4 (2026-11-25)

This revision responds to [later-pass review r4](https://github.com/shaden7/emergence-lab/pull/86#pullrequestreview-6065253424).

- **Shared pilot sizing is explicit.** The blinded pilot emits separate `SD_MM` and `SD_d3` per cell. The shared target uses their maximum, so the pilot-based four-SE 0.01 planning target covers both estimators on the matched sample; realized target SEs determine classification.
- **Matched conditioning and count semantics are explicit.** In arm B both SDs and both primary means use the same `C_3>0` replicates. Pilot and gate-1 budgets are stated as total draws; the target `n_c` is accepted positive replicates. Both total and accepted counts are retained. Arm-B total draws use an exact one-sided 97.5% Clopper–Pearson lower bound plus a 97.5% binomial completion tail (at least 95% combined assurance by union bound). The secondary MM `|R>0` result is excluded from sizing.
- **Gate-1 enumeration is normalized.** Every non-deterministic D=2 cell in the exact-enumerable range is included: arm B N=4…9 and arm A N=4…11. The asymmetry follows from enumerating N points versus N−2 interior points, not from selective omission.
- **CPU feasibility is preregistered.** Pilot (≤60 CPU s), exact enumeration, gate 1, negative control and target share the 600 CPU s cap. A 1.25× target-runtime projection is checked before target execution; a failed budget gate prevents the run.
- **Jensen wording is qualified.** The 91-point convexity check remains numerical only. No global convexity theorem or Jensen bound is claimed, and the Jensen gap is not used by any gate or classification.
- The constants-test helper docstring now names the r3 rule. The exhaustive 3^8 finite-grid check remains the stated scope; no arbitrary-grid theorem is claimed.
- **No D=3 K3 quantity has been computed.** This remains a design revision only; it is not a frozen protocol, authorization, implementation or result.

This revision was authored by the r4 review session. A later-pass review by a different session is required before merge.
