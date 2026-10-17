# S1b — Cost-bounded material-effect replication of the S1 size contrast (Issue #37), preregistration v0.2

**Status: PROPOSED, reviewer-corrected design; no S1b seed drawn, no implementation/run authorized.** This revision responds to the [later-pass REVISE review of v0.1](https://github.com/shaden7/emergence-lab/pull/48#issuecomment-6235832071). A separate later-pass review and tests on the final exact PR head are required before design integration; implementation requires its own review and explicit seed unlock. This is **instrument diagnosis**, not evidence of dimensional reduction, physical spacetime, or a new theorem.

**Date:** 2026-10-17. **Config:** [`configs/spectral_s1b.json`](../configs/spectral_s1b.json). **Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37).
**Basis:** frozen [S1 prereg v0.2](SPECTRAL_S1_PREREGISTRATION.md), [S1 pilot NO-GO](experiments/2026-10-17-s1-pilot.md), [exploratory post-hoc diagnostic](experiments/2026-10-17-s1-pilot-diagnostic.md). This new preregistration does **not** change the S1 outcome or reuse S1 data as S1b test samples.

## 0. Scientific decision and asymmetric scope

The pilot's large-minus-small slope contrast on CAY at W=128–1024 was +0.0706 (tree-level SE 0.02886, 8 independent trees per size). A difference could be finite-size/estimator sensitivity, a generator or sampling defect not captured by existing controls, or chance. The pilot also left UST equivalence unresolved.

**Primary purpose of S1b:** test on fresh seeds whether the CAY contrast is **materially greater than** the engineering margin +0.03 at the preregistered sizes and window, rather than merely positive. This is a **one-direction material-effect replication**, not a balanced proof of equivalence or a newly optimized estimator. The original S1 choice of W=128–1024 was data-informed; possible winner's curse is explicitly acknowledged. The smaller N=2¹⁴ cohort checks shape descriptively, not as a second unadjusted confirmatory test.

**Secondary UST purpose:** estimate its contrast with improved precision and report equivalence if unusually precise; failure to establish UST equivalence will not be interpreted as evidence of a nonzero difference. The two-family equivalence criterion of S1 remains *not achieved*. Neither a CAY null result nor a UST inconclusive result unlocks S2.

Alternatives deferred: substantially more independent trees for a symmetric equivalence design (exceeds this budget), source-allocation/pilot reweighting, a different estimator (quenched source / heat-kernel trace), or stopping the spectral workstream. A 200-CPU-min budget is justified solely for the narrower CAY replication question; an unrevealing outcome triggers a new method/scope decision, not repeated seeds at will.

## 1. Observable and fixed comparison

Unchanged from S1 v0.2 §3: simple random-walk even-time return q_v(t) = [P^(2t)]_vv, uniformly sampled sources without replacement, **annealed** mean across trees and sources before taking logs, window slope d̂_W = −2[ln q̄(hi) − ln q̄(lo)]/ln(hi/lo). Fixed W=(128, 1024), T=4096; killed-ball certified bracket η=10⁻⁴, R initially 64 with doubling, 2×10⁹ edge-step cap per source, unchanged generators (Prüfer CAY; Wilson UST torus).

Primary D_CAY = d̂_W(N=2¹⁸) − d̂_W(N=2¹⁶). Secondary D_UST = d̂_W(L=256) − d̂_W(L=128). Independently seeded **trees** are the sampling units. Tree-level delta-method influence variance and Welch–Satterthwaite two-sided **90% CI** [L,U] follow S1 P3/P5; the 90% CI inside ±0.03 is the ordinary two-one-sided-tests (TOST) equivalence criterion at nominal α=0.05. A one-sided material-positive rule L>+0.03 tests D>+0.03 at nominal one-sided α=0.05 under adequate coverage assumptions. These are **model-based, uncalibrated nominal levels** for heavy-tailed finite-n annealed data, not guarantees.

## 2. Cohorts, controls, fixed seeds

| Family | Sizes | Independently seeded trees per size | Sources per tree | Role |
| --- | --- | ---: | ---: | --- |
| CAY | N={2¹⁴,2¹⁶,2¹⁸} | 24 | 32 | CAY 2¹⁸−2¹⁶ confirmatory; other differences descriptive |
| UST torus | L={128,256} | 48 | 32 | secondary equivalence/contrast descriptive |

Before the first S1b seed, run S1 P0a–P0d engineering controls unchanged; any STOP gate blocks inference. No RRT resampling (already a pilot null). Report q(t=1), P(deg=1) and all S1-compatible windows descriptively; do not make multiplicity-free claims from those comparisons.

Frozen seed base **2036101701**, bootstrap seed **2036101799**, both unused for S1b as of this revision. SeedSequence([seed_base, i_family, i_size, i_rep]) with PCG64; CAY=0, UST=1, indices in size-list order; sources from the same tree-seed child protocol as S1. Draw **only after** separately reviewed implementation and run authorization. Never recycle a partly executed seed tuple. Execute round-robin over replicate index across sizes/families to limit imbalance, but **do not** treat this as a valid optional-stopping adjustment.

## 3. Computation and outcome eligibility

**Fixed full-sample analysis only.** CAY needs exactly 24 complete, valid trees **at each of all three sizes**, UST exactly 48 complete, valid trees at each size. No data-dependent subsampling or replacing unfavorable trees. The implementation should record attempted seeds, COMPLETED/OVER_CAP/PARTIAL status, timings, tree/source counts, and certified errors in a manifest. Missing, censored or OVER_CAP sources are **never** silently dropped. Incomplete per-family sample or any failed numeric control is **BLOCKED / INCONCLUSIVE**, even when its interim CI looks decisive. Primary CAY gate cannot pass on a partial CAY sample, including a completed pair with an incomplete N=2¹⁴ cohort. A complete eligible family can be described even if the other family is blocked, but this never authorizes S2.

Budget: one core, ≤2 GiB externally enforced, no Lightsail, no paid service/network during the experiment. S1 pilot cost per CAY tree: 2¹⁶ ≈82 CPU-s, 2¹⁸ ≈98 CPU-s; 2¹⁴ ≤82 CPU-s is an **unverified projection**. UST: L=128 ≈12.6, L=256 ≈16.5 CPU-s. With fixed n: CAY ≈105 CPU-min, UST ≈23, controls ≈2; ~130 CPU-min projected, **200 total CPU-min absolute stop**, 1.5× each family's projected budget as a secondary STOP. Resource checks and OS limits are required; no automatic extension if an early stop prevents formal classification. Log all completed descriptive data and failures without selective omission.

**Plug-in operating characteristics (assumptions, not observations):** S1 pilot SE(D) CAY 0.028861 and UST 0.042157 at 8 trees/size, extrapolated SE ∝√(8/n), fixed independent normal estimates and symmetric 90%-t half-widths. CAY n=24: SE≈0.01666, half-width≈0.02797; UST n=48: SE≈0.01721, half-width≈0.02859. P(CAY L>0.03 | true D=+0.07)≈**76.5%**, at true D=+0.035 only **8.4%**; P(CAY L>0.03 | D=0)≈0.03%. Thus a negative/undetermined result cannot reliably exclude effects just above 0.03. If *both* true differences were zero, the chance of proving **both** ±0.03 equivalences is only ≈0.63%, so the two-family GO is **not powered**. Analytic audit: [`docs/experiments/s1b_power_audit.py`](experiments/s1b_power_audit.py). Coverage may be worse with unequal Welch df, skew or variance uncertainty. Increasing S within each tree is not assumed cost-equivalent to more independent trees.

## 4. Exact and mutually exclusive outcome classification

For any **eligible complete** family and finite 90% CI [L,U] with L≤U and margin m=0.03, in the following order:
1. **MATERIAL-POSITIVE** iff L>m.
2. **MATERIAL-NEGATIVE** iff U<−m (reported as an unexpected reversed-size effect).
3. **EQUIVALENT** iff L>−m **and** U<m (strict entire containment).
4. **INCONCLUSIVE** otherwise, including intervals entirely above/below 0 but intersecting the margin.

The cases are disjoint mathematically; touching a threshold is INCONCLUSIVE unless another strict condition applies. A positive-sign CI like [+0.010,+0.020] is **EQUIVALENT**, never MATERIAL-POSITIVE. A CI [+0.015,+0.045] is **INCONCLUSIVE**, not proof of a >0.03 effect. Prefix results with C-/U-; a failed family eligibility gate yields **C-BLOCKED** or **U-BLOCKED**, not a calculated confirmatory class. If the finite-n reliability screen fails, return **UNRELIABLE** before applying the CI classification; keep its estimate and interval as descriptive.

**Reliability screen:** any invalid/non-positive q̄, missing certified tolerance/headroom/validity check, nonfinite SE or 90% CI, or degenerate influence variance yields UNRELIABLE. Also report S1 P3 influence skewness and maximal squared share; |g₁|>1.5 or max influence share>0.5 triggers UNRELIABLE. Delete-one-tree jackknife SE >1.25× delta-method SE triggers UNRELIABLE; this 25% cutoff is a **heuristic** and does not validate coverage when it passes. A whole-tree 4096-resample deterministic percentile bootstrap (seed 2036101799) and jackknife/nominal intervals are reported side by side, but not used to change outcome cutoffs after observing results. If headroom at W's hi fails S1's ≥10× per-source floor rule, classify UNRELIABLE; this prevents promoting a known biased window. A mandatory control STOP marks the affected run BLOCKED even if descriptive data exist.

**Consequences for Issue #37:**
- C-MATERIAL-POSITIVE or C-MATERIAL-NEGATIVE: record **replicated material finite-size/estimator dependence at these sizes and this fixed window**, conditional on validity screens, and prioritize a method change or closure of S1 at this budget. No S2 with the current estimator.
- C-EQUIVALENT **and** U-EQUIVALENT: dual size equivalence is *observed on fresh seeds*; an independently reviewed **new S2 preregistration may be drafted** (no S2 seeds unlocked by S1b itself). This is possible but very unlikely under the design's assumed null power.
- All other combinations, including C-INCONCLUSIVE, C-UNRELIABLE, any BLOCKED, and U-INCONCLUSIVE: **no S2**. Record exactly which claim was not established; decide whether redesigning the estimator or dropping this two-family objective is warranted. No automatic repeated replication or assertion of non-equivalence from failure to pass TOST.

The reference deterministic case table and edge-condition tests must pass on the exact implementation head; the run report must include all classification inputs and codes. The pilot and S1b samples are never pooled in the outcome calculation.

## 5. Limitations and staged execution

- New seeds reduce pilot reuse but cannot expose a defect shared by both runs (generator/kernel, stratification, large-t truncation). t=1 and degree controls check only local structure; S1 P0b tests kernels on N≤4096.
- The CAY difference observed post hoc as early as W=8–64 is consistent with source fluctuation but no cause is proven. The claim that N^(3/2) mixing makes this too early for finite-size effects is a **scaling heuristic**, not a finite-N theorem.
- The small equivalence margin is an engineering convention, not an experimentally calibrated tolerance for emergent physics. Nominal Welch coverage and power are not validated for heavy-tailed walks. Statistical classification is **numerical inference**, not mathematical proof.
- After this prereg passes distinct later-pass review, a **separate implementation PR** adds the codepath, seed locks, round-robin scheduler, cost stops, full manifest and synthetic-CI classification tests; exact-head CI/smoke and a new review are required. Then and only then may a **single** controlled S1b run occur with an archived CSV, manifest and independently rechecked arithmetic.
