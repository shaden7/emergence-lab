# Issue #37 — cross-model feasibility screen

## Current status after PR #90 — 2026-11-26

PR #90 was merged with expected head 80d246add91d6056de767921fce527511a67623c as Main commit 2af8c7a80232fc1910b73017f34826c8725a5ff6. The original Graph / _from_edges builder remains simple, but the new MultiGraph / _from_multiedges path preserves parallel edges as repeated unit-valued CSR half-edges; graph_even_returns explicitly coalesces duplicates after row scaling. Exact small-graph dense-oracle tests pass on SciPy 1.18.1. This closes the small-graph Type-II representation/control blocker, not target-scale feasibility.

Current Main CI 45878839010 completed-success on cf08d9f0ee7843b03d9c01dd3e4748a0f473b22a: 1,047 tests and 65 subtests passed in 96.21 seconds. Artifact 15146152250 contains 55 files / 371,221 bytes, SHA-256 70fb0e8146cec7004f32163f1eda8bde88742ff0bc8ebc3111842cb5f9acbe3e. Component manifests pin current Main cf08d9f; the aggregate root manifest still has commit=null. CS0 remains ENGINEERING_ONLY and study_authorized=false; S1b is PARTIAL, SE-audit BLOCKED, S1 P0 remains engineering-only, and coverage/finite-size gates were skipped. No Issue #37 target-map data or S2 authorization is present.

The Type-II UIPT has a direct infinite-volume spectral-dimension theorem: Gwynne–Miller Theorem 1.6 includes maps with no self-loops and parallel edges allowed and proves d_s=2. This is not a finite-N acceptance window or validation of our estimator. Type III still lacks a direct d_s=2 theorem in the cited literature; its annealed root-law exponent transfer is derived below. The projected Type-II target grid exceeds the 100,000,000 directed-edge-step budget for the current exact S0 kernel by operation-count projection; no target-scale benchmark has been run. The S0 preregistration also sets a general 512 MiB process envelope, but the 1.49 GiB CSR estimate below is for the Type-III simple-graph representation, not a Type-II measurement. Type-II memory use remains unbenchmarked. The separate code-level 512 MiB estimated-memory guard is in SelfInclusiveKernel, not in the Type-II graph_even_returns path. **Literature correction:** Angel (2003), Section 2, already gives an exact local peeling sampler for the infinite Type-II UIPT. The missing item is a repository implementation, not a sampler in the literature. Angel's construction samples finite neighborhoods of the infinite UIPT; it is not a finite-N uniform spherical-triangulation generator. An implementation needs a combinatorial-map state with cyclic boundary order / rotation-system data and explicit finite-component fillings; Euclidean coordinates are not needed for the random-walk observable. Finite-size calibration, a scalable estimator with a predeclared power calculation, and target data remain absent.

## Type-II UIPT: exact local peeling sampler and S0 return-probability cross-check

**Evidence class: published sampling construction plus a derived estimator identity; no repository implementation, target seed, or target run.**

### Exact local sampler (Angel, 2003)

Angel studies Type-II triangulations: double / parallel edges are allowed, self-loops are not. For a current unexplored outer face with boundary length \(m+2\), let \(C_m\) denote the infinite-side limiting weight and \(Z_m\) the partition function of finite free triangulations. With \(\alpha=27/2\), the probability that the triangle incident to a selected boundary edge introduces a new vertex is

\[
p_{\mathrm{new}}(m)=\frac{C_{m+1}}{\alpha C_m}
=\frac{2m+3}{3m+3}.
\]

If the third vertex is an existing boundary vertex \(x_i\), \(1\le i\le m\), the two orientations distinguish which of the two resulting components is infinite. Angel's equation (2.4) gives

\[
\mathbb P(y=x_i,\ T_2\ \text{infinite})
=\frac{C_{m-i}Z_{i-1}}{C_m},
\]

and reflection gives the other orientation,

\[
\mathbb P(y=x_i,\ T_1\ \text{infinite})
=\frac{Z_{m-i}C_{i-1}}{C_m}.
\]

The finite component is filled by an independent free Boltzmann triangulation; the infinite component is a UIPT of the remaining polygon. The convention \(\varphi_{0,0}=1\) is essential: it allows a 2-gon to close by gluing its two boundary edges without adding an interior vertex.

Exact rational examples from these formulae:

| \(m\) | Boundary length | \(p_{\mathrm{new}}\) | Total closure probability |
|---:|---:|---:|---:|
| 0 | 2 | \(1\) | \(0\) |
| 1 | 3 | \(5/6\) | \(1/6\) |
| 2 | 4 | \(7/9\) | \(2/9\) |
| 3 | 5 | \(3/4\) | \(1/4\) |

Theorem 1.10 supplies the spatial Markov property and conditional independence of the finite and infinite components. Angel explicitly notes that the next boundary edge may be chosen adaptively from the explored state. To sample a radius-\(r\) neighborhood, peel while any boundary vertex has distance less than \(r\) from the root; this terminates almost surely for fixed \(r\). Thus the literature sampler is already exact for local Type-II UIPT neighborhoods. It is not a finite-\(N\) generator.

For the S0 half-kernel identity, write

\[
q_t(\rho)=P^{2t}(\rho,\rho)
=d_\rho\sum_x\frac{P^t(\rho,x)^2}{d_x}.
\]

Every endpoint \(x\) of a \(t\)-step walk is within graph distance \(t\), and its full degree \(d_x\) enters the identity. Sampling to radius \(r=t+1\) leaves every vertex at distance at most \(t\) in the interior, so all required degrees are known. This is an exact locality statement, not a finite-size approximation.

### Pair-collision U-statistic (derived; same spectral observable)

Conditional on one fixed undirected loop-free graph, let \(X_1,\ldots,X_W\) be independent endpoints of \(W\) simple random walks of \(t\) steps from \(\rho\). Then

\[
\widehat q_t
=\frac{d_\rho}{\binom W2}
\sum_{a<b}\frac{\mathbf 1\{X_a=X_b\}}{d_{X_a}}
\]

is an unbiased U-statistic for the same \(q_t(\rho)\) used by S0. With
\(h(x,y)=d_\rho\mathbf 1\{x=y\}/d_x\),
\(\zeta_1=\operatorname{Var}(\mathbb E[h(X_1,X_2)\mid X_1])\), and
\(\zeta_2=\operatorname{Var}(h(X_1,X_2))\), its exact conditional variance is

\[
\operatorname{Var}(\widehat q_t\mid G)
=\frac{4(W-2)}{W(W-1)}\zeta_1
+\frac{2}{W(W-1)}\zeta_2.
\]

A deterministic exact-rational control on the multigraph with adjacency

\[
A=\begin{pmatrix}
0&2&0&1\\
2&0&1&0\\
0&1&0&1\\
1&0&1&0
\end{pmatrix},
\quad d=(3,3,2,2),\quad \rho=0,\quad t=2,\quad W=3
\]

has \(P^t(\rho,\cdot)=(11/18,0,7/18,0)\), \(q_t=389/648\), and exact enumeration of all \(W\)-endpoint tuples gives
\(\mathbb E[\widehat q_t]=389/648\) and
\(\operatorname{Var}(\widehat q_t)=49511/419904\), matching the U-statistic variance formula. This is a finite-graph algebraic control, not a random-map sample or target measurement.

For a random graph ensemble,
\(\operatorname{Var}(\widehat q_t)
=\mathbb E[\operatorname{Var}(\widehat q_t\mid G)]
+\operatorname{Var}(q_t(G))\); walkers on one map do not replace independent map replicates for graph-level uncertainty. Endpoint degrees must be fully exposed, which the radius-\(t+1\) local sample guarantees.

**Scope restriction:** this is a second computational estimator of the same random-walk return observable, not a distinct dimension-estimator family. Under the adopted S1 spectral next-decision note, algorithmic re-implementations / re-aggregations of the same spectral observable are internal robustness checks and do not satisfy Issue #37's distinct-estimator requirement. No numerical variance-reduction ratio is accepted: earlier scratch ratios have no archived script, graph construction, seed manifest, or raw output.

### Walk-adaptive peeling: implementation proposal, not a result

Because Angel permits the next boundary edge to be chosen from the explored state, a walk-coupled lazy exploration is plausible: if the current walker vertex is on the boundary, peel incident boundary edges until its full star is known, then choose uniformly among its incident half-edges. For the pair-collision estimator, expose each endpoint's star after the \(t\)-step walk. Multiple walkers can be interleaved on the same lazily sampled map, using independent transition randomness.

This is a derived implementation plan, not an already implemented or benchmarked Type-II routine. The implementation must test the conditional-law invariant under adaptive peeling, termination, half-edge multiplicity, endpoint-degree completeness, and graph-level independence. The published walk/peeling construction of Benjamini–Curien (2013) is for the UIPQ; it is an analogue, not direct Type-II UIPT evidence. No resource saving is claimed.

### Root convention and resource consequences

For a finite spherical Type-II triangulation with \(N\) vertices, \(E=3N-6\) and \(\bar d_N=2E/N=6-12/N\). Conditional on the map, the origin of a uniformly selected oriented root edge has law \(P_E(v)=d(v)/(2E)\), whereas a uniform vertex has law \(P_V(v)=1/N\). Hence

\[
\frac{dP_V}{dP_E}(v)=\frac{\bar d_N}{d(v)}.
\]

This exact reweighting matters for finite-\(N\) annealed means and variances. Gwynne–Miller's Type-II \(d_s=2\) theorem is already an almost-sure infinite-volume statement under the natural rooted-map law; they also note that, when the spectral-dimension limit exists, it does not depend on the chosen starting vertex. That does not make finite-\(N\) root averages interchangeable.

Angel's Theorem 1.2 gives Type-II UIPT ball-volume growth exponent 4 with polylogarithmic bounds. This is a mathematical volume statement, not a runtime or memory benchmark. A full local sample can therefore remain large; lazy walk-coupled peeling may reduce explored volume, but its cost has not been measured. The CSR MultiGraph added by PR #90 is the random-walk adjacency representation after sampling; it does not itself retain the planar boundary order needed by the peeling state.

**Decision:** the literature sampler removes the claim that Type-II local sampling is unknown, but not the implementation, finite-size/power, or resource gates. Pair collision is eligible as an S0 cross-check only, not as Issue #37's independent second estimator. No target work is authorized by this note.

Sources: Angel (2003), *Growth and Percolation on the Uniform Infinite Planar Triangulation*, Sections 1.2.2 and 2, equations (2.3)–(2.4), Theorem 1.10, Theorem 1.2: https://arxiv.org/abs/math/0208123. Gwynne–Miller (2020), *Random walk on random planar maps: spectral dimension, resistance, and displacement*, Section 1.3, equations (1.9)–(1.10), Theorem 1.6: https://arxiv.org/abs/1711.00836. Benjamini–Curien (2013), UIPQ walk/peeling analogue: https://arxiv.org/abs/1202.5454.

## Root-law exponent transfer for finite Type-III triangulations (derived; not a finite-N acceptance rule)

Let T_N be a uniform simple spherical triangulation with N vertices. Write d(v) for vertex degree and dbar_N=2E/N=6-12/N. Let V be a uniformly selected vertex and U the origin of a uniformly selected oriented root edge. Conditional on T_N,
\[
\mathbb P(U=v\mid T_N)=\frac{d(v)}{2E}
=\frac{d(v)}{N\bar d_N}.
\]
For Q_t(v)=P^{2t}(v,v) in [0,1], define the annealed returns q_V(N,t)=E[(1/N) sum_v Q_t(v)] and q_E(N,t)=E[(1/(2E)) sum_v d(v)Q_t(v)]. Then
\[
q_E(N,t)=\frac{\mathbb E[d(V)Q_t(V)]}{\bar d_N}.
\]
Since every vertex of a simple triangulation has degree at least 3,
\[
q_E(N,t)\ge \frac{3}{\bar d_N}q_V(N,t).
\]
For every p>1, Hölder and Q_t<=1 give
\[
q_E(N,t)\le
\frac{(\mathbb E[d(V)^p])^{1/p}}{\bar d_N}
q_V(N,t)^{1-1/p}.
\]
Stufler (2024), Proposition 10.1 (restating Angel–Schramm 2003, Lemma 4.1), proves a uniform exponential tail
\(\mathbb P(d(U)=k)\le C(3/4+\varepsilon)^k\) for the origin of the uniform root edge in T_N, uniformly in N. Hence all root-edge degree moments are uniformly bounded. The exact size-bias identity
\(\mathbb E[d(V)^p]=\bar d_N\,\mathbb E[d(U)^{p-1}]\), together with \(3\le\bar d_N<6\), gives uniform moments under the uniform-vertex law as well.

Consequently, if q_V(N,t) has a polynomial return exponent t^{-alpha+o(1)} in a specified joint finite-size regime, the two inequalities and p→infinity imply q_E(N,t)=t^{-alpha+o(1)}. This is an annealed exponent-transfer lemma, conditional on the same regime and uniform moment bounds. It does not prove alpha=1, does not set an admissible finite-N window, and does not make finite-N means, variances or root samples interchangeable. A finite estimator must still state whether it samples root edges or vertices and, if reweighted, account for the induced variance/design effect. It is not a Type-III spectral-dimension proof.

Source: Stufler (2024), Proposition 10.1 (https://alea.impa.br/articles/v21/21-07.pdf), which cites Angel–Schramm (2003), Lemma 4.1 (https://arxiv.org/abs/math/0207153).


**Date:** 2026-11-26  
**Status:** design-only feasibility decision; no UIPT/CDT target seeds, target samples, model implementation, or experiment authorization. Standard PR CI runs the repository's existing fixed-seed engineering/development fixtures on disposable GitHub runners; those outputs are not UIPT/CDT target data or scientific acceptance evidence.

## Question

Can the current project run a defensible, affordable comparison of short-scale dimension across a second model class and at least two independently calibrated observables, without reopening the terminal S1/S1b random-tree size-equivalence work or treating graph representations as physical ontology?

## Decision

**No-go for a stochastic cross-model target run with the currently validated implementations.** The current evidence does not yet provide a common, physically justified observable across the causal-set and candidate model classes, and the existing exact spectral kernel cannot reach the volume-growth size range estimated for random planar maps.

The **uniform infinite planar triangulation (UIPT)** remains a conditional *mathematical calibration candidate*. The original Graph / _from_edges API is still simple, but PR #90 now provides a multiplicity-preserving MultiGraph / _from_multiedges path for small exact S0 controls; graph_even_returns explicitly coalesces repeated CSR columns after row scaling. The Type-II literature pair (d_H,d_s)=(4,2) is therefore representable on small controls, but the repository has no implementation of Angel's exact local rooted Type-II UIPT sampler or target-scale estimator. Type III still lacks a direct d_s=2 theorem; its annealed root-law exponent transfer is conditional on the moment lemma above. Neither model is ready for a stochastic target run. These asymptotic exponents do not evidence a short-scale flow or physical spacetime.

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

The finite ensemble must be pinned before use. In the canonical finite rooted ensemble, the oriented root edge is uniform, so the root vertex is selected proportional to its degree; for type II this is edge-degree, counting parallel edges. A finite rooted triangulation and its local UIPT limit are not identical objects; the admissible radius/time window must remain below finite-volume and mixing cutoffs. The asymptotic exponents are reference targets, not finite-N acceptance thresholds. Type II has a direct infinite-volume d_s=2 theorem and a multiplicity-preserving small-graph S0 path. For Type III, the moment lemma above transfers an annealed polynomial return exponent between root-edge and uniform-vertex laws, but it does not prove d_s=2 or equate finite-N means and variances.

### 3. Causal dynamical triangulations: relevant literature, unresolved operator and data bridge

A 2014 4D CDT analysis reports a spectral dimension decreasing from approximately 4 at large scales to approximately 3/2 at short scales. This is a published numerical result, not a project observation.

The operator cannot be left implicit. Caceffo and Clemente (2023) compare the dual-graph spectrum with a finite-element Laplace–Beltrami spectrum in test geometries, a 2D CDT configuration, and a spatial slice extracted from a 4D CDT configuration. They report that, except for nonpathological cases in two dimensions, the two spectra and spectral dimensions do not generally agree quantitatively or qualitatively. Crucially, they explicitly defer the finite-element refinement problem for full 4D CDT configurations to future work. Their paper therefore supports an operator-bridge warning, not a direct FEM validation or refutation of the published full-4D CDT spectral-dimension flow. A future 4D comparison must preregister which operator is meant and why it is relevant. No raw CDT configurations, pinned generator, or reproducible CDT pipeline were found in this repository audit.

Two-dimensional CDT is not an adequate substitute for an independent random-geometry family here: Durhuus, Jonsson and Wheater (2009) show its uniform infinite version is equivalent to the uniform infinite planar tree, with Hausdorff dimension 2 and spectral dimension at most 2 (equal to 2 for specified reduced versions). This would overlap the already terminal random-tree spectral line and must not be used to reopen S1/S1b.

## Observable definitions required for any future UIPT comparison

For a finite connected graph G, let mu_G be the preregistered root law and draw v_s from mu_G. The root law is part of the model definition, not an implementation detail. Type-II and Type-III UIPT root-edge laws are degree-biased; Type II additionally counts parallel edges. PR #90 makes the S0 transition operator multiplicity-correct for small multigraph controls. The Type-III moment lemma above establishes only conditional equality of annealed polynomial exponents, not equality of finite-N means, variances or samples. The S0 API computes returns from an explicit source; any ensemble estimator must separately sample the canonical root law or apply a justified reweighting with its variance/design effect. For a causal-set Hasse graph, a uniform-event root is a model-specific choice and does not become a UIPT root law by graph conversion. The candidate graph-level observables are:

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
- For type III, the current S0 graph_even_returns kernel caps max_half_time × nnz at 100,000,000 directed-edge steps. The first preregistered G1 slope at m=32 requires max_half_time=64, about 3.84 billion edge-step operations; the full G1 grid through m=128 requires max_half_time=256, about 15.36 billion. Even a hypothetical m=1 slope pair would exceed the cap at about 120 million. Type II has the same half-edge incidence count when parallel edges are counted. PR #90 now preserves that multiplicity for small exact controls, so the 100M operation-count projection also excludes the projected Type-II target grid. The memory estimate in the next bullet is specific to Type-III simple-graph CSR; it does not establish Type-II memory use. A Type-II implementation requires its own memory estimate and benchmark. Deduplication is not a valid workaround.
- D2's existing design uses 8 independent graphs and 256 sources per graph per size: 2,048 BFS traversals per size. At this adjacency size, the order-of-work estimate is about \(1.23\times10^{11}\) adjacency visits per size, or \(3.69\times10^{11}\) across three sizes. This is an algorithmic count, not measured wall time.
- For the type-III simple graph, the `Graph` class retains int64 row pointers (about 80 MB) and int32 adjacency indices (about 240 MB); the float64 CSR data and CSR row pointers add about 520 MB, for at least roughly 840 MB before auxiliary arrays. The S0 transition CSR adds about 760 MB in data, indices and row pointers. Together these are roughly 1.6 GB (about 1.49 GiB) before degree/row vectors and other temporaries. This static payload alone is about 3.0× S0's frozen 512 MiB process budget, so the memory gate fails independently of the 100,000,000 operation cap. This is a static payload estimate, not measured peak RSS. A multiplicity-preserving type-II implementation requires its own memory benchmark.

A Monte Carlo random-walk estimator could avoid the exact-kernel cap, but it would be a new method and needs a separate calibration. For a return indicator with probability \(q(m)\), the conditional relative standard error is approximately \(1/\sqrt{Wq(m)}\) when \(q\) is small. A 10% relative standard error therefore needs roughly \(Wq(m)\ge100\). Since the UIPT type-II asymptotic return probability is \(q(m)=m^{-1+o(1)}\), this implies the asymptotic requirement \(W\gtrsim100m^{1-o(1)}\) up to subpolynomial factors per root/time point. The exponent alone supplies no finite-\(m\) constant lower bound. This is only a walker-noise lower bound: it omits graph-to-graph variation, root heterogeneity, paired-time covariance and finite-size bias. It is **not** a power calculation or a sample-size authorization.

The D2 design-effect sensitivity floor of 3 was established for its tree families and must not be transferred to UIPT without a non-gated pilot. Walkers and roots are nested within a graph; they are not independent graph replicates. The graph is the independent unit for cross-model uncertainty and paired covariance.

## Required gates before any future run

1. **Causal-set representation and root-law design:** decide whether the causal-set Hasse graph is an acceptable graph-level comparison object and specify its root law. For UIPT, keep the canonical root-edge law explicit. The Type-III annealed exponent transfer is derived under uniform degree-moment bounds, and Type II has a direct theorem; finite-N sampling, reweighting, means and variance still need a separately reviewed design. If the Hasse graph is not acceptable, define a causal-set-native diffusion or volume observable and justify the mapping; do not force a graph analogy.
2. **Exact finite ensemble and graph variant:** pin type II or type III, the finite UIPT approximation, root law, boundary treatment, size sequence and finite-volume radius/time cutoffs. The small-graph Type-II multiplicity representation is integrated via MultiGraph; a repository implementation of Angel's exact local sampler and a target-scale implementation are still absent. For Type III, the root-law exponent transfer does not establish d_s=2; a separate spectral-dimension proof/transfer is still needed.
3. **Independent calibration:** calibrate volume growth and spectral return separately on exact controls, then test their finite-size behavior on the chosen random-map ensemble. The new S0 multigraph dense-oracle tests validate small-graph transition semantics only; they do not calibrate a finite-size random-map ensemble or estimator power. The existing tree-only D2 calibration and deterministic-graph S0 calibration remain insufficient.
4. **Scalable spectral estimator:** specify the random-walk estimator, paired-time covariance, return-count stopping/zero-return handling, root-law averaging and error propagation. Preserve edge multiplicity if type II is chosen; do not silently replace it with a simple graph. Do not treat walkers as independent maps.
5. **Graph-level power:** use a separately labeled non-gated pilot to estimate between-map variance and source design effect. Derive power from graph-level variance; do not reuse the 0.997 D2 tree calculation or the Fisher-z correlation-precision example as a paired-test power claim.
6. **Resource gate:** benchmark one bounded implementation on small controls before selecting target sizes. Respect the 2-vCPU / 4-GB environment and do not run on shared Lightsail while EatSleepFeel is at risk.
7. **Later-pass review and authorization:** freeze seeds, manifest, hypotheses, nulls, finite-size windows, uncertainty, CPU/RAM/time limits and stop rules in a separate reviewed preregistration. Only then consider a pilot.

## Conclusion

The current answer to Issue #37 remains **undecidable**. PR #90 closes the small-graph Type-II representation blocker, and Gwynne–Miller directly prove d_s=2 for the infinite Type-II UIPT. No repository implementation of the exact local Type-II sampler, finite-size calibration, scalable estimator or graph-level power calculation exists. For Type III, the annealed root-law exponent bridge is now available under uniform moment bounds, but the cited literature still does not directly prove d_s=2. The D3 causal-set observation and K3 design do not provide two model classes or two independent observable families. Full 4D CDT retains an operator/data bridge blocker; Caceffo and Clemente defer FEM on full 4D configurations. No variant is ready for a stochastic target run using the current validated pipeline.

The next work item is a **design-only implementation plan for Angel's exact local Type-II UIPT sampler and finite-size/root-law handling, plus a scalable independently calibrated spectral estimator and graph-level power calculation**. A Type-III spectral-dimension proof/transfer remains a separate mathematical branch; its root-law exponent bridge alone is not that proof. Clarify the full-4D CDT operator/data path separately. If these cannot be made operational within the resource ceiling, retain the cross-model question as unresolved rather than weaken the gates.

## Literature screened (not a full line-by-line source audit)

- O. Angel and O. Schramm, *Uniform Infinite Planar Triangulations* (2003): https://arxiv.org/abs/math/0207153
- O. Angel, *Growth and Percolation on the Uniform Infinite Planar Triangulation* (2003): https://arxiv.org/abs/math/0208123
- J. R. Lee, *Conformal growth rates and spectral geometry on distributional limits of graphs* (2017): https://arxiv.org/abs/1701.01598
- E. Gwynne and J. Miller, *Random walk on random planar maps: spectral dimension, resistance, and displacement* (2017; revised 2020): https://arxiv.org/abs/1711.00836
- B. Durhuus, T. Jonsson and J. F. Wheater, *On the spectral dimension of causal triangulations* (2009): https://arxiv.org/abs/0908.3643
- D. N. Coumbe and J. Jurkiewicz, *Evidence for Asymptotic Safety from Dimensional Reduction in Causal Dynamical Triangulations* (2014): https://arxiv.org/abs/1411.7712
- F. Caceffo and G. Clemente, *Spectral analysis of causal dynamical triangulations via finite element method*, Phys. Rev. D 107, 074501 (2023): https://doi.org/10.1103/PhysRevD.107.074501


## Implementation update — 2026-11-26 (PR #90 integrated)

The original Graph / _from_edges API remains simple. MultiGraph / _from_multiedges now preserve each parallel edge as a repeated unit-valued CSR half-edge. graph_even_returns validates loop-free, aggregate-symmetric, unit-entry, connected CSR input; row scaling followed by explicit sum_duplicates() creates the multiplicity-weighted transition matrix. The operation budget is checked before coalescing, so all half-edge incidences count.

Seven new tests compare the S0 half-kernel with dense matrix powers, distinguish simple from multi-edge walks, check multiplicity-aware budgeting, and reject loops, invalid endpoints/shapes and asymmetric multiplicities. Local scratch validation on SciPy 1.17.0 exercised 1,100 random connected loop-free multigraphs (2–12 vertices), all roots and half-times 1–8: 61,600 return values versus dense matrix powers, maximum absolute error 5.33e-15. This is a numerical software observation, not a theorem, repository CI result or random-map sample.

The implementation closes the small-graph representation/control blocker for Type II. The projected Type-II target grid still exceeds the 100,000,000 directed-edge-step budget of the current exact S0 kernel. The S0 preregistration's 512 MiB process envelope remains a general run constraint, but the 1.49 GiB static CSR estimate above is for Type-III simple-graph storage; Type-II target-scale memory has not been benchmarked, so no Type-II memory failure is measured. The separate code-level 512 MiB estimated-memory guard is implemented in SelfInclusiveKernel, not in graph_even_returns. The repository still lacks Angel's local Type-II sampler implementation, a combinatorial-map boundary representation/provenance, finite-size calibration, a scalable estimator or graph-level power. No target seeds, target samples, pilot or S2 are authorized by this implementation.
