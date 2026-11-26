# Issue #37 — causal-map candidate screen

**Date:** 2026-11-26  
**Status:** design-only literature and implementation screen. No code, random seeds, target samples, simulation, pilot, S2 work, or experiment authorization.

## Decision

The causal map is a mathematically useful **paired transformation control**: adding horizontal edges to a critical Galton–Watson tree changes the asymptotic spectral dimension while preserving every root-centred volume ball. It is not selected as the next stochastic Issue #37 target.

The reason is scope, not an established resource no-go. The map is constructed from the same Galton–Watson tree conditioned to survive that underlies the terminal S1/S1b random-tree line. Comparing that tree with its causal-map transform would be a controlled intervention on one substrate, not an independent generative model family. Treating it as a way to reopen the random-tree spectral line would conflict with the current Issue #37 handoff. The model is related to 1+1-dimensional causal triangulations; it does not evade the existing exclusion of 2D CDT as a substitute for an independent family.

Retain it as an **analytic transformation control**. It may be reconsidered as one candidate model class in a future comparison against a genuinely independent family (for example causal sets or a separately justified random-map ensemble), but only after explicit scope approval and a new reviewed design.

## Literature model and established results

Curien, Hutchcroft and Nachmias study the infinite planar map \(\mathsf{Causal}(T_\infty)\) obtained from a critical, finite-positive-variance Galton–Watson plane tree conditioned to survive forever by adding horizontal edges between successive vertices in the cyclic ordering of each generation.

Their results in *Geometric and spectral properties of causal maps* (arXiv:1710.03137; JEMS 22 (2020), 3997–4024) include:

The offspring law matters when relating the model to the project's CAY work. The S1 preregistration (§2) identifies the local limit of a uniformly rooted finite CAY tree as the Kesten tree of a critical Poisson(1) Galton–Watson process. Since the causal-map theorem applies to every critical finite-variance offspring law, μ=Poisson(1) gives a CAY-matched causal-map variant. The geometric law μ(k)=2^{-(k+1)} is a different special case; its triangulated version gives UICT. These offspring laws must not be conflated.

- For the causal map, the spectral dimension is \(d_s=2\) almost surely and the typical displacement exponent is \(\nu=1/2\).
- The underlying conditioned tree has \(d_s=4/3\) and \(\nu=1/3\).
- The causal map has rooted volume-growth exponent \(\mathfrak g=2\).
- Horizontal distances at height \(r\) are sublinear but not polynomially smaller: the level diameter is \(o(r)\) and \(r^{1-o(1)}\). Under \(1/r\) metric rescaling, the local Gromov–Hausdorff limit collapses to a semi-infinite line.
- For the geometric offspring law, the triangulated construction gives the uniform infinite causal triangulation (UICT); the paper states that the causal-map and causal-triangulation geometries are qualitatively similar and that its results transfer to the triangulated version.

Primary source: https://arxiv.org/abs/1710.03137  
Published version: https://doi.org/10.4171/JEMS/1001  
Related CDT reference: https://arxiv.org/abs/0908.3643

These are asymptotic mathematical results. They do **not** establish a finite-scale spectral-dimension flow or a short-scale reduction from four dimensions to two. The pair \(d_s(T_\infty)=4/3\) and \(d_s(\mathsf{Causal}(T_\infty))=2\) compares two different graph walks; it is not a scale-dependent curve on one model.

## Exact structural relation: root-volume balls are unchanged

For every vertex \(v\), let \(h(v)\) be its generation (height) in the underlying tree and let \(\rho\) be the root. Tree edges change height by one; horizontal causal-map edges preserve height. The tree path gives \(d(\rho,v)\leq h(v)\), while every path from height zero to height \(h(v)\) needs at least \(h(v)\) vertical edges. Hence, in both graphs,

\[
d_{T_\infty}(\rho,v)
=
d_{\mathsf{Causal}(T_\infty)}(\rho,v)
=
h(v).
\]

Consequently, for every realization and every integer \(r\geq0\),

\[
B_{T_\infty}(\rho,r)
=
B_{\mathsf{Causal}(T_\infty)}(\rho,r)
=
\{v:h(v)\leq r\}.
\]

This is an exact deterministic identity, not a numerical observation. Root-centred volume-growth curves are identical before averaging and have the same exponent \(\mathfrak g=2\). The added horizontal edges change connectivity and random-walk diffusion, not root-ball membership. This is a useful example of why volume-growth and spectral dimensions must not be treated as interchangeable.

## Why this is not ready for the current Issue #37 target

### 1. Model independence and scope

The Poisson(1) causal map is a distinct planar-map graph, but it is a deterministic horizontal augmentation of the same Kesten-tree local limit underlying the terminal S1/S1b CAY line. The tree/map pair is therefore a paired transformation control, not two independent random generators. It cannot by itself establish robustness across independent generators, and a tree-versus-map spectral batch would revisit the terminal random-tree spectral line. The geometric-offspring UICT special case uses a different offspring law, but remains tree-derived and closely related to 1+1 CDT.

The existing Issue #37 feasibility decision explicitly excludes 2D CDT as an independent replacement for the tree line. The causal-map presentation is not identical to the triangulated UICT graph, but the shared conditioned-tree construction and the paper's transfer result mean it should not be presented as an unrelated model family.

### 2. Root law and estimator compatibility

The infinite model is canonically rooted at the spine root of (T_\infty). The root-law relation to the existing CAY work depends on the offspring law:

- For μ=Poisson(1), the rooted Kesten tree is exactly the local weak limit of a uniformly rooted finite CAY tree; this is the relationship stated in `docs/SPECTRAL_S1_PREREGISTRATION.md` §2. The Poisson causal-map variant therefore does not introduce a different asymptotic root law from CAY.
- The geometric law μ(k)=2^{-(k+1)} is a different conditioned-tree law (the UICT special case after triangulation), not the CAY Poisson law.
- D2 sampled 256 uniform vertices per finite CAY tree; S1/S1b sampled 32. A direct Kesten-tree construction supplies one canonical root per independent tree. The local root law is matched in the Poisson case, but D2's multi-source volume uncertainty model and S1's finite-size spectral power analysis do not automatically validate a one-root-per-tree design. A separate finite-size and graph-level variance/power plan would still be required.
- The S0 kernel can evaluate a fixed root, but its deterministic lattice calibration does not validate the causal-map random-walk operator: horizontal edges change degrees and transitions.

The exact root-ball identity means volume counts are unchanged by the map augmentation; the new observable is diffusion, not volume growth. The root is part of the model definition, not an implementation convenience.

### 3. Horizontal-edge convention and current graph code

The paper defines horizontal connections using the cyclic ordering of each generation. The exact finite-level convention for generations containing one or two vertices must be pinned before implementation: a literal cycle convention can raise loop or parallel-edge questions at those levels.

The current implementation is not a safe implicit answer:

- **src/emergence_lab/dimension_d1.py** defines **Graph** as an undirected simple graph; **_from_edges** removes self-loops and collapses duplicate edges.
- **src/emergence_lab/spectral_dimension.py::graph_even_returns** explicitly rejects loops, asymmetric adjacency and non-unit adjacency data.

If the source model counts degenerate cyclic edges with loop or parallel-edge multiplicity, passing them through the current builder changes the random walk. The paper's construction must be resolved at this edge-case level, or a multiplicity-preserving transition representation must be separately specified and calibrated. No such implementation is included in this screen.

### 4. Finite truncation and exact-kernel boundary

The S0 kernel propagates a row distribution for a maximum half-time \(T\), then uses reversibility to obtain \(P^{2T}(\rho,\rho)\). In a rooted causal map, support after \(T\) steps is confined to heights at most \(T\). The degree of every support vertex at height \(T\) depends on its children at height \(T+1\). Therefore a sufficient exact local construction for the requested return probabilities must include complete generations through at least \(T+1\), including all horizontal edges in those generations. A smaller cutoff would alter transition degrees in the support.

For a proposed local slope at \(t=128\), both \(q(128)\) and \(q(256)\) are needed, so the kernel's maximum half-time is \(T=256\) and the conservative generation cutoff is \(H=257\). This is a boundary-completeness condition for the exact root return, not a claim that a finite graph has the infinite model's asymptotic scaling window.

### 5. Conditional resource arithmetic — not a benchmark

For the mean-one geometric offspring law \(\mu(k)=2^{-(k+1)}\), the variance is \(2\). In the corresponding Kesten tree, the size-biased spine construction gives

\[
\mathbb E[Z_n]=1+2n,\qquad
\mathbb E[N_H]
=\sum_{n=0}^{H}(1+2n)
=(H+1)^2.
\]

At \(H=257\), \(\mathbb E[N_H]=66{,}564\). If the horizontal construction contributes at most one edge per vertex per generation, the undirected edge count is at most \(2N_H-1\), giving a directed-incidence upper estimate \(4N_H-2\). At the **expected** vertex count this is \(266{,}254\); multiplying by \(T=256\) gives an expected S0-style work proxy of \(68{,}161{,}024\), below the existing \(100{,}000{,}000\) proxy limit.

For comparison, the CAY-matched Poisson(1) law has variance (1), so \\(\mathbb E[Z_n]=1+n\\) and \\(\mathbb E[N_H]=(H+1)(H+2)/2=33{,}411\\) at (H=257). The same incidence bound gives an expected proxy of (133{,}642\times256=34{,}212{,}352) transition operations. This is a separate expectation-based estimate; the geometric-law proxy above must not be transferred to Poisson(1), or vice versa.

These are only conditional planning arithmetic. They assume the stated edge-count convention, do not resolve the one-/two-vertex layer issue, and are not worst-case bounds. Kesten-tree size is random; no tail probability, graph-level variance, high-quantile memory, wall-time benchmark, or power calculation has been measured. The current kernel still rejects any multiplicity-bearing representation. Therefore neither proxy is a feasibility PASS and neither authorizes a pilot.

## Decision and gates for any reconsideration

**Current decision: retain as an analytic transformation control; do not authorize a Causal Map target run.** No seeds, random graphs, target samples, finite-size fits or simulations were produced.

Before reconsideration, require all of the following in a separate reviewed design:

1. Explicit acceptance that this tree-derived planar map is a sufficiently distinct model class for the intended comparison; do not count the parent tree and its deterministic transform as independent families.
2. Exact definition of the horizontal-edge convention for generation sizes one and two, with multiplicity and loop handling matched to the cited model.
3. Specify the offspring and root law. For μ=Poisson(1), use the CAY local-limit relationship explicitly; for the geometric/UICT variant, treat the offspring law separately. The exact root-ball identity means the volume observable is unchanged, but a one-root-per-tree design still needs its own finite-size and graph-level variance/power plan; D2's S=256 multi-source uncertainty calibration is not automatically transferable.
4. A multiplicity-preserving random-walk operator if required by the source definition, with exact dense-matrix controls on small multigraphs.
5. A finite truncation proof for every requested return time, including the complete boundary generations and finite-volume/mixing censoring.
6. A non-gated resource and graph-size-tail plan with hard caps, followed by graph-level power analysis. No walker or source count may be treated as an independent graph replicate.
7. A separate preregistration, later-pass review and explicit run authorization before any new seeds or target samples.

The current Issue #37 next step remains the type-II/type-III UIPT root-law/operator bridge and a scalable multiplicity-preserving estimator, or a search for another genuinely independent model family. Keep Issue #37 **UNDECIDABLE** until its cross-model and independent-observable criteria are met. Do not reopen S1/S1b through this candidate.
