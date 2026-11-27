# Issue #37 — joint spatial geometry/transport profile

**Status: design proposal only (2026-11-27).** No code, seeds, target samples, simulation, run authorization, or scientific acceptance result. This note proposes an operational resolution to the estimator-semantics question left by the 2026-11-27 handoff; it does not resolve or change Issue #37's owner-proposed acceptance criterion.

## Proposed design choice

Use a **joint spatial geometry/transport profile** as the comparison object:

\[
\mathcal D_M = \bigl(d_H^{\mathrm{eff}},\,d_s^{\mathrm{eff}}\bigr)_M,
\]

with a separately calibrated volume-growth observable and a separately calibrated return-probability observable in each model family.

This is **not** two estimates of one scalar dimension. In particular, do not impose \(d_H=d_s\), average them, or compress them into a single discrepancy score. The profile interpretation is already consistent with the adopted [S1 spectral-leg scope decision](S1_SPECTRAL_NEXT_DECISION.md) and [distinct-estimator comparison design](DIMENSION_COMPARISON_DESIGN.md): a non-spectral volume-growth family is the distinct estimator; a heat-kernel trace or pair-collision reimplementation of the same return observable is not.

The previous proposed 2×2 pairing of causal-set Myrheim–Meyer / midpoint with UIPT \(d_H/d_s\) is not a matched profile: MM and midpoint target a spacetime continuum dimension \(D\), while UIPT \(d_H\) and \(d_s\) are different spatial geometry and transport exponents. Keep the MM/midpoint finite-\(N\) bridge as a separate causal-set estimator branch. Do not combine those rows as if they measured the same object.

## Model families

### A. Causal-set spatial hypersurface

Use the **spatial-hypersurface diffusion** construction of Eichhorn, Surya and Versteegen (2019b), with the induced spatial metric from their 2019a construction; do not use a full-Hasse-graph walk.

- Start with the paper's \(2+1\)-dimensional Minkowski sprinkling and a maximal / inextendible antichain \(\mathcal A\). Freeze the finite spacetime region, sprinkling count law (unconditioned Poisson versus fixed-\(N\) conditional Poisson), antichain extraction and boundary convention from the source paper. The current repository's `causal_set_mm.sprinkle_diamond(n, 3, ...)` draws exactly \(N\) i.i.d. uniform points in a 3D diamond (fixed-\(N\), i.e. Poisson conditioned on \(N\)) and `causal_matrix` constructs their order; neither extracts the required antichain nor constructs the induced spatial distance. Do not silently substitute a greedy maximal antichain or treat fixed-\(N\) sampling as an unconditioned Poisson process.
- For \(p,q\in\mathcal A\), let \(r_m(p,q)\in J^+(p)\cap J^+(q)\) minimize \(V(r)\), where \(V(r)\) is the order-count analogue of \(\operatorname{vol}(J^-(r)\cap J^+(\Sigma))\) above the antichain, with the paper's strict endpoint convention. The published flat-background predistance is
  \[
  \widetilde{\mathbf d}(p,q)=2\left(\frac{V(r_m(p,q))}{\zeta_3}\right)^{1/3},
  \]
  followed by path minimisation over segments bounded by the paper's meso-scale \(\epsilon\) (called \(d_m\) in this project). Freeze the conversion and units explicitly. The direct predistance is not assumed to satisfy the triangle inequality; the segmented path construction is part of the metric definition.
- For a spatial cutoff \(d_c\), define
  \[
  \mathcal N_c(e)=\{e'\in\mathcal A:\mathbf d(e,e')\le d_c\}.
  \]
  The published walk includes \(e\) itself and chooses uniformly from \(\mathcal N_c(e)\), so \(P(e,e')=1/|\mathcal N_c(e)|\). The effective graph has variable degree and can split into small disconnected islands. With \(k_e=|\mathcal N_c(e)|\) (counting the self-choice once), each component \(C\) has stationary law \(\pi_C(e)=k_e/\sum_{x\in C}k_x\). The self-choice makes every component aperiodic. A singleton component has return probability and stationary floor 1: it is trapped, not evidence for a non-degenerate zero-dimensional scaling regime.
- The paper is explicitly **kinematical**: it averages sprinklings into flat \(\mathbb M^3\), not the causal-set path integral. The flat \(2+1\) background, antichain choice, and dimension-dependent distance reconstruction are assumptions, not emergent results.

The published geometry channel is the scaling of the spatial-neighbour count with \(d_c\), \(\overline{|\mathcal N_c|}\sim d_c^{d_H}\), above the discrete-asymptotic-silence scale. For each sprinkling \(g\), define \(\bar n_g(d_c)\) as the mean of \(|\mathcal N_c(e)|\) over its frozen antichain-root sample and use the per-sprinkling slope \(\log_2[\bar n_g(2d_c)/\bar n_g(d_c)]\); aggregate slopes across independent sprinklings. This is not the same metric observable as UIPT graph-hop ball growth; report the two geometry channels separately.

The published transport channel is the return probability of the self-inclusive, variable-degree walk. The paper uses the finite-difference estimator in its Eq. (10), with smoothing span \(n=2\) or \(3\), rather than the dyadic slope below. A project dyadic slope is a common analysis convention, not an exact reproduction of the published estimator; retain the paper's \(n=2,3\) formula as a sensitivity / replication arm.

The published numerical design used ten \(2+1\)-Minkowski sprinklings with about 1,600 antichain elements each, 30 starting points per antichain, and up to \(7\\cdot10^4\) walks per start. A roughly 5% drop in mean neighbour count was used to flag finite-boundary onset. The paper reports a plateau near \(d_s=2\) for \(d_c\\approx5.9\) and \(7.9\), while \(d_c\\approx3.5\) has no plateau and its walkers equilibrate on small islands; \(d_c\\approx9.8\) reaches the finite-boundary cutoff by \(\sigma\\approx7\). These are published finite-sample observations, not new project measurements or asymptotic theorems.

The regular-lattice control in the same paper is important: below one lattice spacing the graph consists of singleton islands and \(d_s=0\); at the lattice spacing it becomes connected and the intermediate-time value is \(d_s=2\). The limit \(d_c\\to0\), where every vertex is isolated and \(d_s=0\), is therefore a **degenerate no-transport limit**, not by itself evidence for a nontrivial ultraviolet scaling regime. The causal-set IR reference for a future finite study must be a predeclared boundary-free, continuum-like plateau (if one exists), not the thermodynamic limit of this finite antichain.

The 2026 Boguña–Krioukov finite-cone link-statistics preprint concerns full-Hasse link sampling. It does **not** directly derive a bias for this spatial-hypersurface operator. It is an additional reason not to substitute an unqualified full-Hasse walk for the selected finite-neighbour spatial operator.

### B. Type-II UIPT

Use the infinite **Type-II uniform infinite planar triangulation**: parallel edges are allowed, self-loops are not.

- Angel (2003), Section 2, equations (2.3)–(2.4) and Theorem 1.10, gives an exact local peeling sampler for Type-II UIPT neighbourhoods. The repository still lacks its implementation and the required boundary-order / rotation-system representation.
- Preserve parallel edges as distinct half-edges in the random walk. The integrated S0 MultiGraph path is the post-sampling adjacency representation; it is not itself a planar-map sampler.
- **Primary root law:** use the canonical oriented-root-edge UIPT for both profile components, matching Angel's rooted peeling construction and the rooted law in the cited UIPT results. For a finite spherical Type-II triangulation with \(N\) vertices and \(E=3N-6\), the origin of a uniform oriented root edge has \(P_E(v)=d(v)/(2E)\). A uniform-vertex sensitivity arm may reweight by
  \[
  \frac{dP_V}{dP_E}(\rho)=\frac{\bar d_N}{d_\rho},
  \qquad \bar d_N=6-\frac{12}{N},
  \]
  with infinite-limit factor \(6/d_\rho\). Root degree counts parallel half-edges. Keep the reweighted arm separate and propagate its weights into uncertainty; do not mix root laws within one profile.
- **Period and finite-map floor:** Type-II triangulations are not bipartite: every triangular face has a boundary closed walk of odd length, so the connected simple random walk has period 1. For finite-map controls, the stationary return floor at root \(\rho\) is \(\pi(\rho)=d_\rho/(2E)\), not \(1/N\) and not the bipartite even-time value \(2\pi(\rho)\). The infinite-UIPT local-neighborhood sample has no finite-map stationary floor; use local-radius and boundary censoring instead.
- Angel's ball-volume theorem gives the asymptotic volume-growth exponent \(d_H=4\), up to polylogarithmic factors. Gwynne–Miller prove the almost-sure spectral dimension \(d_s=2\) for Type-II UIPT. Gwynne–Hutchcroft prove the typical graph-distance displacement exponent \(1/4\), i.e. walk dimension \(d_w=4\) in the asymptotic exponent sense.

These are asymptotic mathematical results, not finite-scale measurements by this repository. In particular, the pair \((4,2)\) is **not** evidence of a short-scale flow. The finite-time \(d_s^{\mathrm{eff}}\) curve must be measured; it is not determined by the asymptotic theorem.

## Observable contract

The two components are reported separately for each model.

### Geometry: volume growth

Use separate local slopes for the two metric observables:

\[
d_{H,\mathrm{UIPT},g}^{\mathrm{eff}}(r)=
\log_2\frac{\bar B_g(2r)}{\bar B_g(r)},
\qquad
d_{H,\mathrm{CS},g}^{\mathrm{eff}}(d_c)=
\log_2\frac{\bar n_g(2d_c)}{\bar n_g(d_c)}.
\]

For each independent realization \(g\), let \(\bar B_g(r)\) be the mean ball cardinality over its frozen root sample and \(\bar n_g(d_c)\) the mean spatial-neighbour count within that sprinkling. The primary finite-scale curves are the per-realization slopes shown above; summarize them across independent maps / sprinklings, preserving graph-level uncertainty and the paired geometry/transport covariance. In the basic UIPT peeling design there is one canonical root per independently sampled map; any additional roots are nested observations, not independent maps. The ratio of ensemble-pooled mean volumes is an annealed sensitivity curve, not a substitute for the per-realization estimator: Angel's almost-sure ball-growth theorem does not by itself identify the exponent of an annealed mean.

These are both volume-growth channels, but use different intrinsic metrics and scale parameters; do not identify their axes or pool their raw values.

The causal-set distance formula uses the assumed \(2+1\)-dimensional flat background and \(\zeta_3\). Its \(d_H\) channel is therefore a kinematical geometry control, not an independent derivation of spatial dimension. Existing D2 calibration on CAY/UST does not automatically validate either new model. UIPT graph-ball growth is closest to D2's observable; the causal-set induced-distance count needs its own exact controls and a reviewed transfer argument.

### Transport: return probability

For a fixed realization \(g\) and root \(\rho\), let \(Q_{g,\rho}(s)=P_g^s(\rho,\rho)\). Average over the frozen within-realization root sample to obtain \(Q_g(s)\), then define the per-realization slope

\[
d_{s,g}^{\mathrm{eff}}(s)=-2\log_2\frac{Q_g(2s)}{Q_g(s)}.
\]

The graph/map-level distribution of these slopes is the inferential unit. A slope formed after pooling return probabilities across independent maps is an annealed sensitivity, not the primary estimator; do not treat roots or walkers as independent graph replicates.

For UIPT, evaluate the even-time subsequence to match the cited \(P^{2n}(\rho,\rho)\) theorem and the S0 half-time convention. This is **not** a bipartiteness correction: Type-II triangulations are non-bipartite and have period 1. Determine the period of every finite-map control explicitly; do not apply a bipartite factor-of-two stationary floor to UIPT. Preserve Type-II half-edge multiplicity. For the causal-set spatial walk, retain the published self-inclusive transition rule as the primary replication target; also preregister any loop-free or constant-laziness variant as a **different operator**, not a silent implementation change. The common dyadic slope is a proposed cross-model analysis convention; reproduce the paper's Eq. (10) with \(n=2,3\) separately so that the published finite-difference choice is not silently replaced.

The current S0 kernel rejects self-loops and disconnected graphs. It cannot be applied unchanged to the causal-set spatial graph. A separate path is now implemented as `SelfInclusiveKernel` (PR #95, Main code commit `b153fd3373b8599cdf691ddf477645d42e023e0b`): it accepts simple, undirected, unweighted, loop-free `Graph` inputs, adds exactly one self-choice, computes full-step `P^s(e,e)`, and supports disconnected components with component-specific stationary floors. It rejects `MultiGraph`; it is not the UIPT kernel, does not construct antichains or induced spatial distances, and has not been run on Issue-37 target data. Its memory guard is an estimate, not an OS-enforced RSS limit. For the published causal-set transition rule, the stationary weight within a component is proportional to \(|\mathcal N_c(e)|\). Singleton components have return probability one and stationary floor one; they must be classified as **trapped / no admissible scaling window**, not converted into a positive dimension estimate.

## What counts as a cross-model result

The owner-proposed Issue #37 criterion asks for the same scale-dependent behaviour in at least two model classes and at least two independently calibrated estimators. Its own calibration example contrasts random-tree Hausdorff dimension 2 with spectral dimension 4/3. That example uses **different exponents**, so the issue does not explicitly require the two estimators to estimate one identical scalar. Do not equate, average, or directly compare the numerical values of d_H and d_s.

The proposed joint profile is therefore a defensible operationalization of the two-estimator requirement: d_H is the geometry / volume-growth observable, while d_s is the transport / return-probability observable. They must be calibrated separately on known-answer controls in each model family. When measured on the same realization, their errors are paired and their covariance must be reported; distinct observables are not statistically independent merely because they have different definitions.

- **Full ROBUST (recommended sufficient criterion):** both d_H and d_s show a predeclared qualitative ultraviolet decrease relative to each model's own admissible infrared reference, in both model classes. Each channel must pass its own positive, null, finite-size, boundary, root-law and operator/cutoff controls; uncertainty is computed at the independent map / sprinkling level; and the conclusion survives the preregistered scale-window sensitivity analysis. “Same behaviour” means the same direction / qualitative scale flow, **not equal exponents or a common numerical scale axis**. This is a conservative sufficient rule for the issue-level ROBUST label, not a claim that the two exponents are one quantity.
- **Transport-channel result only:** d_s decreases in both model classes but d_H does not. Report cross-model transport-channel behaviour narrowly; do not promote it to full two-estimator ROBUST. A stable geometry channel alongside changing transport is a geometry/transport split, not automatically an estimator artifact.
- **Model- or observable-dependent / ARTIFACT:** the apparent decrease is confined to one model or one operator, or is removed by a matched finite-size, boundary, trapping, root-law or cutoff control. Distinguish model dependence from a demonstrated measurement artifact; disagreement between d_H and d_s alone is not sufficient to call the effect an artifact.
- **UNDECIDABLE:** either model lacks an admissible non-degenerate infrared-to-ultraviolet window, graph-level power is inadequate, resource limits prevent the required replication, or operator / root-law / boundary conventions remain unresolved.

This is a proposed operational reading, not an amendment to the Issue #37 body or an authorization to run. It is better supported by the issue's own distinct-exponent calibration example than a same-scalar interpretation. Before target seeds or a final classification, the selected rule must be frozen in a reviewed preregistration. Pair-collision, a heat-kernel trace of the same operator, or a quenched re-aggregation of the same return data remains an algorithmic / aggregation cross-check, not an additional estimator family.
## Scale comparison: no arbitrary map

The scale variables are not interchangeable:

- Causal set: spatial cutoff \(d_c\), distance-reconstruction meso-scale \(d_m\), and external diffusion time \(\sigma\).
- UIPT: graph-ball radius \(r\) and random-walk time \(s\).

Do not identify \(d_c\) with \(r\), \(\sigma\) with \(s\), or set \(r=\sqrt{s}\). The UIPT asymptotic \(d_w=4\) is not a finite-scale conversion rule for the causal-set operator. Show separate axes and compare only predeclared within-model trends relative to each model's own microscopic and infrared references. If a cross-observable scale map becomes essential, estimate and justify a walk exponent separately; do not assume \(d_s=2d_H/d_w\) at finite scales.

## Calibration, uncertainty and controls

1. **Causal-set exact controls:** small antichains with explicit induced-distance matrices; a regular 2D lattice with the same self-inclusive transition convention (including the published threshold control: singleton islands below one lattice spacing, connected walk at the spacing); exact dense transition-matrix return probabilities; singleton, disconnected-island and finite-boundary adversaries. Check the spatial-volume count against exact lattice balls. Preserve all isolated vertices in the primary record.
2. **UIPT exact controls:** retain the existing small Type-II multigraph dense-oracle tests; add deterministic finite-map ball-count, root-reweight and period/stationary-floor oracles. For the half-kernel identity \(P^{2t}(\rho,\rho)=d_\rho\sum_x P^t(\rho,x)^2/d_x\), all endpoint degrees must be complete; exposing the UIPT through graph radius \(t+1\) is sufficient. The exact local sampler must be checked against its peeling transition probabilities, 2-gon closure convention and adaptive-boundary invariance. For finite-map controls use the period-1 root floor \(d_\rho/(2E)\); do not apply a finite stationary floor to the infinite-UIPT local sample.
3. **Root and replicate structure:** independent sprinklings / independent UIPT maps are the graph-level units. Roots and walkers are nested measurements, not independent graph replicates. Report graph-level uncertainty, within-graph source variation, and the paired covariance of geometry and transport measurements on the same map.
4. **Finite-size windows:** for causal sets, preregister the \(d_c,d_m,\sigma\) grid, the 5% boundary-loss check (or a stricter calibrated alternative), component-size distribution, stationary floors and a minimum admissible scaling-window rule. For UIPT, preregister local radius, complete endpoint-degree requirements, root weights, finite-map/boundary censoring, and a graph-level power calculation.
5. **Estimator controls:** use separate finite-graph references for volume growth and return probability. Do not reuse D2's CAY/UST design-effect floor as a UIPT or causal-set power assumption. Do not count walker count as graph-level sample size.
6. **Resource gate:** the exact Type-II target projection already exceeds the current S0 limits (100M edge-step operations / 512 MiB) at proposed sizes. Walk-coupled peeling and pair-collision are possible computational strategies, but remain unimplemented/unbenchmarked; pair-collision is an S0 algorithmic cross-check, not a second dimension estimator. The causal-set spatial-distance construction also needs a bounded benchmark before any target-size choice. No Lightsail run is proposed.

## Dependencies and stop conditions

The minimum implementation sequence is:

1. Freeze the causal-set paper's finite region, Poisson versus fixed-\(N\) conditional sampling law, maximal / inextendible antichain construction and finite-boundary convention. The existing \(D=3\) CS0 sprinkling is only a candidate primitive, not an already matching generator.
2. Implement the induced spatial predistance from the minimum-volume common-future element \(r_m(p,q)\), the order-count \(V(r_m)\), and segmented path minimisation at the frozen \(d_m=\epsilon\); test pair-specific missing-common-future and truncated-cone cases.
3. **Completed in PR #95:** implement a separate reversible transition-kernel abstraction for the self-inclusive, variable-degree, potentially disconnected spatial graph, with exact dense-oracle tests and component-specific stationary floors. Do not weaken S0's existing loop-free Type-II contract.
4. Implement Type-II UIPT peeling state with cyclic boundary order / rotation system, exact finite-component Boltzmann fillings, and tests for 2-gon closure, parallel edges, root degree, period-1 finite-map floors and adaptive peeling.
5. Calibrate each model's geometry and return-probability channels on deterministic controls; then run bounded non-gated resource benchmarks and graph-level variance / power estimates.
6. Only after the Issue #37 estimator criterion is explicitly settled: later-pass-review a versioned preregistration and create a separate run authorization.

No target seeds, target maps, full CS0 study, S2, deployment, paid API, or shared Lightsail work is authorized by this design.

## Literature and repository basis

- Eichhorn, Surya & Versteegen (2019a), *Induced spatial geometry from causal structure*, https://arxiv.org/abs/1809.06192 — the meso-scale induced spatial distance and minimum-volume common-future predistance.
- Eichhorn, Surya & Versteegen (2019b), *Spectral dimension on spatial hypersurfaces in causal set quantum gravity*, https://arxiv.org/abs/1905.13498 — especially §§II–IV.
- Angel (2003), *Growth and Percolation on the Uniform Infinite Planar Triangulation*, https://arxiv.org/abs/math/0208123 — especially §1.2.2, §2, equations (2.3)–(2.4), Theorem 1.10, and Theorem 1.2.
- Gwynne & Miller (2017; revised 2020), *Random walk on random planar maps: spectral dimension, resistance, and displacement*, https://arxiv.org/abs/1711.00836 — Type-II model definition and Theorem 1.6.
- Gwynne & Hutchcroft (2018), *Anomalous diffusion of random walk on random planar maps*, https://arxiv.org/abs/1807.01512 — Type-II UIPT displacement exponent, Theorem 1.1.
- Boguña & Krioukov (2026 preprint), *Sampling biases in sprinkled causal sets*, https://arxiv.org/abs/2610.03247 — full-Hasse link-statistics result; not a direct result for the spatial-hypersurface operator.
- Repository design basis: [S1 spectral-leg scope decision](S1_SPECTRAL_NEXT_DECISION.md), [distinct-estimator comparison design](DIMENSION_COMPARISON_DESIGN.md), [causal-set estimator bridge](ISSUE37_CAUSAL_SET_ESTIMATOR_BRIDGE_20261126.md), and [Type-II UIPT feasibility screen](ISSUE37_CROSS_MODEL_FEASIBILITY_20261126.md).

## Evidence classification and current status

- **Mathematical theorems (literature):** Type-II UIPT asymptotic \(d_H=4\) (with polylogarithmic bounds), \(d_s=2\), and displacement exponent \(1/4\).
- **Published numerical observations:** causal-set spatial-hypersurface \(d_s\) reduction in finite \(2+1\)-Minkowski sprinklings, with the paper's stated island and boundary limitations.
- **Derived / methodological:** the joint profile avoids equating distinct exponents; root-law reweighting and the stationary weights above follow from the specified transition laws.
- **Hypotheses / unverified:** whether the causal-set UV decrease persists in a non-degenerate scaling window after graph-level uncertainty and whether a corresponding UIPT finite-scale decrease exists.
- **Repository facts:** the separate self-inclusive disconnected reversible kernel is present on Main (PR #95); no complete causal-set spatial-hypersurface generator / induced-distance pipeline and no Type-II UIPT peeling implementation are present. The existing S0 kernel remains incompatible with the self-inclusive disconnected causal-set walk.
- **Decision:** retain Issue #37 as **UNDECIDABLE**. This document proposes a design interpretation, not a scientific outcome, an amendment to Issue #37's acceptance criterion, or a run authorization.


## Implementation status update (2026-11-27; PRs #95–#98)

- **PR #95** (`b153fd3373b8599cdf691ddf477645d42e023e0b`): separate self-inclusive reversible kernel for loop-free simple graphs, including disconnected components and singleton traps, with dense-matrix controls.
- **PR #96** (`25e77cc3f99bd406f6070c91858ee52111fe4914`): bounded exact order-theoretic spatial-geometry oracle, including initial-antichain validation, exclusive suspended volumes, minimum-common-future predistances and unrestricted Dijkstra path distances (`N <= 256`).
- **PR #97** (`2c545636a664ce7605d4aa5b018c8c8aac0adadd`): explicit project-owned rectangular (2+1)-Minkowski slab, unconditioned Poisson count with mean from the stated slab volume, exact strict order on represented binary64 coordinates and the shared 256-element cap. This is not a reconstruction of the underspecified published ESV 3D finite patch.
- **PR #98** (`c38d89c3127cea6cc9563870f5b5cd33276ff868`): enumerate all tied global minimum-volume witnesses and apply the spatial-side censor before Dijkstra; reject complex coordinate inputs before float conversion.

These are integrated engineering references, not a complete target pipeline. The side censor addresses spatial sides only. Still absent or uncalibrated: stochastic antichain boundary behaviour; future-boundary and central-root conventions; retained-pair fraction; scalable bitset/CSR suspended-volume calculation and SWB/SIL acceleration; continuum-distance error; model-specific d_H and d_s calibration; and the Type-II UIPT peeling implementation with cyclic boundary order.

PR #98 exact-head push / PR CI and post-merge Main CI passed (1,115 tests + 65 subtests in each run); its Main artifact contains 55 files and 12 manifests pinned to the merge commit. These are engineering and provenance observations only. No Issue-37 target seeds, maps, full CS0 study, S2, scientific acceptance or deployment occurred.

Issue #37 remains **UNDECIDABLE**. The next step is a reviewed calibration / power preregistration for the two distinct channels and two model classes, after the operational acceptance rule is frozen. No target data are authorized by this design note.
