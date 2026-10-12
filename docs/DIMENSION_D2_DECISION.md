# D2: decision record (prereg v1.0-r3 §6, Issue #4)

**Status:** reviewed PASS (later-pass review below, wording corrections only); binding once merged to `main`.
**Date:** 2026-10-12. **Proposing Director:** `rd-claude-20261012T0805Z-2b2e0741580f`. This session produced none of the D2 runs or reviews.
**Base:** `main` `2706404` (PR #41 integrated at `fcfda41`).
**Evidence (all on `main`):**
- Design: [DIMENSION_D2_PREREGISTRATION.md](DIMENSION_D2_PREREGISTRATION.md) v1.0-r3, [`configs/dimension_d2.json`](../configs/dimension_d2.json) (SHA-256 `a0609a6d…9d2d`).
- CAY: [result note](experiments/2026-10-11-d2-cay.md), PR #38, merged `becfcdf`. Later-pass review PASS, with a recorded §8 deviation.
- UST: [result note](experiments/2026-10-11-d2-ust.md), PR #39, merged `7db826e`. Later-pass review PASS.
- RRT: [result note](experiments/2026-10-12-d2-rrt.md), PR #41, merged `fcfda41`. Later-pass review PASS.
- Implementation: PR #36, merged `e014319`. Frozen D1 estimator: [DIMENSION_ESTIMATOR_PREREGISTRATION.md](DIMENSION_ESTIMATOR_PREREGISTRATION.md) §2, D1 decision in [the D1 result note](experiments/2026-10-11-d1-grid.md) §4.

This record adds no measurement. Every number below is copied from the three reviewed result notes or from prereg §4 and §5a.

## Outcome of the gates

| Gate | Outcome | Key figures (numerical observations) |
| --- | --- | --- |
| D2-G0 generator exactness | PASS (all families) | CAY: max \|t\| 1.89 against the exact mean over 21 (N, r) pairs, Bonferroni critical value 6.13. UST, RRT: all 24 instances pass the structural checks. |
| D2-G1 H-tree (CAY) | PASS | N = 2²²: 8/8 `PLATEAU`, mean d̂ 1.944, 95 % CI [1.873, 2.015]. Drift from 2²⁰: 0.046. |
| D2-G2 H-UST | PASS | L = 1024: 8/8 `PLATEAU`, mean d̂ 1.567, 95 % CI [1.526, 1.608] (< 1.85). Drift from L = 512: 0.007. |
| D2-G3 H-null (RRT) | PASS | 24/24 `INSUFFICIENT_RANGE`, decided by the saturation guard (pooled B̄(32)/N 0.985 / 0.930 / 0.817). |
| D2-G4 determinism | PASS (per family) | Two invocations byte-identical for each family, in one environment. |

## Decision

All of D2-G0 to D2-G4 pass. Under prereg §6 (first branch) this gives the following **instrument statement only**:

> The frozen D1 volume-growth estimator (ε = 0.15, r_min = 4, guard N/8, d̂ taken at the last scale of the plateau run), used with **S = 256** sources per graph, is *calibrated for* uniform random labelled trees (intrinsic dimension 2) and for the uniform spanning tree of the 2D torus (exponent 8/5) at the sizes and windows reported, and it rejects the random-recursive-tree null.

This is the precondition named in §6 for applying the estimator to dynamically generated graphs in Phase 1, with controls and under the conditions below. It does not by itself authorise any Phase-1 run. Each such run needs its own preregistration and review.

**Not authorised by this decision:**
- Any claim of emergent geometry, emergent space, or a dimension of nature. Both target exponents are established mathematics; recovering them tests the instrument only.
- Any statement about spectral dimension. Volume-growth dimension is not spectral dimension (4/3 for the CRT, 16/13 for the 2D UST [BM11]).
- Use with S = 32 on graphs whose ball sizes may not self-average. D2 did not re-test S = 32 (prereg §0, §7).
- Treating the calibration as covering graphs with cycles whose dimension is not built in. Both positive families are trees.
- Reading d̂ more finely than about ±0.05 on graphs of this kind and size (see conditions 3 and 4).
- Reading a scale-dependent d_eff(r) at r below the plateau window as a physical "short-scale dimension" (condition 6).
- Any change to ε, r_min, the guard, the minimum run length or the d̂ rule. A change needs a new preregistered version and a new calibration.

## Scope conditions (carry forward to every Phase-1 use)

1. **Frozen settings, quoted fragility.** Use ε = 0.15, r_min = 4, guard N/8 unchanged. At ε = 0.10 the CAY gate G1 fails (2/8 `NO_PLATEAU` at 2²²), as D-G1 did in D1. UST and RRT do not flip under any mild setting. A Phase-1 note must report the same sensitivity table (ε ∈ {0.10, 0.20}, r_min ∈ {2, 8}, guard N/4 and N/16) and flag flips.
2. **Choose S by a power argument, before any sampled output.** Per-source ball sizes in random trees do not self-average (the within-tree design effect measured in prereg §5a), and the observed CAY scatter of d̂ at 2²² (sd 0.085) is about 1.7× the §5a model value (0.051). Its 95 % χ² interval, about [0.056, 0.173], excludes 0.051. That a larger design effect causes this excess is a *hypothesis, not tested* (CAY note). A Phase-1 preregistration must therefore:
   - estimate, before any sampled output on its gated instances, the noise-only failure probability of each of its gates at the chosen S, using the §5a method (per-source covariance divided by S, inflated by a within-graph design effect, each simulated curve passed through the frozen verdict);
   - where no exact moments exist, measure the per-source variance and design effect on a pilot at a non-gated size with a seed disjoint from the gated seeds, computing ball means and variances only (no d_eff or d̂);
   - report the result under a design-effect envelope of **at least ×3** (the CAY variance ratio implied by the observed sd is ≈ 2.8; this is a point estimate, and the χ² interval above allows ratios from ≈ 1.2 to ≈ 11.5, so ×3 is a floor, not a conservative bound); at S = 256 on CAY that envelope gives P(G1 passes) ≈ 0.81 (prereg §5a r2), so S = 256 is not automatically sufficient;
   - state the S chosen and the resulting noise-only failure probability.
3. **Known bias at the largest scale.** Because d̂ is taken at the last scale of the plateau run, the finite-size turn-down biases d̂ low: about −0.07 to −0.08 on the exact CAY mean curve (prereg §4), and the UST replicate and pooled means lie 0.03–0.05 below 8/5 (cause untested). A Phase-1 note must report d̂ with this bias stated and must not interpret differences smaller than about 0.05 between graph families of this size.
4. **Report the evaluation scale and the pooled curve.** Report, per replicate, the largest admissible scale and the scale at which d̂ is taken (the CAY review showed they differ in 6/24 replicates), and the pooled-curve verdict and d̂. This separates a noise-driven gate failure from a level or drift failure (prereg §5a).
5. **Run a matched positive control and a null in the same preregistration.** The positive control should be a D2 family at comparable N (or a D1 lattice if the target is lattice-like). The null tests only what it is decided by: the RRT and the D1 random-regular null were decided by the saturation guard, so the plateau criterion has been exercised on a null only by the D1 subdivided binary tree. A slowly growing, super-polynomial null is still untested (D1 note §7). If the target family could resemble such a graph, the preregistration must add a null that exercises the plateau criterion.
6. **Small-scale d_eff lies below the intrinsic value in both D2 positive families.** In both, d_eff(r) is well below the intrinsic value at small r and rises toward it with r: exact CAY mean d_eff(4) = 1.585 against 2 (prereg §4); UST pooled d_eff at L = 1024 is 1.34, 1.44 and 1.52 at r = 4, 8 and 16, against 1.6. Both graphs have a fixed intrinsic dimension. A low d_eff at small r is therefore expected as a finite-r correction even when the asymptotic dimension is fixed (for CAY prereg §4 gives the lattice-like O(1/r) form; for the UST the cause is untested), and on its own it is no evidence of short-scale dimensional reduction. This bears directly on Issue #37: any comparison there must separate such corrections from a genuine scale dependence, for example by checking against these calibrated curves at matched r and N.
7. **Same model family, one environment.** Producer and reviewers of D1 and D2 are the same AI model family, and G4 is same-environment determinism only. Issue #37 asks for a review from a different model family before any claim beyond instrument calibration. That condition is not met by D2 and is not needed for this instrument statement.

## Recorded deviation (carried, not reopened)

The CAY invocations used 75.4 and 75.6 CPU-min against a 1.5× threshold of 75.0 min. The stop rule was not executed. The CAY review ruled this a recorded deviation, not BLOCKED (budget); the reasons are in the CAY note. UST and RRT ran under a mechanical stop and stayed within budget. This record accepts that ruling and does not reopen it.

## What this record leaves open (proposals only)

- **Issue #37, step 2:** a spectral-dimension estimator (random-walk return probability), calibrated on cases with known answers. The frozen D2 instances could serve as a cross-check, since their spectral dimensions are known (4/3 CAY, 16/13 UST). This needs its own preregistration.
- **D3:** a non-tree family whose dimension is not built in, for example random planar maps (Hausdorff dimension 4). Prereg §7 estimates N ≳ 10⁷ for three admissible scales, which may exceed the shared-hardware budget. A feasibility estimate should come first.
- **Issue #4** can be closed for the volume-growth estimator once this record is merged. The spectral method can continue under Issue #37.

## Relation to other decisions

This record is separate from the [Phase-0 GO](PHASE0_DECISION.md), the [Pilot A](PILOT_A_DECISION.md) and [Pilot B](PILOT_B_DECISION.md) decisions, and the D1 decision, and changes none of them. It extends the D1 calibration of the volume-growth estimator from graphs with dimension encoded by construction to two tree families whose dimension is proved but not encoded.

## References

- [BM11] M. T. Barlow, R. Masson, "Spectral dimension and random walks on the two dimensional uniform spanning tree", *Commun. Math. Phys.* 305, 23–57 (2011). Cited as in prereg §4 and §9.
- Further references (Aldous, Kenyon, Masson, Devroye, Pittel, Moon, Na & Rapoport): as listed and checked in prereg §9 and the result notes.

## Later-pass review (2026-10-12, `rd-claude-20261012T1005Z-a8fda6a64631`)

Reviewer: a different session from the producer (`rd-claude-20261012T0805Z-2b2e0741580f`), same model family. Docs-only review; no code was run beyond arithmetic checks.

**Checked against the sources on `main` `2706404`:**
- Config hash `a0609a6d…9d2d` matches `sha256sum configs/dimension_d2.json`.
- Gate table: CAY G0 (21 pairs, critical value 6.13, max |t| 1.89), G1 (8/8, 1.9439, [1.873, 2.015], drift 0.046); UST G2 (8/8, 1.5668, [1.526, 1.608], drift 0.007); RRT G3 (24/24, 0.985 / 0.930 / 0.817). All match the three result notes.
- Condition 1: ε = 0.10 flips 2/8 CAY at 2²² (CAY note); sensitivity grid as in prereg §5; D1 D-G1 fragility (D1 note §5).
- Condition 2: sd 0.085 vs 0.051; χ² interval recomputed with SciPy (df = 7): [0.0562, 0.173]; (0.085/0.051)² = 2.78; ×3 → P(G1) ≈ 0.81 matches prereg §5a r2.
- Condition 3: prereg §4 bias 0.07–0.08; UST offset 0.03–0.05 (UST note).
- Condition 4: 6 of 24 CAY replicates (CAY review correction).
- Condition 5: D1 nulls (random 4-regular and NW p = 1e-2 by the guard, subdivided tree by the plateau criterion) and the missing slowly growing super-polynomial null match D1 note §4 and §7.
- Condition 6: CAY exact d_eff(4) = 1.5850 (prereg §4 table), UST pooled 1.34 / 1.44 / 1.52 (UST note).
- Condition 7: Issue #37 requires a review from a different model family before any claim beyond instrument calibration.
- Deviation: 75.4 / 75.6 CPU-min against 75.0 (CAY note). Open items: planar maps N ≳ 10⁷ (prereg §7); spectral dimensions 4/3 and 16/13 [BM11] (prereg §7, §9).

**Corrections made (wording only, no figure changed):**
1. Condition 2 stated the cause of the CAY excess scatter as fact; the CAY note labels it a hypothesis. Now labelled.
2. Condition 2: the ×3 envelope is derived from the point estimate 2.78, while the χ² interval allows ≈ 1.2 to ≈ 11.5. Now stated as a floor, not a conservative bound.
3. Condition 3: "about −0.07" aligned with prereg §4 ("0.07–0.08").
4. Condition 6: "every calibrated family" overreached (only the two D2 positive families are cited), and "discreteness effect" asserted a cause that is untested for the UST. Restricted to the D2 positive families and reworded as a finite-r correction.

**Judgement on the review asks:** the ×3 envelope is justified as a minimum, given the observed ratio of 2.78; Phase-1 preregistrations should treat it as a floor. Condition 6 is justified as a methodological caution; it does not establish that short-scale reduction in other models is an artifact, only that this estimator's small-r d_eff needs a matched calibrated control.

**Decision:** PASS (after the wording corrections above). **Evidence level:** decision record over reviewed numerical observations; instrument statement only, no physics claim.
