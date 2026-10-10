# Preregistration — many-batch coverage gate (Phase-0 report gate 4)

**Status:** preregistered 2026-10-10 by Director session `rd-claude-20261010T085643Z-4977d0`, committed **before** the holdout run. `configs/coverage_gate.json` (SHA-256 `a03e68c5c49e2cb93e4718fe33fd7d99d7820579347593860b661bd81594fc1b`, pinned in `tests/test_coverage_gate.py`) and the criteria below must not be edited after this commit; any deviation is reported as a deviation.

## Question

Report gate 4 (`docs/ISING_CALIBRATION_REPORT.md` §D, G4) asks for interval coverage on **new seeds** with enough independent batches that the 95 % Wilson half-width of each primary coverage estimate is below 0.05. The only earlier coverage evidence is 4 × 4 (M4: 24 batches; burn-in replication: 20 batches). Question: **at L = 16 and L = 32 near Tc, do the project's nominal 95 % independent-chain Student-t intervals for the energy per spin cover the exact finite-torus value at close to the nominal rate, with the run length the L32 gate showed to be adequate?** Methods calibration only; no claim about emergent structure or new physics.

## Design

| Item | Value |
| --- | --- |
| Model / sampler | periodic L × L ferromagnetic Ising, J = k_B = 1; even-L checkerboard Metropolis, `critical_gate.run_chain` unchanged (cross-checked against an independent Wolff sampler in PR #15) |
| Sizes, temperature | L ∈ {16, 32}; T = 2.269185 (rounded Tc used throughout; exact reference evaluated at this T) |
| Batches | 400 per size, 4 independently seeded chains per batch → 3,200 chains |
| Starts | all random (hot) |
| Seeds | `2030010001 + size_index·100000 + batch·10 + chain`; 2030010001–2030013994 (L16), 2030110001–2030113994 (L32); disjoint from every earlier config and from the sizing pilot (2031…) |
| Chain | 1,000 warmup sweeps (discarded for the main analysis but **recorded**), 3,000 sampling sweeps, measurement every 4th sweep → 750 draws |
| Budget | 8.19 × 10⁹ attempted flips (cap 9 × 10⁹); ≈ 32 CPU-minutes estimated from the sizing pilot; local or GitHub runner via manual dispatch only, **no Lightsail** |
| Raw data | lossless int16 energy/magnetization sums for every draw from sweep 0, `.npz` SHA-256 and per-array digests in the JSON report; the `.npz` (~10 MB) is an Actions artifact, not committed |

**Batch interval (the object under test).** For each batch, `stats.independent_chain_interval` over the 4 chain means: mean ± t₀.₉₇₅,₃ · sd/√4. A batch with zero spread has an undefined interval and counts as **not covering**.

**Independent reference.** Exact finite-torus energy per spin (Kaufman 1949 / Beale 1996), `exact_finite.py`, checked against 4 × 4 enumeration and an independent transfer matrix: E₁₆ = −1.453065323725986, E₃₂ = −1.4336590464244536 at T = 2.269185. Known mathematics, not a project result. No exact reference exists here for |m|.

## Criteria

Per size L (primary observable: energy per spin):

| ID | Criterion |
| --- | --- |
| C1 | Wilson 95 % half-width of the coverage fraction **< 0.05** (guaranteed by n = 400: worst case 0.0488) |
| C2 | Wilson 95 % **lower bound ≥ 0.90**, i.e. **≥ 372 of 400** batches cover |

**GATE 4 PASS** iff C1 and C2 hold for both L = 16 and L = 32.

**Operating characteristics (computed before the run, exact binomial).** Per size, P(pass) = 0.969 at true coverage 0.95, 0.55 at 0.93, 0.26 at 0.92, 0.024 at 0.90, < 0.001 at ≤ 0.88. Both sizes jointly: false-fail probability ≈ 0.060 for a perfectly calibrated interval. The rule targets material undercoverage (≤ 0.90), not small deviations.

**Secondary analyses (prespecified, reported, not gating):**
1. Exact two-sided binomial p-value of the observed count against 0.95.
2. Pooled bias: mean of all 1,600 chain means minus the exact value, z with SE = sd(chain means)/√1600; **|z| > 3 is flagged** as a finding needing follow-up even if C2 passes, because wide 4-chain intervals are insensitive to biases well below their half-width.
3. Per-chain intervals mean ± 1.96·sd/√(Geyer ESS) over all 1,600 chains per size (the G6 construction of the L32 gate), coverage with Wilson interval.
4. Reference-free calibration for E and |m|: sd of the 400 batch means divided by the RMS batch standard error (expected ≈ 1).

**Power control (prespecified).** The same C1/C2 evaluation on the **first 40 sweeps (10 draws) after a random start, without warmup**, of the same chains. Expected: **C2 fails at both sizes**. If it passes at a size, the coverage criterion is reported as *non-discriminating for start bias* at that size.

## Design-sizing pilot (disclosed)

Before writing this document a pilot on disjoint seeds (2031000001+, 2031100001+; 16 and 24 random-start chains per size) measured cost and sized the control window only: ≈ 0.7–1.0 s per 6,000-sweep chain on this machine (per-call overhead dominates at L16); chain-mean sd of E over 5,000 post-warmup sweeps 0.0106 (L16) and 0.0087 (L32). For the first 40 sweeps from a random start, mean minus exact was +0.070 (L16) and +0.114 (L32) with chain-mean sd 0.079 / 0.046, implying an approximate 4-chain t-interval coverage of 0.76 (L16) and 0.10 (L32) — the basis for the power-control expectation. These draws are not evidence in the gate.

## Decision rule and interpretation

- **PASS:** report gate 4 is met **for the energy per spin, this sampler, these sizes, this temperature and this run length**. Phase 0 is not automatically GO: finite-size gate 5 and archival gate 6 remain open.
- **FAIL:** gate 4 is not met; values are reported. No rerun with new seeds or changed thresholds to obtain a pass; a redesign requires a new preregistration.
- All batches, the power control and the raw `.npz` digest are retained whichever way it goes.

## Known limitations (stated in advance)

- Only the energy has an exact finite-L reference; |m| is checked only by the reference-free spread ratio.
- One temperature, one sampler, random starts only; T is 3·10⁻⁷ below exact Tc (the reference is evaluated at the simulated T).
- Coverage of 4-chain t intervals is a weak test of small biases; secondary analysis 2 addresses that.
- 400 batches estimate coverage to about ± 0.02–0.05; they cannot certify exactly 95 %.
- Independence of chains rests on distinct PCG64 seeds.
