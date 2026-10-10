# Preregistration — L32 critical-mixing gate (Phase-0 blocker)

**Status:** preregistered 2026-10-10 by Director session `rd-claude-20261010T073142Z-d6f71d`, committed **before** the holdout run. Config `configs/l32_critical_gate.json` and the criteria below must not be edited after this commit; any deviation is reported as a deviation, not silently applied.

## Question

Phase 0 is **NO-GO** because the PR #12 pilot found insufficient effective sample sizes for the 2D Ising checkerboard-Metropolis sampler at L = 32, T ≈ Tc (median |m| ESS 23.9 of 180, minimum 4.16; prospective rule failed). Question: **with a separated warmup, a longer run and modern diagnostics, are this sampler's L32/Tc estimates and their uncertainty statements trustworthy at the stated budget?** This is a methods-calibration question. It does not concern emergent spacetime or any new physics.

## Design

| Item | Value |
| --- | --- |
| Model / sampler | periodic 32 × 32 ferromagnetic Ising, J = k_B = 1; even-L checkerboard Metropolis (same update rule as `mixing_pilot`) |
| Temperature | T = 2.269185 (the rounded Tc used in all earlier pilots; exact Tc = 2.2691853142…) |
| Chains | 16 random (hot) starts + 16 fully ordered (cold) starts = 32 independently seeded chains |
| Seeds | `base_seed + start_index·1000 + rep`, base 2028010001 → 2028010001–2028010016, 2028011001–2028011016; disjoint from every earlier config |
| Warmup | 5,000 sweeps discarded per chain |
| Sampling | 40,000 sweeps, measurement after every 4th sweep → 10,000 draws per chain |
| Observables | energy per spin E, absolute magnetization per spin |m| |
| Budget | 1.47 × 10⁹ attempted flips (cap 1.6 × 10⁹); ≈ 1–3 min on 2 cores; GitHub runner or local only, **no Lightsail** |
| Raw data | lossless int16 energy/magnetization sums per draw in `.npz`; SHA-256 recorded in the JSON report |

**Independent reference.** The exact finite-lattice energy of the periodic 32 × 32 torus (Kaufman 1949, form of Beale 1996), implemented in `src/emergence_lab/exact_finite.py` and checked in tests against brute-force 4 × 4 enumeration and an independent transfer-matrix computation (agreement ≈ 1e-13). Reference value used: **E₃₂(T = 2.269185) = −1.4336590464244536**. This is known mathematics, not a result of this project. No exact finite-L reference for |m| is used.

**Diagnostics.** Rank-normalized split-R̂ (bulk) and folded split-R̂ (tail), bulk-ESS and tail-ESS (Vehtari et al., Bayesian Analysis 16, 2021), per-chain ESS by Geyer's initial positive/monotone sequence; `src/emergence_lab/convergence.py`. Locally cross-checked against ArviZ 1.3.0 on six synthetic cases (iid, AR(1) φ = 0.9 / 0.99, location shift, scale mismatch, ties): bulk/tail R̂ and bulk/tail/mean ESS agree to ≈ 1e-12.

## Criteria (all must hold for GATE PASS)

| ID | Criterion | Applies to |
| --- | --- | --- |
| G1 | max(bulk, tail) rank-normalized split-R̂ **< 1.01** over all 32 chains | E and |m| |
| G2 | bulk-ESS **≥ 400** and tail-ESS **≥ 400** | E and |m| |
| G3 | every chain's Geyer ESS **≥ 100** (no undefined ESS) | E and |m| |
| G4 | hot-minus-cold difference of chain means, Welch **|z| ≤ 3** | E and |m| |
| G5 | 32-chain Student-t 95 % interval of E **contains** the exact reference **and** |z| ≤ 3 | E |
| G6 | at least **27 of 32** per-chain 95 % intervals (mean ± 1.96·sd/√ESS) contain the exact reference | E |

**Operating characteristics (computed before the run).** G6: if per-chain intervals are calibrated, P(fail) = 0.0046; if standard errors are underestimated by a factor 2 (true coverage 0.67), P(pass) = 0.033; by √2 (coverage 0.84), P(pass) ≈ 0.6. G5 and each G4 test have ≈ 0.003 false-fail probability under correct sampling. The gate is conjunctive, so overall false-fail probability under a correct sampler is roughly 1–2 %.

**Power control (prespecified).** The same criteria are also applied to the first 1,800 post-warmup sweeps (450 draws) — the run length of the failed PR #12 pilot. Expected: **G3 fails**. If G3 passes on that window, G3 is reported as non-discriminating and the gate outcome is labelled *uninformative on per-chain ESS*.

## Design-sizing pilot (disclosed)

Before writing this document, one design pilot sized the run length only: 4 chains, seeds 2028090001/2/2028091001/2 (disjoint from the holdout), warmup 2,000, 40,000 sweeps, every 4. Observed per-chain Geyer τ (draws): E 8.1–10.4, |m| 17.8–26.4; per-chain ESS for |m| 379–563. The criteria above were chosen without reference to these numbers except the run length; the pilot's draws are not part of the evidence. *Numerical observation:* the PR #12 heuristic τ_int ≈ 19 sweeps for |m| is roughly half of the design pilot's Geyer τ_int ≈ 36–52 sweeps, consistent with the earlier caution that short windows underestimate autocorrelation.

## Decision rule and interpretation

- **PASS** (G1–G6 all true): the L32/Tc critical-mixing blocker is cleared **for this sampler, size, temperature and budget**. Phase 0 is not automatically GO: the burn-in replication (state priority 2) and raw-artifact archival (priority 3) remain open, and the Director records the Phase-0 decision separately.
- **FAIL** (any criterion false): NO-GO stands; the failing criteria are reported with values. No rerun with new seeds or changed thresholds to obtain a pass; a redesign requires a new preregistration.
- Either way, all 32 chains, the power control and the raw `.npz` are retained.

## Known limitations (stated in advance)

- Diagnostics cannot detect parts of state space that no chain visited; passing is not a convergence proof.
- Only E has an exact reference; for |m| only R̂, ESS and hot/cold agreement apply.
- One size, one temperature, one sampler; the rounded temperature is 3·10⁻⁷ below exact Tc (the reference is evaluated at the simulated temperature, so this does not bias G5/G6).
- Per-chain intervals use a normal approximation; 32 chains give only a coarse coverage check.
- Independence of chains rests on distinct PCG64 seeds, not on a proof.
