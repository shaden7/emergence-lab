# S1 — Spectral-dimension estimator on random trees: feasibility and power pilot (Issue #37), preregistration v0.2

**Status: REVIEW-CORRECTED DESIGN (v0.2), pending final CI and integration. No return probability has been computed on a sampled tree for this preregistration.** No seed in §4 has been drawn. Review amendments are recorded in §10; any change after pilot sampling requires a versioned deviation note.
**Date:** 2026-10-13. **Base:** `main` `d05ffbe` (S0 merged via PR #43, `fd91bfb`). **Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37). **Config:** [`configs/spectral_s1_pilot.json`](../configs/spectral_s1_pilot.json).
**Author:** Director session `rd-claude-20261013T0704Z-325a097e3638`.

## 0. What this is and is not

- **It is** the S1 step required by [SPECTRAL_S0_PREREGISTRATION.md](SPECTRAL_S0_PREREGISTRATION.md) §5: a **feasibility and power pilot** on non-gated seeds that measures cost, numerical accuracy, variance components, source-degree bias and the drift of the dyadic spectral slope with time on the two D2 positive families (CAY, 2D torus UST), plus controls.
- **It is not** a calibration verdict. The pilot has **no tolerance on the measured spectral dimension**. Its d_s values are descriptive and will be disclosed in the later S2 preregistration (the gated calibration), which must use fresh seeds. This separates choosing the time window and sample sizes (pilot data) from testing (S2 data).
- **It is not** a statement about short-scale dimensional reduction, emergent geometry or spacetime. Trees are a relational test bed ([REPRESENTATION_STRATEGY.md](REPRESENTATION_STRATEGY.md)); their spectral dimensions are established mathematics (§2).
- **Order of work:** (1) review and merge this design; (2) a separate implementation PR (killed-ball kernel, generators reused from D2, P0 tests), reviewed before any pilot seed is drawn; (3) the pilot run and a result note; (4) the S2 preregistration, or a documented reduced-scope / NO-GO decision (§7).

## 1. Questions (pilot, all descriptive or engineering)

- **Q1 (numerics):** can q_v(t) be computed on N ≳ 2¹⁸ trees up to half-time T = 2¹² with a *certified* truncation error far below sampling error, within a 1-core / 2-GiB budget?
- **Q2 (power):** how many trees × sources would give a 95 % interval half-width ≤ 0.03 on a window slope? The two literature targets differ by only 4/3 − 16/13 ≈ 0.103 (the volume-growth values differ by 0.4), so precision is the central question.
- **Q3 (window):** in which dyadic half-time window, if any, does d_s,eff(t) look stable, and how strongly does it drift at small t (pre-asymptotic regime)? Is it size-independent at fixed t, as expected when t is far below the mixing time?
- **Q4 (bias):** how does q_v(t) depend on the degree of the source, and how much do within-tree sources correlate (design effect)?

## 2. Mathematical reference (literature, not measured)

- **CAY (uniform labelled tree on N vertices).** A uniform source in a uniform labelled tree converges locally to Kesten's tree (the critical Poisson(1) Galton–Watson tree conditioned to survive, i.e. the incipient infinite cluster on trees). The simple random walk on it has spectral dimension **4/3** (Kesten 1986; Barlow & Kumagai, *Random walk on the incipient infinite cluster on trees*, Illinois J. Math. 50 (2006) 33–65, which treats quenched and annealed return-probability bounds). Scaling limit: Aldous' CRT, walk dimension 3, so displacement ~ t^(1/3) and mixing time ~ N^(3/2).
- **UST of Z².** Spectral dimension **16/13**, walk dimension 13/5, volume exponent 8/5 (Barlow & Masson, Commun. Math. Phys. 305 (2011) 23–57). The torus UST agrees with it on scales small compared with L (as in D2 §3).
- These are **asymptotic** statements (t → ∞ after N → ∞), with possible logarithmic fluctuations in the quenched case. Finite-t values may differ substantially; the pilot measures how much. No finite-t prediction is made.
- **Finite-state floor (S0 §2):** trees are bipartite, so the even-time floor is 2π(v) = deg(v)/(N−1). The S0 10× headroom rule applies. A scaling-only illustration, **not a prediction or lower bound**, at N = 2¹⁶, t = 2¹², degree 2 and unit prefactor q(t) ≈ t^(−2/3) = 1/256 gives q(t)/[deg(v)/(N−1)] ≈ 128, **not ≥ 10⁴**. Actual prefactors and source degrees vary. Mixing and finite-size effects must be measured; N^(3/2) is a CAY scaling heuristic, not a certified mixing bound for these finite instances. The 10× headroom criterion remains an empirical gate (P5).

## 3. Observable and numerical method (frozen)

Observable exactly as S0 §2: q_v(t) = [P^(2t)]_vv for the simple random walk (no holding), sources uniform without replacement, **annealed** average q̄(t) = mean over all (tree, source) pairs **before** logarithms, dyadic slope d_s,eff(t) = −2 log₂(q̄(2t)/q̄(t)). Half-times t ∈ {1, 2, 4, …, T}, T = 2¹² by default (§6 ladder).

**Killed-ball kernel with certified bound (new; replaces the full-graph S0 kernel, whose 10⁸ operation cap is far too small here).** For source v and radius R, let P_R be the walk killed on leaving the tree-distance ball B(v, R). Then for every s ≤ 2T

  [P_R^s]_vv ≤ [P^s]_vv ≤ [P_R^s]_vv + m_R(s),  with m_R(s) = 1 − Σ_x [P_R^s](v, x),

because a path that returns at step s without leaving B is counted in the first term and every other returning path has left B by step s (killed mass is non-decreasing). The kernel iterates the sparse sub-stochastic matrix for 2T steps from δ_v and reads q directly at s = 2t. Exact when R ≥ 2T.
- **Radius rule:** start at R = 64; double R until m_R(2T) ≤ η · [P_R^(2T)]_vv with **η = 10⁻⁴**, or R ≥ 2T. Reported value: the lower bound [P_R^(2t)]_vv; relative error ≤ η at all t ≤ T (m_R is non-decreasing and q is non-increasing in even time for a reversible walk — the latter is a known fact, checked numerically in P0). The effect on any dyadic slope is ≤ 2·log₂(1+η) ≈ 3·10⁻⁴.
- **Internal consistency check:** for t ≤ T the reversibility identity of S0 applied to P_R (still symmetric with respect to the degree weights of G) must reproduce the directly read q to ≤ 10⁻¹² absolute.
- **Per-source cost cap:** 2T · nnz(P_R) ≤ 2·10⁹ edge-steps; a source over the cap is recorded as OVER_CAP (never silently dropped), and the §6 ladder applies.

**Estimators reported (none gated):** (a) annealed slope of q̄ at each dyadic t; (b) window slope d̂_W = −2·[ln q̄(t_hi) − ln q̄(t_lo)] / ln(t_hi/t_lo) for every dyadic window with ≥ 3 consecutive slopes and t_lo ≥ 2³; (c) for comparison, mean over trees of per-tree slopes (fit-of-mean vs mean-of-fits, S0 §5).

## 4. Families, sizes, seeds

| Family | Role | Sizes | Trees × sources |
| --- | --- | --- | --- |
| CAY (Prüfer, D2 generator unchanged) | target 4/3 | N ∈ {2¹⁶, 2¹⁸} | 8 × 32 per size |
| UST of L×L torus (Wilson, D2 generator unchanged) | target 16/13 | L ∈ {128, 256} | 8 × 32 per size |
| RRT (D2 generator) | null, no finite dimension | N = 2¹⁶ | 4 × 32 |
| Z² torus, L = 64 | positive control (d_s = 2 built in) | — | 32 fixed sources, compared with S0 Fourier |
| CAY exact enumeration, N = 5, 6, 7 | exact annealed reference | all N^(N−2) trees, all vertices | rational arithmetic, t = 1…4 |

- **Seeds:** `seed_base = 2036101301`, disjoint from the D2 base 2036101101 and from every seed constant in `configs/`, `docs/`, `src/`, `tests/` (grep at `d05ffbe`). Rule as in D2: `np.random.SeedSequence([seed_base, i_family, i_size, i_rep])`, PCG64, family order CAY, UST, RRT; sources from a child of the same sequence. **S2 must use a different base.** The frozen D2 instances are not used, so that the pilot cannot borrow information from, or contaminate, the D2 record.
- Sizes are deliberately below D2's: at t ≤ 2¹² the ball of a killed walk is far smaller than N, so cost depends on T, not N, and size-independence (P5) is the check that justifies small instances.

## 5. Pilot outputs and engineering STOP gates

**STOP gates (any failure: report FAIL, no pilot interpretation, investigate before S2):**
- **P0a, exact reference:** pipeline annealed q(t), t = 1…4, on all labelled trees with N = 5, 6, 7 (all vertices as sources) equals the exact rational enumeration to ≤ 10⁻¹².
- **P0b, kernel agreement:** on 3 instances per family at N ≤ 4096 and T = 2⁸, the killed-ball kernel with R ≥ 2T equals the S0 full-graph kernel (`graph_even_returns`) to ≤ 10⁻¹²; with forced small R the certified bracket contains the exact value in every case.
- **P0c, positive control:** Z² torus L = 64, t ≤ 2⁸: killed-ball q within the certified bracket of the S0 Fourier value, and the bracket width ≤ η·q.
- **P0d, provenance:** manifest with code revision, config SHA-256, Python/NumPy/SciPy versions, seed tuples; byte-identical numeric CSV on a second same-environment run of one CAY tree.

**Reported (descriptive, no tolerance):**
- **P1 cost:** per-source wall time, R, |B(v, R)|, edge-steps, peak memory; projection of CPU time for the S2 candidate designs.
- **P2 curves:** d_s,eff(t) for every family, size and window; d̂_W for every admissible window; per-tree slopes.
- **P3 uncertainty and power for the *actual annealed estimator*:** fix S = 32 sources per tree in S2 projections (no unmeasured extrapolation to other S). For each window W = (lo, hi), let Qᵢ(t) = (1/S) Σ_v qᵢ,v(t), and Q̄(t) = (1/n) Σᵢ Qᵢ(t), where **trees** i = 1,…,n are the independent units. The primary estimate is d̂_W = −2[ln Q̄(hi) − ln Q̄(lo)]/ln(hi/lo). Compute tree-level delta-method influences ψᵢ = −2/ln(hi/lo) × [(Qᵢ(hi)−Q̄(hi))/Q̄(hi) − (Qᵢ(lo)−Q̄(lo))/Q̄(lo)]. Their sample variance s²_ψ = Σᵢ(ψᵢ−mean ψ)²/(n−1) estimates variance **per independent tree**, including finite-S source noise and covariance between times. With n = 8 at each positive-family size, set U = (n−1)s²_ψ/χ²_(0.05,n−1) as a **normal-theory, approximate 95% upper variance limit**, not a nonparametric guarantee. At a candidate gated count n′ ≥ 8 with S = 32, project h(n′) = t_(0.975,n′−1) √(U/n′). Report also results with 3U and whole-tree bootstrap (4096 deterministic resamples, separately seeded; descriptive percentile intervals), plus within-tree delete-one-source jackknife and estimates from mean-of-tree-slopes. The latter do **not** substitute for the primary estimator's variance. If influence distributions are grossly skewed, dominated by one tree, or U = 0 with n = 8, classify the power projection as UNRELIABLE rather than GO. Identify the smallest integer n′ within 180 CPU-min under measured cost (include tree generation, walk kernels, manifests).
- **P4 degree bias:** mean q_v(t) by source degree class (1, 2, ≥3) at each t, and the share of the annealed mean from leaves.
- **P5 size check:** for each candidate W shared between both sizes, estimate the large-minus-small *annealed* window-slope difference using the independent trees at each size and tree-level delta-method standard errors. Require a **90% two-sided CI entirely inside [−0.03, +0.03]** (equivalence/TOST criterion); merely including zero is insufficient. Report point difference, CI, and failure or indeterminacy. At every candidate window's t_hi, calculate headroom **per sampled source** q_v(t_hi)/[deg(v)/(N−1)] and require the minimum ≥ 10. Report the full distribution and any censored or OVER_CAP sources; never drop them silently.
- **P6 null:** RRT curves and headroom, expected to show no stable window (not gated).

## 6. Budget, ladder and stops

- 1 core, ≤ 2 GiB, **≤ 120 CPU-min for the whole pilot**, local or CI runner; no Lightsail, no network during the run, no paid service.
- **Sizing illustration, not a benchmark:** an 8192-step sparse update on ~5·10⁴ directed edges would require ≈ 4·10⁸ edge-steps **per source**, before radius doubling, graph generation or repeated windows. No CPU-seconds-per-source claim is justified without an actual benchmark; memory usage and time may force the ladder. The total 120 CPU-min pilot stop overrides projected work; a larger killed ball or poor locality can invalidate the initial estimates.
- **Ladder (decided on cost only, from tree 0 of the smallest size of each family, before any other tree):** if the projected family time exceeds 45 CPU-min or any source is OVER_CAP, set T = 2¹¹; if still over, T = 2¹⁰; if still over, stop that family and record BLOCKED (budget). Tree 0's values still count. The ladder must not be applied on the basis of q values.
- Hard stop at 1.5× the projected time or 120 CPU-min total; partial results are reported as partial.

## 7. Decision rule for the next step (fixed now)

Let W* be, per family, the admissible window (§3, headroom ≥ 10× **for every sampled source at t_hi**, certified relative error ≤ η, the P5 **90% equivalence CI** wholly within ±0.03, and absolute difference of any two adjacent dyadic slopes within the window ≤ 0.10). Select among qualifying windows the one with smallest projected half-width at the larger pilot size; break ties by earlier t_lo and then smaller t_hi. Report the number of tested windows and all failures. Using the revised P3 tree-influence variance projection at **fixed S = 32** and the measured P1 cost model, with an S2 budget of ≤ 180 CPU-min per family (D2 budget), 1 core, 2 GiB:

- **GO (full S2):** both CAY and UST reach h ≤ 0.03 on W*. S2 preregisters CAY and UST with fresh seeds, W*, n_trees and S, and **tolerances set before any S2 draw**, disclosing the pilot values and the pilot drift.
- **GO (reduced):** **both** families qualify with h ≤ 0.05, but the full criterion is not met. S2 is preregistered with that precision and the explicit consequence: h = 0.05 for each separate family yields a combined difference uncertainty that may be too wide to resolve the target gap 0.103. If only one family qualifies, report its feasibility as a descriptive finding, **not** a two-family GO.
- **NO-GO (scoped):** otherwise, including no admissible window, failed size equivalence, over-budget source/radius, or an unreliable variance projection. Record the result as "two-family spectral calibration not demonstrated feasible at this budget" (not proof of mathematical impossibility). Decide in Issue #37 whether to change method (e.g. a Lanczos/heat-kernel trace estimator) or scope. Always retain negative pilot results.

Whatever the branch, the pilot does **not** establish that the instrument recovers 4/3 or 16/13; agreement or disagreement of pilot values with the targets is reported as a numerical observation only.

## 8. Threats and alternatives (stated in advance)

- **Slow convergence and equivalence power:** pre-asymptotic drift may dominate up to T = 2¹², and only eight trees per size may be insufficient to establish ±0.03 size equivalence. Then no window passes and a scoped NO-GO/undetermined outcome is honest, not a reason to widen tolerances after observing data.
- **Annealed vs quenched:** the annealed mean is dominated by sources with large return probability (leaves near short dead ends). The literature exponent applies to both, but finite-t biases differ; estimator (c) is reported to expose this.
- **Fit-and-test leakage:** pilot curves inform W*, n_trees and S only; the S2 test uses fresh seeds and fixed tolerances.
- **Monte Carlo walkers** were considered and rejected for the default: at t = 2¹², q ~ 10⁻³, so a 1 % relative error needs ~10⁷ walkers per curve point. They remain a fallback only with a new version.
- **Reviewer independence:** a later-pass review by a different session is required before the implementation PR; a different-model-family review is required before any interpretation beyond instrument calibration (Issue #37).

## 9. Provenance

Implementation (later PR): `src/emergence_lab/spectral_s1.py`, tests `tests/test_spectral_s1.py`, result note `docs/experiments/YYYY-MM-DD-spectral-s1-pilot.md` with CSV and manifest (release asset if > 5 MiB, as D2-G4).

References: H. Kesten, *Subdiffusive behavior of random walk on a random cluster*, Ann. IHP Probab. Stat. 22 (1986) 425–487; M. T. Barlow & T. Kumagai, Illinois J. Math. 50 (2006) 33–65, [Project Euclid](https://projecteuclid.org/euclid.ijm/1258059469); M. T. Barlow & R. Masson, Commun. Math. Phys. 305 (2011) 23–57; D. Aldous, *The continuum random tree I*, Ann. Probab. 19 (1991) 1–28. Bibliographic details to be re-checked by the reviewer.

## 10. v0.2 later-pass corrections (2026-10-14, before any pilot sample)

Review of the proposed v0.1 design found: (1) the ≥10⁴ finite-size headroom was an incorrect heuristic; (2) the power calculation used mean-of-tree-slopes variance despite defining slope-of-means as the primary estimator; (3) a CI containing zero does not establish size equivalence; (4) the reduced GO condition could pass with one unusable family; (5) the sparse-kernel runtime forecast was unsupported. The changes above repair these design errors **before** any pilot tree is sampled. The 0.03 equivalence margin is a prospective engineering choice, smaller than one third of the 0.103 target gap; it is not a demonstrated physical threshold. The ±0.10 adjacent-slope stability threshold preserves the original proposal's descriptive drift limit. Confirm the new design in a separate implementation review before the P0 tests and any pilot measurements. See [later-pass review](experiments/2026-10-14-s1-prereg-review.md).
