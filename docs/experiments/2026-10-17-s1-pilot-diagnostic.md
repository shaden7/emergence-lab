# S1 pilot post-hoc diagnostic: local-limit check and size difference by time (exploratory)

**Status: exploratory, post-hoc, not gated.** Uses only the archived pilot CSV (SHA-256 `526d2df5…`, [result note](2026-10-17-s1-pilot.md)); no new pilot seeds, no new walk simulation. It informs the design of the S1b replication ([SPECTRAL_S1B_PREREGISTRATION.md](../SPECTRAL_S1B_PREREGISTRATION.md)); it does not change the frozen S1 §7 NO-GO and is not a test of any hypothesis (fitting and testing on the same data are kept apart: S1b uses fresh seeds).
**Date:** 2026-10-17. **Director:** `rd-claude-20261017T0846Z-21c3330dce46`. **Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37). Environment: Python 3.13.16, NumPy 2.5.3, Director sandbox.

## Question

The pilot's CAY size difference (larger-minus-smaller annealed slope +0.035 to +0.071, 20/28 uncorrected CIs exclude zero) could be (a) a defect or non-uniformity in tree or source sampling, (b) a genuine N-dependence of the annealed return probability at fixed t ≤ 4096, or (c) sampling fluctuation with eight trees per size. This diagnostic asks only which of these the archived data can already exclude.

## Known-answer check at the smallest time (established result + independent arithmetic)

**Derivation (standard local limit, not new):** the uniform labelled tree rooted at a uniform vertex converges locally to the Poisson(1) Galton–Watson tree conditioned to survive (Grimmett 1980; Aldous 1991). The root has degree 1 + Poisson(1), its spine neighbour 2 + Poisson(1), every other neighbour 1 + Poisson(1). With E[1/(1+X)] = (e−1)/e and E[1/(2+X)] = 1/e for X ~ Poisson(1):

  lim E[P_v(X₂ = v)] = (e−1)/e · 1/e + 1/e · (e−1)/e = **2(e−1)/e² = 0.46509**, and P(deg = 1) → 1/e = 0.36788.

**Independent numerical reference** ([`s1_cay_local_limit_reference.py`](s1_cay_local_limit_reference.py), separate heapq Prüfer decoder, all vertices of 40 trees at N = 20 000, throwaway check seed 20261017): q(1) = 0.46503 ± 0.00009, P(deg 1) = 0.36827. Agrees with the limit.

**Pilot data** ([`s1_pilot_local_limit_check.py`](s1_pilot_local_limit_check.py), tree-cluster SE over 8 trees, 32 sources each):

| Family, size | q(t=1) | P(deg = 1) | mean source degree |
| --- | --- | --- | --- |
| CAY 2¹⁶ | 0.4652 ± 0.0090 | 0.340 ± 0.028 | 2.109 ± 0.053 |
| CAY 2¹⁸ | 0.4612 ± 0.0098 | 0.418 ± 0.032 | 1.918 ± 0.064 |
| UST L = 128 | 0.4870 ± 0.0075 | 0.273 ± 0.025 | 2.066 ± 0.034 |
| UST L = 256 | 0.4708 ± 0.0056 | 0.281 ± 0.015 | 1.996 ± 0.025 |
| RRT 2¹⁶ (null) | 0.4438 ± 0.0178 | 0.547 ± 0.049 | 1.781 ± 0.084 |

Reference values: CAY 0.46509 / 0.36788 / 2; UST on Z² P(deg 1) = 8/π²·(1 − 2/π) = 0.29454 (Manna, Dhar & Majumdar 1992), mean degree 2. **Numerical observation:** all pilot cells are within 1.6 SE of their references. The local (t = 1) statistics of the pilot trees and sources are therefore consistent with correct uniform sampling at both sizes; explanation (a) is not supported at this level, although a non-uniformity that only affects larger scales is not excluded. The SE of P(deg 1) (≈ 0.03) equals the binomial value for 256 sources, so at small t the variance is dominated by **source sampling** (S = 32), not by tree-to-tree variation (exhaustive per-tree averages vary by ≈ 0.0006).

## Size difference as a function of time (pilot data)

ln(Q̄_large(t)/Q̄_small(t)), delta-method SE over trees (both sizes independent):

| t | 1 | 4 | 16 | 64 | 256 | 1024 | 2048 | 4096 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAY 2¹⁸ vs 2¹⁶ | −0.009 ± 0.029 | −0.016 ± 0.035 | −0.052 ± 0.044 | −0.096 ± 0.055 | −0.131 ± 0.067 | −0.186 ± 0.057 | −0.199 ± 0.048 | −0.192 ± 0.055 |
| UST 256 vs 128 | −0.034 ± 0.020 | −0.025 ± 0.028 | −0.019 ± 0.040 | −0.007 ± 0.047 | +0.006 ± 0.039 | +0.018 ± 0.048 | +0.015 ± 0.045 | +0.010 ± 0.039 |

Per-tree CAY window slopes 128–1024: N = 2¹⁶ {1.335, 1.324, 1.324, 1.261, 1.246, 1.268, 1.402, 1.316}; N = 2¹⁸ {1.403, 1.351, 1.489, 1.294, 1.317, 1.429, 1.317, 1.392}. The shift is not driven by a single tree.

**Numerical observations:** for CAY the difference is absent at small t and grows monotonically to about −0.19 in ln Q̄ (≈ 17 % lower return probability for the larger trees) at t ≥ 1024, |z| ≈ 3–4 at t ≥ 1024 (single comparisons, no multiplicity correction; the values at different t are strongly correlated because they share trees and sources, so the monotone growth is partly built in and is **not** independent evidence). For UST no difference is resolved at any t.

## Source-degree composition does not explain the CAY difference

By chance the CAY 2¹⁸ sources contain more leaves than the 2¹⁶ sources (0.418 vs 0.340), and late-time q_v grows with deg(v) (pilot P4), so a composition effect was a candidate. [`s1_pilot_degree_poststrat.py`](s1_pilot_degree_poststrat.py) re-weights the per-class means (degree 1, 2, 3, ≥ 4) to the exact 1 + Poisson(1) limit (CAY) or to the pooled empirical shares (UST), with delete-one-tree jackknife SEs:

| Window | CAY diff, raw | CAY diff, post-stratified | UST diff, raw | UST diff, post-stratified |
| --- | --- | --- | --- | --- |
| 8–64 | +0.065 ± 0.034 | +0.043 ± 0.034 | −0.013 ± 0.032 | −0.027 ± 0.031 |
| 32–256 | +0.051 ± 0.045 | +0.043 ± 0.044 | −0.021 ± 0.029 | −0.027 ± 0.028 |
| 128–1024 | +0.071 ± 0.029 | +0.075 ± 0.031 | −0.015 ± 0.042 | −0.016 ± 0.042 |
| 256–2048 | +0.066 ± 0.036 | +0.069 ± 0.035 | −0.008 ± 0.033 | −0.010 ± 0.034 |
| 512–4096 | +0.035 ± 0.048 | +0.035 ± 0.048 | +0.001 ± 0.036 | −0.001 ± 0.036 |

**Numerical observations:** post-stratification leaves the CAY 128–1024 difference unchanged (+0.071 → +0.075); the jackknife SE (0.029) agrees with the pilot's delta-method SE. A CAY difference of similar size is already present in the **early window 8–64** (+0.065 ± 0.034 raw), where the walk explores only a few dozen vertices and the local limit is N-independent. Variance decomposition at t = 1024: the expected source-sampling part of the tree-mean variance (within-tree variance / 32) is as large as the whole between-tree-mean variance (ratio 1.1 at 2¹⁶, 1.8 at 2¹⁸, 2.2 at UST 256; noisy estimates), so at S = 32 the SEs are dominated by source sampling, not by true tree-to-tree variation.

## Interpretation (hypotheses only)

- **Against an ordinary finite-volume effect (heuristic scaling argument, not a proof):** the random-walk mixing time on a uniform tree of size N scales as N^{3/2} (Aldous' continuum-random-tree scaling); at N = 2¹⁶ that is ~1.7·10⁷ steps, versus 2t ≤ 8192 here, a ratio ≲ 5·10⁻⁴. For even-step returns on a finite bipartite tree, the stationary floor is 2π(v) = deg(v)/(N−1), approximately 3·10⁻⁵ at degree 2 and N = 2¹⁶, below q̄(4096) ≈ 4·10⁻³. The floor therefore gives roughly 130-fold annealed headroom in this illustration; it is not a finite-time bias bound and does not replace the per-source ≥10× screen. A ~17 % N-dependence of q̄ at these times would therefore be surprising, unless the annealed mean is dominated by rare, large-q configurations whose frequency depends on N.
- **Sampling fluctuation (c)** remains plausible: eight clusters per size, a heavy-tailed annealed mean and many correlated windows; a single ~3σ excursion propagated through correlated times would look like this.
- A difference of similar size already in the 8–64 window, where no finite-N effect is expected, makes a slowly varying N-dependence of the late-time walk a less natural explanation than (c), and this particular coarse degree post-stratification does not explain the contrast; it cannot exclude degree-related effects within strata or other structural sampling effects; but a difference in the early window is itself only ≈ 1.9σ.
- Hence (b) versus (c) is still **undetermined** from the pilot. The cheapest discriminating step is a direct replication at the same two sizes with fresh seeds and more trees, plus a third smaller size to show whether any difference follows N. Variance at small t could be reduced cheaply by more sources per tree (source noise dominates there); that is a method change and is left to a later version.

## Limitations

Post-hoc and exploratory; the analyses were chosen after seeing the pilot. The local-limit check tests t = 1 only (two walk steps), not the kernel at large t (P0b covers that up to N = 4096). The UST degree reference is a literature value, not recomputed here. No different-model-family review.
