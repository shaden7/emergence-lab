# D1 — volume-growth dimension estimator calibration (Issue #4), preregistration v1.0

**Status:** PROPOSED DESIGN, no implementation and no numerical output on any random graph. It freezes when it is merged to `main`; any later change to a preregistered parameter needs a new version and an explicit deviation note.
**Date:** 2026-10-11. **Base:** `main` `798dd72`. **Issue:** [#4](https://github.com/shaden7/emergence-lab/issues/4), deliverable 1 ("research-design document with preregistered observables, tests, null models and compute budget"). **Config:** [`configs/dimension_d1.json`](../configs/dimension_d1.json).
**Author:** Director session `rd-claude-20261011T005644Z-6efe9a` (see the PR). Producer self-review only; a later-pass review by a different session is required before merge.

## 0. What this is and is not

- **It is** a calibration of one *measuring instrument*: a scale-dependent volume-growth dimension on graphs, with fixed decision rules, positive controls, adversarial nulls and a compute budget.
- **It is not** a search for emergent space. Every graph used here either has its dimension **encoded by construction** (lattices, random geometric graphs embedded in a torus) or is a **null** without any finite Euclidean dimension. A recovered "2" on a 2D torus is an input, not a discovery (Issue #4; [RESEARCH_DIRECTOR.md](RESEARCH_DIRECTOR.md), *Substrate neutrality*).
- Graphs are a convenient relational test bed, not an ontological commitment ([REPRESENTATION_STRATEGY.md](REPRESENTATION_STRATEGY.md)). Spectral dimension is out of scope for v1.0; Issue #4 makes it an optional second method after this one is calibrated.
- Phase-0 constraint **C4** applies: the Ising calibration does not validate this estimator; it needs its own controls, which this document defines.

## 1. Question and hypotheses

**Q.** For which graph classes and scale windows does the dyadic volume-growth estimator below (a) return the encoded dimension within a declared tolerance, and (b) refuse to report a finite dimension where none exists?

- **H-pos (methodological hypothesis):** on 2D random geometric graphs with mean degree 12, the estimator returns a plateau with |d̂ − 2| ≤ 0.15, stable across three sizes.
- **H-null (methodological hypothesis):** on expander-like and exponentially growing graphs (random 4-regular, subdivided binary tree) the estimator never returns `PLATEAU`.
- **H-SW (literature-motivated hypothesis):** on a 2D torus with Newman–Watts shortcuts, any plateau near 2 is confined to scales below a crossover length of order ξ = (2p)^(−1/2) [NW99]; beyond it d_eff rises.

## 2. Observable and estimator (definitions)

For a connected graph G with N vertices and graph distance d_G, the ball is B(v, r) = {u : d_G(u, v) ≤ r}.

- **Sources.** For vertex-transitive lattices one source (vertex 0) suffices and is exact. For every random graph, S = 32 distinct sources are drawn uniformly without replacement from the giant component, using the replicate's own stream. B̄(r) is the mean of |B(v, r)| over sources.
- **Dyadic effective dimension:** d_eff(r) = log₂( B̄(2r) / B̄(r) ), evaluated at r ∈ {4, 8, 16, …}. This is the discrete form of d log|B| / d log r in Issue #4.
- **Admissible scales:** A = { r ∈ {4, 8, 16, …} : 8 · B̄(2r) ≤ N }, where N is the giant-component size. The lower cut r_min = 4 excludes the smallest lattice scales; the guard B̄(2r) ≤ N/8 excludes finite-size saturation. Neither cut uses d_eff values.
- **Verdict** (per graph or replicate), with ε = 0.15:
  - `INSUFFICIENT_RANGE` if |A| < 3. No dimension is reported.
  - Otherwise, consider every run of ≥ 3 *consecutive* admissible scales whose d_eff values have max − min ≤ ε. If none exists, the verdict is `NO_PLATEAU`.
  - Otherwise the verdict is `PLATEAU`. Among valid runs, choose the one with the largest last scale r_last, and break ties by length. Report d̂ = d_eff(r_last), the window [r_first, 2·r_last], and d_eff at the next admissible scale after the run if it exists ("post-window drift").
- **Why d̂ is taken at the largest scale:** on lattices, d_eff approaches d from below with an O(1/r) correction (§4). The run mean would carry a larger bias.
- **Design disclosure:** ε, r_min and the N/8 guard were chosen while looking at the *analytic* lattice table in §4, and at nothing else. The lattice gate therefore checks the implementation, not the choice of ε. The random-graph gates (D-G2…D-G4) are the actual tests of these choices, and no random-graph output exists at freeze time.

## 3. Graph families, sizes and seeds

All tori are periodic. "Replicate" means an independently generated graph.

| Family | Role | Sizes | Replicates × sources |
| --- | --- | --- | --- |
| Z¹ ring, Z² torus, Z³ torus (nearest neighbour) | exact positive control | Z¹: L ∈ {1024, 4096, 16384}; Z²: L ∈ {256, 512, 1024}; Z³: L ∈ {144, 168, 192} | 1 × 1 (vertex-transitive) |
| RGG-2D: N points uniform in the unit 2-torus, edge iff Euclidean torus distance < ρ, ρ = √(k̄/(πN)), k̄ = 12 | non-lattice positive control (dimension encoded by the embedding) | N ∈ {2¹⁷, 2¹⁹, 2²¹} | 8 × 32 |
| Random 4-regular (configuration model; self-loops and multi-edges dropped, so a few vertices have degree < 4; giant component) | null (expander) | N ∈ {2¹⁶, 2¹⁸, 2²⁰} | 8 × 32 |
| Subdivided binary tree: complete binary tree of depth h, each edge replaced by a path of ℓ = 4 edges | null (exponential growth with a 1D short-scale regime) | h ∈ {14, 16, 18} | 1 tree, 8 × 32 source draws |
| NW-2D: Z² torus L = 512 plus Newman–Watts shortcuts (each of the 2N lattice edges independently adds, with probability p, one edge between two uniform random vertices) | adversarial crossover | p ∈ {1e-4, 1e-3, 1e-2} | 8 × 32 |

- **Seeds:** `seed_base = 2035101101`, disjoint from all earlier seed bases in `configs/` and the preregistrations. Each (family index, size index, replicate index) gets `np.random.SeedSequence([seed_base, i_family, i_size, i_rep])` with NumPy's default PCG64. Source draws use a child of the same sequence. Independence of pseudorandom streams is a modelling assumption.
- **3D RGG is not run.** At k̄ ≈ 24, three admissible dyadic scales starting at r = 8 would need N of order 10⁷, which is outside the budget (§8). This is the documented feasibility rationale Issue #4 allows.

## 4. Analytic reference table (proved, not measured)

On Zᵈ with the graph (L¹) metric, |B(r)| = Σ_{k=0}^{d} 2ᵏ C(d,k) C(r,k) (standard lattice-point count). On a torus the ball equals the infinite-lattice ball whenever 2r < L/2. The N/8 guard implies this for every size above. The values follow from the formula; they are not simulation output.

| r | Z¹ |B| / d_eff | Z² |B| / d_eff | Z³ |B| / d_eff |
| --- | --- | --- | --- |
| 4 | 9 / 0.917538 | 41 / 1.822357 | 129 / 2.690945 |
| 8 | 17 / 0.956931 | 145 / 1.910203 | 833 / 2.852656 |
| 16 | 33 / 0.977974 | 545 / 1.954965 | 6017 / 2.929019 |
| 32 | 65 / 0.988859 | 2113 / 1.977464 | 45825 / 2.965305 |
| 64 | 129 / 0.994397 | 8321 / 1.988730 | 357889 / 2.982868 |

Expected verdicts under §2:

| Lattice | N | Admissible A | Verdict | Window | d̂ |
| --- | --- | --- | --- | --- | --- |
| Z¹ L=1024 | 1024 | 4, 8, 16 | PLATEAU | [4, 32] | 0.977974 |
| Z¹ L=4096 | 4096 | 4 … 64 | PLATEAU | [4, 128] | 0.994397 |
| Z¹ L=16384 | 16384 | 4 … 256 | PLATEAU | [4, 512] | 0.998593 |
| Z² L=256 | 65536 | 4, 8, 16 | PLATEAU | [4, 32] | 1.954965 |
| Z² L=512 | 262144 | 4 … 32 | PLATEAU | [8, 64] | 1.977464 |
| Z² L=1024 | 1048576 | 4 … 64 | PLATEAU | [8, 128] | 1.988730 |
| Z³ L=144, 168, 192 | 2.99M, 4.74M, 7.08M | 4 … 32 | PLATEAU | [8, 64] | 2.965305 |

Z³ fails ε at r ∈ {4, 8, 16} (range 0.238), so its window starts at 8. This is a known lattice effect, stated in advance.

## 5. Gates (fixed before any random-graph output)

- **D-G0, implementation exactness (STOP on failure).** For every lattice and every r used, the BFS ball count equals the formula in §4 as an integer. The verdicts, windows and d̂ equal the expected-verdict table to 1e-12. Graph generators are checked as well:
  - degree histogram and edge count for the lattices;
  - for the configuration model, the number of dropped self-loops and multi-edges, which is reported;
  - for the RGG, mean degree within 3 standard errors of the Poisson expectation k̄ = 12.
- **D-G1, positive control: lattices.** All 9 lattices are `PLATEAU` with |d̂ − d| ≤ 0.10. Given D-G0, this follows from §4; it is the declared tolerance, not an independent test.
- **D-G2, nulls (H-null).** No replicate of random 4-regular (24 replicates) or of the subdivided tree (24 source draws) returns `PLATEAU`. `INSUFFICIENT_RANGE` and `NO_PLATEAU` both pass. The tree is the stronger null: at r ≫ ℓ, d_eff grows roughly like r/ℓ, so the expected verdict is `NO_PLATEAU` rather than a trivial `INSUFFICIENT_RANGE`. Any `PLATEAU` here is a failure of the estimator, not a property of the null.
- **D-G3, non-lattice positive control (H-pos).**
  - At N = 2²¹, all 8 replicates are `PLATEAU`, and the replicate mean of d̂ has |mean − 2| ≤ 0.15.
  - The replicate means at N = 2¹⁹ and 2²¹ differ by ≤ 0.10.
  - Uncertainty is a Student-t 95 % interval over the 8 independent replicate d̂ values (C1: ≥ 4 independent replicates). A source bootstrap within each replicate is reported only descriptively.
  - The N = 2¹⁷ result is reported but not gated, because its admissible range is marginal.
- **D-G4, crossover adversary (H-SW).** At p = 1e-2 (ξ ≈ 7), no replicate returns a `PLATEAU` whose window upper end 2·r_last exceeds 32. At p ∈ {1e-4, 1e-3}, the full d_eff(r) curves, verdicts, windows and post-window drift are reported descriptively. If a plateau appears beyond 4ξ, it is reported as a counterexample to H-SW, not as a dimension.
- **D-G5, provenance and determinism (C5).**
  - Outputs: full per-replicate, per-source |B(v, r)| tables (CSV) and a JSON manifest. The manifest records the prereg blob SHA, config SHA-256, executing commit, Python/NumPy/SciPy versions, seed tuples, runtime, peak memory and file hashes.
  - Two invocations in the same environment are byte-identical except for timestamps and runtime.
  - Raw counts are small integers. If total output exceeds 5 MiB, it goes to a release asset with a pinned digest instead of Git.
- **Sensitivity (reported, never gated).** Verdicts are recomputed at ε ∈ {0.10, 0.20}, r_min ∈ {2, 8} and guard N/4 or N/16. A gate outcome that flips under these settings is flagged as fragile in the result note.

## 6. Decision rule

- **D0–D5 pass:** the estimator is *calibrated for* vertex-transitive lattices (exact) and 2D RGG at k̄ = 12 in the reported windows, and it rejects the tested nulls. This permits its use as a Phase-1 instrument with controls. It says nothing about emergent geometry.
- **D-G3 fails, others pass:** the estimator is validated only for lattices. Dimension statements about non-lattice graphs stay blocked until a corrected estimator or the spectral method is preregistered and calibrated.
- **D-G2 or D-G4 fails:** the estimator is rejected for dimension claims. A redesign is a new version.
- **D-G0 fails:** STOP. Fix the implementation, then rerun with the same seeds; this is not a design change.
- A failed gate is published. No ε, window, size, k̄, p or seed may change after any random-graph output exists.

## 7. Falsifiers and anticipated limitations

**Falsifiers of the method:**
- a `PLATEAU` on an exponentially growing null;
- a 2D plateau extending well past the shortcut crossover;
- RGG d̂ drifting with N beyond tolerance;
- a gate that flips under the mild sensitivity settings.

**Limitations:**
- Dyadic d_eff is coarse: three scales span only a factor of 8 in r.
- Graph distance on an RGG is a stretched Euclidean distance; the stretch factor tends to a constant only asymptotically [DMPP16]. Finite-k̄ distortion is part of what D-G3 measures.
- Volume growth is not the Hausdorff dimension in the measure-theoretic sense, and it is not the spectral dimension. They agree only in suitably regular settings ([literature review §2.1](LITERATURE_REVIEW_EMERGENT_SPACETIME_2026-10-09.md)).
- Fractal controls (e.g. the Sierpiński gasket, volume-growth dimension log 3 / log 2 [Bar98]) are left to a later version, because log-periodic oscillation would need its own tolerance design.

## 8. Budget

- Single core, ≤ 1.5 GiB RAM, ≤ 30 min wall for the full grid (the largest graph is the Z³ torus at 7.08M vertices; BFS via `scipy.sparse.csgraph`).
- No Lightsail deployment, no background job, no network access during the run, no spending.
- Implementation, tests and the run are a separate PR after this design is merged. CI pytest plus a deterministic local run are required before any result is reported.

## 9. References (to be re-checked by the later-pass review)

- [NW99] M. E. J. Newman, D. J. Watts, "Scaling and percolation in the small-world network model", *Phys. Rev. E* 60, 7332 (1999). Source of the crossover length ξ = (p k d)^(−1/d), here k = 1, d = 2.
- [WS98] D. J. Watts, S. H. Strogatz, "Collective dynamics of 'small-world' networks", *Nature* 393, 440 (1998).
- [Pen03] M. Penrose, *Random Geometric Graphs*, Oxford University Press (2003).
- [DMPP16] J. Díaz, D. Mitsche, G. Perarnau, X. Pérez-Giménez, "On the relation between graph distance and Euclidean distance in random geometric graphs", *Adv. Appl. Probab.* 48(3), 848–864 (2016).
- [Bar98] M. T. Barlow, "Diffusions on fractals", *Lectures on Probability Theory and Statistics (Saint-Flour 1995)*, LNM 1690, Springer (1998).
