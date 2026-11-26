# Issue #37 — cross-model feasibility screen

**Date:** 2026-11-26  
**Status:** design-only feasibility decision; no UIPT/CDT target seeds, target samples, model implementation, or experiment authorization. Standard PR CI runs the repository's existing fixed-seed engineering/development fixtures on disposable GitHub runners; those outputs are not UIPT/CDT target data or scientific acceptance evidence.

## Question

Can the current project run a defensible, affordable comparison of short-scale dimension across a second model class and at least two independently calibrated observables, without reopening the terminal S1/S1b random-tree size-equivalence work or treating graph representations as physical ontology?

## Decision

**No-go for a stochastic cross-model target run with the currently validated implementations.** The current evidence does not yet provide a common, physically justified observable across the causal-set and candidate model classes, and the existing exact spectral kernel cannot reach the volume-growth size range estimated for random planar maps.

The **uniform infinite planar triangulation (UIPT)** remains a conditional *mathematical calibration candidate*. The cited literature pairing is specifically for the type-II UIPT: Angel's graph-volume result is proved for type II and translated to type III through the type-II/type-III relation; the spectral-dimension result of Gwynne and Miller, combined with Lee's upper bound, is stated for type II. The project's frozen S0 implementation accepts only simple graphs and its `Graph` builder collapses parallel edges, so it cannot faithfully run simple random walk on type II. Type III fits the current simple-graph representation, but the cited spectral-dimension theorem does not directly establish \(d_s=2\) for type III. Thus the two literature exponents are a valid type-II model pairing, but not yet a pairing that the current implementation can reproduce. They do not evidence a short-scale flow or physical spacetime.

No UIPT/CDT target experiment, pilot, new research seed, target sample, S2 work, or implementation is authorized by this screen. Existing fixed-seed CI engineering fixtures are permitted by the repository workflow and are not target runs.

## Candidate assessment

### 1. Causal sets: existing evidence is not a model comparison

The integrated D3-E0/M0 v1 archive is one fixed-input flat D=3 causal-diamond control. Its arm-dependent sign reversal is a numerical observation for that ensemble and estimator, not a cross-model result.

The merged K3 proposal adds the 3-chain abundance statistic \(d_3\), but \(d_3\) and Myrheim–Meyer remain in the same chain-abundance family. They do not constitute two independently calibrated observable families. K3 is design-only: no implementation, pilot, or target measurements exist.

A tempting common graph representation is the undirected Hasse diagram of a causal set. Graph-ball growth and simple-random-walk return probability are mathematically definable on it, but forgetting edge orientation discards part of the causal order. Until that representation is justified and calibrated, these quantities must be called **Hasse-graph diagnostics**, not causal-set spacetime dimension or physical diffusion.

### 2. UIPT / random planar maps: conditional mathematical calibration candidate

For the **type-II UIPT**, Angel (2003) proves almost-sure graph-ball growth \(r^{4+o(1)}\) with explicit polylogarithmic bounds; the paper states that the volume-growth result translates to type III through the relation between the two UIPT laws. Gwynne and Miller (2017; revised 2020) treat the type-II UIPT, and their lower bound combined with Lee (2017)'s upper bound yields almost-sure spectral dimension 2 for type II: the quenched return probability after \(2n\) steps is \(n^{-1+o(1)}\). The cited sources therefore support the paired asymptotic reference \((d_H,d_s)=(4,2)\) for the same type-II model, not an unqualified statement about every triangulation variant.

These are different asymptotic observables on the same random-map model. They are **not** two estimates of one interchangeable scalar dimension:
- graph-volume / Hausdorff growth: \(d_H=4\);
- random-walk spectral dimension: \(d_s=2\).

That makes type-II UIPT a strong mathematical calibration case because its volume-growth and spectral-return exponents are distinct observables. It does not show dimensional reduction from 4 to 2 with scale; the two values refer to different definitions in one asymptotic model. The variant choice is decisive for implementation: type II allows parallel edges (but no loops), and its simple-random-walk transition probabilities count edge multiplicity. Type III forbids parallel edges and loops. The repository's `Graph` is explicitly a simple graph; `src/emergence_lab/dimension_d1.py::_from_edges` drops loops and collapses duplicate edges, while `src/emergence_lab/spectral_dimension.py::graph_even_returns` requires a simple, unweighted graph. Feeding a type-II edge list through that builder changes the random walk. Choosing type III avoids that code mismatch, but requires a separate proof or reviewed literature extension that the type-II spectral-dimension result transfers to type III.

The finite ensemble must be pinned before use. In the canonical finite rooted ensemble, the oriented root edge is uniform, so the root vertex is selected proportional to its degree; for type II this is edge-degree, counting parallel edges. A finite rooted triangulation and its local UIPT limit are not identical objects; the admissible radius/time window must remain below finite-volume and mixing cutoffs. The asymptotic exponents are reference targets, not finite-N acceptance thresholds. Type II gives the directly cited \((4,2)\) literature pair but needs a multiplicity-preserving random-walk implementation. Type III fits the current simple-graph code, but its spectral-dimension transfer remains unproved in the cited sources.

### 3. Causal dynamical triangulations: relevant literature, unresolved operator and data bridge

A 2014 4D CDT analysis reports a spectral dimension decreasing from approximately 4 at large scales to approximately 3/2 at short scales. This is a published numerical result, not a project observation.

The operator cannot be left implicit. Caceffo and Clemente (2023) compare the dual-graph spectrum with a finite-element Laplace–Beltrami spectrum in test geometries, a 2D CDT configuration, and a spatial slice extracted from a 4D CDT configuration. They report that, except for nonpathological cases in two dimensions, the two spectra and spectral dimensions do not generally agree quantitatively or qualitatively. Crucially, they explicitly defer the finite-element refinement problem for full 4D CDT configurations to future work. Their paper therefore supports an operator-bridge warning, not a direct FEM validation or refutation of the published full-4D CDT spectral-dimension flow. A future 4D comparison must preregister which operator is meant and why it is relevant. No raw CDT configurations, pinned generator, or reproducible CDT pipeline were found in this repository audit.

Two-dimensional CDT is not an adequate substitute for an independent random-geometry family here: Durhuus, Jonsson and Wheater (2009) show its uniform infinite version is equivalent to the uniform infinite planar tree, with Hausdorff dimension 2 and spectral dimension at most 2 (equal to 2 for specified reduced versions). This would overlap the already terminal random-tree spectral line and must not be used to reopen S1/S1b.

## Observable definitions required for any future UIPT comparison

For a finite connected graph \(G\), let \(\mu_G\) be the preregistered root law and draw \(v_s\sim\mu_G\). The root law is part of the model definition, not an implementation detail. In the canonical rooted finite UIPT ensemble, the oriented root edge is uniform, so the root vertex is selected proportional to its degree. For type II this is edge-degree (parallel edges count); for type III it equals ordinary simple-graph degree. This differs from the frozen D2 source rule and the S0 multi-source extension, which require uniform vertex sources. The two laws are not interchangeable. In addition, the type-II edge multiplicities must be preserved in the transition operator; deduplicating them changes both transition probabilities and degree bias. Until the root-law bridge and graph-variant/operator bridge are resolved, the UIPT literature exponents cannot be treated as direct acceptance targets for the current D2/S0 convention. The candidate graph-level observables are:

\[
\bar B_G(r)=\frac{1}{S}\sum_{s=1}^{S}|B_G(v_s,r)|,\quad v_s\sim\mu_G,
\qquad
d_V(r)=\log_2\frac{\bar B_G(2r)}{\bar B_G(r)}.
\]

For simple random walk on the unweighted primal map graph, with each parallel edge counted as a separate unit-weight transition in type II (so \(P_G(v,w)=m_{vw}/d_{\mathrm{edge}}(v)\), where \(m_{vw}\) is edge multiplicity):

\[
q_G(m)=\frac{1}{S}\sum_{s=1}^{S}P_G^{2m}(v_s,v_s),\quad v_s\sim\mu_G,
\qquad
d_s(m)=-2\log_2\frac{q_G(2m)}{q_G(m)}.
\]

Average return probabilities before taking logarithms. Preserve the same root sample across times and, where possible, across volume and spectral measurements. Keep the root law \(\mu_G\) separate from the random-walk transition operator; do not silently substitute uniform-vertex roots for the UIPT's canonical root-edge law or vice versa. Report the two running curves separately; do not require \(d_V=d_s\). For a causal-set Hasse graph, a uniform-event root is a natural candidate, but it is a different model-specific law and any cross-model comparison must state how root-law differences are handled.

For a causal-set Hasse graph these definitions remain representation-level diagnostics only. A common graph observable does not, by itself, establish a common physical metric or diffusion operator.

## Feasibility and power screen

The repository's D2 decision estimates that planar-map volume growth would need roughly \(N\gtrsim10^7\) to obtain three admissible dyadic scales under its existing guard. This is a design projection, not a measured threshold for a UIPT implementation.

For a closed spherical type-III triangulation with \(N\) vertices, \(E=3N-6\) and the simple CSR graph has \(\mathrm{nnz}=6N-12\). A type-II multigraph has the same edge-incidence count when parallel edges are counted, but only a multiplicity-preserving adjacency represents its simple random walk. At \(N=10^7\):

- Type III nnz = 59,999,988.
- For type III, the current S0 `graph_even_returns` kernel caps `max_half_time × nnz` at 100,000,000 directed-edge steps. The first preregistered G1 slope at \(m=32\) requires `max_half_time=64`, about 3.84 billion edge-step operations; the full G1 grid through \(m=128\) requires `max_half_time=256`, about 15.36 billion. Even a hypothetical \(m=1\) slope pair would exceed the cap at about 120 million. For type II, preserving all parallel-edge incidences gives a comparable operation count, while the current `Graph` builder's duplicate collapse invalidates the intended walk; a smaller post-deduplication `nnz` would not be a valid workaround.
- D2's existing design uses 8 independent graphs and 256 sources per graph per size: 2,048 BFS traversals per size. At this adjacency size, the order-of-work estimate is about \(1.23\times10^{11}\) adjacency visits per size, or \(3.69\times10^{11}\) across three sizes. This is an algorithmic count, not measured wall time.
- For the type-III simple graph, the `Graph` class retains int64 row pointers (about 80 MB) and int32 adjacency indices (about 240 MB); the float64 CSR data and CSR row pointers add about 520 MB, for at least roughly 840 MB before auxiliary arrays. The S0 transition CSR adds about 760 MB in data, indices and row pointers. Together these are roughly 1.6 GB before degree/row vectors and other temporaries. This is a static payload estimate, not measured peak RSS. A multiplicity-preserving type-II implementation requires its own memory benchmark.

A Monte Carlo random-walk estimator could avoid the exact-kernel cap, but it would be a new method and needs a separate calibration. For a return indicator with probability \(q(m)\), the conditional relative standard error is approximately \(1/\sqrt{Wq(m)}\) when \(q\) is small. A 10% relative standard error therefore needs roughly \(Wq(m)\ge100\). Since the UIPT type-II asymptotic return probability is \(q(m)=m^{-1+o(1)}\), this implies the asymptotic requirement \(W\gtrsim100m^{1-o(1)}\) up to subpolynomial factors per root/time point. The exponent alone supplies no finite-\(m\) constant lower bound. This is only a walker-noise lower bound: it omits graph-to-graph variation, root heterogeneity, paired-time covariance and finite-size bias. It is **not** a power calculation or a sample-size authorization.

The D2 design-effect sensitivity floor of 3 was established for its tree families and must not be transferred to UIPT without a non-gated pilot. Walkers and roots are nested within a graph; they are not independent graph replicates. The graph is the independent unit for cross-model uncertainty and paired covariance.

## Required gates before any future run

1. **Representation and root-law bridge:** decide whether the causal-set Hasse graph is an acceptable graph-level comparison object, and specify its root law. Resolve the UIPT canonical root-edge law versus the frozen D2/S0 uniform-vertex source convention; either justify exponent equivalence or make a separately reviewed method revision. If the Hasse graph is not acceptable, define a causal-set-native diffusion or volume observable and justify the mapping; do not force a graph analogy.
2. **Exact finite ensemble and graph variant:** pin type II or type III, the finite UIPT approximation, root law, boundary treatment, size sequence and finite-volume radius/time cutoffs. If type II is chosen, preserve parallel-edge multiplicity in the adjacency and random-walk operator. If type III is chosen, establish the type-II-to-type-III spectral-dimension transfer before using \(d_s=2\) as a reference.
3. **Independent calibration:** calibrate volume growth and spectral return separately on exact controls, then test their finite-size behavior on the chosen random-map ensemble. The existing tree-only D2 calibration and deterministic-graph S0 calibration do not suffice; S0's simple-graph controls do not certify a multiplicity-preserving type-II walk.
4. **Scalable spectral estimator:** specify the random-walk estimator, paired-time covariance, return-count stopping/zero-return handling, root-law averaging and error propagation. Preserve edge multiplicity if type II is chosen; do not silently replace it with a simple graph. Do not treat walkers as independent maps.
5. **Graph-level power:** use a separately labeled non-gated pilot to estimate between-map variance and source design effect. Derive power from graph-level variance; do not reuse the 0.997 D2 tree calculation or the Fisher-z correlation-precision example as a paired-test power claim.
6. **Resource gate:** benchmark one bounded implementation on small controls before selecting target sizes. Respect the 2-vCPU / 4-GB environment and do not run on shared Lightsail while EatSleepFeel is at risk.
7. **Later-pass review and authorization:** freeze seeds, manifest, hypotheses, nulls, finite-size windows, uncertainty, CPU/RAM/time limits and stop rules in a separate reviewed preregistration. Only then consider a pilot.

## Conclusion

The current answer to Issue #37 remains **undecidable**. The D3 causal-set observation and the K3 design do not provide two model classes or two independent observable families. UIPT remains a conditional mathematical candidate: the cited \((d_H,d_s)=(4,2)\) pairing is type II, but the frozen S0 simple-graph implementation cannot faithfully represent its parallel edges. Type III fits the current graph code, but the cited spectral-dimension theorem does not directly establish the same result for type III. Full 4D CDT also retains an operator/data bridge blocker; Caceffo and Clemente explicitly defer FEM on full 4D configurations. No variant is ready for a stochastic run using the current validated pipeline.

The next work item is a **design-only type-II/type-III and root-law bridge, together with a multiplicity-preserving scalable spectral-estimator specification or a reviewed type-III spectral-dimension transfer**. Clarify the full-4D CDT operator/data path separately. If these cannot be made operational within the resource ceiling, retain the cross-model question as unresolved rather than weaken the gates.

## Literature screened (not a full line-by-line source audit)

- O. Angel and O. Schramm, *Uniform Infinite Planar Triangulations* (2003): https://arxiv.org/abs/math/0207153
- O. Angel, *Growth and Percolation on the Uniform Infinite Planar Triangulation* (2003): https://arxiv.org/abs/math/0208123
- J. R. Lee, *Conformal growth rates and spectral geometry on distributional limits of graphs* (2017): https://arxiv.org/abs/1701.01598
- E. Gwynne and J. Miller, *Random walk on random planar maps: spectral dimension, resistance, and displacement* (2017; revised 2020): https://arxiv.org/abs/1711.00836
- B. Durhuus, T. Jonsson and J. F. Wheater, *On the spectral dimension of causal triangulations* (2009): https://arxiv.org/abs/0908.3643
- D. N. Coumbe and J. Jurkiewicz, *Evidence for Asymptotic Safety from Dimensional Reduction in Causal Dynamical Triangulations* (2014): https://arxiv.org/abs/1411.7712
- F. Caceffo and G. Clemente, *Spectral analysis of causal dynamical triangulations via finite element method*, Phys. Rev. D 107, 074501 (2023): https://doi.org/10.1103/PhysRevD.107.074501
