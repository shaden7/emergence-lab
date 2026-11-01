# Issue #37 — distinct-estimator comparison design (C0, v0.1)

**Status: PROPOSED DESIGN ONLY.** This is the design-selection step requested by the [adopted scope decision](S1_SPECTRAL_NEXT_DECISION.md), not a preregistration or run authorization. Date: 2026-11-01. No new samples, seeds, simulations, timings or physical claims.

## Question and decision

Which additional measurement most economically tests whether an apparent dimension change depends on the measuring procedure?

**Select the existing D2 volume-growth instrument as the substantively distinct family for a future joint diagnostic; do not implement another ball-growth estimator.** D2 is already calibrated within its recorded scope. The missing work is a controlled comparison protocol, not its reinvention. First propose a deterministic C0 comparison-calibration step on exact controls. A separate reviewed preregistration must freeze its gates before implementation/execution. This does not reopen the terminal S1/S1b size-equivalence line, authorize S2 or certify the unresolved spectral instrument on random trees.

| Candidate | What it measures | Independence and decision |
| --- | --- | --- |
| Quenched mean of per-tree spectral slopes | Log-return scaling conditional on a graph, then averaged | Useful internal aggregation check; shares return data/kernel and is not a second estimator family. Do not select as cross-family evidence. |
| Independently computed heat-kernel trace | Spectral return observable, with explicitly specified operator and vertex weighting | Can catch kernel implementation defects but remains spectral. Do not label algorithmic agreement cross-observable corroboration. |
| Frozen D2 ball-growth instrument | Volume growth in intrinsic graph distance | Distinct observable/algorithm; already available. Select for joint diagnostic design, carrying all D2 restrictions. |
| Walk displacement or exit-time exponent | Transport scaling, often expressed as walk dimension | Potential additional discriminator, but requires a new instrument and calibration. Defer; it is not a cheap replacement for spectral dimension. |

These methods are not statistically independent merely because they use different algorithms: paired graph measurements share graph-to-graph variation.

## Definitions and comparison contract

Retain the frozen definitions:
- Volume: Bbar(r) is the mean closed-ball cardinality over uniformly selected sources; dV(r) = log2[Bbar(2r)/Bbar(r)]. D1/D2 plateau selection and the N/8 guard remain unchanged.
- Spectral: q(t) is the uniformly averaged return probability after **2t physical steps**; ds(t) = -2 log2[q(2t)/q(t)]. No degree-weighted source substitution. Retain the appropriate bipartite stationary floor and existing headroom rules.

**Do not test dV = ds on arbitrary graphs.** The two observables have different model-specific limits. The UST literature provides a decisive counterexample: volume exponent 8/5 and spectral dimension 16/13. The project's CAY/CRT reference is volume 2 versus spectral 4/3, subject to its stated limiting assumptions. These are asymptotic references, not finite-size tolerances. A difference between them is not an estimator defect.

Report a pair of control-relative curves, not one "dimension discrepancy" score. Each component is compared to its own finite-graph analytical reference where available. Joint agreement means both instruments satisfy their own controls; it does not mean their raw numbers coincide.

Do not set r = sqrt(t) on random trees. A relation such as ds = 2*dV/dw requires appropriate scaling assumptions and a separately justified walk exponent dw; it is not a universal finite-scale identity. Until a scale map is preregistered and justified, show radius and half-time on separate axes and describe only within-observable scale dependence. An apparent reduction in one curve cannot be paired with an arbitrary point on the other.

## C0: smallest next calibration proposal

**Target:** demonstrate that a joint reporting/interpretation procedure distinguishes exact finite-scale corrections and saturation from failures of an instrument. No random graphs or new model comparison in C0.

Suggested preregistration grid (design inputs, not frozen authorization):
- Positive controls: cycle C1024 and a 256-by-256 square torus; graph-distance radii r = 4, 8, 16 and spectral half-times t = 8, 16, 32, 64, 128, 256.
- Volume oracle before wrapping: |B(r)| = 2r+1 on the cycle and 1+2r(r+1) on the square torus when the full ball does not wrap. For every dV(r), verify that this includes **2r**, not only r.
- Spectral oracle: S0's finite-torus Fourier formula and infinite-lattice combinatorial reference. Compare to the finite reference for implementation accuracy; any asymptotic comparison must separately quantify finite-time error.
- Saturation controls: C8 and K32, using S0's correct stationary floors. For volume, require the existing guard/range classification; never convert a saturated zero slope into a positive zero-dimensional verdict.
- Small-radius adversary: the exact cycle/torus volume curves themselves lie below their limiting exponents at small r. The report must identify the known finite-r correction and must not label it evidence of new dimensional reduction.
- Tree-family reference: carry the reviewed D2 CAY/UST records as **historical calibration evidence**, including CAY's exact finite-N mean curve in D2 prereg §4. No old output becomes a fresh confirmation. No new tree run is included in C0.

The next preregistration should set exact-arithmetic tolerances for ball counts, floating-point tolerances for q and slopes (using existing S0 checks as a starting point), admissibility/headroom checks and an explicit outcome table. It must separate pointwise local curves from D1's whole-range plateau verdict: three listed radii do not alone authorize a PLATEAU claim.

**Falsifiers:** disagreement with an exact finite-graph oracle; incorrect parity/stationary floor; declaring saturation a valid positive dimension; classifying a known finite-r control correction as new physics; requiring raw spectral/volume equality on trees; or implying an unjustified radius-to-time map. A failure blocks the comparison pipeline, not the established reference mathematics.

**Proposed ceiling:** one worker, 5 CPU-min, 512 MiB peak memory, 10 min wall time, 5 MiB output. No Lightsail, Docker deployment, paid API or remote experiment. The prereg must specify enforceable CPU/memory/wall stops before execution; a projected fit is not a timing observation. If exact graph-kernel checks exceed the cap, stop and report incomplete; do not silently replace the test with reference-versus-reference agreement or increase limits.

**Provenance:** deterministic inputs, so no RNG or seed manifest is needed for C0; record explicit "RNG not used". Save graph definitions, exact executing commit, config and prereg hashes, package versions, all control outputs/failures, CPU/wall/memory observations and file hashes. Preserve evidence under the repository's existing archive conventions.

## What remains blocked after C0

Even a C0 PASS would establish only the joint pipeline's exact-control behavior. It would not extend D2 to smaller random graphs, remove its source-count/power requirements, solve spectral CAY size stability, calibrate arbitrary cyclic graphs or answer the robust/artifact question in Issue #37.

A later stochastic comparison needs a separate power/feasibility preregistration: independent graph replicates and new seed inventory; D2's at-least-times-three design-effect sensitivity and sampling argument; paired graph-level covariance (sources are not independent replicates); separate finite-size/window tests for each observable; a justified scale map if cross-observable scale claims are attempted; matched positive/null controls; and a fixed budget. Existing D2 and S1b outputs can inform design only, with that reuse disclosed.

If a calibrated spectral leg remains unaffordable, retain **unresolved** for it and choose another discriminating model/observable question. Do not reinterpret different dimension definitions as an "artifact" finding. Any substantive conclusion still requires Issue #37's different-model-family review and its requested expert scrutiny.

## Sources and evidence level

- [D2 adopted decision](DIMENSION_D2_DECISION.md), especially conditions 1–7: existing calibration scope, bias, source-count fragility and small-r caution.
- [D2 preregistration](DIMENSION_D2_PREREGISTRATION.md) §4: exact finite-N CAY mean and reference distinctions.
- [S0 spectral protocol](SPECTRAL_S0_PREREGISTRATION.md) §§2–5: half-time convention, exact controls, parity and saturation.
- Barlow & Masson, *Spectral dimension and random walks on the two dimensional uniform spanning tree*: https://arxiv.org/abs/0912.4765 ; author-hosted revised text https://personal.math.ubc.ca/~barlow/preprints/ust2S.pdf .
- Barlow, Croydon & Kumagai, *Subsequential scaling limits of simple random walk on the two-dimensional uniform spanning tree*: https://arxiv.org/abs/1407.5162 .

External theorems, previously reviewed numerical observations, proposed tolerances/budgets and methodological judgment remain separate. This document supplies a design choice and failure cases; it reports no new numerical result or theorem.
