# Issue #37 — bounded causal-set spatial-geometry reference

**Status: engineering reference candidate, 2026-11-27.** This note describes the bounded exact implementation on the current research branch. It is not a sprinkling generator, preregistration, target run, or scientific result. Issue #37 remains **UNDECIDABLE**.

## Why this step

The integrated self-inclusive random-walk kernel is only useful after the spatial antichain and its induced distance are defined. The 2018 construction of Eichhorn, Surya & Versteegen (ESV) gives the order-theoretic definition; the 2019 spectral-dimension paper applies diffusion to the resulting finite-neighbour graph.

Primary sources:

- ESV, [Induced Spatial Geometry from Causal Structure](https://arxiv.org/abs/1809.06192), especially §3, Eqs. (27)–(31), §4 and Appendix A.
- Eichhorn, Surya & Versteegen, [Spectral dimension on spatial hypersurfaces in causal set quantum gravity](https://arxiv.org/abs/1905.13498).
- Surya, [The causal set approach to quantum gravity](https://doi.org/10.1007/s41114-019-0023-1), for the explicit exclusive/inclusive `Fut` / `Past` conventions.

## Antichain and finite-region semantics

For a finite strict partial order `prec[i, j] == True` iff `i ≺ j`, choose the **set of all minimal elements**:

\[
\mathcal A = \{a\in C:\operatorname{Past}(a)=\varnothing\}.
\]

This is the paper's initial/past antichain, not a greedy maximal-antichain heuristic. In a finite poset it is an inextendible antichain: every nonminimal element has a finite descending chain that terminates at a minimal element. The implementation also accepts a caller-supplied antichain only after checking pairwise incomparability and that every other element is strictly to its future; mere maximality by inclusion is insufficient for this initial-surface construction.

ESV's numerical construction uses the antichain to the past of all other elements and assumes that, at sufficiently high sprinkling density, it hugs the initial boundary of the finite Minkowski region. That approximation is not guaranteed for an arbitrary finite poset. For its flat \(K=0\), three-spacetime-dimensional example, Appendix A reports \(L_t=L_x=L_y=60\), \(N=75{,}510\), and \(|\mathcal A|=1{,}571\). Those are **published paper parameters**, not project measurements.

The paper also explicitly warns that its finite region is not causally convex and has edge effects; such effects become more important in higher spacetime dimensions. A future target generator must therefore freeze the finite region, count law, initial boundary, antichain rule, root/edge censoring and future-cap convention before any seeds are drawn. The existing `causal_set_mm.sprinkle_diamond` is fixed-\(N\) conditional sampling in a causal diamond; it is not the paper's unconditioned Poisson sprinkling into its finite slab and must not be silently substituted.

## Exclusive volume and predistance

Use the exclusive causal future and past:

\[
\operatorname{Fut}(\mathcal A)=
\{x:\exists a\in\mathcal A,\ a\prec x\},
\qquad
\operatorname{Past}(c)=\{x:x\prec c\}.
\]

For each \(c\in\operatorname{Fut}(\mathcal A)\), the suspended order-volume is

\[
N(c)=|\operatorname{Fut}(\mathcal A)\cap\operatorname{Past}(c)|.
\]

For distinct \(a,b\in\mathcal A\), let
\(F(a,b)=\operatorname{Fut}(a)\cap\operatorname{Fut}(b)\) and

\[
V(a,b)=\min_{c\in F(a,b)}N(c).
\]

In spacetime dimension \(n\),

\[
\zeta_n=\frac{\pi^{(n-1)/2}}
{n\,\Gamma((n+1)/2)},\qquad
\widetilde d(a,b)=2\left(\frac{V(a,b)}{\zeta_n}\right)^{1/n}.
\]

The selected Issue-37 spatial model is \(2+1\)-dimensional Minkowski, so \(n=3\) and \(\zeta_3=\pi/3\). `Fut` and `Past` are exclusive: neither the antichain elements nor the candidate \(c\) are counted as interior elements. This matters at finite cardinality and is not interchangeable with inclusive intervals.

Two finite-boundary/degeneracy outcomes are kept explicit:

- If \(F(a,b)\) is empty **inside the frozen finite causal set**, the pair is censored (`+inf`), not assigned an invented distance.
- If the minimum strict suspended count is zero, the predistance is zero. It is not clipped to one or regularized. Such a finite-poset degeneracy must be reported and cannot be interpreted as a physical zero-dimensional regime.

## Full path-distance reference

The predistance need not satisfy the triangle inequality. For a meso-cutoff \(\ell>0\), allow a path edge only when the strict condition \(\widetilde d(a,b)<\ell\) holds, and minimize the sum of edge predistances over all finite paths on \(\mathcal A\). This is Eq. (31) of ESV and is exactly the shortest-path problem on the resulting undirected weighted graph.

The implementation in `src/emergence_lab/causal_set_spatial.py` is deliberately a **full-path reference oracle** using Dijkstra. It does not implement ESV's SWB/SIL search-space accelerations. A later optimized implementation must be checked against this unrestricted reference on small posets before being used at larger sizes.

## Implemented reference contract (branch candidate)

- Dense boolean strict-order input; validate irreflexivity, antisymmetry and transitivity.
- Hard cap `N <= 256` before the reference calculation. This is intentionally far below the paper's \(N=75{,}510\), \(|A|=1{,}571\); it is an exact oracle, not a production solver.
- Extract all minimal elements, or validate a supplied initial antichain (pairwise incomparable, with every other element strictly to its future).
- Compute exclusive suspended counts, minimum-common-future predistances and the full Eq. (31) shortest-path distance matrix.
- Return `+inf` for absent common futures / disconnected cutoff graphs; preserve zero-volume degeneracies.
- No coordinates, sprinkling, RNG, seeds, target samples, simulation, or deployment are involved.

The deterministic test suite includes: minimal-antichain/initial-surface controls; invalid antichain and poset rejection; strict endpoint-volume counts; a fixture where path minimization is strictly shorter than direct predistance; strict meso-cutoff behavior; absent-common-future censoring; zero-volume preservation; dimension/input/resource validation; input immutability; and vertex-relabeling invariance.

## Remaining dependencies and limits

1. **Not implemented:** a faithful finite \(2+1\)-Minkowski slab generator with unconditioned Poisson count law and the paper's boundary conventions.
2. **Not implemented:** scalable order representation, common-future minimum search, bitset/CSR suspended-volume calculation, or SWB/SIL acceleration. The dense oracle cannot be run on the published-scale example.
3. **Not calibrated:** boundary/root censoring, continuum-distance error, the discrete-asymptotic-silence scale, mesoscale window, or the spatial neighbour-count \(d_H^{\mathrm{eff}}\) curve.
4. **Not authorized:** target seeds, target maps, transport measurements, S2, or any scientific acceptance decision.

## Evidence classification

- **Mathematical fact:** minimal elements of a finite poset form an inextendible antichain; Dijkstra computes the minimum path sum for nonnegative edge weights.
- **Literature definition:** the exclusive suspended count, minimum-common-future predistance and meso-cutoff path metric above.
- **Engineering observation (PR candidate only):** deterministic fixtures test the implementation contract; CI must validate the exact PR head before integration.
- **Not established:** that a generated antichain hugs the intended continuum boundary, that the distance converges to the continuum metric for a selected finite region, or that any UV dimensional reduction is robust.

Issue #37 remains **UNDECIDABLE** until the model-specific calibration, independent graph-level uncertainty/power plan, criterion settlement, preregistration and separate authorization are complete.
