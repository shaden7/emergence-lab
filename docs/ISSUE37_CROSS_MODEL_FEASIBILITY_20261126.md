# Issue #37 — cross-model feasibility screen

**Date:** 2026-11-26  
**Status:** design-only feasibility decision; no seeds, samples, code implementation, or experiment authorization.

## Question

Can the current project run a defensible, affordable comparison of short-scale dimension across a second model class and at least two independently calibrated observables, without reopening the terminal S1/S1b random-tree size-equivalence work or treating graph representations as physical ontology?

## Decision

**No-go for a stochastic cross-model target run with the currently validated implementations.** The current evidence does not yet provide a common, physically justified observable across the causal-set and candidate model classes, and the existing exact spectral kernel cannot reach the volume-growth size range estimated for random planar maps.

The **uniform infinite planar triangulation (UIPT)** is the preferred *mathematical calibration candidate* for a later design. It is substantively different from causal sets and random trees, and the literature establishes two distinct asymptotic graph dimensions on the same model: volume growth exponent 4 (up to polylogarithmic factors) and spectral dimension 2. This is useful precisely because the two dimensions are not equal. It is not evidence of a short-scale flow and is not a physical-spacetime result.

No target experiment, pilot, new seed, S2 work, or implementation is authorized by this screen.

## Candidate assessment

### 1. Causal sets: existing evidence is not a model comparison

The integrated D3-E0/M0 v1 archive is one fixed-input flat D=3 causal-diamond control. Its arm-dependent sign reversal is a numerical observation for that ensemble and estimator, not a cross-model result.

The merged K3 proposal adds the 3-chain abundance statistic \(d_3\), but \(d_3\) and Myrheim–Meyer remain in the same chain-abundance family. They do not constitute two independently calibrated observable families. K3 is design-only: no implementation, pilot, or target measurements exist.

A tempting common graph representation is the undirected Hasse diagram of a causal set. Graph-ball growth and simple-random-walk return probability are mathematically definable on it, but forgetting edge orientation discards part of the causal order. Until that representation is justified and calibrated, these quantities must be called **Hasse-graph diagnostics**, not causal-set spacetime dimension or physical diffusion.

### 2. UIPT / random planar maps: strongest mathematical calibration candidate

For the UIPT, Angel (2003) proves almost-sure graph-ball growth \(r^{4+o(1)}\) (with polylogarithmic qualifications in the stated bounds). Lee (2017), combined with Gwynne and Miller (2017/2020), establishes almost-sure spectral dimension 2 for the UIPT class: the quenched return probability after \(2n\) steps is \(n^{-1+o(1)}\).

These are different asymptotic observables on the same random-map model. They are **not** two estimates of one interchangeable scalar dimension:
- graph-volume / Hausdorff growth: \(d_H=4\);
- random-walk spectral dimension: \(d_s=2\).

That makes the UIPT a strong method-calibration case for the project's two observable families. It does not show dimensional reduction from 4 to 2 with scale; the two values refer to different definitions in one asymptotic model.

The finite ensemble must be pinned before use. A finite rooted triangulation and its local UIPT limit are not identical objects; the admissible radius/time window must remain below finite-volume and mixing cutoffs. The asymptotic exponents are reference targets, not finite-N acceptance thresholds.

### 3. Causal dynamical triangulations: relevant literature, unresolved operator and data bridge

A 2014 4D CDT analysis reports a spectral dimension decreasing from approximately 4 at large scales to approximately 3/2 at short scales. This is a published numerical result, not a project observation.

The operator cannot be left implicit. Caceffo and Clemente (2023) compare the dual-graph spectrum with a finite-element Laplace–Beltrami spectrum on piecewise-flat CDT manifolds and report that, except for nonpathological cases in two dimensions, the two spectra and spectral dimensions do not generally agree quantitatively or qualitatively. A future CDT comparison must therefore preregister which operator is meant and why it is the relevant one. No raw CDT configurations, pinned generator, or reproducible CDT pipeline were found in this repository audit.

Two-dimensional CDT is not an adequate substitute for an independent random-geometry family here: Durhuus, Jonsson and Wheater (2009) show its uniform infinite version is equivalent to the uniform infinite planar tree, with Hausdorff dimension 2 and spectral dimension at most 2 (equal to 2 for specified reduced versions). This would overlap the already terminal random-tree spectral line and must not be used to reopen S1/S1b.

## Observable definitions required for any future UIPT comparison

For a finite connected graph \(G\), let \(\mu_G\) be the preregistered root law and draw \(v_s\sim\mu_G\). The root law is part of the model definition, not an implementation detail. In the UIPT, finite triangulations are rooted by a uniformly selected oriented root edge; the root vertex is therefore degree-biased. This differs from the frozen D2 source rule and the S0 multi-source extension, which require uniform vertex sources. The two laws are not interchangeable. Until their exponent-equivalence is proved or a reviewed method revision is made, the UIPT literature exponents cannot be treated as direct acceptance targets for the current D2/S0 source convention. The candidate graph-level observables are:

\[
\bar B_G(r)=\frac{1}{S}\sum_{s=1}^{S}|B_G(v_s,r)|,\quad v_s\sim\mu_G,
\qquad
d_V(r)=\log_2\frac{\bar B_G(2r)}{\bar B_G(r)}.
\]

For simple random walk on the unweighted primal graph:

\[
q_G(m)=\frac{1}{S}\sum_{s=1}^{S}P_G^{2m}(v_s,v_s),\quad v_s\sim\mu_G,
\qquad
d_s(m)=-2\log_2\frac{q_G(2m)}{q_G(m)}.
\]

Average return probabilities before taking logarithms. Preserve the same root sample across times and, where possible, across volume and spectral measurements. Keep the root law \(\mu_G\) separate from the random-walk transition operator; do not silently substitute uniform-vertex roots for the UIPT's canonical root-edge law or vice versa. Report the two running curves separately; do not require \(d_V=d_s\). For a causal-set Hasse graph, a uniform-event root is a natural candidate, but it is a different model-specific law and any cross-model comparison must state how root-law differences are handled.

For a causal-set Hasse graph these definitions remain representation-level diagnostics only. A common graph observable does not, by itself, establish a common physical metric or diffusion operator.

## Feasibility and power screen

The repository's D2 decision estimates that planar-map volume growth would need roughly \(N\gtrsim10^7\) to obtain three admissible dyadic scales under its existing guard. This is a design projection, not a measured threshold for a UIPT implementation.

For a triangulation with \(N\) vertices, \(E\approx3N-6\), hence the symmetric CSR graph has approximately \(6N\) directed adjacency entries. At \(N=10^7\):

- nnz ≈ 59,999,988.
- The current S0 graph_even_returns kernel caps max_half_time × nnz at 100,000,000 directed-edge steps. The first preregistered G1 slope at \(m=32\) requires max_half_time=64, about 3.84 billion edge-step operations; the full G1 grid through \(m=128\) requires max_half_time=256, about 15.36 billion. For comparison, even a hypothetical \(m=1\) slope pair would exceed the cap at about 120 million. The current deterministic kernel therefore cannot reach this candidate size under its frozen cap.
- D2's existing design uses 8 independent graphs and 256 sources per graph per size: 2,048 BFS traversals per size. At this adjacency size, the order-of-work estimate is about \(1.23\times10^{11}\) adjacency visits per size, or \(3.69\times10^{11}\) across three sizes. This is an algorithmic count, not measured wall time.
- The Graph class retains int64 row pointers (about 80 MB) and int32 adjacency indices (about 240 MB); the float64 CSR data and CSR row pointers add about 520 MB, for at least roughly 840 MB before auxiliary arrays. The S0 transition CSR adds about 760 MB in data, indices and row pointers. Together these are roughly 1.6 GB before degree/row vectors and other temporaries. This is a static payload estimate, not measured peak RSS.

A Monte Carlo random-walk estimator could avoid the exact-kernel cap, but it would be a new method and needs a separate calibration. For a return indicator with probability \(q(m)\), the conditional relative standard error is approximately \(1/\sqrt{Wq(m)}\) when \(q\) is small. A 10% relative standard error therefore needs roughly \(Wq(m)\ge100\). Since the UIPT asymptotic return probability is \(m^{-1+o(1)}\), this suggests \(W\) grows at least on the order of \(100m\), up to slowly varying factors, per root/time point. This is only a walker-noise lower bound: it omits graph-to-graph variation, root heterogeneity, paired-time covariance and finite-size bias. It is **not** a power calculation or a sample-size authorization.

The D2 design-effect sensitivity floor of 3 was established for its tree families and must not be transferred to UIPT without a non-gated pilot. Walkers and roots are nested within a graph; they are not independent graph replicates. The graph is the independent unit for cross-model uncertainty and paired covariance.

## Required gates before any future run

1. **Representation and root-law bridge:** decide whether the causal-set Hasse graph is an acceptable graph-level comparison object, and specify its root law. Resolve the UIPT canonical root-edge law versus the frozen D2/S0 uniform-vertex source convention; either justify exponent equivalence or make a separately reviewed method revision. If the Hasse graph is not acceptable, define a causal-set-native diffusion or volume observable and justify the mapping; do not force a graph analogy.
2. **Exact finite ensemble:** pin the finite UIPT approximation, root law, boundary treatment, size sequence and finite-volume radius/time cutoffs.
3. **Independent calibration:** calibrate volume growth and spectral return separately on exact controls, then test their finite-size behavior on the chosen random-map ensemble. The existing tree-only D2 calibration and deterministic-graph S0 calibration do not suffice.
4. **Scalable spectral estimator:** specify the random-walk estimator, paired-time covariance, return-count stopping/zero-return handling, uniform-root averaging and error propagation. Do not treat walkers as independent maps.
5. **Graph-level power:** use a separately labeled non-gated pilot to estimate between-map variance and source design effect. Derive power from graph-level variance; do not reuse the 0.997 D2 tree calculation or the Fisher-z correlation-precision example as a paired-test power claim.
6. **Resource gate:** benchmark one bounded implementation on small controls before selecting target sizes. Respect the 2-vCPU / 4-GB environment and do not run on shared Lightsail while EatSleepFeel is at risk.
7. **Later-pass review and authorization:** freeze seeds, manifest, hypotheses, nulls, finite-size windows, uncertainty, CPU/RAM/time limits and stop rules in a separate reviewed preregistration. Only then consider a pilot.

## Conclusion

The current answer to Issue #37 remains **undecidable**. The D3 causal-set observation and the K3 design do not provide two model classes or two independent observable families. UIPT is the preferred mathematical calibration candidate, while 4D CDT is a literature target with an unresolved operator/data bridge. Neither is ready for a stochastic run using the current validated pipeline.

The next work item is a **design-only operator/representation bridge plus a scalable UIPT random-walk estimator specification**. If that cannot be made operational within the resource ceiling, retain the cross-model question as unresolved rather than weaken the gates.

## Literature screened (not a full line-by-line source audit)

- O. Angel and O. Schramm, *Uniform Infinite Planar Triangulations* (2003): https://arxiv.org/abs/math/0207153
- O. Angel, *Growth and Percolation on the Uniform Infinite Planar Triangulation* (2003): https://arxiv.org/abs/math/0208123
- J. R. Lee, *Conformal growth rates and spectral geometry on distributional limits of graphs* (2017): https://arxiv.org/abs/1701.01598
- E. Gwynne and J. Miller, *Random walk on random planar maps: spectral dimension, resistance, and displacement* (2017; revised 2020): https://arxiv.org/abs/1711.00836
- B. Durhuus, T. Jonsson and J. F. Wheater, *On the spectral dimension of causal triangulations* (2009): https://arxiv.org/abs/0908.3643
- D. N. Coumbe and J. Jurkiewicz, *Evidence for Asymptotic Safety from Dimensional Reduction in Causal Dynamical Triangulations* (2014): https://arxiv.org/abs/1411.7712
- F. Caceffo and G. Clemente, *Spectral analysis of causal dynamical triangulations via finite element method*, Phys. Rev. D 107, 074501 (2023): https://doi.org/10.1103/PhysRevD.107.074501
