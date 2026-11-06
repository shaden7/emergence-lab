# CS0 — Myrheim–Meyer ordering-fraction calibration on causal sets (PROPOSED, v0.2)

**Status: PROPOSED preregistration + scope decision, not a run authorization.** Proposed 2026-11-06 by Director `rd-claude-20261106T0803Z-c7f85c29`. No gated seeds have been drawn and no gated data exist. Execution requires (1) a later-pass review of this document and of `src/emergence_lab/causal_set_mm.py` at an exact commit, then (2) a separate versioned run authorization that freezes the seed entropy. This document is AI-authored; its review is AI-mediated.

## 1. Scope decision (Issue #37)

**Decision proposed: DEFER the random-tree paired D2/spectral pilot; do not declare UNDECIDABLE yet.**

- Evidence for deferral (process observation, not a physics result): the paired pilot has been on HOLD since 2026-11-05 03:22Z ([main 3dc3df6](https://github.com/shaden7/emergence-lab/commit/3dc3df6)); the exit items listed in `docs/RESEARCH_STATE.md` remain unfrozen. The lock-branch history shows 16 further Director lease acquisitions between that commit and this proposal, none of which wrote to `main`, Issue #37 or a PR.
- Issue #37's *robust* criterion requires ≥2 **model classes**. Random trees are an estimator-calibration family with known, mutually different volume/spectral limits; even a perfect tree comparison cannot answer the guiding question alone. A second family is required in every branch of the decision tree.
- Issue #37 order-of-work item 3 names causal sets sprinkled into 2D/4D Minkowski space, and `docs/LITERATURE_REVIEW_EMERGENT_SPACETIME_2026-10-09.md` (section on Myrheim–Meyer) already proposes this calibration with chain/antichain/layered nulls.
- The tree line is preserved: C0-v2 PASS, S1/S1b and D2 decisions are unchanged. It may be resumed by freezing the HOLD exit items. If the 2027-03-31 milestone approaches with the line unresolved, record UNDECIDABLE-under-resources for it explicitly.

## 2. Question

Is the Myrheim–Meyer (MM) ordering-fraction estimator a correctly implemented, finite-N-calibrated instrument for the dimension of a causal set sprinkled into a **given** flat Alexandrov interval, and does it fail detectably or silently on non-manifold-like partial orders?

This is instrument calibration. The dimension D is put in by construction, so a PASS says nothing about emergent spacetime (`docs/RESEARCH_DIRECTOR.md`, substrate neutrality).

## 3. Definitions and analytic references

- **Assumption/definition.** A causal set is represented as a strict partial order on N elements. R is the number of comparable unordered pairs, and the ordering fraction is r = R / C(N,2).
- **Established result** (Myrheim 1978; Meyer 1988; review: Surya 2019, Living Rev. Relativ. 22:5, [DOI](https://doi.org/10.1007/s41114-019-0023-1)). For two points drawn i.i.d. uniformly from a D-dimensional flat causal diamond (D includes time), P(related) = r_D = Γ(D+1)Γ(D/2) / (2Γ(3D/2)). This gives r_2 = 1/2, r_3 = 8/35 and r_4 = 1/10.
- **Elementary consequence (proved here by linearity of expectation).** Under fixed-N i.i.d. sampling, E[r] = r_D **exactly for every N ≥ 2**, because every pair has the same relation probability. The gates are therefore placed on r, which is unbiased. d_MM = r_D⁻¹(r) is nonlinear and biased at finite N, so it is reported only descriptively.
- **Elementary results for the nulls** (proved here):
  - Total order (chain): r = 1.
  - Antichain: r = 0, which is out of range. It must not be read as "high dimension".
  - Two-layer order with link probability p: E[r] = p·a·b / C(N,2), with a = ⌊N/2⌋ and b = N − a.
  - Random k-order (intersection of k independent uniform linear orders): E[r] = 2^(1−k). For k = 2 it has the same distribution as the D = 2 diamond in light-cone coordinates. For k ≥ 3 it is **not** a flat-diamond sprinkling, yet it gives a finite non-integer d_MM. The exact inverse values are d_MM(1/4) ≈ 2.889 for k = 3 and d_MM(1/8) ≈ 3.734 for k = 4 (closed-form arithmetic, not data). This is the adversarial null.
- **Sampling.** Points are drawn by rejection from the bounding box of |t| + |x| ≤ 1/2, conditioned on N. This is not an unconditioned Poisson process. Poisson-N variation is out of scope.

## 4. Design (frozen values proposed for review)

| Item | Proposed value |
| --- | --- |
| Positive controls | Flat diamond, D ∈ {2, 3, 4}; N ∈ {128, 256, 512, 1024}; 30 independent realizations per (D, N) cell (12 cells, 360 orders) |
| Nulls | For each N above, 30 realizations each of: two-layer p = 0.5; random 3-order; random 4-order. Plus one exact chain and one exact antichain per N |
| Seeds | `numpy.random.SeedSequence(entropy=E, spawn_key=(family_index, D_or_k, N, rep))`. E is frozen only in the run authorization, never chosen after inspecting data |
| Observable | r per realization; d_MM per realization and d_MM(mean r) (descriptive); classification IN_RANGE / TOTAL_ORDER / OUT_OF_RANGE |
| Uncertainty | Realizations are independent, so the standard error is SE = sd(r)/√30. No autocorrelation arises because there is no Markov chain |
| Implementation | `emergence_lab.causal_set_mm` at the reviewed exact commit; every generated order passes the exact partial-order check |

## 5. Gates and falsification

- **G0, exactness.** All unit tests pass at the exact commit, including the analytic time and radial marginal checks of D = 3, 4 sprinkling. Every order passes `check_partial_order`. Every sprinkled point lies inside the diamond. Chain gives TOTAL_ORDER with d = 1. Antichain gives OUT_OF_RANGE.
- **Multiplicity scope (v0.2, corrected after the [later-pass REVISE](https://github.com/shaden7/emergence-lab/pull/66#issuecomment-6681691664)).** The stochastic mean-tests form one family of **24 cells**: 12 positive-control cells (G1) and 12 null cells (G3: two-layer, 3-order and 4-order at each of 4 values of N). Each cell uses t = (mean r − E[r]) / (sd(r)/√30) with 29 degrees of freedom. Reject a cell if |t| > c, where c = t₂₉ upper quantile at 0.05/(2·24) = **3.3806** (Bonferroni, nominal family-wise 5%).
  - *Correction of v0.1:* v0.1 claimed a 3·SE rule had 0.27% per cell and about 3% family-wise over 12 cells. That treated the statistic as N(0,1). Under t(29), P(|t| > 3) ≈ 0.0055 per cell, giving ≈ 6.4% over 12 independent cells and ≈ 12.4% over 24. The v0.1 figures were wrong and are withdrawn.
  - *Caveat:* the t-reference assumes approximately normal realization-level r. In fact r is bounded and may be skewed at small N or high D, so the 5% is a nominal operational error rate, **not a guarantee**. A null-calibrated Monte Carlo check of the false-alarm rate is deferred; it is not part of CS0.
- **G1, unbiasedness on positive controls.** All 12 positive-control cells satisfy |t| ≤ 3.3806.
- **G2, discrimination.** At N = 1024, the mean r of each pair of positive-control dimensions must differ by more than 6× the combined SE.
- **G3, null exactness.** All 12 null cells satisfy |t| ≤ 3.3806 against their exact E[r].
- **Predeclared expected limitation (not a gate).** The 3- and 4-orders are expected to yield finite, non-integer d_MM in the IN_RANGE class. CS0 therefore cannot certify manifold-likeness. Every CS0 report must state that MM alone does not distinguish a flat-diamond sprinkling from a random k-order. Any later causal-set dimension claim requires a second, independently calibrated discriminator, such as interval-abundance or midpoint-scaling consistency.
- **Outcomes:**
  - **PASS:** G0–G3 all hold.
  - **FAIL:** any of G0–G3 is violated. Record it and do not rerun to hide it. Classify the failure as follows:
    - **G0 (exact-check) failure** demonstrates an implementation defect.
    - **G1/G2/G3 (stochastic) failure** is a *stochastic gate failure*. It is expected with roughly nominal 5% probability even for a correct implementation, so it is not by itself proof of a defect. The instrument is still not accepted. Diagnosis needs a new reviewed authorization with fresh entropy, while the failed run stays in the record.
  - **INCOMPLETE:** a resource or provenance stop. No automatic retry.

## 6. Budget and stop conditions

- **Development timing** (non-gated observation, this cloud host, Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1): one N = 1024, D = 4 sprinkle plus relation matrix took 0.041 s CPU, and the exact order check took 0.036 s CPU.
- **Projection, not a bound:** the whole grid (about 840 orders) is projected at under 2 CPU-minutes.
- **Hard caps for the authorized run:**
  - 10 CPU-minutes total.
  - 1 GiB peak RSS.
  - 50 MB of output.
  - Exceeding any cap means INCOMPLETE.
- **Execution location:** CI or a local runner only. **Not on the shared Lightsail host.**
- **Missing component (blocks authorization).** This PR contains only the reference library and tests, not a gated runner. Before any run authorization, a separately reviewed runner must:
  - enforce the aggregate CPU, RSS and output caps above in a supervised child process;
  - write a durable INCOMPLETE manifest on any cap breach or setup or provenance failure;
  - refuse to run unless the checkout is clean at the pinned exact commit.
  The run authorization must pin that commit and the seed entropy E.

## 7. Artifacts and provenance

- Per-realization CSV with columns family, D_or_k, N, rep, spawn_key, R, r, d_mm, classification.
- `manifest.json` with code commit, blob hashes of `causal_set_mm.py`, config, seed entropy, Python/NumPy/SciPy versions, CPU/RSS/bytes and SHA-256 of all outputs.
- An independent recheck script recomputes r from stored R and verifies the closed-form references.
- Results are retained whether PASS or FAIL.

## 8. Relation to the guiding question, and next step (not authorized)

CS0 calibrates a **global** dimension instrument only. It has no scale dependence and cannot address dimensional reduction.

If CS0 passes, the proposed CS1 applies MM to causal sub-intervals of varying proper-time extent inside D = 4 sprinklings. That yields a scale-resolved curve whose flat-space expectation is constant, up to discreteness effects at small sub-interval occupancy. CS1 would be compared with the same nulls, and with the literature on causal-set dimensional reduction and spectral dimension cited in Issue #37 (arXiv:1506.08775, arXiv:1507.00330), audited before freezing.

Any small-scale deviation in CS1 must first be tested against the finite-occupancy bias of d_MM. That bias is predictable from the exact unbiasedness of r combined with the nonlinearity of the inverse, so a deviation is not evidence of dimensional reduction until it survives that test.
