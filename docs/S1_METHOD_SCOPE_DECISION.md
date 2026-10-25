# S1/S1b method and scope decision for the spectral estimator (Issue #37), proposal v0.1

**Status: ADOPTED decision record.** A later-pass review returned PASS ([record](https://github.com/shaden7/emergence-lab/pull/54#issuecomment-6395192707)), and it was merged via PR #54 at `7281443` on 2026-10-25. The text below is unchanged from the reviewed proposal. The proposed audit prereg ([PR #55](https://github.com/shaden7/emergence-lab/pull/55)) replaces the § 3 χ² bound of 1.29 with an F(15, 176) reference (1.313), because the denominator is estimated. No seed has been drawn for anything proposed here, and no run is authorized.
**Date:** 2026-10-24. **Author:** Director `rd-claude-20261024T0703Z-ce170500`. **Base:** `main` `614902c` (S1b audit merged via PR #53).
**Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37). **Inputs:** [S1 prereg v0.2](SPECTRAL_S1_PREREGISTRATION.md), [S1 pilot NO-GO](experiments/2026-10-17-s1-pilot.md), [S1b prereg v0.2](SPECTRAL_S1B_PREREGISTRATION.md) § 4 ("decide whether redesigning the estimator or dropping this two-family objective is warranted"), and the [S1b run record](experiments/2026-10-23-s1b-run.md) with its [later-pass review](https://github.com/shaden7/emergence-lab/pull/53#issuecomment-6381240253).

This record concerns **instrument diagnosis only**. It says nothing about dimensional reduction, emergent geometry or spacetime.

## 1. What is established, and at what level

**Frozen outcomes (unchanged):** S1 is NO-GO (scoped). S1b is **C-INCONCLUSIVE, U-EQUIVALENT → no S2**.

**Numerical observations.** Annealed d̂_W at W = 128–1024, release `s1b-run-v1`, commit `5c77016`, seed base 2036101701. Levels are nominal and uncalibrated.

| Cohort | d̂_W ± tree-level SE | Literature asymptote |
| --- | --- | --- |
| CAY N = 2¹⁴, 2¹⁶, 2¹⁸ | 1.302 ± 0.016, 1.337 ± 0.020, 1.293 ± 0.019 | 4/3 ≈ 1.333 |
| UST L = 128, 256 | 1.202 ± 0.008, 1.207 ± 0.011 | 16/13 ≈ 1.231 |

The asymptotes are established mathematics (Barlow & Kumagai 2006; Barlow & Masson 2011). They are asymptotic statements and **no finite-t tolerance was preregistered**. The table is therefore descriptive and is not a calibration verdict.

**The precision problem (descriptive, post hoc):**
- The CAY 2¹⁸−2¹⁶ contrast was +0.071 (SE 0.029, 8 trees per size) in the pilot and −0.043 (SE 0.027, 24 trees per size) in S1b. That is a difference of about 2.9 combined SE.
- The S1b SE(D_CAY) was **1.64×** the prereg plug-in value of 0.0167, which had been extrapolated as SE ∝ 1/√n.
- For UST, the observed SE was 0.81× its plug-in value.
- Within S1b, the tree-level summaries are not pathological: |g₁| ≤ 0.35, jackknife/delta ratio ≈ 1.00, excess kurtosis of q̄(1024) between −0.6 and 1.1.

Readings that remain open and untested:
- (a) the 8-tree pilot SE was a chance underestimate;
- (b) a winner's-curse inflation of the pilot contrast;
- (c) the tree-level delta SE misstates the sampling error of the annealed CAY slope at these N;
- (d) a run-specific defect.

Reading (c) matters most, because every further power calculation for CAY rests on that SE.

## 2. Options considered

| Option | What it buys | Cost / risk |
| --- | --- | --- |
| **A. Close the two-family ±0.03 size-equivalence objective at this budget** | Honest terminal record: size stability of the annealed W=128–1024 slope is *not established* for CAY and *observed* for UST | Zero compute. Leaves the spectral estimator uncalibrated for Issue #37 step 3. |
| **B. Symmetric CAY-only equivalence study (S1c)** with fresh seeds | Direct answer at ±0.03 | About 192 trees per size at 2¹⁶ and 2¹⁸ ≈ **220 CPU-min**, using S1b's per-tree cost (29 s and 40 s) and SD. Nominal P(equivalence \| D=0) is ≈ 0.85, but ≈ 0 if the true \|D\| is ≈ 0.04. Power rests on the SE model, which is questioned in (c). |
| **C. New estimator** (quenched per-tree statistic or heat-kernel trace) | Addresses annealed-average sensitivity. Descriptively, S1b's median per-tree slopes for CAY (1.321, 1.321, 1.307) differ from the annealed values by ~0.02. | Needs a new prereg, implementation, review and a pilot. That is multi-week, and its own error model is untested. |
| **D. Error-model audit first** (small, no confirmatory claim) | Discriminates reading (c) from (a)/(b) before any larger spend, and directly decides between B and C | Small budget (§ 3). Uses non-confirmatory engineering seeds only. |

## 3. Proposed decision

1. **Adopt A for the frozen line.** The S1 / S1b two-family size-equivalence objective is closed at this budget as *not established*. There will be no further seeds under the S1b design and no pooling of the pilot with S1b. This is a scope statement, not a negative claim that size dependence exists.
2. **Next step: D, an error-model audit of the tree-level SE for the annealed CAY slope.** It is a separate preregistration plus a small run, reviewed before any seed is drawn. Sketch, to be fixed by that prereg:
   - **Question:** at fixed CAY size, does the between-batch spread of d̂_W match the mean tree-level delta SE?
   - **Discriminating null:** a same-size contrast has true D = 0 *exactly*, so coverage can be checked without a literature value.
   - **Design:** N = 2¹⁴ (≈ 16 s per tree), 16 disjoint batches of 12 fresh-seeded trees with 32 sources each. That is 192 trees ≈ **53 CPU-min**, on the hosted-runner containment path.
   - **Statistic:** R = sd across batches of d̂_W ÷ RMS within-batch delta SE.
   - **Falsification:** R > ≈ 1.29 means the SE model is rejected → go to C.
     - 1.29 is the nominal one-sided 5 % chi-square bound on 15 df under R = 1.
     - Nominal power is ≈ 0.83 at a true R of 1.6 and ≈ 0.47 at 1.3, assuming approximately normal batch estimates. An 8 × 24 split would give only ≈ 0.60 at 1.6.
   - R consistent with 1 means the SE model is not rejected at N = 2¹⁴ → B becomes a defensible, separately preregistered option.
   - **Limitation:** an audit at 2¹⁴ cannot certify the SE at 2¹⁶–2¹⁸.
3. **Issue #37 milestone (2027-03-31):** this decision keeps "undecidable with the available resources" as a live, acceptable outcome for the spectral leg. It does not change the D2 ball-growth calibration already on `main`.

## 4. What would change this proposal

A later-pass reviewer should reject or revise if any of the following holds:
- the batch-SE audit cannot discriminate at the stated budget. Recheck the chi-square power in § 3, and whether 12-tree batch estimates are close enough to normal;
- the S1b run record already contains enough within-run information to answer (c). For example, a split of the 24 trees into disjoint halves gives only 2 batches, which I judge too few, but the reviewer should check;
- closing A conflicts with an obligation in the S1/S1b preregistrations.

## 5. Evidence level and limitations

- This is a decision proposal built on numerical observations at nominal levels. It contains no theorem and no empirical claim.
- The cost figures are extrapolated from one hosted-runner run.
- The R threshold and the batch split are engineering choices to be frozen by the prereg, not here.
