# D2 — out-of-sample test of the frozen D1 dimension estimator on graphs whose dimension is not built in (Issue #4), preregistration v1.0

**Status:** PROPOSED DESIGN. No implementation exists, and no ball count, d_eff value or verdict has been computed on any sampled instance of a D2 family. The design freezes when it is merged to `main`; any later change to a preregistered parameter needs a new version and an explicit deviation note.
**Date:** 2026-10-11. **Base:** `main` `65d2ce9` (D1 decision integrated via PR #34). **Issue:** [#4](https://github.com/shaden7/emergence-lab/issues/4). **Config:** [`configs/dimension_d2.json`](../configs/dimension_d2.json).
**Author:** Director session `rd-claude-20261011T095635Z-d05fc0`. Producer self-review only. A later-pass review by a different session is required before merge.

## 0. What this is and is not

- **It is** an out-of-sample test of the D1 instrument (the dyadic volume-growth estimator of [DIMENSION_ESTIMATOR_PREREGISTRATION.md](DIMENSION_ESTIMATOR_PREREGISTRATION.md) §2, frozen at ε = 0.15, r_min = 4, guard N/8, S = 32 sources). It uses two graph families whose large-scale intrinsic dimension is **not put in by an embedding or a lattice**, but is a **proved** property of the random structure:
  - the uniform random labelled tree on N vertices, intrinsic volume-growth dimension 2;
  - the uniform spanning tree (UST) of the 2D torus, intrinsic volume-growth exponent 8/5.
- **It is not** a discovery of emergent space. Both exponents are established mathematics (§4). Recovering them tests the instrument; it says nothing about nature. Trees are a relational test bed, not an ontological proposal ([REPRESENTATION_STRATEGY.md](REPRESENTATION_STRATEGY.md)).
- **Why this is the right next step:** D1 calibrated the estimator only on graphs whose dimension is encoded (lattices, a torus-embedded RGG) and on nulls with no finite dimension. Before the instrument is used on dynamically generated graphs (Phase 1), it must be shown to return a dimension that the construction does not hand it, including a **non-integer** one, and to cope with **non-self-averaging** ball-size fluctuations (balls in random trees do not concentrate: |B(v, r)|/r² has a non-degenerate limit law).
- **No estimator parameter is changed.** The D1 code path (`emergence_lab.dimension_d1.verdict`, `shell_counts`, `ball_sizes`, `mean_balls`) is reused unchanged; only generators and a driver are new.

## 1. Question and hypotheses

**Q.** Does the frozen D1 estimator return the proved intrinsic dimension on graphs where that dimension is not encoded by construction, and does it reject a matched random-tree null without a finite dimension?

- **H-tree (methodological hypothesis):** on uniform random labelled trees, the estimator returns `PLATEAU` with |d̂ − 2| ≤ 0.15, stable across sizes.
- **H-UST (methodological hypothesis):** on the UST of the 2D torus, measured in the tree's own graph distance, the estimator returns `PLATEAU` with |d̂ − 8/5| ≤ 0.15, stable across sizes, and clearly separated from the ambient lattice value 2.
- **H-null (methodological hypothesis):** on random recursive trees (no finite dimension; typical distances of order log N) the estimator never returns `PLATEAU`.

## 2. Observable and estimator

Identical to D1 §2, applied to the **tree's own** graph distance. Sources: S = 32 distinct vertices drawn uniformly without replacement from each instance (every instance is connected). B̄(r) is the mean of |B(v, r)| over the 32 sources; d_eff(r) = log₂(B̄(2r)/B̄(r)); admissible scales A = {r ∈ {4, 8, 16, …} : 8·B̄(2r) ≤ N}; verdict, run selection, d̂ = d_eff(r_last) and post-window drift exactly as in D1 §2.

**Pooled curve (reported, gated only in D2-G0):** for each family and size, B̄_pool(r) is the mean over all 8 × 32 sources. The verdict of the pooled curve is reported descriptively; per-replicate verdicts are what the gates use, as in D1.

## 3. Families, sizes and seeds

| Family | Role | Generator | Sizes | Replicates × sources |
| --- | --- | --- | --- | --- |
| **CAY**: uniform random labelled tree on [N] | positive control, dimension 2 not encoded | uniform Prüfer sequence in [N]^(N−2), decoded in linear time; this is exactly uniform over the N^(N−2) labelled trees (Cayley/Prüfer bijection) | N ∈ {2¹⁸, 2²⁰, 2²²} | 8 × 32 |
| **UST**: uniform spanning tree of the L × L periodic square lattice | positive control, non-integer exponent 8/5 not encoded | Wilson's algorithm [Wil96], root vertex 0, vertices processed in a uniform random order from the replicate stream (Wilson's algorithm is exact for any root and order) | L ∈ {256, 512, 1024} (N = L²) | 8 × 32 |
| **RRT**: random recursive tree on [N] | matched null (random tree, no finite dimension) | vertex i ≥ 1 attaches to a uniform vertex in {0, …, i−1} | N ∈ {2¹⁸, 2²⁰, 2²²} | 8 × 32 |

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

**UST, proved exponent (up to constants).** For the UST of Z², intrinsic balls satisfy c r^(8/5) ≤ E|B_int(0, r)| ≤ C r^(8/5), with matching high-probability bounds [BM11], resting on the planar loop-erased random walk growth exponent 5/4 [Ken00, Mas09, BM10]. **Caveat that matters for the gate:** a two-sided bound up to constants proves that log|B|/log r → 8/5, but it does **not** prove that the dyadic ratio log₂(B(2r)/B(r)) converges, nor bound its finite-r corrections. A `NO_PLATEAU` on the UST therefore does not contradict the theorem; it means the instrument is not usable on this family at these sizes. No finite-N UST reference curve is available.

**RRT.** The height of a random recursive tree is ≈ e·log N and typical distances are ≈ 2 ln N (≈ 30 at N = 2²²; height ≈ 41) [Dev87, Pit94]. Balls therefore reach a positive fraction of N within a few dyadic scales. **Expected decisive mechanism (heuristic, not computed):** the saturation guard (`INSUFFICIENT_RANGE`), as for the random 4-regular null in D1. This null tests the guard, not the plateau criterion; the result note must state which verdict decided it.

## 5. Gates (fixed before any sampled output)

- **D2-G0, generator exactness (STOP on failure).**
  - *Unit tests (tiny graphs, exhaustive or exact):* Prüfer decoding is a bijection for N ≤ 7 and reproduces the §4 formula exactly. Wilson's algorithm on a small graph with a known spanning-tree count (matrix-tree theorem; e.g. the 3 × 3 torus) produces every spanning tree, and a χ² test against uniformity over ≥ 10⁵ draws does not reject at α = 10⁻³. RRT parent indices satisfy parent(i) < i.
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
- Sizes were chosen so that the CAY mean curve has ≥ 6 admissible dyadic scales and the UST, whose intrinsic diameter grows like L^(5/4), has comparable range; they were not tuned on outputs.

## 6. Decision rule

- **G0–G4 pass:** the frozen estimator is *calibrated for* two families whose intrinsic dimension is not encoded by construction, including a non-integer exponent, at the reported sizes and windows. This is the precondition for applying it, with controls, to dynamically generated graphs in Phase 1. It is still an instrument statement, not a statement about emergent geometry.
- **G1 passes, G2 fails:** the instrument is validated only for dimension-2 tree/CRT-class graphs and for the D1 classes. Non-integer dimension statements stay blocked until a revised estimator (new version) or the spectral method is preregistered and calibrated. The failure mode (no plateau, wrong level, or size drift) is recorded.
- **G1 fails:** the D1 calibration does not transfer to non-embedded graphs. Likely causes to be distinguished in the result note, not fixed after the fact: non-self-averaging fluctuations with 32 sources, or the largest-scale d̂ rule interacting with the √N cutoff. A redesign (e.g. pooled sources or a different d̂ rule) is a new version with new seeds.
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

## 8. Budget

- Single core, ≤ 1.5 GiB RAM, ≤ 30 min wall for the full grid. Largest instances: CAY and RRT with N = 2²² ≈ 4.2·10⁶ vertices (CSR adjacency ≈ 8.4·10⁶ entries); UST L = 1024 (N ≈ 1.05·10⁶). Generation: Prüfer decoding O(N); Wilson's algorithm, expected O(N log N) walk steps in 2D; RRT O(N). BFS via the D1 `shell_counts`.
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
