# D2: decision record (prereg v1.0-r3 §6, Issue #4)

**Status:** PROPOSED, not yet reviewed. It becomes binding only after a later-pass review by a different session and a merge to `main`.
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
2. **Choose S by a power argument, before any sampled output.** Per-source ball sizes in random trees do not self-average, and the observed CAY scatter of d̂ at 2²² (sd 0.085) is about 1.7× the §5a model value (0.051). Its 95 % χ² interval, about [0.056, 0.173], excludes 0.051. A Phase-1 preregistration must therefore:
   - estimate, before any sampled output on its gated instances, the noise-only failure probability of each of its gates at the chosen S, using the §5a method (per-source covariance divided by S, inflated by a within-graph design effect, each simulated curve passed through the frozen verdict);
   - where no exact moments exist, measure the per-source variance and design effect on a pilot at a non-gated size with a seed disjoint from the gated seeds, computing ball means and variances only (no d_eff or d̂);
   - report the result under a design-effect envelope of **at least ×3** (the CAY variance ratio implied by the observed sd is ≈ 2.8); at S = 256 on CAY that envelope gives P(G1 passes) ≈ 0.81 (prereg §5a r2), so S = 256 is not automatically sufficient;
   - state the S chosen and the resulting noise-only failure probability.
3. **Known bias at the largest scale.** Because d̂ is taken at the last scale of the plateau run, the finite-size turn-down biases d̂ low: about −0.07 on the exact CAY mean curve (prereg §4), and the UST replicate and pooled means lie 0.03–0.05 below 8/5 (cause untested). A Phase-1 note must report d̂ with this bias stated and must not interpret differences smaller than about 0.05 between graph families of this size.
4. **Report the evaluation scale and the pooled curve.** Report, per replicate, the largest admissible scale and the scale at which d̂ is taken (the CAY review showed they differ in 6/24 replicates), and the pooled-curve verdict and d̂. This separates a noise-driven gate failure from a level or drift failure (prereg §5a).
5. **Run a matched positive control and a null in the same preregistration.** The positive control should be a D2 family at comparable N (or a D1 lattice if the target is lattice-like). The null tests only what it is decided by: the RRT and the D1 random-regular null were decided by the saturation guard, so the plateau criterion has been exercised on a null only by the D1 subdivided binary tree. A slowly growing, super-polynomial null is still untested (D1 note §7). If the target family could resemble such a graph, the preregistration must add a null that exercises the plateau criterion.
6. **Small-scale d_eff is a discreteness effect in every calibrated family.** In every calibrated family d_eff(r) rises toward the intrinsic value at small r: exact CAY mean d_eff(4) = 1.585 against 2 (prereg §4); UST pooled d_eff at L = 1024 is 1.34, 1.44 and 1.52 at r = 4, 8 and 16, against 1.6. Both graphs have a fixed intrinsic dimension. A low d_eff at small r is therefore expected from discreteness alone and is no evidence of short-scale dimensional reduction. This bears directly on Issue #37: any comparison there must separate such corrections from a genuine scale dependence, for example by checking against these calibrated curves at matched r and N.
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
