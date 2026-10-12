# Research plan

**Current guiding question (Issue #37; milestone 2027-03-31):** Is reported short-scale "dimensional reduction" robust across substantively different model classes and independently calibrated observables, or is it estimator/model/finite-size dependent?

The motivating literature reports several scale-dependent dimensions, but comparability and universality are **open questions**. A negative or resource-limited result is acceptable. We do not infer that spacetime is a graph or discrete substrate.

## Completed calibration and its limits

- Phase 0: reviewed **scoped GO** as statistical-method calibration using the known 2D Ising model. This does not validate any fundamental-physics claim (docs/PHASE0_DECISION.md).
- D1 / D2: volume-growth estimator calibrated for two random-tree families (CAY and 2D torus UST) and null controls. D2 gates G0–G4 pass, with finite-size biases, non-self-averaging source effects and scale fragility (docs/DIMENSION_D2_DECISION.md). **This does not calibrate spectral dimension.**
- Pilot A/B: instrument checks for operational causal propagation with prescribed model locality; not emergent Lorentz invariance or spacetime.

## Ordered experimental programme

1. **Completed:** D2 volume-growth estimator validation and reviewed decision; Issue #4 closed.
2. **Next:** S0 spectral-dimension return-probability estimator, defined on even-step random walks, with analytic 1D/2D lattice controls, finite-size saturation and fast-mixing nulls. Freeze design first (docs/SPECTRAL_S0_PREREGISTRATION.md). Validate independent exact kernels before interpreting any slopes.
3. **Then:** S1 preregistered tree-family feasibility and calibration; CAY spectral dimension 4/3 and 2D UST 16/13 are literature targets only in the appropriate asymptotic sense. Derive computational cost and statistical power on disjoint non-gated seeds before deciding S, time ranges and sizes. A no-go under 2-vCPU/4-GiB constraints is a valid outcome.
4. **Only with two calibrated estimators:** compare scale dependence across at least two genuinely different families, including a null. Candidate later families: finite causal sets and dynamical triangulations, *after* verifying that their operational return probabilities and dimension definitions are comparable and studying their known analytical literature. Avoid conflating intrinsic distance and prescribed embeddings.
5. **By 2027-03-31:** write a documented robust / artefact / undecidable decision with uncertainties, failure modes and explicit remaining hypotheses; if not supportable, revise scope or the question. Obtain a different model-family review before claims exceeding instrument calibration and seek an expert review for major results.

For each batch freeze hypotheses, controls, observable, falsification thresholds, seeds, analysis, memory/CPU/time budget and archival process **before** drawing gated data. Report exact code revision, held-out measurements, null results, fit-window sensitivity and finite-size trends. Only robust internal mathematical phenomena may motivate later analytic or Lean formalisation, with empirical correspondence requiring additional evidence.
