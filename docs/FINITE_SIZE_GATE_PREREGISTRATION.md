# Preregistration — finite-size gate (Phase-0 report gate 5)

**Status:** preregistered 2026-10-10 by Director session `rd-claude-20261010T095628Z-d3ba3e`, committed **before** any draw with the registered seeds. `configs/finite_size_gate.json` (SHA-256 `2176235a66c7c437d008307ebe8129519b138c7ec62520b0afbda6b073fae6a2`, pinned in `tests/test_finite_size_gate.py`) and the criteria below must not be edited after this commit; any deviation is reported as a deviation. No pilot was run on any seed; the only pre-run measurement was a 2,000-sweep timing of `run_chain` at L = 8 and 48 (seed 1, discarded).

## Question

Report gate 5 (`docs/ISING_CALIBRATION_REPORT.md` §D, G5) asks for L = 8…32 or larger with long chains, hot/cold checks, and stability against L_min and the fit window. Question: **does the project's sampler-plus-analysis pipeline, applied at L = 8…48 at T ≈ Tc, (a) reproduce the exact finite-torus energy and specific heat at each size, and (b) recover the known 2D Ising exponents β/ν = 1/8, γ/ν = 7/4 and 1/ν = 1 to a stated accuracy that is stable across fit windows, while (c) rejecting, by the same rule, two controls that are not critical?** Methods calibration only: the exponents are known results (Onsager 1944; Yang 1952; e.g. Baxter, *Exactly Solved Models*), and recovering them is not a discovery.

## Design

| Item | Value |
| --- | --- |
| Model / sampler | periodic L × L ferromagnetic Ising, J = k_B = 1; even-L checkerboard Metropolis, `critical_gate.run_chain` unchanged (validated by the L32 gate, PR #13; Wolff cross-check, PR #15; coverage gate, PR #17) |
| Sizes, temperature | L ∈ {8, 12, 16, 24, 32, 48}; T = 2.269185 (exact Tc = 2.2691853…; references evaluated at the simulated T) |
| Chains | per size 16: 8 random (hot) + 8 ordered (cold) starts |
| Seeds | `base + size_index·100000 + start_index·1000 + rep`: main 2032010001–2032511007; disjoint from all earlier configs (checked in the test) |
| Chain length | 10,000 warmup sweeps (discarded); sampling 20,000 (L ≤ 16), 40,000 (L = 24, 32), 80,000 (L = 48) sweeps; measurement every 2nd sweep |
| Budget | main 4.82 × 10⁹ + controls 0.87 × 10⁹ = 5.69 × 10⁹ attempted flips (cap 6 × 10⁹); ≈ 20–25 CPU-minutes estimated from timing; local or GitHub runner via manual dispatch, **no Lightsail** |
| Raw data | lossless int16 energy/magnetization sums per draw, all chains incl. controls, in one `.npz` whose SHA-256 is in the JSON report; the report can be regenerated from the `.npz` (`--reanalyse`) |

L = 48 sampling length was chosen from the L32 gate's measured τ_int(|m|) ≈ 85 sweeps and an assumed dynamic exponent z ≈ 2.17 (τ₄₈ ≈ 200 sweeps), so that each split half-chain holds ≳ 150 effective draws and R̂ < 1.01 is not a coin flip. L = 64 was considered and dropped for budget.

## Estimators (between-chain uncertainty)

Per size, pooling all draws of the 16 chains (per-spin e and m): ⟨e⟩, ⟨|m|⟩, χ = L²⟨m²⟩/T, specific heat c = L²(⟨e²⟩ − ⟨e⟩²)/T², Binder U = 1 − ⟨m⁴⟩/(3⟨m²⟩²), and D = ∂ln⟨|m|⟩/∂K = L²(⟨e⟩ − ⟨|m|e⟩/⟨|m|⟩) with K = 1/T. Standard errors: leave-one-chain-out jackknife (also of ln of each quantity). Energy test: `stats.independent_chain_interval` over the 16 chain means (Student-t). Single-chain ESS intervals are **not** used (PR #17 showed undercoverage at L32).

**Exponent fits.** Weighted least squares of ln O on ln L with weights 1/SE²(ln O), no correction-to-scaling terms; slope SE multiplied by √max(1, χ²/dof). β/ν = −slope of ln⟨|m|⟩, γ/ν = slope of ln χ, 1/ν = slope of ln D. Windows: **primary** {12, 16, 24, 32, 48}; **stability** {8…48}, {16…48}, {8…32}, {12…32}.

**Exact references (known mathematics, not ours):** finite-torus energy (Kaufman 1949; `exact_finite.py`) and its central-difference T-derivative (h = 10⁻⁴; checked to change by ≤ 6 × 10⁻⁵ when h = 10⁻³) as exact finite-L specific heat.

## Criteria

Per size L (all six sizes):

| ID | Criterion |
| --- | --- |
| E1 | energy: \|⟨e⟩ − e_exact(L)\| / SE ≤ 4 |
| E2 | specific heat: \|c − c_exact(L)\| / SE_jk ≤ 4 |
| M1 | R̂ (rank-normalized bulk and folded tail, split) < 1.01 for e and \|m\| |
| M2 | bulk and tail ESS ≥ 400 for e and \|m\| |
| M3 | hot − cold Welch z on chain means, \|z\| ≤ 4, for e and \|m\| |

Threshold 4 (not 3) because 36 per-size z-tests are made: with ≈ 15 dof, P(\|t\| > 4) ≈ 0.001 per test.

Exponents, in the primary **and every** stability window:

| ID | Criterion |
| --- | --- |
| X | \|estimate − exact\| ≤ 3·SE + δ, with δ = 0.005 (β/ν), 0.03 (γ/ν), 0.08 (1/ν) |

δ is a prespecified accuracy allowance for uncorrected finite-size corrections at L ≤ 48, chosen before the run; it is informed by the earlier exploratory L = 8…32 pilot (PR #12: β/ν ≈ 0.122, connected-χ slope ≈ 1.714 — different seeds, and the connected χ is not the primary χ here) and by the expectation that D has larger corrections. The gate therefore tests *recovery to a stated accuracy* (≈ 4 % for β/ν, ≈ 2 % for γ/ν, ≈ 8 % for 1/ν plus statistical error), not a precision measurement.

Controls (same fit rule, primary window):

| ID | Control | Expected | Criterion |
| --- | --- | --- | --- |
| C1 | Ising, **T = 2.6** (disordered, ξ ≈ 4 lattice spacings), 4 + 4 chains, 5,000 + 20,000 sweeps, seeds 2033010001+ | \|m\| ~ L⁻¹, χ saturates | X fails for **both** β/ν and γ/ν |
| C2 | **J = 0**, exact i.i.d. spins (Metropolis is non-ergodic at J = 0), 8 × 2,000 draws, seeds 2034010001+ | slopes −1 and 0 | X fails for **both** β/ν and γ/ν |

For C2 the measured "e" is the nearest-neighbour sum, not the (zero) Hamiltonian, so its D is not meaningful and is not used.

**GATE 5 PASS** iff all E1, E2, M1, M2, M3 at every size, X for all three exponents in all five windows, and C1, C2 rejected.

**Secondary (reported, not gating):** Binder U(L) compared with the literature value U* = 0.61069 for the square-lattice torus (Salas & Sokal, J. Stat. Phys. 98, 551 (2000), arXiv:cond-mat/9904038; not re-derived here); connected-χ slope; z-scores without δ; χ²/dof; median per-chain τ.

**Rough a-priori precision (estimate, not a criterion):** slope SEs ≈ 0.003–0.005 (β/ν), ≈ 0.01–0.02 (γ/ν), ≈ 0.03–0.06 (1/ν).

## Decision rule and interpretation

- **PASS:** report gate 5 is met for this sampler, T and size range: the pipeline recovers the known exponents to the stated accuracy, with window stability and a demonstrated ability to reject non-critical controls. Phase 0 remains NO-GO until archival gate 6 is decided.
- **FAIL:** reported as is with every failing check. No rerun with new seeds or changed tolerances to obtain a pass; a redesign requires a new preregistration. A failure of X with E/M checks passing would point at corrections to scaling or estimator bias, not at the sampler, and is itself informative.
- All chains, controls and the raw `.npz` digest are retained either way.

## Known limitations (stated in advance)

- Fits without correction terms; δ absorbs them by assumption.
- One sampler (local Metropolis), one T, periodic square lattice; T 3 × 10⁻⁷ below exact Tc.
- Only e and c have exact finite-L references; |m|, χ, D and U do not.
- The two controls show the rule *can* reject; they are not an exhaustive false-positive analysis (e.g. a weakly first-order or a different universality class is not included).
- Self-review by the producing session; a later-pass challenge is invited.
