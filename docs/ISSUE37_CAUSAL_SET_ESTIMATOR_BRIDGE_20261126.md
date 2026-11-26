# Issue #37 — causal-set finite-N estimator bridge

**Status:** literature/design audit only, 2026-11-26. No code, seeds, simulation, run authorization, or scientific acceptance result was produced. This note does not modify the CS0 v0.2 grid or authorize its execution.

## Question

Can the short-scale Myrheim–Meyer (MM) decrease reported for nested causal-set intervals be separated from (a) finite-N normalization, (b) conditioning on nonempty intervals, and (c) loss of estimator resolution? Can an independently calibrated midpoint-scaling estimator distinguish the same scales?

This is a candidate design path for Issue #37, not a selected target experiment. It should be compared against the Type-II/Type-III UIPT operator bridge before either path is started.

## 1. A finite-N normalization difference that matters

The current CS0 v0.2 implementation uses the fixed-N ordering fraction

\[
r = \frac{R}{\binom{N}{2}},
\qquad
r_D = \frac{\Gamma(D+1)\Gamma(D/2)}{2\Gamma(3D/2)}.
\]

For N i.i.d. uniform points in a fixed D-dimensional Minkowski diamond, each unordered pair is related with probability r_D. Therefore \(\mathbb E[r]=r_D\) exactly for every fixed N≥2. The current causal_set_mm.myrheim_meyer_dimension function inverts this r_D relation.

The finite-volume estimator used in the nested-subdiamond literature is instead based on the Meyer-type relation-density ratio

\[
f(D)=\frac{\Gamma(D+1)\Gamma(D/2)}{4\Gamma(3D/2)}
=\frac{r_D}{2},
\qquad
\widehat f=\frac{R}{N^2}
\]

(with the paper's interval-count convention). These are asymptotically related, but they are **not the same finite-N estimator**.

For the current fixed-N sampling convention, the exact expectation is

\[
\mathbb E\!\left[\frac{R}{N^2}\middle|N\right]
=\frac{\binom{N}{2}}{N^2}r_D
=\frac{N-1}{N}f(D).
\]

This factor is a finite-occupancy effect, not a numerical approximation.

**Exact two-element check.** For a two-element chain, N=2 and R=1:

- CS0 ordering fraction: r=1, hence the current inverse maps it to D=1.
- Meyer-type relation-density ratio: R/N²=1/4=f(2), hence the literature convention maps it to D=2.

Thus the often-quoted two-element D_M=2 floor is not reproduced by the current CS0 inverse. This is not a defect in CS0: it is a different normalization/estimand. It does mean that CS0 v0.2 alone cannot reproduce the finite-volume endpoint in Abajian–Carlip.

For an edgeless interval R=0, the Meyer inverse is out of range. At N=2, R is either 0 or 1. Conditional on retaining only R>0 intervals, R/N²=1/4 deterministically, irrespective of the background dimension; the inclusion probability is r_D. Thus the conditional estimate is exactly D_M=2 for every background D, while the unconditional mean remains (N-1)f(D)/N. This is an exact finite-occupancy selection mechanism, not a UV theorem. Abajian–Carlip explicitly compare assigning such intervals dimension zero with discarding them. Discarding is a selection rule; it changes the conditional sample and must never be silently applied.

## 2. What the nested-interval literature actually reports

Abajian and Carlip study successively smaller subdiamonds inside large Poisson Minkowski sprinklings in D=3,4,5, averaging over 10,000 sprinklings. Each subdiamond therefore has random occupancy; this differs from CS0 v0.2's fixed-N sampling conditional on N. They report transition volumes of roughly 8, 16, and 22 elements respectively. At small volumes:

- assigning edgeless causal sets dimension zero drives the minimum toward zero;
- discarding edgeless sets gives minima 2.08±0.26, 2.13±0.39, and 2.19±0.40 for backgrounds D=3,4,5.

They explain the latter endpoint by the smallest retained nonempty causal set: a two-element, one-relation chain, which has R/N²=1/4 and hence D_M=2 under their convention. These are **published numerical observations under a particular estimator and selection policy**, not a theorem that the ultraviolet dimension is two.

The source also notes that the result depends on how isolated points are handled. That makes the edgeless-interval policy a primary experimental factor, not a reporting detail.

## 3. An independent causal-set estimator: midpoint scaling

Reid's midpoint-scaling estimator uses a different statistic. For an interval I[y,z] with N elements, choose an element x that maximizes the smaller of the two subinterval sizes N1,N2. Write that maximum smaller size as N_small. Assuming the longest-chain length tracks proper time, the midpoint relation gives

\[
D_{\rm mid}\approx\log_2\!\left(\frac{N}{N_{\rm small}}\right).
\]

This is not a chain-abundance estimator and is a plausible independent calibration of the same causal-set model family. It has its own resolution limit: Reid reports that for subintervals below about 10 elements, the D=2,3,4 Minkowski midpoint curves are effectively indistinguishable. Such bins should be classified as **dimension-unresolved**, not interpreted as evidence for a common dimension.

Endpoint inclusion, treatment of tied midpoints, empty subintervals, and averaging over endpoint pairs must be fixed explicitly before implementation. The formula above is not sufficient to specify those conventions.

## 4. Spectral dimension is also operator-dependent in causal sets

The phrase “causal-set spectral dimension” does not identify a unique diffusion operator.

1. **Full Hasse-diagram walk.** Eichhorn–Mizera use a finite-regulator undirected walk that chooses uniformly among retained link-neighbours, in both future and past directions. It does not respect causal time orientation. In an infinite Minkowski sprinkling, every event has infinitely many future and past links, so uniform choice from the full link set does not define a probability transition kernel. Their finite-region simulations introduce an infrared link-length cutoff to control this nonlocality. Their reported small-diffusion-time behaviour is an increase d_s>D, attributed to nonlocal superdiffusion.
2. **Causal spectral dimension.** The same paper defines a different quantity from the meeting probability of two forward-in-time causal walkers:
   \[
   d_{cs}(\sigma)=-2\frac{d\ln P_{\rm meet}(\sigma)}{d\ln\sigma}.
   \]
   It is a different observable from the return probability. The paper reports small-scale increase in the sprinkled causal sets it studies and shows that it can differ from ordinary d_s on a crystalline, preferred-foliation causal set.
3. **Spatial-hypersurface diffusion.** Eichhorn, Surya and Versteegen instead select an inextendible antichain, define an induced spatial distance, and use temporal localisation to obtain a finite neighbour set. For D=3 Minkowski sprinklings they report agreement with the spatial Hausdorff dimension at intermediate scales and indications of small-scale reduction. This is a spatial-slice observable with a different neighbour construction, not a contradiction in the same operator.

The literature therefore already contains a strong **estimator/operator-dependence mechanism** within causal sets: MM on small subintervals can fall toward two under an edgeless-selection convention, while the full Hasse walk and causal-walker meeting observable show small-scale increase, and a spatially localised hypersurface walk shows reduction. These are not interchangeable measurements. The differences may reflect genuinely different geometric questions, not merely implementation error. A 2026 preprint adds a finite-volume cutoff-dependence mechanism for link statistics in spatial dimension d≥2; it does not establish a spectral-dimension shift.


### 4.1 Finite-volume link cutoffs are part of the estimator

Boguña & Krioukov (2026, arXiv:2610.03247; preprint submitted 2 October 2026) analyze the link set from a root event in a Poisson sprinkling of \(d+1\)-dimensional Minkowski spacetime. They derive the link-intensity measure

\[
d\Lambda_{e_0}=\rho\,\tau^d e^{-\rho v_d\tau^{d+1}}\,d\tau\,dV_{\mathbb H^d},
\]

whose total mass is infinite because \(\operatorname{Vol}(\mathbb H^d)=\infty\). The normalized proper-time profile per unit hyperbolic volume is

\[
q(\hat\tau)=(d+1)\hat\tau^d e^{-\hat\tau^{d+1}},
\]

but this is **not** a probability distribution for a uniformly chosen link from the full infinite link set: no such uniform probability measure exists.

For the finite future cone \(t<T\), the rapidity cutoff depends on proper time,
\(\chi_c(\tau)=\operatorname{arcosh}(T/\tau)\). For spatial dimension \(d>1\), the hyperbolic-volume factor contributes \(\mathcal V_d(\chi_c)\propto(T/\tau)^{d-1}\), changing the normalized large-cone limit to

\[
p_T(\hat\tau)=\frac{d+1}{\Gamma(2/(d+1))}\,\hat\tau e^{-\hat\tau^{d+1}},\qquad d>1.
\]

This remains different from \(q(\hat\tau)\) as the cone grows. In \(d=1\), the cutoff dependence is logarithmic and convergence to the intensity profile is slow. Thus the finite-cone bias is dimension-dependent and does not behave like an ordinary correction that disappears merely by increasing the region.

The preprint proposes an event-centred product window with independent proper-time and rapidity cutoffs, \(0<\tau<\tau_c\) and \(0<\chi<\chi_c\), where \(\chi_c\) is independent of \(\tau\). Its truncated intensity profile is

\[
p_{\rm pw}(\hat\tau)=
\frac{(d+1)\hat\tau^d e^{-\hat\tau^{d+1}}}
{1-e^{-\hat\tau_c^{d+1}}},
\qquad
\hat\tau_c=(\rho v_d)^{1/(d+1)}\tau_c.
\]

The profile approaches \(q\) when \(\rho v_d\tau_c^{d+1}\gg1\). However, a finite rapidity cutoff is defined relative to a timelike reference direction and introduces a preferred frame; this is a controlled **intensity-profile estimator**, not an automatic Lorentz-invariant random-walk prescription. The authors' exact-link simulations in 1+1, 2+1 and 3+1 dimensions (5,000, 400 and 250 independent sprinklings respectively) agree with their finite-cone and product-window predictions. These are the preprint's numerical observations, not Emergence Lab measurements.

**Implications and limits for Issue #37**

- A full-Hasse simple random walk on the infinite sprinkling has no canonical uniform-neighbour transition rule. Any finite-region implementation defines a cutoff-dependent kernel; the cutoff geometry and its scaling are part of the estimator, not incidental implementation details.
- For \(d\ge2\), a constant-time-cone exhaustion retains a different normalized link proper-time profile even as the cone grows. A finite-cone Hasse-walk or forward causal-walker study must therefore specify its exhaustion and link cutoff, and test sensitivity to alternative regularizations before claiming an intrinsic infinite-volume spectral observable.
- The same concern is **potentially** relevant to forward causal walkers because they also select future links, but this preprint does not derive their meeting probability or a bias in \(d_{cs}\). It does not directly analyze the spatial-hypersurface operator.
- The finite-cone profile has leading power \(\hat\tau^1\) for every \(d>1\), unlike the intensity-profile power \(\hat\tau^d\). Fitting the former as if it were the latter could produce an apparent lower-dimensional link statistic. That is a sampling consequence, **not** evidence of physical ultraviolet dimensional reduction.
- This result does not directly alter CS0's Myrheim–Meyer relation count or the midpoint-scaling statistic: neither selects a uniformly random link. No such bias should be imputed to those estimators without a separate derivation.


## 5. Current repository dependency audit

At main 45107e899c0f6889a79cca579ef0a3f5420028db:

- src/emergence_lab/causal_set_mm.py and its tests implement the fixed-N ordering-fraction reference.
- src/emergence_lab/cs0_worker.py is a row producer for the full 728-row grid (720 stochastic rows plus 8 exact controls) and a 40-row engineering fixture.
- src/emergence_lab/cs0_recheck.py independently checks stored counts, fractions, classifications and gates; it explicitly cannot certify that the original relations were partial orders or that points lay inside the diamond.
- src/emergence_lab/cs0_supervisor.py is a per-worker supervisor building block.
- src/emergence_lab/cs0_engineering.py runs only the fixed engineering fixture and records aggregate_caps_enforced=false.
- docs/CS0_CONTAINER_ENGINEERING.md and the Docker wrapper establish an engineering-only cgroup/containment path, not a full-study authorization or the CS0 ten-minute aggregate CPU budget.

**The full CS0 study launcher is still missing.** It must validate a committed, versioned authorization and frozen entropy; enforce aggregate CPU/RSS/output limits; verify a clean exact-pinned checkout; and leave a durable INCOMPLETE record on every setup/provenance/resource stop. The lower-level worker's full-mode CLI is not an authorization gate and must not be invoked directly as a study run. No full-run authorization exists and no CS0 full-grid seeds have been drawn.

The old branch research/causal-set-cs0-prereg-20261106 has two commits ahead but is 116 behind main; its worker and test blobs match main, while its preregistration blob is older. It contains no missing implementation to merge.

## 6. Design decision required before any run

A later-pass review should decide whether a versioned CS0 v0.3 / CS1 design is worthwhile. If pursued, the minimum design matrix should include:

- fixed-N ordering fraction R/binom(N,2) (CS0 v0.2, unchanged);
- the finite-volume R/N² convention with its exact finite-N expectation and explicit Poisson-N versus fixed-N sampling;
- midpoint scaling with all endpoint/tie/empty conventions frozen;
- nested subdiamonds with **all** intervals retained in the primary record, plus separately reported conditional-on-nonempty summaries;
- a predeclared dimension-resolution censor for midpoint bins where D=2,3,4 controls are not separable (the Reid result suggests N<10 is not informative, but the project's own calibration must set the gate);
- null partial orders and an independent stored-artifact recheck.

The two relation-count normalizations R/binom(N,2) and R/N² are deterministic transforms of the same R,N and **do not count as independent estimators**. Midpoint scaling is the distinct statistic. These can be evaluated on the same sprinkled samples, but paired dependence must be reported; “independent estimator” means a separately calibrated statistic, not statistically independent samples. The CS0 v0.2 global calibration is not a substitute for this scale-resolved design.

Do not draw seeds, add a run authorization, or start a full study until the design and a full containment/authorization runner receive later-pass review. The UIPT Type-II/Type-III bridge remains a valid alternative design candidate; this note does not reject it.

## Evidence classification

- **Literature results / published numerical observations:** the Abajian–Carlip nested-diamond findings; Reid's midpoint-resolution findings; the distinct diffusion behaviours reported by Eichhorn–Mizera and Eichhorn–Surya–Versteegen.
- **2026 preprint analytic result and preprint simulations:** Boguña–Krioukov derive a finite-cone link proper-time distribution that remains cutoff-dependent for spatial dimension d≥2, and report independent sprinkling simulations matching the finite-cone and product-window predictions. This is a result about link statistics, not a spectral-dimension theorem.
- **Exact arithmetic derived here:** the fixed-N expectation for R/N² and the two-element-chain normalization comparison.
- **Repository facts:** the code/runner status in §5, verified from main.
- **Hypothesis:** a material part of the reported D_M≈2 endpoint is induced by finite occupancy plus conditioning on nonempty intervals. This mechanism is strongly supported by the estimator definition and the cited small-interval analysis, but has not been measured independently in this repository.
- **Not established:** universal dimensional reduction, its absence, or any physical-spacetime conclusion.

## Sources

- Abajian & Carlip, [Dimensional reduction in manifold-like causal sets](https://arxiv.org/abs/1710.00938), especially §§2–4.
- Reid, [The Manifold Dimension of a Causal Set: tests in conformally flat spacetimes](https://arxiv.org/abs/gr-qc/0207103), especially §III and Fig. 1 discussion.
- Surya, [The causal set approach to quantum gravity](https://doi.org/10.1007/s41114-019-0023-1), especially §4.1.
- Eichhorn & Mizera, [Spectral dimension in causal set quantum gravity](https://arxiv.org/abs/1311.2530), especially §§III–IV.
- Eichhorn, Surya & Versteegen, [Spectral dimension on spatial hypersurfaces in causal set quantum gravity](https://arxiv.org/abs/1905.13498), especially §§I–II and results.
- Boguña & Krioukov, [Sampling biases in sprinkled causal sets](https://arxiv.org/abs/2610.03247) (2026 preprint), especially §§II–V and VII.
