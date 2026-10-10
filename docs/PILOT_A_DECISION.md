# Pilot A — scoped reference-calibration decision

**Decision date:** 2026-10-10. **Later-pass Director:** `rd-gpt6-20261010T153936Z-6b85701b`.
**Audited base:** `main` `b14c43de8597457665b415faf3dc9ca33f3d31f7`, CI success [38062057844](https://github.com/shaden7/emergence-lab/actions/runs/38062057844).
**Decision: GO only for the specified deterministic *reference calibration*; NO-GO for treating threshold fronts as inferred strict causal boundaries, a model-independent signalling velocity, or evidence of emergent spacetime.** This is an evaluation of Pilot A, *not* a reversal or enlargement of the separate [Phase-0 GO](PHASE0_DECISION.md).

## Question and evidence hierarchy

Can the preregistered intervention-response witness `S_M(r,t)` numerically distinguish known strict-support examples (W, CA) from known nonstrict ones (H, Q), using the declared model-specific metrics, clocks and null controls, without mistaking a detection threshold for mathematical support? This is the bounded H1 methodology question of [Pilot A protocol v1.0](PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md).

**Mathematical facts/assumptions, not discovered results:** strict W domain of dependence from d'Alembert; CA radius-one propagation from the rule and induction; positive H heat kernel; generically nonzero Q propagation tails (with possible interference zeros). Their declared `SUPPORT_CLASS` labels are *inputs* to the software. Spatial distances, temporal units, velocities/couplings and quantum initial preparations are also inputs.

**Numerical evidence:** [development note](experiments/2026-10-10-pilot-a-references-dev.md), [one-shot holdout note](experiments/2026-10-10-pilot-a-holdout.md), immutable [holdout JSON](experiments/2026-10-10-pilot-a-holdout-result.json) and [holdout CSV](experiments/2026-10-10-pilot-a-holdout-rows.csv). Holdout execution was on code commit `c4f2793c3cb8fd4d93cd4d9ed69c9d5ae800bb11`; config SHA-256 `a55fcfa875c77d8818bd051bf57ef1c05b0239f4df59fe6d7d637ef7da3795a4`, protocol SHA-256 `c8061aed335bda61c9f35cc72b601aac8d1287436c49c83883ea5ec36b9e4c96`, rows digest `a99bdb4df582d54c850acf6cbe0102e5fff161aa3da15c6b5dc70e697460d30c`.

**This Director's actual check:** read and regroup the committed holdout `result.json` by model/status, checked the 27 archived `fronts` rows for all nine (model, L, t) groups and the monotone threshold order, examined the recorded direct A3 witnesses, compared findings with the pinned protocol, implementation and development note. **No simulation or holdout re-execution** and **no separate independent physical validation** took place in this decision session. The earlier producer ran `pytest -q` (207 passing tests), and the merge commit's [CI](https://github.com/shaden7/emergence-lab/actions/runs/38062057844) passed; this Director did not rerun that test suite.

## Gate audit (strictly bounded)

| Criterion | Verdict | Basis and caveat |
| --- | --- | --- |
| **A1** intervention, observational correlation null N1 | **PASS, reused control** | Same 4000 paired samples and seed 2027050101 in development and holdout: corr ≈ 0.497, remote Δ=0, local Δ=1. Grid-independent control, **not an independent holdout replication**. |
| **A2** strict-support controls | **PASS for known models** | Holdout: 14 W exterior cells and 16 CA exterior cells are exactly zero. W uses a Courant-1 leapfrog, CA a direct synchronous update. The actual strict-support theorems are assumed analytic benchmarks, **not inferred from numerical zeros**. |
| **A3** nonstrict positive witnesses | **PASS, with censoring** | Registered (t,r)=(1,4),(1,6) evaluated directly for H and Q; all match. Beyond the W cone: 25 non-censored H/Q cells match, 17 are censored (<1e-8) and never called zero. The fixed registered witnesses were not on the holdout grid; the nonvacuity clarification was made *before* the one-shot evaluation. |
| **A4** finite-ring Q reference | **PASS** | Q `eigh` vs Fourier: 24 matches, 12 censored; norm error ≤1.1e-15. Finite-ring Fourier is the primary reference; Bessel is a separate infinite-line comparison. |
| **A5** adversarial long-range shortcut | **PASS on development only** | N2 edge at r*=L/4 with ε=0.05 gives ≈4.4e-4 / 5.2e-4 / 3.6e-4 at t=0.5/1/2; Taylor reference agrees; unmodified ring far weight ≤2.3e-30. Shortcut is **built in**, not emergent nonlocality. |
| **A6** threshold diagnostic | **REPORTED, limited** | 27 holdout H/Q fronts for η∈{1e-3,1e-6,1e-9}; the detected radius is nondecreasing as η decreases, but depends on the *six sampled sites*. These are not strict-support results. The program does not supply a noise-robust front estimator, nor complete W/CA threshold-front tables. |
| **A7** unretuned holdout | **PASS for A1–A4** | 108 cells: 58 match, 33 analytic_zero_ok, 17 censored, 0 mismatch; maximum relative error over matched cells ≈2.1e-13. This is **deterministic numerical accuracy**, not a confidence interval. Optional N5 noise part is **unimplemented**. |

The 108 cells break down as W 18 (1 match, 17 zero), H 18 (13 match, 5 censored), CA 36 (20 match, 16 zero), Q 36 (24 match, 12 censored). The W holdout contains only **one nonzero cell**, limiting its power as a numerical positive control. H1 survived the registered grid; it is **not proved**.

## Threshold sensitivity (direct read of holdout fronts)

The stored `r_eta` is the *furthest sampled site at or above η*, **not** an interpolated location or maximum possible influence distance.

| Model/time | η=1e-3 | η=1e-6 | η=1e-9 | Caveat |
| --- | ---: | ---: | ---: | --- |
| Q, t=0.75 (L=512 and 1024) | 3 | 5 | 5 | Sparse-grid plateau does not mean a zero tail. |
| Q, t=1.5 (both sizes) | 5 | 7 | 7 | Strict support is not established. |
| Q, t=3 (both sizes) | 7 | 11 | 11 | All quantities use the *preassigned* ring distance. |
| H, t=0.75 | 3 | 5 | 7 | Positive analytic H kernel outside each measured front. |
| H, t=1.5 | 5 | 7 | 7 | Plateau is an observation-grid artifact. |
| H, t=3 | 7 | 11 | 15 | 15 is the furthest sampled site, not an endpoint of support. |

A single threshold/front fit can therefore suggest a sharp cone even in a mathematically nonstrict model. The registered N4 Euler control provides a stronger direct counterexample: at t=1,r=6 its finite-stencil numerical response is exactly zero although the continuum H reference is ≈4.8e-5. **H2's noise-dependence remains untested** (N5 optional, not run); the threshold-dependence component is observed.

## Decision, permitted use, and risks

**GO (limited):** use the fixed W/H/CA/Q reference module, manifest and classifier as regression benchmarks to check whether *another implementation* reproduces known mathematical behavior. Retain the `censored` status, the exact-grid and units metadata, and independent analytic controls. This GO is for **method calibration**, not for a new model's physical claims.

**NO-GO:** no inference of a universal maximal signal speed from `r_eta(t)`, no claim that `Q` tails imply instantaneous usable communication, no strict-causality verdict from a finite set of numerical zeros, no transfer of the Pilot A classifier's reliability to an untested family. `S_Q` is a local occupation-probability difference after a specific preparation, not a supremum over messages/measurements. Apparent model agreement is not equivalence of causal structures or ontologies.

**Carry-over constraints:**
1. **N5 optional but necessary before noisy-data use:** register a measurement protocol first; 20 independent noise realisations for each σ∈{0,1e-6,1e-4} and η∈{1e-3,1e-6,1e-9}, with a stated estimator, false-positive policy and uncertainty over independent realisations. Keep stochastic observation noise separate from dynamics; never relabel a mathematical support class based on detection.
2. **Resolution attack:** an alternative, finer site grid/window may move every `r_eta`; record observation windows and undefined fronts. Retain the finite-ring Fourier reference for Q.
3. **Fresh representation-specific controls:** any new graph, PDE, quantum or other model requires its **own** preregistration, null/positive controls, held-out evaluation and budget, following C1–C5 in [Phase-0 decision](PHASE0_DECISION.md) as applicable; this decision does not approve its implementation or Lightsail deployment.
4. **Reviewer independence:** source, implementation and reviews are AI-mediated, chiefly by the same model family. Artifact re-tabulation here is a separate reading of the data, not external peer review or an independent numerical solver.

**No new experiment, AWS run, deployment, expenditure, code change or proof** was produced by this decision. The purpose is to prevent an unjustified promotion from correct reference classification to emergent physics.

**Next single discriminating step:** preregister and implement *N5 measurement-noise stress* in a separate small code PR, including calibrated false detections in analytically zero regions, 20 independent per-(σ,η) realisations, explicit confidence intervals and fixed seed splits. Do not rerun the one-shot deterministic holdout or retune its gates. Issue [#4](https://github.com/shaden7/emergence-lab/issues/4) remains a separate geometry-estimator design workstream after its own preregistration.
