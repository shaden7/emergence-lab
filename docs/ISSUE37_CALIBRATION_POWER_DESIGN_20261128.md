# Issue #37 — calibration and graph-level power design

**Status: DESIGN ONLY (v0.1, 2026-11-28).** This is a design memo, not a preregistration, run authorization, seed manifest, or scientific acceptance decision. No target seeds, target maps, samples, simulations, or deployments are included. The two-channel rule remains a proposed sufficient operationalization; the owner-authored Issue #37 body is unchanged.

**Base:** Main **8a7754204a847b20f1ab0d188d871c5e673dfcba** (PR #99 integrated; its handoff CI was subsequently verified successful).

## 1. Decision object and four estimands

Issue #37 asks whether the same short-scale behaviour occurs in at least two model classes with at least two independently calibrated estimators. Its random-tree example deliberately gives different Hausdorff and spectral limits. Accordingly, \(d_H\) and \(d_s\) are distinct observables, not two estimates of one scalar. Do not equate, average, or combine their raw values.

The proposed full-ROBUST comparison is a four-cell profile:

| Model class | Geometry channel | Transport channel | Independent unit |
|---|---|---|---|
| Causal-set spatial hypersurface | Spatial-neighbour-count / volume-growth \(d_H^{\mathrm{eff}}\) | Self-inclusive spatial-walk return \(d_s^{\mathrm{eff}}\) | Independent sprinkling |
| Type-II UIPT | Graph-ball volume-growth \(d_H^{\mathrm{eff}}\) | Multiplicity-preserving random-walk return \(d_s^{\mathrm{eff}}\) | Independent UIPT map / rooted local sample |

The two geometry channels use different intrinsic metrics and scale axes. The two transport channels also use different operators. “Same behaviour” means a predeclared qualitative direction of within-model scale flow, not equal exponents, identical curves, or a numerical map between the model-specific scales.

### 1.1 Causal-set spatial hypersurface

Use the ESV spatial-hypersurface construction, not a full-Hasse-graph walk.

For sprinkling \(g\), freeze the initial inextendible antichain, induced ESV distance, meso-cutoff \(d_m\), spatial cutoff grid \(d_c\), root sample, finite region, and boundary rules. The geometry channel is the per-sprinkling slope

\[
d_{H,g}^{\mathrm{eff}}(d_c)
=\log_2\frac{\bar n_g(2d_c)}{\bar n_g(d_c)},
\]

where \(\bar n_g(d_c)\) is the mean self-inclusive neighbour count over the fixed root sample in that sprinkling. The assumed \(2+1\)-dimensional Minkowski background and the dimension-dependent ESV reconstruction make this a **kinematical geometry control**, not an independent derivation of spatial dimension.

For each sprinkling, construct the self-inclusive transition rule

\[
P_g(e,e')=\frac{1}{|\mathcal N_c(e)|}
\quad\text{for }e'\in\mathcal N_c(e),
\]

with the root itself included exactly once. Let \(Q_g(\sigma)\) be the mean return probability over the same frozen root sample. The common dyadic transport convention is

\[
d_{s,g}^{\mathrm{eff}}(\sigma)
=-2\log_2\frac{Q_g(2\sigma)}{Q_g(\sigma)}.
\]

The published ESV spectral paper's finite-difference Eq. (10), with smoothing span \(n=2,3\), must remain a separately reported replication/sensitivity arm. A dyadic slope is a project analysis convention, not an exact reproduction of that estimator.

Singleton components have return probability and stationary floor one. They are trapped/no-transport cases, not a zero-dimensional scaling regime. Preserve them in the primary accounting; do not silently drop isolated vertices or average them as ordinary sources.

### 1.2 Type-II UIPT

Use the infinite Type-II UIPT: parallel edges are allowed and self-loops are not. Preserve every parallel half-edge as a separate unit transition.

The primary root law is the canonical oriented-root-edge law. The root vertex is degree-biased; do not silently replace it with a uniform-vertex root. A uniform-vertex sensitivity arm may use the finite-map Radon–Nikodym factor \(\bar d_N/d_\rho\), but it must remain separate and its weights must enter the uncertainty calculation.

For a map \(g\), let \(\bar B_g(r)\) be the mean closed graph-ball cardinality over its frozen root sample. The geometry channel is

\[
d_{H,g}^{\mathrm{eff}}(r)
=\log_2\frac{\bar B_g(2r)}{\bar B_g(r)}.
\]

For the transport channel use the S0 half-time convention \(Q_g(s)=P_g^{2s}(\rho,\rho)\), averaged over the frozen roots within that map, and

\[
d_{s,g}^{\mathrm{eff}}(s)
=-2\log_2\frac{Q_g(2s)}{Q_g(s)}.
\]

Type-II UIPT is non-bipartite and has period one. Do not apply a bipartite even-time stationary-floor correction. A finite-map control has root-specific stationary floor \(d_\rho/(2E)\); an infinite-UIPT local-peeling sample has no finite-map stationary floor and instead needs a local-radius completeness rule.

**Local-peeling radius correction.** The exact half-kernel identity for \(Q_g(s)=P^{2s}(\rho,\rho)\) requires complete degrees of vertices reached within \(s\) steps, so radius \(s+1\) is sufficient for \(Q_g(s)\) alone. The dyadic transport slope also needs \(Q_g(2s)=P^{4s}(\rho,\rho)\), whose half-kernel identity requires degrees out to distance \(2s\), hence exposure through radius \(2s+1\). Separately, the geometry estimator \(d_{H,g}^{\mathrm{eff}}(r)\) uses the graph ball \(B_g(2r)\), so it requires exposure through radius \(2r\). Therefore a local Type-II sample used for the paired geometry/transport profile must expose at least \(R_{\mathrm{pair}}=\max(2r,2s+1)\). If a later within-UIPT design sets \(r=s\), the spectral requirement dominates by one hop; do not assume that equality in advance because the geometry-radius and transport-time axes are distinct. A cost or memory estimate based only on \(s+1\), or only on \(2s+1\) when \(2r\) is larger, is insufficient for the paired profile.

Angel's local peeling law is an infinite-volume neighbourhood sampler, not a finite-\(N\) uniform spherical-map generator. The repository still needs the boundary-order / rotation-system implementation, finite-component filling, and exact transition/termination tests.

### 1.3 No cross-model scale map

Keep the axes separate:

- Causal-set geometry: \(d_c\); ESV path construction: \(d_m\); transport: \(\sigma\).
- UIPT geometry: graph radius \(r\); transport: half-time \(s\).

Do not set \(d_c=r\), \(\sigma=s\), or \(r=\sqrt{s}\). The UIPT asymptotic walk-displacement exponent is not a finite-scale conversion rule for the causal-set operator. Freeze UV and IR windows independently for each model and observable.

## 2. Primary scale-flow statistic and inferential unit

For model \(M\), channel \(e\in\{H,s\}\), and independent realization \(g\), define

\[
\Delta_{M,e,g}
=
\operatorname{mean}_{u\in W^{UV}_{M,e}}
 d_{M,e,g}^{\mathrm{eff}}(u)
-
\operatorname{mean}_{u\in W^{IR}_{M,e}}
 d_{M,e,g}^{\mathrm{eff}}(u).
\]

The windows \(W^{UV}_{M,e}\) and \(W^{IR}_{M,e}\) are model- and channel-specific, fixed from deterministic controls and a **non-gated** feasibility pilot before target data are drawn. A negative \(\Delta\) means the effective dimension is lower in the UV window. Window points, weights, minimum window length, headroom, and all sensitivity windows must be frozen in the later preregistration. No post-hoc window selection is allowed.

The independent unit is the **sprinkling/map**, not a root, walker, time point, or pair of vertices:

- Multiple antichain roots and walkers within one causal-set sprinkling are nested observations. Aggregate them to one per-sprinkling channel curve and one \(\Delta\).
- A UIPT root-edge sample is one independent rooted local-map realization. If multiple roots are taken from one map, they remain clustered within that map.
- Measure \(d_H\) and \(d_s\) on the same realization and, where possible, the same frozen root sample. Preserve their within-map covariance. Distinct estimators are not statistically independent merely because they target different observables.
- The two model classes use independent ensembles; do not pair their maps or treat scale points as replicates.

The causal-set 5% mean-neighbour-count drop used in the published ESV finite-sample design is a boundary-onset reference, not a project-validated universal threshold. The later preregistration must freeze this check or a stricter control-calibrated rule, plus the future-boundary convention, central-root rule, minimum retained-pair fraction, antichain rule, and component/trapping accounting. The current side-witness censor addresses spatial sides only.

For UIPT, require complete local neighbourhoods for every ball and return quantity used in a slope. For a finite-map control, apply its correct period and root-specific stationary floor. For the infinite local UIPT, use the radius-completeness condition rather than inventing a finite stationary floor.

If a model/channel has no admissible non-degenerate IR reference or no contiguous UV-to-IR window after the frozen censoring rules, it is **UNDECIDABLE** for the full comparison; do not manufacture a plateau.

## 3. Calibration matrix — what existing work does and does not establish

| Cell | Existing instrument evidence | Required model-matched controls before target data |
|---|---|---|
| Causal-set \(d_H\) | Dense exact ESV order oracle and slab sampler are engineering references capped at \(N\le256\); neither is a target generator or calibrated spatial-dimension curve. | Exact small antichains and induced-distance fixtures; exact 2D lattice neighbour-count/ball controls under the same counting convention; relabelling, zero-volume, no-common-future, side/future-boundary and root-censor adversaries; a scalable implementation cross-checked against the dense oracle. |
| Causal-set \(d_s\) | S0 exact kernels do not accept this operator unchanged. **SelfInclusiveKernel** supports simple disconnected graphs and adds one self-choice; it has not been run on target data. | Dense transition-matrix return oracle; regular 2D lattice threshold control (singleton islands below one spacing, connected walk at the spacing); disconnected islands, singleton traps, component-specific stationary floors, finite-boundary and root controls; compare the published Eq. (10) and project dyadic slope. |
| Type-II UIPT \(d_H\) | D1/D2 volume-growth calibration covers lattices and specified tree families, not random planar maps. Angel's and related asymptotic results give \(d_H=4\) up to polylogarithmic factors, not a finite-size acceptance band. | Deterministic finite-map ball-count oracles; exact root-edge versus uniform-vertex weighting checks; a Type-II sampler with verified map/half-edge structure; a non-gated finite-size pilot to establish bias, variance, and admissible radii. |
| Type-II UIPT \(d_s\) | S0's MultiGraph path preserves parallel-edge multiplicity and has small-graph dense-oracle tests. Gwynne–Miller's \(d_s=2\) is an infinite-volume theorem, not a finite-time tolerance. | Exact rational small-map return controls; multiplicity, root law, period-one and stationary-floor checks; Angel peeling transition probabilities including 2-gon closure and adaptive-edge invariance; transport-slope local-radius completeness at \(2s+1\); the paired profile additionally requires \(R_{\mathrm{pair}}=\max(2r,2s+1)\). For one local root sample reused across multiple scale points, expose through \(R_{\mathrm{sample}}=\max(2r_{\max},2s_{\max}+1)\), where the maxima cover the preregistered geometry and transport windows. A scalable estimator benchmarked against the exact kernel. |

Do not transfer D2's tree-family design effect or its \(S=256\) source count to UIPT or causal sets. D2 itself records source-count fragility, finite-size bias and a design-effect sensitivity floor of at least \(\times3\) for its own tree families. The cross-model feasibility note explicitly says that this factor is not a UIPT or causal-set power assumption. Likewise, S0 lattice controls and the Type-II small-multigraph dense-oracle tests validate transition semantics, not random-map finite-size power.

The C0-v2 deterministic comparison is complete and useful for exact-control reporting. It does not certify random-tree spectral size stability, random-map calibration, or Issue-37 cross-model behaviour. The terminal S1/S1b size-equivalence decision remains unchanged.

## 4. Non-gated pilot and power calculation

A pilot is for nuisance quantities and feasibility only. It must not be used as confirmatory evidence, and its seeds must be disjoint from any later gated seed inventory.

### 4.1 Pilot outputs required

For each model, record:

1. Per-realization \(d_H\), \(d_s\), UV/IR contrasts, and their paired covariance.
2. Within-realization root variation and the effect of the frozen root-sampling rule.
3. For stochastic walks, conditional walker noise at each time and covariance across the paired time points.
4. Between-map/sprinkling variance, skewness, influential-realization diagnostics, and leave-one-map-out sensitivity.
5. The admissible windows under the frozen boundary, component, stationary-floor, and headroom rules.
6. Wall time, CPU time, peak RSS, operation counts, output bytes, and exact software / code / config provenance.

The published ESV choice of ten sprinklings, thirty roots per antichain, and up to \(7\cdot10^4\) walks per root is a **published design**, not a project power calculation or a budget authorization. It may inform a feasibility benchmark but must not be copied as if it established 80% power. Likewise, one root per independent Type-II UIPT map is the canonical primary design; more walkers reduce conditional Monte Carlo noise but do not increase the number of independent maps.

For a return indicator estimated from \(W\) independent trajectories conditional on a fixed map/root, the first-order relative Monte Carlo standard error is

\[
\frac{\operatorname{SE}(\hat q\mid G,\rho)}{q}
\approx
\sqrt{\frac{1-q}{Wq}},
\qquad
W\gtrsim\frac{1-q}{\epsilon_q^2 q}
\]

for target relative error \(\epsilon_q\). This is only a **conditional walker-noise** calculation. It omits between-map variation, root heterogeneity, paired-time covariance, finite-size bias, and window uncertainty. It cannot determine the number of independent maps.

### 4.2 Map-level power

For each of the four primary contrasts, estimate the between-map variance from the non-gated pilot and use a conservative upper confidence bound \(\sigma_U\), not the raw pilot standard deviation. A chi-square variance bound is appropriate only under a defensible approximately normal map-level model; otherwise use a predeclared robust / bootstrap sensitivity and mark power unreliable if the upper bound is unstable. The D2 record's observed variance excess is a direct warning against treating a small pilot SD as known. The later preregistration must state the coverage level and construction of every \(\sigma_U\), including the assumptions supporting that bound; do not select or revise it after target outcomes.

Before target data, derive a minimum non-artifactual decline \(\delta_{M,e}>0\) for each cell. It is an operational false-flow exclusion margin, not a universal physical effect size or a cross-model magnitude: it should be no smaller than a predeclared upper tolerance bound on spurious UV-IR contrasts under matched null / finite-size controls, with a repeatability-resolution floor. The later preregistration must state the combination rule and propagate uncertainty in the control bound. If only a measurement-resolution floor is supportable, label it a detection threshold rather than a scientifically meaningful effect. Do not choose \(\delta\) from target outcomes. If a positive control-derived margin cannot be justified, report directional estimates descriptively and do not claim a calibrated robust reduction.

For a cell, the confirmatory hypotheses are

\[
H_{0,M,e}:\Delta_{M,e}\ge-\delta_{M,e},
\qquad
H_{1,M,e}:\Delta_{M,e}<-\delta_{M,e}.
\]

The single full-ROBUST claim is the **conjunction** of all four alternatives. It is an intersection-union test: test each component one-sided at \(\alpha=0.05\), and accept the global claim only if all four pass. Under the global null at least one component null is true, so the probability of falsely accepting the conjunction is at most 0.05; a Bonferroni correction is not needed for this one conjunctive claim. If separate confirmatory claims are made about individual cells, or multiple windows are promoted to primary, multiplicity must be controlled separately.

Power is a separate requirement. The control-derived margin \(\delta_{M,e}\) is the minimum non-artifactual decline and defines the null boundary; it is **not** the effect at which power can be claimed. For each cell, the later preregistration must freeze a design alternative \(\Delta^*_{M,e}<-\delta_{M,e}\) (plus a sensitivity grid where useful), justified from independent calibration / literature or an explicitly conservative planning scenario, never from target outcomes. The 80% joint-power requirement applies to the vector \(\boldsymbol{\Delta}^*=(\Delta^*_{CS,H},\Delta^*_{CS,s},\Delta^*_{UIPT,H},\Delta^*_{UIPT,s})\). At the component boundary \(\Delta_{M,e}=-\delta_{M,e}\), a correctly calibrated test has rejection probability no greater than its size; asking for 80% power there is impossible by design. If no defensible \(\Delta^*\) can be selected, report the joint-power curve as a function of \(\boldsymbol{\Delta}^*\) and keep the sample-size decision unresolved rather than claiming 80% power.

Estimate the joint probability that **all four** component tests pass at this predeclared design-alternative vector using the pilot covariance structure: resample whole maps / sprinklings, preserve paired \(d_H,d_s\) values within each realization, and resample the two independent model ensembles separately. Require at least 80% joint power. If the joint covariance estimate is too unstable, use the conservative union-bound fallback: at least 95% marginal power for each component at its own \(\Delta^*_{M,e}\) implies at least 80% joint power. Solve sample sizes with the appropriate finite-sample t / bootstrap operating characteristics using \(\sigma_U\); do not substitute a normal approximation without checking it.

No numerical sample size is specified here because the required between-map variances, root design effects, admissible windows, and target-scale costs do not yet exist for either selected model. A numeric \(n\) now would be invented precision. The later preregistration must show the inputs, the exact calculation, sensitivity to variance inflation and skew, and the resulting total CPU/RSS/output budget. If the required number of independent maps exceeds the resource ceiling, retain **UNDECIDABLE under available resources** rather than reducing \(\delta\), treating walkers as maps, or dropping difficult realizations.

### 4.3 Equivalence and ARTIFACT claims

Failure to reject a decrease is not evidence of no decrease. To call a channel/model cell materially unchanged, use a predeclared two-one-sided-test (TOST) equivalence rule with its control-derived margin and adequate power. An **ARTIFACT / model-dependent** outcome requires positive evidence that the effect is confined to a model/operator or is removed by a matched finite-size, boundary, trapping, root-law, or cutoff control. Mere disagreement between \(d_H\) and \(d_s\), or a nonsignificant estimate, is insufficient.

If both \(d_s\) cells pass but a \(d_H\) cell is underpowered, report a transport-channel pattern as descriptive and keep the full Issue-37 result **UNDECIDABLE**. If \(d_H\) is shown to have a distinct or opposite scale flow, report the geometry / transport split explicitly; do not call it transport-only. Reserve a **transport-only** claim for cases where the geometry channel is itself shown equivalent to no material flow.

## 5. Dependency and authorization gates

The following order is mandatory; passing one gate does not imply the next.

1. **Finite-region contract (causal set):** freeze the slab, Poisson count law, initial antichain, future boundary, central root, \(d_m\), \(d_c\), side/future censoring, and minimum retained-pair fraction. The current dense spatial oracle and slab relation are capped at \(N\le256\); a scalable bitset/CSR and SWB/SIL path must be checked against the exact oracle.
2. **Type-II local sampler:** implement Angel's local peeling with cyclic boundary order / rotation-system data, correct finite-component fillings and 2-gon closure, canonical oriented-root-edge law, and tests for adaptive-edge invariance and complete endpoint degrees. It is not a finite-\(N\) spherical-map generator.
3. **Estimator calibration:** complete the four-cell exact-control matrix above, including the correct operator and root law. A small-graph dense-oracle pass alone is not finite-size calibration.
4. **Resource benchmark:** benchmark the actual target algorithms on non-gated controls. The existing `graph_even_returns` path enforces a 100,000,000 directed-edge-step operation proxy; the self-inclusive kernel separately estimates / guards sparse-kernel memory at 512 MiB. Neither is a measured resource budget for a future Type-II local-peeling implementation. The cross-model feasibility screen projects multi-billion operations and roughly 1.49 GiB static payload for a \(10^7\)-vertex adjacency. That 1.49 GiB figure is a static CSR-layout proxy derived from the existing Type-III simple-graph representation, which has the same asymptotic half-edge incidence count; it is **not** a measured Type-II memory estimate. A multiplicity-preserving Type-II implementation requires its own benchmark. Do not bypass the operation limit by deduplicating parallel edges. A Monte Carlo / walk-coupled peeling path is a new method and needs its own calibration.
5. **Pilot and power:** estimate graph-level variance, covariance, admissible windows and cost; calculate the four-cell joint power and sample size.
6. **Preregistration:** freeze the four contrasts, scale windows, control-derived margins, roots, walkers, map/sprinkling counts, seed derivation, uncertainty method, multiplicity, sensitivity analyses, stop rules, and archive manifest at an exact code commit. Obtain a later-pass review.
7. **Separate run authorization:** only a distinct reviewed authorization may freeze target seed entropy and permit target maps/sprinklings. This design memo authorizes none.

## 6. Resource and safety boundary

- No target run in this memo; no seed entropy is chosen or drawn.
- Use GitHub-hosted or otherwise isolated **non-Lightsail** runners for deterministic controls and feasibility work. Do not use the shared Lightsail host while EatSleepFeel shares it.
- Retain the current S0 operation and memory caps until a separately reviewed replacement method is calibrated. Do not infer that the 4 GB Lightsail machine makes a 1.49 GiB target implementation safe to run alongside EatSleepFeel.
- No deployment, paid API, new infrastructure, credential handling, or changes to the nightly cron.
- Keep all failed, censored, and over-cap pilot realizations in the provenance record. Never silently replace them or lower a frozen sample size.

## 7. Evidence classification and next action

**Established mathematics / literature anchors:** the Type-II UIPT asymptotic \(d_H=4\) (up to polylogarithmic factors) and \(d_s=2\); the finite-poset and reversible-walk identities used by the exact reference code. These do not imply a finite-scale UV decrease.

**Existing numerical observations:** D1/D2, S0/S1/S1b, C0-v2, and the current causal-set engineering CI records, each within its documented scope. None is a target measurement for the four cells above.

**Hypotheses:** a full two-channel UV decrease may occur in both model classes; the causal-set finite-region and Type-II finite-size windows may be too narrow or too costly to establish it. Neither is tested by this design.

**Not proved / not established:** no new theorem, no cross-model numerical result, no robust dimensional reduction, no ARTIFACT classification, and no physical-spacetime inference.

**Next single informative step:** later-pass review this design against the exact estimator APIs and resource limits, concentrating on the four-cell contrast, the intersection-union test, the control-derived effect margins, and the paired UIPT peeling-radius requirement \(R_{\mathrm{pair}}=\max(2r,2s+1)\), and the corresponding maximum over all preregistered scale points for a shared root sample. Only after that review should the team freeze a non-gated implementation/feasibility pilot; target seeds remain locked behind a separate preregistration and authorization.

## References carried from reviewed repository sources

- [Joint geometry/transport profile](ISSUE37_JOINT_GEOMETRY_TRANSPORT_PROFILE_20261127.md).
- [Distinct-estimator comparison design](DIMENSION_COMPARISON_DESIGN.md).
- [D2 decision and scope restrictions](DIMENSION_D2_DECISION.md).
- [S1 spectral scope decision](S1_SPECTRAL_NEXT_DECISION.md).
- [Cross-model feasibility screen](ISSUE37_CROSS_MODEL_FEASIBILITY_20261126.md).
- [Causal-set finite-region audit](ISSUE37_CAUSAL_SET_FINITE_REGION_AUDIT_20261127.md).
- Angel, *Growth and Percolation on the Uniform Infinite Planar Triangulation* (2003), https://arxiv.org/abs/math/0208123.
- Gwynne & Miller, *Random walk on random planar maps: spectral dimension, resistance and displacement* (2017; revised 2020), https://arxiv.org/abs/1711.00836.
- Eichhorn, Surya & Versteegen, *Induced Spatial Geometry from Causal Structure* (2018), https://arxiv.org/abs/1809.06192.
- Eichhorn, Surya & Versteegen, *Spectral dimension on spatial hypersurfaces in causal set quantum gravity* (2019), https://arxiv.org/abs/1905.13498.
