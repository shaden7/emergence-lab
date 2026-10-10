# N5 — preregistered measurement-noise stress for Pilot A

**Status:** FROZEN DESIGN BEFORE FIRST N5 NUMERICAL OUTPUT.
**Date:** 2026-10-10. **Base:** `main` `173397e340ae9dbfed653e318347d868054656c4` after the [scoped Pilot A decision](PILOT_A_DECISION.md).
**Parent protocol:** [Pilot A v1.0](PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md); original protocol SHA-256 `c8061aed335bda61c9f35cc72b601aac8d1287436c49c83883ea5ec36b9e4c96`.
**Scope:** optional N5 noise component only; never rerun, reinterpret or retune the deterministic holdout/A1–A7 results. No unknown-model search.

## Hypothesis and failure cases

**H2-noise (methodological hypothesis):** even where W/CA intervention response is mathematically exactly zero, finite noisy measurements can yield nonzero `S_hat` and spurious threshold fronts. Their frequency should match the *known Gaussian null distribution*, not a newly discovered propagation effect. A supposedly strict cone inferred solely from thresholded measurements is invalid unless its false-positive process is controlled. The established analytical support classes must remain unchanged.

**Potential falsifiers of the proposed implementation:** a sigma-zero result differs from the exact reference front; known-zero W/CA responses are not reported as mathematical zeros separately from noisy observations; a Gaussian pair-noise generator fails its analytic tail check; random draws are reused across supposedly independent replicates; noise changes the underlying PDE, Hamiltonian, CA, or `SUPPORT_CLASS`; a failed/censored observation is labelled a proof of no influence.

## Fixed experimental design (no parameter fitting)

Reference models **at development settings only** (unseen holdout untouched):
- W: top-hat d'Alembert, `t=1`; H: heat-kernel reference, `t=1`; Q: finite-ring *Fourier reference* with `L=128,t=1`; CA: exact radius-one update reference, `L=128,n=2`.
- Measurement sites fixed at `r=[0,1,2,4,6,8,12]`. Each model has its preassigned metric and clock. Local intervention gives reference response `S_true(r)`, null control gives 0. For W, the top-hat may have intervening zero regions even *within* the broad cone; only **theorem-known remote exterior sites** are used as false-positive nulls.
- `sigma=[0,1e-6,1e-4]`, `eta=[1e-3,1e-6,1e-9]`, `n_replicates=20`, `seed_base=2027101005`; these are fixed *before* running. One independent pseudorandom stream per **(sigma index, eta index, replicate index, model index)** via `np.random.SeedSequence([seed_base, i_sigma, i_eta, i_rep, i_model])` and NumPy's default PCG64 generator. Seeds are disjoint by construction but pseudorandom independence is a modelling assumption, not a theorem.
- Each cell observes `Y_do=S_true+epsilon_do`, `Y_control=0+epsilon_control`, with two independent draws `epsilon_*=sigma*N(0,1)`. The reported **nonnegative** influence estimator is `S_hat=abs(Y_do-Y_control)`. This is one measurement *per arm* per cell (not an ensemble-averaged statistical estimate of E[O]). Gaussian readout noise is an imposed detector model, not a new dynamical interaction. At sigma=0, `S_hat=S_true` exactly on references.
- A detection is `S_hat>=eta`; per-replicate `r_eta` is the maximum among the seven *measured* sites, else `null` (undefined). No interpolation or claim of an actual maximum causal distance. The support class stays a separate field taken from the known mathematical model.
- For controls W at `t=1` and CA at `n=2`, `r=6` is the preregistered **sentinel**: `S_true=0` by analytical support. Record sentinel false-detection counts out of 20 *independent replicates* for each sigma/eta/model. Also record per-replicate `any_false_exterior` for all theorem-exterior sites; those sites within a replicate are *not* independent trials for confidence intervals.
- H and Q far response at `r=6,t=1` are positive analytical counterexamples; their **nondetection** is only a threshold outcome, never a claim of strict support. Store every trial/site, including undetected and far-outside cells.
- For each sentinel count k/20, publish Wilson 95% interval. This is a descriptive interval over independent realisations **for that fixed condition**, not a physics-confidence interval and not a multiple-testing adjusted result. Report the distribution of per-replicate fronts (including `null`) descriptively; do not assign CIs by treating multiple sites or thresholds as independent replicates.

## Independent analytical null and predeclared gates

At a genuinely zero-response site, `Y_do-Y_control~N(0,2 sigma^2)`. Therefore for sigma>0:
`P[S_hat>=eta|S_true=0] = erfc(eta/(2 sigma))`.
For sigma=0 and eta>0 this probability is exactly zero. This expression is a mathematical consequence of the **assumed detector model**, not physical propagation. Verify it independently from Monte Carlo and retain both predicted and observed rates.

**N5-G1 (noise-free exactness):** with sigma=0, for every model, eta and one of the 20 replicates, `S_hat=S_true` at all seven sites and `r_eta` matches the deterministic reference front. The strict-support sentinels must never be detected. Failure is a STOP.

**N5-G2 (no reinterpretation):** `SUPPORT_CLASS` remains exactly W/CA strict, H/Q nonstrict for every sigma, eta, replicate. No negative noisy reading is clipped *before* the subtraction/absolute-value step; the noise is reported separately from the true response. Failure is a STOP.

**N5-G3 (analytic power extremes, each W and CA sentinel):**
- sigma=1e-6, eta=1e-3: **0 of 20 detections**, since the analytic null probability is essentially 0.
- sigma=1e-4, eta=1e-9: **at least 19 of 20 detections**, since the analytic null probability is >0.99999.
Failure indicates a generator or threshold problem, or a rare preregistered stochastic result (report it; do not rerun just to pass).

**N5-G4 (intermediate probabilistic check, each W and CA sentinel):**
- sigma=1e-6, eta=1e-6: **2 through 18 of 20 detections**; exact null probability `erfc(0.5)≈0.4795`. Failure must be reported as such, not used to select new seeds.
- In every (sigma, eta), report 20-trial Wilson intervals and the exact Gaussian null probability; do not demand that *all* nominal 95% CIs contain the analytic p across the 18 jointly reported conditions.

**N5-G5 (provenance):** no duplicate tuples of seed inputs, 20 trials for each sigma/eta/model, full CSV including negatives, JSON manifest recording parent protocol SHA, preregistration git commit, executing commit, grid, noise formula, versions, seed tuple, observed counts, null probabilities, numerical thresholds, runtime, file hashes. Two byte-identical outputs under repeated invocations in the same environment, except for manifest timestamps and runtime, if a determinism check is run. Do not claim cross-environment byte identity without reproducing it.

**N5-G6 (interpretation):** results must explicitly preserve the analytic W/CA zeros, correctly label detected noise at those zeros as false positive, and label H/Q nondetection as nondetection, not strict support. If false-positive rates differ from the analytic model, report a methodological failure, not novel physics.

**Decision rule:** N5 can pass as a *noise-accounting reference stress* if G1–G6 hold. That does **not** validate noisy signalling, maximum information propagation speed, or any cross-model physical inference. A failure remains published; no threshold, grid or seed may be changed after seeing outputs.

## Budget and record

Maximum 0.5 vCPU-equivalent CPU usage, 1.5 GiB RAM, 30 min wall; target under 60 s local CPU and <2 MiB of CSV/JSON. No AWS Lightsail deployment or background job. Run only after this design and its JSON config are committed; subsequent changes to preregistered parameters require a **new version and explicit deviation**. Exclude holdout evaluation entirely. CI pytest and a separate deterministic local smoke plus hashes are required before reporting passing results.

**Anticipated limitations:** a *single* measurement per arm creates a positively biased `|Y_do-Y_control|` at zero; 20 trials yield wide Wilson intervals; Gaussian white noise is a convenient instrument model, not a claim about realistic measurement correlations, detector thresholds or quantum measurement backaction. This is a test of reporting discipline and classification under measurement noise, not of geometry emergence.
