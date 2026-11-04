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
4. **Current next step — design only:** evaluate whether an affordable, genuinely discriminating paired D2/spectral comparison can be preregistered without relying on the unresolved random-tree spectral size-stability claim (docs/DIMENSION_COMPARISON_DESIGN.md). Require graph-level independent replicates, paired covariance, D2's ≥3× design-effect sensitivity, per-observable finite-size and window controls, matched nulls and an explicit CPU/memory ceiling. Do not equate volume and spectral dimensions on trees or impose r=√t without an independently justified scale map. If no affordable valid comparison exists, document UNDECIDABLE under resources rather than running a weak experiment. Later candidate families include finite causal sets and dynamical triangulations, only after reviewing operational definitions and relevant literature.
5. **By 2027-03-31:** write a documented robust / artefact / undecidable decision with uncertainties, failure modes and explicit remaining hypotheses; if not supportable, revise scope or the question. Obtain a different model-family review before claims exceeding instrument calibration and seek an expert review for major results.

For each batch freeze hypotheses, controls, observable, falsification thresholds, seeds, analysis, memory/CPU/time budget and archival process **before** drawing gated data. Report exact code revision, held-out measurements, null results, fit-window sensitivity and finite-size trends. Only robust internal mathematical phenomena may motivate later analytic or Lean formalisation, with empirical correspondence requiring additional evidence.
