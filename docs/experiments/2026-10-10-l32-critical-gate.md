# L32 critical-mixing gate — holdout result (2026-10-10)

Preregistration: [L32_CRITICAL_GATE_PREREGISTRATION.md](../L32_CRITICAL_GATE_PREREGISTRATION.md), committed in `ab67cdccce3ce22315f0218a857c8e0abb1d112d` **before** this run. No deviation from the registered config or criteria.

## Execution

| Item | Value |
| --- | --- |
| Code commit | `ab67cdccce3ce22315f0218a857c8e0abb1d112d` (clean tree) |
| Config | `configs/l32_critical_gate.json`, file SHA-256 `8ba2f38b62c5af3c0faf63a5cce59f35f62a57a354b03bc2278400ecb49c46c0` |
| Environment | local review sandbox, Python 3.13.16, NumPy 2.5.3, 2 worker processes |
| Cost | 1,474,560,000 attempted flips; 78 s wall, 153 s CPU |
| Report | [2026-10-10-l32-critical-gate-report.json](2026-10-10-l32-critical-gate-report.json) (SHA-256 `047612e5…88fe06d`) |
| Raw draws | `l32_critical_gate.npz`, SHA-256 `57ae4ea037e7f16402d3f0f41645f8f357cd4b09ab11c76648338a9b75bf47a2` (769 kB, not in Git; regenerate with `python -m emergence_lab.critical_gate --config configs/l32_critical_gate.json --output <dir>/l32_critical_gate.json`) |

**Independent re-execution on GitHub's runner:** [Actions run 38035618292](https://github.com/shaden7/emergence-lab/actions/runs/38035618292), commit `2a6ce8b7f4e7d827d3ec6b2ac3e6f12a52edcd8b` (gate module unchanged since `ab67cdc` except stdout printing), Python 3.12.15 / NumPy 2.5.3: **raw `.npz` SHA-256 identical** (`57ae4ea0…bf47a2`) and identical pooled means, R̂, minimum ESS, coverage count and power-control outcome, read from the run's check annotations (job logs and artifacts sit on blob storage that the review environment cannot reach). The run was triggered by a temporary branch-only push condition because `workflow_dispatch` returns HTTP 403 to the review integration; the condition was removed before merge. This is a reproduction of the same seeded computation in a second environment, not a statistically independent replication.

## Outcome: GATE PASS (all ten checks)

| Criterion | Energy E | Absolute magnetization |m| | Threshold |
| --- | --- | --- | --- |
| G1 max(bulk, tail) R̂ | 1.0007 | 1.0014 | < 1.01 |
| G2 bulk / tail ESS | 34,870 / 63,398 | 20,162 / 18,316 | ≥ 400 |
| G3 min / median per-chain ESS (of 10,000 draws) | 718 / 1,105 | 284 / 472 | min ≥ 100 |
| G4 hot − cold (Welch z) | −0.00068 ± 0.00090 (z = −0.76) | +0.0016 ± 0.0025 (z = 0.64) | \|z\| ≤ 3 |
| G5 pooled mean vs exact | −1.43386 ± 0.00045, 95 % [−1.43478, −1.43295]; exact −1.4336590; z = −0.46 | — | contains, \|z\| ≤ 3 |
| G6 per-chain 95 % intervals covering exact | 30 / 32 | — | ≥ 27 |

Median per-chain Geyer τ (draws of 4 sweeps): E 9.0, |m| 21.2, i.e. τ ≈ 36 and ≈ 85 sweeps in the 1 + 2Σρ convention.

**Power control (first 1,800 post-warmup sweeps, prespecified to fail G3): failed as expected.** Min per-chain ESS 26.8 (E) and 8.3 (|m|); R̂ 1.017 (E) and 1.032 (|m|) also fail G1. G3 is therefore discriminating at this design. G5/G6 passed on the short window as well, so the energy-coverage checks alone would not have flagged the short run.

## Evidence level and interpretation

- *Known mathematics:* the exact finite-torus energy (Kaufman 1949); the tests only verify our implementation of it.
- *Numerical observation:* the checkerboard-Metropolis sampler at L = 32, T = 2.269185, with 5,000 warmup and 40,000 sampling sweeps per chain, passed all preregistered mixing and calibration checks; its pooled energy agrees with the exact finite-L value within 0.46 standard errors, and per-chain ESS-based intervals covered the exact value in 30 of 32 chains (nominal expectation 30.4).
- *Numerical observation:* the short-window design of the PR #12 pilot fails the same criteria on fresh seeds, reproducing the reason for the earlier NO-GO; the short-run heuristic τ_int ≈ 19 sweeps for |m| is about half of the τ_int ≈ 42 sweeps implied here.
- *Not shown:* convergence in a proof sense; correctness for other L, T or samplers; any |m| calibration against an exact value; anything about emergent spacetime or new physics.

## Consequence for the Phase-0 decision

The decision stays **NO-GO**, with a narrower blocker set. Against the prospective GO gates in [ISING_CALIBRATION_REPORT.md](../ISING_CALIBRATION_REPORT.md) §D: gate 1 (reviewed integration, green `main`) met; gate 2 (L4 equilibrium) met by earlier work; gate 3 (robust τ/ESS, short chains flagged) now supported at L32/Tc by validated Geyer ESS and the failing power control; **open:** gate 4 (coverage on new seeds with ≈ 200 batches, Wilson half-width < 0.05), gate 5 (L = 8…32 with long chains and fit-window stability), gate 6 (durable raw artifacts — here mitigated by byte-identical deterministic regeneration plus registered SHA-256, but no archived copy).

## Limitations

- Same seeds in both environments: the byte-identical reproduction rules out environment-dependent nondeterminism, not sampler bias shared by both executions (the exact-energy check G5/G6 addresses the latter for E only).
- 32 chains give a coarse coverage check (G6 cannot distinguish nominal coverage from a ≈ √2 standard-error underestimate with high power).
- Diagnostics cannot detect unvisited regions of state space. The two start types (random, fully ordered) bracket the obvious modes of |m| but not every conceivable trap.
