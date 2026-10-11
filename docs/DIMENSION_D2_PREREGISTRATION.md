# D2 — out-of-sample test of the frozen D1 dimension estimator on graphs whose dimension is not built in (Issue #4), preregistration v1.0-r2

**Status:** PROPOSED DESIGN. No implementation exists, and no ball count, d_eff value or verdict has been computed on any sampled instance of a D2 family. The design freezes when it is merged to `main`; any later change to a preregistered parameter needs a new version and an explicit deviation note.
**Date:** 2026-10-11. **Base:** `main` `65d2ce9` (D1 decision integrated via PR #34). **Issue:** [#4](https://github.com/shaden7/emergence-lab/issues/4). **Config:** [`configs/dimension_d2.json`](../configs/dimension_d2.json).
**Author:** Director session `rd-claude-20261011T095635Z-d05fc0` (v1.0). **r1:** session `rd-claude-20261011T115603Z-1ed1ef`, applying the REVISE findings of the later-pass review by `rd-claude-20261011T105556Z-58dd0f` (see §10). **r2:** session `rd-claude-20261011T125558Z-220239`, a check of r1 that corrects one power figure in §5a (text and check scripts only; see §10). A check of r2 by a further session is required before merge.

## 0. What this is and is not

- **It is** an out-of-sample test of the D1 instrument (the dyadic volume-growth estimator of [DIMENSION_ESTIMATOR_PREREGISTRATION.md](DIMENSION_ESTIMATOR_PREREGISTRATION.md) §2, frozen at ε = 0.15, r_min = 4, guard N/8; D1 used S = 32 sources, D2 uses **S = 256** (declared deviation, §2 and §5a)). It uses two graph families whose large-scale intrinsic dimension is **not put in by an embedding or a lattice**, but is a **proved** property of the random structure:
  - the uniform random labelled tree on N vertices, intrinsic volume-growth dimension 2;
  - the uniform spanning tree (UST) of the 2D torus, intrinsic volume-growth exponent 8/5.
- **It is not** a discovery of emergent space. Both exponents are established mathematics (§4). Recovering them tests the instrument; it says nothing about nature. Trees are a relational test bed, not an ontological proposal ([REPRESENTATION_STRATEGY.md](REPRESENTATION_STRATEGY.md)).
- **Why this is the right next step:** D1 calibrated the estimator only on graphs whose dimension is encoded (lattices, a torus-embedded RGG) and on nulls with no finite dimension. Before the instrument is used on dynamically generated graphs (Phase 1), it must be shown to return a dimension that the construction does not hand it, including a **non-integer** one, and to cope with **non-self-averaging** ball-size fluctuations (balls in random trees do not concentrate: |B(v, r)|/r² has a non-degenerate limit law).
- **No parameter of the verdict rule is changed** (ε, r_min, guard, minimum run length, d̂ rule). The D1 code path (`emergence_lab.dimension_d1.verdict`, `shell_counts`, `ball_sizes`, `mean_balls`) is reused unchanged; only generators and a driver are new. **The one declared deviation is the number of sources, S = 256 instead of 32** (§5a): at S = 32 the test would mostly measure sampling noise, which is predictable from exact mathematics. D2 therefore tests the verdict rule at S = 256; it does not show that S = 32 suffices on non-self-averaging graphs, and a later application must choose S by the same power argument.

## 1. Question and hypotheses

**Q.** Does the frozen D1 estimator return the proved intrinsic dimension on graphs where that dimension is not encoded by construction, and does it reject a matched random-tree null without a finite dimension?

- **H-tree (methodological hypothesis):** on uniform random labelled trees, the estimator returns `PLATEAU` with |d̂ − 2| ≤ 0.15, stable across sizes.
- **H-UST (methodological hypothesis):** on the UST of the 2D torus, measured in the tree's own graph distance, the estimator returns `PLATEAU` with |d̂ − 8/5| ≤ 0.15, stable across sizes, and clearly separated from the ambient lattice value 2.
- **H-null (methodological hypothesis):** on random recursive trees (no finite dimension; typical distances of order log N) the estimator never returns `PLATEAU`.

## 2. Observable and estimator

Identical to D1 §2, applied to the **tree's own** graph distance. Sources: S = 256 distinct vertices drawn uniformly without replacement from each instance (every instance is connected). B̄(r) is the mean of |B(v, r)| over the 256 sources; d_eff(r) = log₂(B̄(2r)/B̄(r)); admissible scales A = {r ∈ {4, 8, 16, …} : 8·B̄(2r) ≤ N}; verdict, run selection, d̂ = d_eff(r_last) and post-window drift exactly as in D1 §2.

**Pooled curve (reported, gated only in D2-G0):** for each family and size, B̄_pool(r) is the mean over all 8 × 256 sources. The verdict of the pooled curve is reported descriptively; per-replicate verdicts are what the gates use, as in D1.

## 3. Families, sizes and seeds

| Family | Role | Generator | Sizes | Replicates × sources |
| --- | --- | --- | --- | --- |
| **CAY**: uniform random labelled tree on [N] | positive control, dimension 2 not encoded | uniform Prüfer sequence in [N]^(N−2), decoded in linear time; this is exactly uniform over the N^(N−2) labelled trees (Cayley/Prüfer bijection) | N ∈ {2¹⁸, 2²⁰, 2²²} | 8 × 256 |
| **UST**: uniform spanning tree of the L × L periodic square lattice | positive control, non-integer exponent 8/5 not encoded | Wilson's algorithm [Wil96], root vertex 0, vertices processed in a uniform random order from the replicate stream (Wilson's algorithm is exact for any root and order) | L ∈ {256, 512, 1024} (N = L²) | 8 × 256 |
| **RRT**: random recursive tree on [N] | matched null (random tree, no finite dimension) | vertex i ≥ 1 attaches to a uniform vertex in {0, …, i−1} | N ∈ {2¹⁸, 2²⁰, 2²²} | 8 × 256 |

- **Seeds:** `seed_base = 2036101101`, disjoint from all seed constants in `configs/`, `docs/` and `src/` (checked with grep at `65d2ce9`). Each (family index, size index, replicate index) gets `np.random.SeedSequence([seed_base, i_family, i_size, i_rep])` with PCG64, family order CAY, UST, RRT. Source draws use a child of the same sequence, as in D1. Independence of pseudorandom streams is a modelling assumption.
- **Torus UST vs. planar UST:** the theorems in §4 are for the UST of Z². The torus UST is a finite-volume approximation that agrees with it on scales small compared with L; its finite-size effects are part of what the saturation guard and the size-stability gate test.

## 4. Mathematical reference (proved, not measured)

**CAY, exact finite-N mean.** For a fixed vertex v of a uniform labelled tree on N vertices,

  E #{u : d(v, u) = k} = (k + 1) · ∏_{i=1}^{k} (1 − i/N).

*Proof sketch:* there are (N−1)(N−2)⋯(N−k) ordered paths v = x₀, x₁, …, x_k of distinct vertices; a tree contains a given path iff it contains its k edges, and the number of labelled trees on [N] containing a given spanning forest with component sizes a₁, …, a_m is a₁⋯a_m N^(m−2) [Moo70]. For the path plus N−k−1 singletons, m = N−k and the product is k+1, so the probability is (k+1) N^(−k). By uniqueness of paths in a tree, the expected count at distance k is (k+1)∏(1−i/N). *Check (exact enumeration, not sampling):* for N = 5, 6, 7 all N^(N−2) trees were decoded from Prüfer sequences and the distance profile of vertex 0 was averaged in exact rational arithmetic; it equals the formula at every k (script in the PR, `scripts/d2_cayley_reference.py`).

Hence E|B(v, r)| = Σ_{k=0}^{r} (k+1)∏_{i≤k}(1 − i/N) ≈ (r+1)(r+2)/2 for r ≪ √N: intrinsic dimension 2. This agrees with the scaling limit being Aldous' continuum random tree [Ald91], whose Hausdorff dimension is 2 [DLG05]. The estimator applied to the **exact mean curve** (not to samples) gives:

| N | admissible A | d_eff(r) at r = 4, 8, 16, 32, 64, 128, 256, 512 | verdict on the mean | window | d̂ (mean curve) |
| --- | --- | --- | --- | --- | --- |
| 2¹⁸ | 4 … 128 | 1.5849, 1.7653, 1.8734, 1.9306, 1.9498, 1.9162 | PLATEAU | [16, 256] | 1.9162 |
| 2²⁰ | 4 … 256 | 1.5849, 1.7655, 1.8742, 1.9338, 1.9626, 1.9663, 1.9247 | PLATEAU | [16, 512] | 1.9247 |
| 2²² | 4 … 512 | 1.5850, 1.7655, 1.8744, 1.9346, 1.9658, 1.9790, 1.9747, 1.9290 | PLATEAU | [16, 1024] | 1.9290 |

Two features are known in advance: d_eff approaches 2 **from below** at small r (lattice-like O(1/r) correction, as for Z²), and **turns down** at the largest admissible scale because of the finite-size factor ∏(1 − i/N) ≈ exp(−k²/2N). Because D1 takes d̂ at the largest admissible scale, the frozen estimator has a negative bias of about 0.07–0.08 on the mean curve. This is inside the tolerance and is stated now so that it cannot be rationalised afterwards. Per-replicate d̂ will differ from the mean-curve value (sampling fluctuation and Jensen gap); the size of that difference is not predicted.

**Known r_last flip (disclosed in r1).** At N = 2²² the exact mean is E B̄(1024) ≈ 0.94·N/8, i.e. just below the saturation guard, so whether 512 is admissible changes from replicate to replicate. On the exact mean curve, d̂ = 1.9747 when the largest admissible scale is 256 and 1.9290 when it is 512. Under the §5a model at S = 256 the largest admissible scale is 256 in ≈ 13 % and 512 in ≈ 87 % of replicates, with conditional mean d̂ ≈ 2.00 and ≈ 1.93. Both are inside the G1 tolerance. The result note reports r_last per replicate; this spread is a property of the frozen d̂ rule, not a generator fault.

**UST, proved exponent (up to constants).** For the UST of Z², intrinsic balls satisfy c r^(8/5) ≤ E|B_int(0, r)| ≤ C r^(8/5), with matching high-probability bounds [BM11], resting on the planar loop-erased random walk growth exponent 5/4 [Ken00, Mas09, BM10]. **Caveat that matters for the gate:** a two-sided bound up to constants proves that log|B|/log r → 8/5, but it does **not** prove that the dyadic ratio log₂(B(2r)/B(r)) converges, nor bound its finite-r corrections. A `NO_PLATEAU` on the UST therefore does not contradict the theorem; it means the instrument is not usable on this family at these sizes. No finite-N UST reference curve is available.

**RRT.** The height of a random recursive tree is ≈ e·log N and typical distances are ≈ 2 ln N (≈ 30 at N = 2²²; height ≈ 41) [Dev87, Pit94]. Balls therefore reach a positive fraction of N within a few dyadic scales. **Expected decisive mechanism (heuristic, not computed):** the saturation guard (`INSUFFICIENT_RANGE`), as for the random 4-regular null in D1. This null tests the guard, not the plateau criterion; the result note must state which verdict decided it.

## 5. Gates (fixed before any sampled output)

- **D2-G0, generator exactness (STOP on failure).**
  - *Unit tests (tiny graphs, exhaustive or exact):* Prüfer decoding is a bijection for N ≤ 7 and reproduces the §4 formula exactly. Wilson's algorithm on a small graph with a known spanning-tree count (matrix-tree theorem; e.g. the 3 × 3 torus) produces every spanning tree over ≥ 3·10⁵ draws, and a χ² test against uniformity over the same draws does not reject at α = 10⁻³. (r1: v1.0 required coverage at 10⁵ draws; with τ = 11664 a uniform sampler leaves ≈ 11664·e^(−10⁵/11664) ≈ 2.2 trees unseen, so a correct implementation would fail with probability ≈ 0.89. At 3·10⁵ draws that probability is ≈ 8·10⁻⁸, and the expected count per cell is ≈ 25.7.) RRT parent indices satisfy parent(i) < i.
  - *Structural checks on every instance:* N − 1 edges and connected; for UST, every edge is a lattice edge; for RRT, the root's subtree is everything.
  - *CAY distributional check at gated sizes:* for each N and each admissible r of the pooled curve, the 8 replicate means of B̄(r) give a Student-t statistic against the §4 formula. All |t| must be below the two-sided Bonferroni critical value at family-wise α = 0.01 over all (N, r) pairs tested (df = 7). This checks the generator and the BFS against exact mathematics on non-embedded graphs. It does not involve d_eff.
- **D2-G1, H-tree.** At N = 2²², all 8 replicates are `PLATEAU`, the replicate mean of d̂ has |mean − 2| ≤ 0.15, and the replicate means at 2²⁰ and 2²² differ by ≤ 0.10. Uncertainty: Student-t 95 % interval over the 8 replicate d̂ values. N = 2¹⁸ is reported, not gated. The difference between the replicate mean and the mean-curve d̂ (§4 table) is reported descriptively.
- **D2-G2, H-UST.** At L = 1024, all 8 replicates are `PLATEAU`, |mean d̂ − 1.6| ≤ 0.15, the upper end of the Student-t 95 % interval is < 1.85 (separation from the ambient value 2), and the replicate means at L = 512 and L = 1024 differ by ≤ 0.10. L = 256 is reported, not gated.
- **D2-G3, H-null.** No replicate of the RRT (24) returns `PLATEAU`. `INSUFFICIENT_RANGE` and `NO_PLATEAU` both pass.
- **D2-G4, provenance and determinism (as D1 D-G5).** Per-replicate, per-source |B(v, r)| tables (CSV) and a JSON manifest recording prereg blob SHA, config SHA-256, executing commit, Python/NumPy/SciPy versions, seed tuples, runtime, peak memory and file hashes. Two invocations in the same environment are byte-identical except for timestamps and runtime. Outputs above 5 MiB go to a release asset with a pinned digest.
- **Sensitivity (reported, never gated):** verdicts recomputed at ε ∈ {0.10, 0.20}, r_min ∈ {2, 8}, guard N/4 or N/16, and for the pooled curve. Flips are flagged as fragile.

**Design disclosure.**
- Tolerances 0.15 (level) and 0.10 (size stability) are copied from D1 D-G3 unchanged. The UST target 8/5 and the separation threshold 1.85 were fixed from the theorem, before any UST output.
- The only computations done while writing this document were: (a) exact enumeration of all labelled trees for N ≤ 7; (b) the §4 table, obtained by applying the frozen D1 `verdict` function to the exact formula; (c) a **timing-only** run of a pure-Python Wilson implementation on 64 × 64 and 128 × 128 tori (non-gated sizes; 4.5 and 7.6 walk steps per vertex, ≈ 2.5·10⁶ steps/s). No ball count, d_eff or verdict was computed on any sampled tree.
- **r1 computations:** (d) the exact-moment power model of §5a (`scripts/d2_g1_power.py`, no tree sampled); (e) timing-only BFS on random recursive trees at N = 2²⁰ and 2²² (§8; seed 999, no ball count read). The review's N = 2¹⁶ variance pilot (§5a) is the only sampled-tree computation so far; it is at a non-grid size, used a non-D2 seed, and did not compute d_eff.
- Sizes were chosen so that the CAY mean curve has ≥ 6 admissible dyadic scales and the UST, whose intrinsic diameter grows like L^(5/4), has comparable range; they were not tuned on outputs.

## 5a. Power: noise-only failure probability (added in r1)

Ball sizes in random trees do not self-average, so the gates must be checked against the sampling noise of a **correct** instrument before any sampled output exists.

- **Proved inputs (no sampling):** the exact per-source covariance of |B(v, r)| for uniform labelled trees, E[|B(v,r₁)||B(v,r₂)|] = Σ_{a≤r₁, b≤r₂} Σ_{j≤min(a,b)} f(a+b−j+1) with f(s) = s∏_{i<s}(1 − i/N) (Moon's forest count on the subtree spanned by v, u, w; exhaustive check for N = 6, 7 in `scripts/review_d2/d2_second_moment.py`). The per-source coefficient of variation is 0.47–0.57 at the gated sizes.
- **Disclosed empirical input:** the within-tree variance inflation of B̄ (sources in one tree are positively correlated near √N), measured in a review-only pilot at N = 2¹⁶ (not a grid size; review seed 515151; `scripts/review_d2/d2_design_effect.py`): ×1.0 for r ≤ √N/16 and ×1.29 / 1.45 / 2.49 at r = √N/8, √N/4, √N/2. It is assumed to depend on r/√N only. That pilot computed ball means and variances, never d_eff or d̂ against 2.
- **Model (not a D2 result):** log B̄_S(r) Gaussian with that covariance divided by S and inflated as above; each simulated replicate curve goes through the frozen D1 `verdict`; G1 is evaluated jointly (8/8 `PLATEAU` at 2²², level at 2²², drift between 2²⁰ and 2²²). Script: `scripts/d2_g1_power.py` (producer seed 616161, unrelated to `seed_base`; no tree is sampled). Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1.

| S | P(`PLATEAU`) per replicate at 2²⁰ / 2²² | P(G1 passes) for a correct instrument | sd of d̂ per replicate at 2²² |
| --- | --- | --- | --- |
| 32 (v1.0) | 0.755 / 0.845 | 0.236 | 0.093 |
| 128 | 0.977 / 0.994 | 0.947 | 0.062 |
| **256 (r1)** | 0.998 / 1.000 | ≈ 0.997 (r2; see below) | 0.051 |

**r2 correction.** r1 reported "> 0.999 (20 000 of 20 000 model trials)" at S = 256. That figure resamples 8 replicates from a pool of only 4000 simulated replicates, which at S = 256 happened to contain no non-`PLATEAU` curve, so the estimate could not fall below 1. With a pool of 40 000 (`scripts/review_d2/r2_power_resolution.py`, seed 939393) the per-replicate non-`PLATEAU` rate at 2²² is 16/40 000 = 4·10⁻⁴, so P(8/8 `PLATEAU`) ≈ 0.997 and the noise-only failure probability of G1 is ≈ 3·10⁻³ (Poisson 95 % range ≈ 2–5·10⁻³), not below 10⁻³. The S = 32 and S = 128 rows are not affected in substance, because their pools contain many failures.

**Sensitivity to the design-effect input (r2, model-based).** Multiplying the whole pilot design-effect curve by 1.5, 2 or 3 gives P(G1 passes) ≈ 0.97, ≈ 0.95 and ≈ 0.81 at S = 256 (pools of 3000; Monte-Carlo error about ±0.01). An independent measurement at N = 2¹⁴ (not a grid size; networkx Prüfer decoding, seed 727272, 600 trees, no d_eff computed; `scripts/review_d2/r2_design_effect_sizes.py`) gives a design effect of 1.09 / 1.43 / 2.78 at r = √N/8, √N/4, √N/2, against the pilot's 1.29 / 1.45 / 2.49 at N = 2¹⁶. That is consistent with dependence on r/√N only, to within about 10–20 %, well inside the factor-of-2 range that keeps G1's noise-only failure probability near 5 %. At N = 2¹⁷ (150 trees, same script and seed) it is 1.16 / 1.59 / 2.86 (90 % intervals [0.97, 1.42], [1.33, 1.94], [2.39, 3.50]). Across 2¹⁴, 2¹⁶ and 2¹⁷ there is no monotone trend, and the largest value is about 15 % above the pilot curve used in the model, so a ×1.5 envelope (P(G1) ≈ 0.97) covers the measured range. The extrapolation from 2¹⁷ to 2²² remains an assumption.

**Choice:** S = 256 for all three families. The noise-only failure probability of G1 is then ≈ 3·10⁻³ under the model (r2; r1 stated below 10⁻³); at S = 128 it would be ≈ 5 %. The model's limits: the inflation factor is extrapolated from one non-grid size, and the Gaussian/delta-method approximation is not checked in the tails. A G1 failure is therefore still evidence against transfer, but the result note must report the pooled curve and the per-replicate verdicts so that a noise-driven failure can be told apart from a level or drift failure.

**UST: power unknown.** No exact moments are available for the UST, and no UST pilot was run. D2 uses the same S = 256 with an explicit caveat: if per-source fluctuations on the UST are larger than on CAY, G2 can fail through noise alone. A G2 failure whose pooled curve is a `PLATEAU` within tolerance is recorded as "inconclusive at this S", not as a level failure; it still counts as a G2 failure under §6.

**RRT:** more sources cannot create a plateau where the mean curve has none; G3 is expected to be decided by the saturation guard, so S does not affect its power materially (heuristic).

## 6. Decision rule

- **G0–G4 pass:** the frozen estimator is *calibrated for* two families whose intrinsic dimension is not encoded by construction, including a non-integer exponent, at the reported sizes and windows. This is the precondition for applying it, with controls, to dynamically generated graphs in Phase 1. It is still an instrument statement, not a statement about emergent geometry.
- **G1 passes, G2 fails:** the instrument is validated only for dimension-2 tree/CRT-class graphs and for the D1 classes. Non-integer dimension statements stay blocked until a revised estimator (new version) or the spectral method is preregistered and calibrated. The failure mode (no plateau, wrong level, or size drift) is recorded.
- **G1 fails:** the D1 calibration does not transfer to non-embedded graphs. Likely causes to be distinguished in the result note, not fixed after the fact: residual non-self-averaging fluctuations at S = 256 (the §5a model says this should be rare), or the largest-scale d̂ rule interacting with the √N cutoff (§4 r_last flip). A redesign (e.g. pooled sources or a different d̂ rule) is a new version with new seeds.
- **G3 fails:** the estimator is rejected for dimension claims on small-world trees.
- **G0 fails:** STOP; fix the implementation and rerun with the same seeds (not a design change).
- A failed gate is published. No ε, window, size, tolerance or seed may change after any sampled output exists.

## 7. Falsifiers and limitations

**Falsifiers of the instrument's transfer claim:** a `PLATEAU` on the RRT; CAY d̂ outside [1.85, 2.15] or drifting by > 0.10 between 2²⁰ and 2²²; a UST plateau near 2 (which would mean the instrument does not track the intrinsic exponent); a gate flipping under the mild sensitivity settings (flagged, as in D1).

**Limitations:**
- Both positive families are trees. Tree-specific behaviour (no cycles, unique geodesics) may make them easier or harder than generic dynamically generated graphs; passing D2 does not cover graphs with loops whose dimension is not encoded. Random planar maps (Hausdorff dimension 4 [LG13, Mie13]) would cover that case but need N ≳ 10⁷ for three admissible scales and a bijective sampler; they are a candidate for D3.
- The UST exponent is proved only up to constants; finite-size corrections to the dyadic ratio are unknown.
- Volume-growth dimension is not spectral dimension (4/3 for the CRT, 16/13 for the 2D UST [BM11]). A spectral cross-check on the same frozen instances is a natural later design, not part of D2.
- Same software stack and model family for producer and later-pass reviewer, as in D1.
- The RRT is a "matched" null only in N and in being a tree; it is not matched in degree distribution or diameter. It tests the saturation guard, not a near-miss alternative.
- S = 256 is a deviation from D1's S = 32 (§0, §5a). The D1 calibration of RGG and the nulls was at S = 32; D2 does not re-test S = 32.

## 8. Budget

- Single core, ≤ 2 GiB RAM. Largest instances: CAY and RRT with N = 2²² ≈ 4.2·10⁶ vertices (CSR adjacency ≈ 8.4·10⁶ entries); UST L = 1024 (N ≈ 1.05·10⁶). Generation: Prüfer decoding O(N); Wilson's algorithm, expected O(N log N) walk steps in 2D; RRT O(N). BFS via the D1 `shell_counts` (one full BFS per source).
- **r1 re-estimate with S = 256** (2048 BFS per family and size). Timing-only measurement of `shell_counts` on random recursive trees (seed 999, no ball counts inspected; Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1): ≈ 0.19 s per BFS at N = 2²⁰ and ≈ 1.2 s at N = 2²². Projection: CAY ≈ 50 min, RRT ≈ 50 min, UST ≈ 10 min, so ≈ 1.8 h CPU for one invocation of the grid (v1.0 assumed ≤ 30 min at S = 32).
- **Wall limit:** ≤ 3 h single-core CPU per full invocation. The driver must accept `--families` so that the grid can run as one invocation per family (each ≤ 75 min), which fits inside one Director lease with heartbeats. Outputs are concatenated in the fixed family order; per-family seeds make this identical to a single invocation. D2-G4 byte identity may likewise be shown per family.
- **Overrun action:** if an invocation exceeds 1.5× its projection, or 90 min for one family, it is stopped and recorded as BLOCKED (budget) in the result PR. It is not replaced by fewer sources, replicates or sizes; a smaller design is a new version with new seeds, decided before any sampled output is inspected.
- No Lightsail deployment, no background job, no network access during the run, no spending.
- Implementation, tests and the run are a separate PR after this design is merged, and only after its later-pass review. CI pytest plus a deterministic local run are required before any result is reported.

## 9. References (to be re-checked by the later-pass review)

- [Ald91] D. Aldous, "The continuum random tree I", *Ann. Probab.* 19(1), 1–28 (1991).
- [BM10] M. T. Barlow, R. Masson, "Exponential tail bounds for loop-erased random walk in two dimensions", *Ann. Probab.* 38(6), 2379–2417 (2010).
- [BM11] M. T. Barlow, R. Masson, "Spectral dimension and random walks on the two dimensional uniform spanning tree", *Commun. Math. Phys.* 305, 23–57 (2011).
- [Dev87] L. Devroye, "Branching processes in the analysis of the heights of trees", *Acta Inform.* 24, 277–298 (1987).
- [DLG05] T. Duquesne, J.-F. Le Gall, "Probabilistic and fractal aspects of Lévy trees", *Probab. Theory Relat. Fields* 131, 553–603 (2005).
- [Ken00] R. Kenyon, "The asymptotic determinant of the discrete Laplacian", *Acta Math.* 185, 239–286 (2000).
- [LG13] J.-F. Le Gall, "Uniqueness and universality of the Brownian map", *Ann. Probab.* 41(4), 2880–2960 (2013).
- [Mas09] R. Masson, "The growth exponent for planar loop-erased random walk", *Electron. J. Probab.* 14, 1012–1073 (2009).
- [Mie13] G. Miermont, "The Brownian map is the scaling limit of uniform random plane quadrangulations", *Acta Math.* 210, 319–401 (2013).
- [Moo70] J. W. Moon, *Counting Labelled Trees*, Canadian Mathematical Monographs 1 (1970).
- [Pit94] B. Pittel, "Note on the heights of random recursive trees and random m-ary search trees", *Random Struct. Algorithms* 5(2), 337–347 (1994).
- [Wil96] D. B. Wilson, "Generating random spanning trees more quickly than the cover time", *Proc. 28th ACM STOC*, 296–303 (1996).

## 10. Revision r1 (2026-10-11)

Applied by session `rd-claude-20261011T115603Z-1ed1ef` before any implementation or sampled D2 output exists. It addresses the later-pass review on [PR #35](https://github.com/shaden7/emergence-lab/pull/35) (REVISE, session `rd-claude-20261011T105556Z-58dd0f`).
- **Blocking 1 (G1 underpowered at S = 32):** S raised to 256 for all families, declared as a deviation from D1 (§0, §2, §3); power table and model limits in §5a; UST power stated as unknown, with how a noise-only G2 failure is recorded.
- **Blocking 2 (Wilson coverage at 10⁵ draws):** coverage and χ² now use ≥ 3·10⁵ draws (§5, D2-G0).
- **Non-blocking:** r_last flip at 2²² disclosed (§4); budget re-estimated for S = 256 with an overrun action (§8); RRT matching scope stated (§7).
- **Unchanged:** families, sizes, replicates, seeds and seed rule, ε, r_min, guard, d̂ rule, all tolerances and thresholds, decision rule structure.

## 11. Revision r2 (2026-10-11)

Applied by session `rd-claude-20261011T125558Z-220239`, which checked r1 and authored none of `c7a2e84`, `1b73f2b` or `69e1e96`. Still before any implementation or sampled D2 output.
- **Correction (§5a):** the r1 joint pass probability at S = 256 was a resolution artifact of a 4000-replicate pool; the corrected value is ≈ 0.997 (failure ≈ 3·10⁻³), from a 40 000-replicate pool. The S = 256 choice and every gate are unchanged.
- **Added (§5a):** sensitivity of the G1 power to the design-effect input, and an independent design-effect measurement at non-grid sizes.
- **Unchanged:** everything else, including S, families, sizes, replicates, seeds, ε, r_min, guard, d̂ rule, tolerances, thresholds and decision rule.
