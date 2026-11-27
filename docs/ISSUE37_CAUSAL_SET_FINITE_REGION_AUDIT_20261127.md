# Issue #37 — finite-region audit and explicit Poisson slab convention

**Status:** engineering/design note only. The sampler in this change is a bounded small-fixture generator. No Issue-37 target seed, target map, S2 run, or scientific acceptance is authorized by this document.

## 1. Literature audit: the published 3D patch is not exactly reconstructible from the cited description

The spatial-distance paper by Eichhorn, Surya and Versteegen ([arXiv:1809.06192](https://arxiv.org/abs/1809.06192)) states in §4.1.1 that its 2D flat case sprinkles into an open set \(I\times I\subset\mathbb M^2\), with initial boundary \(t=0\). It describes a rectangular region and explicitly warns that the chosen region is not causally convex and therefore has edge effects; these become more important in higher dimensions. In §4.1.3 it reports the flat \(K=0\) case in \(\mathbb M^3\), but does not give the 3D patch as an explicit coordinate set.

Appendix A says \(L_t,L_x,L_y\) are the continuum dimensions of the patch and reports for \(n=3\):
- \(L_t=L_x=L_y=60\)
- realized causal-set cardinality \(N=75{,}510\)
- minimal inextendible antichain cardinality \(|\mathcal A|=1{,}571\)

The same table reports \(L_t=L_x=400\), \(N=58{,}674\) for the 2D case. The appendix does not state coordinate bounds, the exact 3D shape, or a volume formula from those three \(L\)-parameters. The naive full-box products would be \(60^3=216{,}000\) and \(400^2=160{,}000\), respectively, roughly 2.86 and 2.73 times the reported realized counts. With \(\rho=1\), those products cannot be treated as the Poisson means: deviations of that size are not plausible Poisson fluctuations. The table's \(L\)-values therefore do not license reconstructing a full rectangular box or its volume.

Versteegen's dissertation ([Heidelberg repository PDF](https://archiv.ub.uni-heidelberg.de/volltextserver/27383/1/Dissertation_Fleur_Versteegen.pdf), §§3.3.3 and 3.3.5) gives the 2+1 spatial-distance conversion and reports ten 3D sprinklings with antichains of about 1,600 elements and 30 central starting points per antichain. It still does not specify the exact finite 3D coordinate patch or its volume. The later spectral paper ([arXiv:1905.13498](https://arxiv.org/abs/1905.13498)) should not be read as supplying a missing region definition by implication.

**Conclusion:** exact reproduction of the published 3D finite region and its Poisson mean is blocked by an underspecified domain, not by the distance formula. Do not infer \(\rho\,\mathrm{Vol}(M)\) from the realized \(N=75{,}510\), and do not silently substitute \(60^3\).

## 2. Explicit project-defined slab (not a claim of exact ESV reproduction)

For a reproducible engineering fixture, this change defines the separate project-owned family

\[
M(T,L_x,L_y)=[0,T)\times[-L_x/2,L_x/2)\times[-L_y/2,L_y/2)
\]

with Minkowski metric \(\eta=\mathrm{diag}(-1,1,1)\). Its exact spacetime volume is

\[
\mathrm{Vol}(M)=T L_x L_y,
\qquad
N\sim\mathrm{Poisson}(\rho T L_x L_y).
\]

Conditional on the single Poisson draw \(N\), the \(N\) coordinates are iid uniform in the stated region. The causal relation is the strict timelike order

\[
p\prec q
\iff
\Delta t>0
\quad\land\quad
(\Delta t)^2>(\Delta x)^2+(\Delta y)^2.
\]

The initial/past antichain is the set of all minimal elements of the resulting finite poset. For a finite poset it is an initial inextendible antichain. The sampler uses no fixed-\(N\) conditioning and does not resample or truncate an over-limit Poisson draw.

The default \(N\leq256\) allocation guard exists solely to keep this generator compatible with the current dense exact spatial-geometry oracle. If the single sampled count exceeds the guard, the sampler raises PoissonDrawExceedsLimit with the realized count and allocates no coordinates. This is an explicit resource refusal, not a change to the Poisson law.

## 3. Boundary and censoring rules still required before a target run

The project-defined rectangular slab has timelike side boundaries and is not causally convex. The full minimal antichain can therefore include side-boundary-induced minimal elements; it must not be described as a uniformly sampled \(t=0\) slice.

For a continuum-distance comparison, a future geometry API should expose the minimizing common-future witness \(c_*(a,b)\). A conservative pair-level side-boundary censor is then to retain a pair only when the entire past cone of that witness down to \(t=0\) lies inside the spatial rectangle:

\[
m(c_*)=
\min\!\left(
x_*+L_x/2,\ L_x/2-x_*,
y_*+L_y/2,\ L_y/2-y_*
\right)
\geq t_*.
\]

This condition prevents the candidate's past-cone base from being clipped by a spatial side. It is not yet implemented: causal_set_spatial.py currently returns distances, not witness indices. Pairs with no common future in the finite slab remain censored as \(+\infty\), as in the exact reference; no finite distance is imputed. The future boundary \(t=T\), central-root selection, and the accepted uncensored-pair fraction must be frozen before any target batch.

Keep the two scales separate:
- \(d_m\): strict path-edge rule \(\widetilde d<d_m\) in the spatial metric.
- \(d_c\): inclusive diffusion-neighbour rule \(d\leq d_c\), including the current vertex; the PR #95 kernel adds exactly one self-choice to a loop-free input graph.

## 4. Evidence classification

- **Mathematical facts:** the rectangular volume \(T L_x L_y\); the homogeneous Poisson count law; conditional iid-uniform coordinates; transitivity of the strict Minkowski timelike relation; and the finite-poset property of the set of minimal elements.
- **Engineering observations:** deterministic tests of the one-draw Poisson implementation, coordinate bounds, strict partial-order validity and explicit resource refusal. These are unit tests, not target measurements.
- **Hypotheses, not tested here:** that a sufficiently large central uncensored subset of the chosen slab recovers the flat Euclidean spatial distance at a mesoscale; that the resulting neighbour graph has a stable transport window.
- **Not proved or established:** exact reproduction of the ESV finite patch, continuum convergence, dimensional reduction, cross-model robustness, or any Issue-37 conclusion.

## 5. Next discriminating work

1. Add minimizing-witness indices to the exact geometry oracle without changing its distance outputs.
2. Test the witness-based side-boundary censor on exact small posets and embedded-coordinate fixtures.
3. Freeze one explicit \(T,L_x,L_y,\rho\), central-root rule, future-boundary policy, and minimum retained-pair fraction in a separate preregistration before drawing target seeds.
4. Only then implement a scalable bitset/CSR relation and SWB/SIL path routine, checking every small case against unrestricted Dijkstra.
5. Connect the loop-free off-diagonal \(d\leq d_c\) graph to the PR #95 self-inclusive kernel only after graph-level connectivity, power and resource gates pass.

No target seeds or maps were drawn for this change. Issue #37 remains **UNDECIDABLE**.
