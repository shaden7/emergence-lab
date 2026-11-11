# Research plan

**Current guiding question (Issue #37; milestone 2027-03-31):** Is reported short-scale "dimensional reduction" robust across substantively different model classes and independently calibrated observables, or is it estimator/model/finite-size dependent?

The motivating literature reports several scale-dependent dimensions, but comparability and universality are **open questions**. A negative or resource-limited result is acceptable. We do not infer that spacetime is a graph or discrete substrate.

## Completed calibration and its limits

- Phase 0: reviewed **scoped GO** as statistical-method calibration using the known 2D Ising model. This does not validate any fundamental-physics claim (docs/PHASE0_DECISION.md).
- D1 / D2: volume-growth estimator calibrated for two random-tree families (CAY and 2D torus UST) and null controls. D2 gates G0–G4 pass, with finite-size biases, non-self-averaging source effects and scale fragility (docs/DIMENSION_D2_DECISION.md). **This does not calibrate spectral dimension.**
- Pilot A/B: instrument checks for operational causal propagation with prescribed model locality; not emergent Lorentz invariance or spacetime.

## Ordered experimental programme

1. **Completed:** D2 volume-growth estimator validation and reviewed decision; Issue #4 closed.
2. **Completed within exact-control scope:** S0 spectral return-probability calibration and C0-v2 joint D2/spectral reporting on deterministic cycles, square tori and saturation nulls. C0-v2 passed its frozen gates on 2026-11-04 (docs/experiments/2026-11-04-c0-v2.md); this does **not** certify spectral size stability on random trees or a cross-model dimension claim. The first C0-v1 run remains INCOMPLETE for provenance.
3. **Completed with unresolved limitations:** S1/S1b tree-family spectral feasibility and SE audit have frozen, qualified outcomes (see docs/RESEARCH_STATE.md and docs/S1_SPECTRAL_NEXT_DECISION.md). The size-stability/equivalence line is not certified; do not silently reopen it or promote literature asymptotics (CAY 4/3, UST 16/13) to finite-size acceptance tolerances. A resource-limited outcome is legitimate.
4. **Current finite-occupancy control line:** D2-M0 (no mandatory endpoints, R>0 conditioning) and D2-E0 v1 (mandatory ordered endpoints) both completed as deterministic D=2 MM instrument controls. At the same total N, endpoint E[d]<2 throughout N=2..32 whereas no-endpoint conditional E[d]>2 at N=4..32; see docs/experiments/2026-11-11-d2-e0-run.md. This is an ensemble-dependent estimator-artifact example, not a cross-model or physical result. **Next, design only:** the smallest fixed-input D=3 reference separating endpoint and finite-occupancy MM effects under a preregistered feasible budget, with the D=2 exact curve as a positive control. The broader paired volume/spectral comparison remains subject to docs/DIMENSION_COMPARISON_DESIGN.md: graph-level independent replicates, paired covariance, D2 design-effect sensitivity, per-observable finite-size/window controls, matched nulls and enforceable compute ceilings. Unresolved random-tree size stability cannot be assumed, dimensions cannot be equated on trees, and r=√t needs a justified scale map. If no affordable valid comparison exists, record UNDECIDABLE under resources.
5. **By 2027-03-31:** write a documented robust / artefact / undecidable decision with uncertainties, failure modes and explicit remaining hypotheses; if not supportable, revise scope or the question. Obtain a different model-family review before claims exceeding instrument calibration and seek an expert review for major results.

For each batch freeze hypotheses, controls, observable, falsification thresholds, seeds, analysis, memory/CPU/time budget and archival process **before** drawing gated data. Report exact code revision, held-out measurements, null results, fit-window sensitivity and finite-size trends. Only robust internal mathematical phenomena may motivate later analytic or Lean formalisation, with empirical correspondence requiring additional evidence.
