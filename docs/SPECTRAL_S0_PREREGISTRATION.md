# S0 — Spectral-dimension estimator: analytical and finite-graph calibration (Issue #37)

**Status: preregistration proposed (v0.1), not a completed measurement.**
**Date:** 2026-10-12. **Prerequisite:** D2 instrument decision on main (PR #42, merge a517b0b).
**Scope:** calibration only; no claim of short-scale dimensional reduction, emergent geometry, or physical spacetime.

## 1. Question and epistemic scope

Does a new random-walk return-probability instrument (a) reproduce known spectral dimensions on one- and two-dimensional lattices and (b) reject finite-size saturation, parity artefacts and fast-mixing graph nulls as spurious "dimension reduction"?

This S0 tests **implementation and scale diagnostics**, not the hypotheses of Issue #37 about spacetime. The graph is an instrument representation, not an assumed ontology. The known lattice dimension is *built in*, so successful recovery is not emergence. CAY and UST are reserved for the next independently preregistered S1 feasibility/power step; in particular the D2 volume-growth calibration does NOT validate a spectral estimator.

## 2. Frozen mathematical observable

For a connected, finite, undirected **simple** graph G, let A be its adjacency matrix and D the diagonal degree matrix, P = D^(-1) A. No self-loops, no holding probability, and no teleportation. Starting from a vertex v, define q_v(t) = [P^(2t)]_(v,v) for positive **half-time** t. Even steps remove the odd-time zero-return pathology of bipartite graphs. The source is fixed, not sampled from the stationary measure. When multiple sources are used later they must be **uniformly sampled vertices**, with degree dependence explicitly reported, and their return probabilities averaged *before* taking logarithms. Avoid mixing q_v with the heat-kernel trace weighted by degree.

The dyadic local spectral dimension is

    d_s,eff(t) = -2 [ln q(2t) - ln q(t)] / ln 2

so q(t) is the return probability at physical walk time 2t. A measured dyadic slope at one t is **not** automatically an asymptotic dimension. A stable scaling window, finite-size headroom, controls, statistical power and a preregistered decision rule will be necessary in S1.

**Mathematical identity (proved from reversibility, used for the code reference):**

    q_v(t) = deg(v) * sum_x ([P^t]_(v,x))^2 / deg(x).

Proof: detailed balance gives deg(x) [P^t]_(x,v) = deg(v) [P^t]_(v,x); multiply the two half-step kernels and sum over x. This is exact in mathematics; floating-point implementation and graph validity are distinct concerns. Isolated vertices are forbidden.

**Finite-state null:** q_v(t) approaches pi(v)=deg(v)/(2|E|) for connected non-bipartite G, and 2*pi(v) on the even subsequence for connected bipartite G. Thus a declining d_s,eff(t) near this floor is an expected finite-size/periodicity artefact. A future positive spectral-dimension verdict must censor times at which q_v(t) <= 10 times the appropriate stationary floor, and test robustness to thresholds 5 and 20. For CAY/UST, whose graphs are trees, that floor is 2*pi(v), **not** 1/N; root-degree dependence matters.

## 3. Independent known-answer controls (no random draws)

For infinite nearest-neighbour simple random walks, exact combinatorial return probabilities at 2t steps are

    Z^1: q(t) = C(2t,t) / 4^t.
    Z^2: q(t) = [C(2t,t) / 4^t]^2.

For a finite d-dimensional periodic torus (d=1 or 2, side L), exact discrete Fourier diagonalisation gives

    q(t) = L^(-d) sum_{k in {0,...,L-1}^d}
              [(1/d) sum_j cos(2*pi*k_j/L)]^(2t).

These are **different computations** from the graph-based transition matrix implementation. Their agreement is the cross-check; they are not independent empirical observations.

- **S0-G0, exact-graph implementation (STOP):** On cycle C8, 6x6 periodic square lattice, a 5-vertex star (nonregular degrees), triangle and single edge K2, compare the 2t-step return probabilities from the reversibility identity against independently assembled dense transition-matrix powers at t=1,2,4. Absolute error <= 1e-12 in all cases. Verify even-time K2 returns 1 and odd-time K2 returns 0. Reject invalid time, vertex, disconnected/isolated inputs and work budgets exceeded.
- **S0-G1, lattice spectrum:** Compute Fourier q for (d,L)=(1,256),(2,64) at t=32,64,128,256. For each t, relative discrepancy from its infinite-lattice combinatorial reference <= 0.01; for dyadic slopes at t=32,64,128, |d_s,eff(t)-d| <= 0.03. Also compare direct graph-based q at t=1,2,4 for C8 and the 6x6 torus against Fourier to absolute tolerance 1e-12. Test an explicitly non-bipartite cycle C7 against Fourier, since parity is not universal.
- **S0-G2, saturation negative control:** For C32 and the 16x16 torus at t=4096,8192, the Fourier return must agree to within 1% of the **even-time** stationary limit 2/N; |d_s,eff(4096)| <= 0.02. Classify this as SATURATED, never as a positive observation of zero-dimensional space. C32 and L16 are even/bipartite by construction.
- **S0-G3, rapidly mixing null:** For complete K32, check exact q(t) = 1/32 + 31/32 * (1/31)^(2t). At t=4 and 8, return within 1% of the non-bipartite stationary 1/32 and |d_s,eff(4)| <= 0.02. It must be labelled SATURATED, not a power-law plateau.
- **S0-G4, provenance:** Deterministic reference outputs with code revision, Python/NumPy/SciPy version, configuration and float tolerances. A second invocation must give byte-identical numeric output (not runtime fields). No random seeds or stochastic confidence intervals apply to S0. All four gates and all deviations must be reported.

**Disclosure before gated numerical execution:** During design we evaluated only the infinite-lattice closed form and the (independent) Fourier-vs-infinite relative differences, not a sampled-tree outcome. The largest relative finite-torus deviation anticipated for these grids is about 0.00134 (2D, t=256), comfortably below the predeclared 0.01 tolerance. This is an analytic-model sizing check, **not blinded statistical testing**. Gates test engineering exactness, not discovery.

## 4. Resource budget and stops

S0 runs locally or in standard CI, no Lightsail deployment: 1 worker, <= 5 CPU-min, <= 512 MiB. The transition-kernel code must enforce a maximum directed-edge-times-step budget of 100,000,000 updates per request, and refuse graph inputs with isolated vertices or asymmetric adjacency. No production-sized D2 sampled trees in S0. Do not launch an unbounded random-walk simulation; do not spend resources on the shared EatSleepFeel host.

On any gate failure: preserve the numerical result, report FAIL and investigate before any S1 run. Altering a tolerance, time window or definition after observing a failure requires a versioned preregistration amendment with an explicit deviation. Gate success means only that the S0 instrument is internally and analytically calibrated for these cases.

## 5. Precommitment for S1 planning — NOT an authorised batch

**Known mathematics (literature):** Brownian continuum random tree (uniform labelled-tree scaling limit) has spectral dimension 4/3; the 2D infinite uniform spanning tree has spectral dimension 16/13 (Barlow & Masson, 2011). These are asymptotic targets with finite-volume and sample-source difficulties, not finite-N pointwise equality claims.

S1 must separately preregister a power/feasibility pilot on NON-gated random-tree seeds and sizes, using no gated output to pick a time window or source count. Examine return probability near stationarity, within-tree correlation of sampled vertices, source-degree bias, variance across independent graphs, finite-size drift, computation/memory cost and sensitivity to estimators (fit-of-mean versus mean-of-fits). If Monte Carlo walkers are used, very low return counts require a prespecified precision calculation and independent repeats; zero counts must not be converted to zero dimension. Favor exact sparse kernels with numerically bounded truncation error if cost permits. Use the 2D torus lattice as a control and a fast-mixing null. At least one different-model-family review is required before interpreting any result as beyond instrument calibration (Issue #37).

Potential outcome: S1 may be infeasible on 2 vCPUs / 4 GiB. Documenting an explicit NO-GO or reduced scope is an acceptable result. The intended project-level comparison remains one estimator against the separately calibrated D2 volume-growth estimator; their differing asymptotic dimensions are expected and are **not** an artefact by themselves.

## 6. Reproducibility and provenance

Implementation module: src/emergence_lab/spectral_dimension.py.
Tests: tests/test_spectral_dimension.py.
Future exact-result note: docs/experiments/YYYY-MM-DD-spectral-s0.md (record exact commit and environment).
Issue: https://github.com/shaden7/emergence-lab/issues/37.
Reference: M. T. Barlow & R. Masson, *Spectral dimension and random walks on the two dimensional uniform spanning tree*, Commun. Math. Phys. 305 (2011), 23–57; see D2 decision for scope.
