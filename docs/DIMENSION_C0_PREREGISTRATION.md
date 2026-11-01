# C0 joint dimension reporting: preregistration v0.1

Status: PROPOSED; requires review and integration before implementation or gated execution.
Date: 2026-11-01. Dependency: corrected PR #61 design.
Scope: deterministic instrument calibration only; no random trees, S2, or physics claim.

## Question and frozen estimands

Can the existing graph-based volume and return kernels feed a joint report that agrees with separate finite-graph oracles and rejects saturation?
Use unchanged dimension_d1.shell_counts / ball_sizes / verdict and spectral_dimension.graph_even_returns / local_spectral_slope. Neither oracle may substitute for a measured kernel.
Volume slope is log2(B(2r)/B(r)); spectral slope is -2 log2(q(2t)/q(t)), q(t)=P^(2t)[v,v].
No radius/time correspondence and no equality gate between the two slopes.

## Deterministic inputs

Use source vertex 0 on C1024, the 256-by-256 square nearest-neighbour torus, C8 and K32.
These graphs are vertex-transitive: source 0 equals the uniform-source mean mathematically. This does not validate uniform averaging on irregular graphs. RNG not used.
Build lattices through existing torus_lattice; construct K32 as the simple undirected complete graph.

Positive slope radii: 4,8,16; required ball radii: 4,8,16,32.
Positive spectral slope half-times: 8,16,32,64,128; required return half-times: 8,16,32,64,128,256.
Null return half-times: 8,16,32,64,128,256. Null slopes use adjacent pairs.
Null volume verdict: use existing required_radii and mean_balls to supply the full dyadic prefix through first inadmissibility. Do not feed a truncated prefix to verdict.
Positive volume rows are POINTWISE_CONTROL, not a plateau verdict. No positive whole-range PLATEAU claim is tested.

## Oracles and gates

C0-G0, structure and budget:
- Each lattice has N=L^d, all degrees 2d, N*d undirected edges, no loops or duplicate edges.
- K32 has 32 vertices, all degrees 31 and 496 edges.
- All four graphs connected, simple and undirected.
- Each graph-kernel call retains MAX_TRANSITION_OPS=100000000. Maximum positive request is 4*256^2*256 = 67108864.
- Assert requested return times include every slope's doubled time. An absent endpoint is an error, never interpolated.
- The original PR #61 endpoint t=256 was changed during static review because q(512) requires 134217728 edge-steps. No gated output informed this change.

C0-G1, ball-count implementation:
- Compare actual BFS counts at all required positive radii with integer 2r+1 (cycle) and 1+2r(r+1) (square).
- Establish 2r<L/2 for every slope, so neither oracle wraps.
- Integer count difference must be zero. Derived volume slope absolute error <=1e-12.
- Independent reference arithmetic must use these explicit formulas, not lattice_ball_exact from the production module.
- For each positive curve, report limiting d=1 or 2, exact finite-r slope, observed slope, their residual, and finite-r offset. Exact finite-r slopes below d are labelled FINITE_RADIUS_CORRECTION, never dimensional reduction.

C0-G2, return implementation:
- Compare graph q at all required times against finite-torus Fourier formula for cycles/square, and 1/32+(31/32)*(1/31)^(2t) for K32.
- Absolute q error <=1e-12 AND relative q error <=1e-9. Slope absolute error <=1e-9.
- Finite reference is primary. Infinite-lattice combinatorial q is descriptive only; output its relative difference from finite reference and its slope offset from limiting d.
- No requirement that finite-time spectral and volume slopes coincide.

C0-G3, guards and nulls:
- Stationary even floors: 2/1024, 2/65536, 2/8 and 1/32 respectively.
- Report headroom at ratios 5,10,20 for both endpoints of every spectral slope. Primary admissibility requires both endpoints pass ratio 10.
- Positive controls must pass primary headroom for all listed slopes. Ratio-20 failures, if any, remain disclosed sensitivity outcomes, not silently removed rows.
- C8 and K32 must have both endpoints within 1% of their stationary even floor at t=128,256 and |ds(128)|<=0.02.
- Both null volume verdicts must be INSUFFICIENT_RANGE under unchanged N/8 guard; d_hat must be null.
- Null spectral classification must be SATURATED. Never assign a positive zero-dimensional conclusion.
- Report earlier null times even when not yet within 1% saturation; lack of power-law headroom alone is not the same as within-1% saturation.

C0-G4, reporting and repeatability:
- JSON contains graph definitions, source, half-time convention, separate radius/time arrays, all observed/oracle values and residuals, every gate and sensitivity outcome.
- Include no interpolated cross-scale comparison, tree measurement or new physical conclusion.
- Two fresh process invocations must give byte-identical canonical numerical JSON; exclude timings and environment fields from that comparison.
- A deliberate missing doubled endpoint and wrong bipartite floor must be detected by tests. Tests must also reject oracle-only payloads as absent kernel evidence, and saturated output labelled as a positive dimension.
- Record both invocation hashes, not only the successful one.

## Resource enforcement and outcomes

One worker with BLAS/OpenMP thread counts set to 1 before imports. Total envelope for both gated invocations: 300 CPU seconds, 600 wall seconds, 512 MiB peak memory per process, 5 MiB combined output. No Lightsail or paid API.
Run invocations sequentially under a supervisor with an absolute wall deadline. Use process CPU hard limits allocated from the remaining aggregate budget; include child CPU use. Set Linux address-space hard limit to 512 MiB before imports, conservatively stronger than a resident-memory cap. If imports or allocations fail under it, report INCOMPLETE; do not increase the limit. Cap output using RLIMIT_FSIZE plus supervisor aggregate-size checks.
Supervisor must persist partial output, exit code/signal, elapsed time and budget status on timeout, allocation failure, or signal. Test supervisor failure handling on tiny artificial limits before gated work.

Outcome precedence: FAIL if an observed scientific/engineering gate fails; otherwise INCOMPLETE if any required output, repetition, provenance or resource observation is absent or a limit stops execution; PASS only if every gate and both repetitions complete within the envelope. Record failures even if another part is incomplete. No automatic rerun after a failure. Any changed threshold/grid requires a versioned amendment with prior outcome retained.

## Provenance and interpretation

Before execution record exact implementation commit, this preregistration SHA-256, machine-readable config SHA-256, source blob hashes, Python/NumPy/SciPy versions, platform and thread configuration. Record actual CPU/wall/peak-memory/output-byte observations and SHA-256 for all outputs, including failed runs.
Store result and manifest using repository archive conventions; a result note must link retrievable bytes. Do not claim execution from configuration or CI alone.
Static design and known-oracle sizing are not blinded hypothesis tests. C0 PASS calibrates only these deterministic controls and report semantics. Historical D2 is design context, not new evidence. Random-tree spectral size stability and Issue #37 remain unresolved.

## Review record (2026-11-01)

PASS for preregistration, conditional on integration before implementation. Continuing agent review is nonindependent, not an external later-pass scientific review. Checked endpoint closure, vertex-transitive source equivalence, no-wrap domain, separate estimands, full-prefix null verdict inputs and outcome precedence against the existing kernels. A setup-only import check succeeded with 512 MiB RLIMIT_AS and one BLAS thread (NumPy 2.3.5, SciPy 1.17.0); this does not establish whole-run feasibility. Original candidate CI 41349498129 completed-success. No gated C0 output has been computed. Implementation must test supervisor failure paths and record its exact commit before execution.
