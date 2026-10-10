# Pilot B — blinded black-box interventional bound test (preregistration v1.0)

**Status:** PROPOSED DESIGN, frozen for review before any Pilot B code or numerical output exists. Not yet binding until merged to `main` after a later-pass review; any change after merge requires v1.1 with an explicit deviation note.
**Pre-merge revision r1 (later-pass review, `rd-claude-20261010T175613Z-1698f5`):** B-G3 restated as a counted tolerance (the original all-or-nothing form failed with probability ≈ 0.20 under perfect calibration); blind/dev key byte encodings pinned; S2 reference path clarified; power-test composition stated in §10. No numerical Pilot B output existed before or during this revision.
**Date:** 2026-10-10. **Author session:** `rd-claude-20261010T165622Z-55e236`. **Base:** `main` `8d6adac`.
**Parents:** [Pilot A v1.0](PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md) (SHA-256 `c8061aed…`), [Pilot A scoped decision](PILOT_A_DECISION.md), [N5 noise stress](PILOT_A_N5_NOISE_PREREGISTRATION.md) and its [result note](experiments/2026-10-10-pilot-a-n5.md).
**Scope:** methodology only. Every model below is a stipulated textbook-type linear dynamics on a ring whose support class is known to the evaluator. **Nothing here is a claim about physical spacetime, signalling or causality in nature.**

## 1. Why this step

Pilot A showed that a deterministic intervention-response witness classifies known models when the analyst already knows the model, its clock and its metric. N5 showed that thresholding single noisy readouts produces spurious "fronts" at mathematically zero sites at the analytic Gaussian rate (W 9/20, CA 8/20 at σ=η=1e-6). Before the witness is pointed at any exploratory model, it must be tested in the situation that matters later: **the analyst does not know the model class, has a finite noisy measurement budget, and must fix its decision rule before seeing the instances.**

A second, mathematical point shapes the design. **No finite set of measurements can establish strict support**, and no finite set of detections can establish non-strict support either: any finite detection pattern is consistent with *some* strict cone of large enough speed. What finite data *can* do is reject a **declared composite null** such as "strict support with speed at most v_max". Pilot B therefore tests a bounded-speed null, not "strictness" itself.

## 2. Question and hypotheses

**Question:** with a frozen, noise-aware decision rule and a fixed budget, does a black-box intervention test (a) keep the family-wise rate of false "bound violated" verdicts at or below its nominal level on instances that satisfy the bound, (b) never overestimate the speed of a strict instance beyond its true stencil radius except at the controlled error rate, and (c) detect bound violations whenever their analytic size is well above the preregistered detection limit?

- **H-B1 (soundness, methodological hypothesis):** on instances whose true dynamics satisfies H0(v_max), the verdict `H0_REJECTED` occurs with per-instance probability ≤ α = 0.05.
- **H-B2 (speed soundness):** on strict instances, the reported front `r̂(t)` exceeds the true radius bound `k·t` with per-instance probability ≤ α.
- **H-B3 (power):** on non-strict instances whose largest analytic exterior response is at least twice the detection limit, `H0_REJECTED` is returned in ≥ 90 % of instances.
- **Expected and intended negative lesson (not a hypothesis to "pass"):** some genuinely non-strict instances will return `CONSISTENT_WITH_H0`. That outcome must be reported as *undetected*, never as strict support.

**Falsifiers of the method:** too many false rejections (B1), speed overestimates (B2), missed large violations (B3), any verdict asserting proven strictness, or any decision-rule change after the beacon value is known.

## 3. Instance family (ground truth known only to the evaluator)

All instances live on a ring of `L = 256` sites with ring distance `r`. State `x_t ∈ ℝ^L`. **Intervention:** the `do` arm starts from `x_0 = e_0` (unit amplitude at site 0); the `control` arm starts from `x_0 = 0`. Because every family member is linear, the true response is `S(r,t) = x_t^{do}(r) − x_t^{control}(r) = (G_t e_0)(r)` for the instance's propagator `G_t`. Clock: one unit of `t` is one update step for discrete-time members and one unit of the generator time for continuous-time members. **The common clock, metric and site indexing are inputs given to the analyst**; they are not inferred.

| Class | Code | Dynamics (ground truth) | Parameters drawn by the blinded key | Count |
| --- | --- | --- | --- | ---: |
| strict | S1 | `x_{t+1} = A x_t`, circulant, radius `k`, positive weights summing to 1 | `k ∈ {1,2,3,4}` uniform; weights ∝ Uniform(0.1,1) on offsets `−k…k` | 6 |
| strict | S2 | second-order leapfrog `u_{t+1} = 2u_t − u_{t−1} + c²Δu_t`, `u_{−1}=u_0` (radius 1 per step) | `c² ∈ [0.25, 1]` uniform | 4 |
| strict | S3 | as S1 but signed weights, normalised so `Σ|a_j| = 1` (interference zeros possible inside the cone) | `k ∈ {1,2,3,4}`; signs fair coin; magnitudes Uniform(0.1,1) | 6 |
| null | C1 | identity, `A = I` (response only at `r=0`) | none | 4 |
| null | C2 | do arm identical to control (no intervention effect anywhere) | instance dynamics drawn as S1 | 4 |
| non-strict | N1 | continuous-time heat `G_t = exp(tγΔ)` | `γ ∈ [0.2, 1]` log-uniform | 5 |
| non-strict | N2 | discrete-time power-law stencil, weights ∝ `(1+|j|)^{−α}` on offsets `j = −127…128`, normalised to 1 | `α ∈ [2, 4]` uniform | 5 |
| non-strict | N3 | `A = B + ε(E_{0d} + E_{d0} − E_{00} − E_{dd})`: a **symmetric** S1-type stencil `B` (`w_j = w_{−j}`) of radius `k`, plus one symmetric shortcut of weight `ε` between the intervention site 0 and site `d`; rows still sum to 1 and all entries stay ≥ 0 because `B`'s diagonal ≥ 0.02 > ε | `k ∈ {1,2}`; `ε ∈ [1e-6, 1e-2]` log-uniform; `d ∈ {20,…,100}` uniform | 6 |

Total 40 instances: 16 strict (k ≤ 4), 8 null, 16 non-strict. All strict and null instances satisfy H0(v_max = 4); all non-strict instances violate it mathematically (N1 and N2 have strictly positive kernels at every ring distance; N3 couples sites `d > 4t` for `t ≥ 1` — whether that coupling reaches a *measured* site is part of the test). The instance order is a uniform random permutation drawn from the key. **Counts per class are fixed by this document; the analyst sees only instance indices 0…39.**

## 4. Black-box access and budget (identical for every instance)

- Query grid: `t ∈ {1, 2, 4}`; `r ∈ {0,1,2,3,4,6,8,12,16,24,32}` → 33 cells, measured on the `+r` side only.
- Per cell, `n = 50` independent readouts per arm: `Y = x_t(r) + σ·ε`, `ε ~ N(0,1)` i.i.d., `σ = 1e-4` (declared to the analyst; Gaussian white noise is an imposed detector model, as in N5).
- Budget: 33 × 2 × 50 = 3,300 readouts per instance, 132,000 in total. No adaptive querying; no other access (no matrix entries, no class label, no parameter).
- Estimator per cell: `D = mean(Y_do) − mean(Y_control)`, with `D ~ N(S, 2σ²/n)` exactly under the detector model, so `SE = σ·√(2/n) = 2.0e-5`.

## 5. Frozen decision rule (the analyst's only output)

- **H0(v_max = 4):** `S(r,t) = 0` for all `r > 4t`. Exterior cells on the grid: `t=1`: r ∈ {6,8,12,16,24,32}; `t=2`: r ∈ {12,16,24,32}; `t=4`: r ∈ {24,32} → **m = 12** tests.
- Exterior test: two-sided, Bonferroni, `|D| / SE > z₁ = Φ⁻¹(1 − 0.05/(2·12)) = 2.8653` (detection limit `|S| ≈ 5.73e-5`). Any exterior detection → `H0_REJECTED`.
- Front: separately, two-sided Bonferroni over all **33** cells, `z₂ = Φ⁻¹(1 − 0.05/(2·33)) = 3.1718`. `r̂(t)` = largest grid `r` detected at time `t`, else `null`.
- Verdict vocabulary, exhaustive: `NO_RESPONSE` (no cell detected under z₂ and no exterior detection), `CONSISTENT_WITH_H0` (some detection, none exterior), `H0_REJECTED`. **There is no verdict "strict" or "proved".** `CONSISTENT_WITH_H0` means only "no violation of the declared bound was detected with this budget".
- Under the detector model, Bonferroni guarantees family-wise error ≤ 0.05 for each instance satisfying H0, with no further assumption. This is an exact property of the stipulated noise, not of any physical detector.

## 6. Blinding (commit, then reveal with external randomness)

1. Stage-1 implementation (separate PR) contains: the generator `instances(key)`, the noisy oracle, the frozen analyst module that receives **only** the oracle, and the evaluator. The analyst module must not import the generator; a test enforces this.
2. **Development set:** 40 instances from the fixed public key `"pilot-b-dev-2027101101"`, used as `key = SHA-256(b"pilot-b-dev-2027101101")`. Labels visible. It may be used **only** to verify correctness (gates below with the frozen numbers). No threshold, grid, budget or rule may change in response; a failure stops the pilot and requires v1.1 with a deviation note **before** any blind key exists.
3. **Blind key:** `key = SHA-256(b"pilot-b-v1|" + ascii_decimal(R) + b"|" + bytes.fromhex(randomness_R))` (32-byte digest; `randomness_R` is the 64-hex-character `randomness` field of the beacon), where `randomness_R` is the published value of drand *quicknet* round `R`, and `R` is the first round whose timestamp is ≥ 24 h after the **merge commit** of the stage-1 implementation on `main`. The quicknet chain hash and round arithmetic must be recorded and verified in stage 1 before merge; if they cannot be verified, the pilot is BLOCKED (no substitute seed).
4. The blind evaluation runs exactly once, on `main`, in GitHub Actions (the sandbox proxy blocks drand). It logs `R`, `randomness_R`, its source URL and signature-verification status, the key, the code commit, and the hashes of all outputs. If the beacon fetch fails, the run fails closed and may be retried only on the **same** `R`.
5. **Limits of this blinding (stated, not hidden):** the analyst and the generator are written by the same AI model family, which therefore knows the family-level design (classes, ranges, counts). Blinding prevents tuning to the *specific drawn instances*, not to the family. It is not an independent test by an outside party.

## 7. Seeds and randomness

- Instance parameters: `np.random.default_rng(SeedSequence([int.from_bytes(key[:16], 'big'), 1]))`.
- Oracle noise per instance `i`, cell `c`, arm `a`: `SeedSequence([key_int, 2, i, c, a])`, PCG64. One stream per (instance, cell, arm); no reuse. Pseudorandom independence is a modelling assumption.

## 8. Gates (fixed before any output)

Let P = the 24 instances satisfying H0 (S1–S3, C1, C2), K = the 16 strict instances, and N = the 16 non-strict instances.

- **B-G0 (exact references):** for every instance, the evaluator's `S(r,t)` is cross-checked by two paths to |Δ| ≤ 1e-12: matrix power (or `scipy.linalg.expm` for N1) versus the explicit circulant Fourier sum for every translation-invariant member (S1, S2, S3, C1, C2, N1, N2; for the second-order S2 the "matrix power" path is the 2L×2L companion matrix of the leapfrog recursion), and versus `eigh` of the symmetric matrix for N3, which is not translation invariant. Every exterior cell of every P instance is exactly `0.0` in the matrix-power path. In addition, the noise-free oracle (σ = 0, run as a unit test only) returns `S` exactly. Failure → STOP.
- **B-G1 (soundness):** `#{P instances with H0_REJECTED} ≤ 3` of 24. Expected ≈ 1.2 at the Bonferroni bound; P(X ≥ 4 | n=24, p=0.05) = 0.030.
- **B-G2 (speed soundness):** `#{K instances with r̂(t) > k·t for some t} ≤ 3` of 16 (P(X ≥ 4 | 16, 0.05) = 0.007; the per-instance rate is ≤ 0.05 by the 33-cell Bonferroni).
- **B-G3 (null controls):** (a) every C1 instance detects `r = 0` at all three `t` (true `S = 1`, i.e. 5×10⁴ SE; a miss indicates a bug); (b) call a C instance *spurious* if it has any detection outside its true support (C2: any cell under z₂ or any exterior cell under z₁; C1: any `r > 0` cell under z₂ or any exterior cell under z₁). Require `#{spurious C instances} ≤ 2` of 8. Under perfect calibration the per-instance spurious probability is ≤ 0.079 (C2; C1 0.075), so P(X ≥ 3 | 8, 0.079) = 0.020. Every spurious instance is reported individually with its cells and z values. *(r1: the v1.0 draft required all eight C instances to be clean except for B-G1 exterior rejections; interior false detections at the nominal z₂ rate made that gate fail with probability 0.201 analytically, 0.202 in a 2×10⁵-replicate Monte Carlo, for a perfectly calibrated method.)*
- **B-G4 (power):** define *detectable* N instances post-unblinding from the **analytic** `S` only: `max over the 12 exterior cells of |S| ≥ 2 × 5.73e-5`. Require `H0_REJECTED` in ≥ 90 % of detectable N instances (vacuous pass flagged if fewer than 3 are detectable, and then reported as "power untested"). Expected per-instance power at the boundary ≈ 0.998.
- **B-G5 (honest vocabulary):** no output, note or summary uses "strict", "proved", "causal cone" or "speed of light" as a verdict for any instance. Every undetected N instance is listed with its analytic maximal exterior `|S|` next to the detection limit.
- **B-G6 (provenance):** manifest with this document's Git blob SHA, the config SHA-256, the stage-1 code commit, beacon round/value/verification, key, NumPy/Python versions, per-instance rows (all 33 cells, D, SE, z, detections, verdict, and post-unblinding class/parameters/analytic S), CPU time and output SHA-256. Development outputs byte-identical on two invocations in the same environment.

**Decision rule:** pass all of B-G0…B-G6 → GO only for using this frozen bounded-speed test as a *noise-aware calibration instrument* on further stipulated models. Any failure is published as a failure; no rerun on a new key, no grid or threshold changes after unblinding. Non-detection rates for N instances are reported descriptively with Wilson 95 % intervals and are *not* a pass criterion beyond B-G4.

## 9. Budget, resources, out of scope

- CPU ≤ 2 min, RAM ≤ 512 MiB, outputs ≤ 5 MiB, both dev and blind. Ring propagators by matrix power/`expm` on 256 × 256. GitHub Actions and local sandbox only; **no Lightsail run, no deployment, no paid services**.
- Out of scope: inferring the metric, the clock or `v_max` from data; non-linear or quantum-measurement dynamics; multi-site interventions; adaptive designs; claims about real signalling. Geometry Issue #4 is separate.

## 10. Anticipated limitations

- Bonferroni is conservative, so B-G1/B-G2 can pass while power is wasted; this is accepted for a first calibration.
- B-G4 power is expected to be tested mainly on N2: an analytic review probe (not a Pilot B run) found every N2 α ∈ [2, 4] above 2× the detection limit (max exterior |S| 3.6e-4…9.0e-3), but only N1 with γ ≳ 0.89 (≈ 10 % of the log-uniform range) and ≈ 4 % of random N3 draws. B-G4 therefore says little about heat-type or sparse-shortcut violations; their non-detection is reported descriptively.
- Results depend on the declared grid and v_max; a shortcut landing between grid sites (N3) can be invisible by construction.
- 24 / 16 instances give wide intervals; B-G1/B-G2 thresholds detect gross miscalibration only.
- Known σ and Gaussian white noise are idealisations; an unknown-σ or correlated-noise version is a later step.
- AI-mediated design, implementation and review by the same model family (see §6.5).

## 11. Stage plan

1. **This PR:** design and config only. A later-pass review in a different Director session checks the arithmetic (z values, binomial tails, detection limit), the null claims for each class, and the blinding procedure, then merges or requests v1.1.
2. **Stage 1 (separate PR):** generator, oracle, analyst, evaluator and tests; dev-set run with B-G0, B-G2/B-G3 on dev, and the analyst-isolation test. Record the drand chain hash and verification method.
3. **Stage 2:** after the 24 h beacon delay, one blind run on `main` via GitHub Actions; result note, durable archive as for N5, decision record.
