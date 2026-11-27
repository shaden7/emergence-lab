# Issue #37 — joint spatial geometry/transport profile

**Status: design proposal only (2026-11-27).** No code, seeds, target samples, simulation, run authorization, or scientific acceptance result. This note resolves the estimator-semantics question left by the 2026-11-27 handoff; it does not change Issue #37's owner-proposed guiding question.

## Decision

Use a **joint spatial geometry/transport profile** as the comparison object:

\[
\mathcal D_M = \bigl(d_H^{\mathrm{eff}},\,d_s^{\mathrm{eff}}\bigr)_M,
\]

with a separately calibrated volume-growth observable and a separately calibrated return-probability observable in each model family.

This is **not** two estimates of one scalar dimension. In particular, do not impose \(d_H=d_s\), average them, or compress them into a single discrepancy score. The profile interpretation is already consistent with the adopted [S1 spectral-leg scope decision](S1_SPECTRAL_NEXT_DECISION.md) and [distinct-estimator comparison design](DIMENSION_COMPARISON_DESIGN.md): a non-spectral volume-growth family is the distinct estimator; a heat-kernel trace or pair-collision reimplementation of the same return observable is not.

The previous proposed 2×2 pairing of causal-set Myrheim–Meyer / midpoint with UIPT \(d_H/d_s\) is not a matched profile: MM and midpoint target a spacetime continuum dimension \(D\), while UIPT \(d_H\) and \(d_s\) are different spatial geometry and transport exponents. Keep the MM/midpoint finite-\(N\) bridge as a separate causal-set estimator branch. Do not combine those rows as if they measured the same object.

## Model families

### A. Causal-set spatial hypersurface

Use the **spatial-hypersurface diffusion** construction of Eichhorn, Surya and Versteegen (2019), not a full-Hasse-graph walk.

- Start with a Poisson sprinkling into \(2+1\)-dimensional Minkowski spacetime and an inextendible antichain \(\mathcal A\).
- Reconstruct the induced spatial distance from causal information. The published flat-background predistance uses
  \[
  \widetilde{\mathbf d}(p,q)=2\left(\frac{V(\mathbf e)}{\zeta_3}\right)^{1/3},
  \]
  followed by path minimisation and a meso-scale cutoff \(d_m\).
- For a spatial cutoff \(d_c\), define
  \[
  \mathcal N_c(e)=\{e'\in\mathcal A:\mathbf d(e,e')\le d_c\}.
  \]
  The published walk includes \(e\) itself and chooses uniformly from \(\mathcal N_c(e)\), so \(P(e,e')=1/|\mathcal N_c(e)|\). The effective graph has variable degree and can split into small disconnected islands.
- The paper is explicitly **kinematical**: it averages sprinklings into flat \(\mathbb M^3\), not the causal-set path integral. The flat \(2+1\) background, antichain choice, and dimension-dependent distance reconstruction are assumptions, not emergent results.

The published geometry channel is the scaling of the spatial-neighbour count with \(d_c\), \(\overline{|\mathcal N_c|}\sim d_c^{d_H}\), above the discrete-asymptotic-silence scale. For a project estimate, define \(\bar n(d_c)\) as the mean of \(|\mathcal N_c(e)|\) over uniformly sampled antichain roots and use a local slope such as \(\log_2[\bar n(2d_c)/\bar n(d_c)]\). This is not the same metric observable as UIPT graph-hop ball growth; report the two geometry channels separately.

The published transport channel is the return probability of the self-inclusive, variable-degree walk. The paper uses the finite-difference estimator in its Eq. (10), with smoothing span \(n=2\) or \(3\), rather than the dyadic slope below. A project dyadic slope is a common analysis convention, not an exact reproduction of the published estimator; retain the paper's \(n=2,3\) formula as a sensitivity / replication arm.

The published numerical design used ten \(2+1\)-Minkowski sprinklings with about 1,600 antichain elements each, 30 starting points per antichain, and up to \(7\\cdot10^4\) walks per start. A roughly 5% drop in mean neighbour count was used to flag finite-boundary onset. The paper reports a plateau near \(d_s=2\) for \(d_c\\approx5.9\) and \(7.9\), while \(d_c\\approx3.5\) has no plateau and its walkers equilibrate on small islands; \(d_c\\approx9.8\) reaches the finite-boundary cutoff by \(\sigma\\approx7\). These are published finite-sample observations, not new project measurements or asymptotic theorems.

The regular-lattice control in the same paper is important: below one lattice spacing the graph consists of singleton islands and \(d_s=0\); at the lattice spacing it becomes connected and the intermediate-time value is \(d_s=2\). The limit \(d_c\\to0\), where every vertex is isolated and \(d_s=0\), is therefore a **degenerate no-transport limit**, not by itself evidence for a nontrivial ultraviolet scaling regime. The causal-set IR reference for a future finite study must be a predeclared boundary-free, continuum-like plateau (if one exists), not the thermodynamic limit of this finite antichain.

The 2026 Boguña–Krioukov finite-cone link-statistics preprint concerns full-Hasse link sampling. It does **not** directly derive a bias for this spatial-hypersurface operator. It is an additional reason not to substitute an unqualified full-Hasse walk for the selected finite-neighbour spatial operator.

### B. Type-II UIPT

Use the infinite **Type-II uniform infinite planar triangulation**: parallel edges are allowed, self-loops are not.

- Angel (2003), Section 2, equations (2.3)–(2.4) and Theorem 1.10, gives an exact local peeling sampler for Type-II UIPT neighbourhoods. The repository still lacks its implementation and the required boundary-order / rotation-system representation.
- Preserve parallel edges as distinct half-edges in the random walk. The integrated S0 MultiGraph path is the post-sampling adjacency representation; it is not itself a planar-map sampler.
- The natural rooted-map law is edge-rooted. For a finite spherical Type-II triangulation with \(N\) vertices, a uniform oriented root edge gives a degree-biased root vertex. Conversion to a uniform-vertex root law uses
  \[
  \frac{dP_V}{dP_E}(\rho)=\frac{\bar d_N}{d_\rho},
  \qquad \bar d_N=6-\frac{12}{N}.
  \]
  In the infinite limit the factor is \(6/d_\rho\). Root degree counts parallel edges. Freeze one root law for both profile components and carry its weights into uncertainty estimates.
- Angel's ball-volume theorem gives the asymptotic volume-growth exponent \(d_H=4\), up to polylogarithmic factors. Gwynne–Miller prove the almost-sure spectral dimension \(d_s=2\) for Type-II UIPT. Gwynne–Hutchcroft prove the typical graph-distance displacement exponent \(1/4\), i.e. walk dimension \(d_w=4\) in the asymptotic exponent sense.

These are asymptotic mathematical results, not finite-scale measurements by this repository. In particular, the pair \((4,2)\) is **not** evidence of a short-scale flow. The finite-time \(d_s^{\mathrm{eff}}\) curve must be measured; it is not determined by the asymptotic theorem.

## Observable contract

The two components are reported separately for each model.

### Geometry: volume growth

Use separate local slopes for the two metric observables:

\[
d_{H,\mathrm{UIPT}}^{\mathrm{eff}}(r)=
\log_2\frac{\overline B(2r)}{\overline B(r)},
\qquad
d_{H,\mathrm{CS}}^{\mathrm{eff}}(d_c)=
\log_2\frac{\bar n(2d_c)}{\bar n(d_c)}.
\]

Here \(\overline B(r)\) is the mean Type-II graph-ball cardinality under the frozen root law, while \(\bar n(d_c)\) is the causal-set spatial-neighbour count defined above. They are both volume-growth channels, but use different intrinsic metrics and scale parameters; do not identify their axes or pool their raw values.

The causal-set distance formula uses the assumed \(2+1\)-dimensional flat background and \(\zeta_3\). Its \(d_H\) channel is therefore a kinematical geometry control, not an independent derivation of spatial dimension. Existing D2 calibration on CAY/UST does not automatically validate either new model. UIPT graph-ball growth is closest to D2's observable; the causal-set induced-distance count needs its own exact controls and a reviewed transfer argument.

### Transport: return probability

For the specified reversible walk, let \(Q_M(s)\) be the root-averaged return probability after \(s\) physical steps. Define

\[
d_s^{\mathrm{eff}}(s)=-2\log_2\frac{Q_M(2s)}{Q_M(s)}.
\]

For UIPT, use even physical times to avoid bipartite parity effects and preserve the Type-II half-edge multiplicity. For the causal-set spatial walk, retain the published self-inclusive transition rule as the primary replication target; also preregister any loop-free or constant-laziness variant as a **different operator**, not a silent implementation change. The common dyadic slope is a proposed cross-model analysis convention; reproduce the paper's Eq. (10) with \(n=2,3\) separately so that the published finite-difference choice is not silently replaced.

The current S0 kernel rejects self-loops and disconnected graphs. It cannot be applied unchanged to the causal-set spatial graph. A separate reversible-kernel path must support self-inclusive transitions, variable stationary weights, disconnected components, and component-specific stationary floors. For the published causal-set transition rule, the stationary weight within a component is proportional to \(|\mathcal N_c(e)|\). Singleton components have return probability one and stationary floor one; they must be classified as **trapped / no admissible scaling window**, not converted into a positive dimension estimate.

## What counts as a cross-model result

The common question is whether the **transport** component \(d_s^{\mathrm{eff}}\) decreases toward the ultraviolet relative to each model's own infrared reference. For the finite causal-set sprinkling, that reference means a predeclared continuum-like plateau inside a boundary-free window (the published (d_c\approx5.9,7.9) plateaux are literature observations, not project tolerances); if no such window exists, no UV comparison is made. For UIPT, (d_s=2) is an asymptotic theorem anchor, while finite-time convergence to it must be calibrated. The geometry component \(d_H^{\mathrm{eff}}\) is a separately calibrated companion that shows whether transport changes while geometric volume growth remains stable; it is not a second vote for the same scalar.

- **Robust within these two model classes:** both model families show a predeclared, statistically resolved ultraviolet decrease in \(d_s^{\mathrm{eff}}\) relative to their own infrared reference, in non-degenerate windows, and the result survives each model's finite-size, boundary, root-law and operator/cutoff controls. Report the two geometry profiles alongside it. Do not require the raw \(d_H\) and \(d_s\) values to agree.
- **Model-/estimator-dependent:** the decrease appears only in one model family, only for one operator or cutoff convention, or disappears when island trapping, finite-volume equilibration, or boundary effects are excluded. Distinguish a model-specific effect from an estimator artifact; they are not synonyms.
- **Undecidable:** no admissible common within-model scale window, inadequate graph-level replication/power, unbounded resource projection, or unresolved operator/root-law mismatch.

This is an interpretation of Issue #37's “independently calibrated estimators” as **distinct operational geometry and transport estimators**, consistent with the adopted S1/C0 design. It does not satisfy a stricter reading that demands two independent estimators of the *same scalar* in each model family. If that stricter reading is adopted, Issue #37's criterion must be explicitly amended before any target run; pair-collision, heat-kernel trace, or a quenched re-aggregation of the same return data cannot fill that gap.

## Scale comparison: no arbitrary map

The scale variables are not interchangeable:

- Causal set: spatial cutoff \(d_c\), distance-reconstruction meso-scale \(d_m\), and external diffusion time \(\sigma\).
- UIPT: graph-ball radius \(r\) and random-walk time \(s\).

Do not identify \(d_c\) with \(r\), \(\sigma\) with \(s\), or set \(r=\sqrt{s}\). The UIPT asymptotic \(d_w=4\) is not a finite-scale conversion rule for the causal-set operator. Show separate axes and compare only predeclared within-model trends relative to each model's own microscopic and infrared references. If a cross-observable scale map becomes essential, estimate and justify a walk exponent separately; do not assume \(d_s=2d_H/d_w\) at finite scales.

## Calibration, uncertainty and controls

1. **Causal-set exact controls:** small antichains with explicit induced-distance matrices; a regular 2D lattice with the same self-inclusive transition convention (including the published threshold control: singleton islands below one lattice spacing, connected walk at the spacing); exact dense transition-matrix return probabilities; singleton, disconnected-island and finite-boundary adversaries. Check the spatial-volume count against exact lattice balls. Preserve all isolated vertices in the primary record.
2. **UIPT exact controls:** retain the existing small Type-II multigraph dense-oracle tests; add deterministic finite-map ball-count oracles and root-reweight tests. The exact local sampler must be checked against its peeling transition probabilities, 2-gon closure convention and adaptive-boundary invariance.
3. **Root and replicate structure:** independent sprinklings / independent UIPT maps are the graph-level units. Roots and walkers are nested measurements, not independent graph replicates. Report graph-level uncertainty, within-graph source variation, and the paired covariance of geometry and transport measurements on the same map.
4. **Finite-size windows:** for causal sets, preregister the \(d_c,d_m,\sigma\) grid, the 5% boundary-loss check (or a stricter calibrated alternative), component-size distribution, stationary floors and a minimum admissible scaling-window rule. For UIPT, preregister local radius, complete endpoint-degree requirements, root weights, finite-map/boundary censoring, and a graph-level power calculation.
5. **Estimator controls:** use separate finite-graph references for volume growth and return probability. Do not reuse D2's CAY/UST design-effect floor as a UIPT or causal-set power assumption. Do not count walker count as graph-level sample size.
6. **Resource gate:** the exact Type-II target projection already exceeds the current S0 limits (100M edge-step operations / 512 MiB) at proposed sizes. Walk-coupled peeling and pair-collision are possible computational strategies, but remain unimplemented/unbenchmarked; pair-collision is an S0 algorithmic cross-check, not a second dimension estimator. The causal-set spatial-distance construction also needs a bounded benchmark before any target-size choice. No Lightsail run is proposed.

## Dependencies and stop conditions

The minimum implementation sequence is:

1. Causal-set antichain extraction and induced spatial-distance construction with explicit \(d_m\) handling.
2. A separate reversible transition-kernel abstraction for the self-inclusive, variable-degree, potentially disconnected spatial graph, with exact dense-oracle tests. Do not weaken S0's existing loop-free Type-II contract.
3. Type-II UIPT peeling state with cyclic boundary order / rotation system, exact finite-component Boltzmann fillings, and tests for 2-gon closure, parallel edges, root degree and adaptive peeling.
4. Model-specific geometry and return-probability calibration on deterministic controls.
5. Bounded non-gated resource benchmarks, graph-level variance / power estimates, then a later-pass-reviewed preregistration and a separate run authorization.

No target seeds, target maps, full CS0 study, S2, deployment, paid API, or shared Lightsail work is authorized by this design.

## Literature and repository basis

- Eichhorn, Surya & Versteegen (2019), *Spectral dimension on spatial hypersurfaces in causal set quantum gravity*, https://arxiv.org/abs/1905.13498 — especially §§II–IV.
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
- **Repository facts:** no causal-set spatial-hypersurface implementation and no Type-II UIPT peeling implementation are present on Main; the current S0 kernel is not directly compatible with the self-inclusive disconnected causal-set walk.
- **Decision:** retain Issue #37 as **UNDECIDABLE**. This document selects a design interpretation, not a scientific outcome or run authorization.
