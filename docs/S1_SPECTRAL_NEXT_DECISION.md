# Issue #37 spectral-leg scope decision — 2026-11-01 (proposal v0.1)

**Status: PROPOSED, pending later-pass review and merge.** This note does not authorize seeds, runs or deployments.

## Decision

**Choose A as the terminal outcome for the existing annealed random-walk spectral-estimator size-equivalence line. Decline B at the present budget. Explore C only as a separately preregistered, methodologically different estimator, not as an automatic continuation of S1b.**

This is a scope and resource-allocation decision, not a claim that dimensional reduction has been demonstrated or refuted. Issue #37 remains open through the 2027-03-31 milestone. The final robust/artifact/undecidable classification has **not** been reached.

## Evidence and rationale

1. **Frozen numerical observations:** S1 NO-GO; S1b C-INCONCLUSIVE and U-EQUIVALENT; the SE audit at CAY N=2^14 is SE-NOT-REJECTED (R=0.7017 versus the preregistered 1.313 threshold). This audit does not certify N=2^16 or 2^18. See `docs/S1_METHOD_SCOPE_DECISION.md` and `docs/RESEARCH_STATE.md`.
2. **Observed scale-dependent precision:** the 24-tree S1b pooled CAY slope SDs at N=2^16 and 2^18 are 0.0986 and 0.0910, exceeding the audit upper sensitivity factor 0.08696. This does not prove SE misspecification; it makes naive precision transfer optimistic.
3. **Option B projected cost, not measured runtime:** 192 trees at each large size cost about 221 CPU-min on the faster runner, 373 CPU-min on the slower one, before substantial safety headroom. The slower estimate exceeds one six-hour hosted job. Estimated symmetric ±0.03 equivalence power is about 0.82–0.92 if true D=0 but only about 0.30 at |D|=0.02, conditional on the variance model. See `docs/experiments/2026-10-31-option-b-feasibility.md` and its reproducible script.
4. **Information gain:** even a non-equivalent B result alone would not distinguish a model-intrinsic scale effect from estimator sensitivity. A separately calibrated second estimator addresses Issue #37's central discriminator more directly. Avoid adding multi-job orchestration merely to repeat the current observable.

## Next step: C, design only

Produce **one reviewed preregistration proposal** for a quenched (per-tree) spectral slope or an independently implemented heat-kernel trace, not both at once. Before any exploratory samples or seed draw, freeze:

- Formula, random-walk time windows, fitting protocol, and the distinction between quenched and annealed expectation.
- At least one exactly/analytically controlled lattice or finite graph, a misleading finite-size/null control, and a tree family with a literature asymptote. Predeclare finite-size ranges where reference limits are *not* applicable.
- Failure modes: window-selection bias, graph-size effects, fit dependence and tree-to-tree correlation; nominal or calibrated uncertainty and seed independence.
- A small fixed CPU/memory/time budget; stop rules; deterministic seed manifest and archive location.
- A discriminator: whether the new estimator is calibrated under the controls, and whether it agrees with annealed measurements at matched sizes/windows within predeclared uncertainty. Agreement alone does not establish universality or a physical claim.

**Gate:** no simulation until preregistration passes later-pass review. If a distinct estimator cannot be calibrated affordably, record the spectral leg as unresolved and redirect Issue #37 to other model/estimator comparisons. Do not reinterpret S1/S1b results post hoc as confirmatory.

## Evidence classification

- **Established mathematics (external):** asymptotic spectral-dimension values for specified random-tree families, conditional on their respective mathematical assumptions; not finite-size reference tolerances.
- **Numerical observation (archived):** S1b contrasts and SDs; the SE audit R at N=2^14.
- **Projection/assumption:** option-B throughput transfer, CPU expenditure and nominal power.
- **Judgment:** favor an independent estimator design over repeating the annealed estimator at large N.
- **Not established:** short-scale dimensional reduction, cross-model robustness, artifact causation, new physics, or empirical applicability to spacetime.

No code, tests, runtime measurements, new seeds, or infrastructure changes are part of this documentation-only proposal.
