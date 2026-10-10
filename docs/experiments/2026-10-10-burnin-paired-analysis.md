# Burn-in sensitivity: paired bias analysis (2026-10-10)

**Status:** exploratory, *post hoc* analysis of an already preregistered and executed fixed-seed experiment. Numerical observation only; no theorem, no new physics claim.

## Data and reproduction

- Experiment: `configs/exact4_burnin_sensitivity.json` (base seed 2027021001; 3 temperatures × 10 batches × 4 chains × burn-in arms 0/100/400/1600; 800 sampling sweeps, every 5th recorded). Original CI execution: [run 37995173975](https://github.com/shaden7/emergence-lab/actions/runs/37995173975) on `7518f095e4776b3c8a751c354ada320350d80648`.
- **Independent re-execution (2026-10-10):** the same config was re-run locally (Python 3.13.16, NumPy 2.5.3; CI used Python 3.12) on the PR #10 branch merged with `main` at `e16d6643`. All 24 coverage counts reproduce the CI table exactly; runtime ≈62 s single-core.
- **Not compared byte-for-byte:** the CI artifact ZIP (id 11647295336) could not be downloaded from the reviewing environment (blob storage blocked by its egress policy). The match therefore rests on identical coverage counts plus deterministic seeding, not on a file hash.
- Reproduce: `python -m emergence_lab.burnin4 --config configs/exact4_burnin_sensitivity.json --output results/exact4_burnin.json`, then compute, per (arm, T, observable), the mean and standard error over the 10 batches of `mean - reference` (bias) and of `paired_mean_shift` (arm minus burn-in 0, same seeds). Two-sided Student-t, 9 degrees of freedom.

## Method notes

Batches within an arm use disjoint seeds and are treated as independent replicates; each batch value is a mean over 4 chains. Arms reuse the same seeds and the same random initial spin configuration, so arm-to-arm contrasts are **paired**. The analysis was chosen after seeing the coverage table (the PR itself named it as the next step), so it is not a preregistered test. 24 bias tests and 18 paired tests were inspected; Bonferroni thresholds are 0.0021 and 0.0028.

## Numerical observations

Bias relative to exact 4×4 enumeration (mean ± SE over 10 batches):

| Burn-in | T=1.5 energy | T=1.5 \|M\| | T=2.269 energy | T=2.269 \|M\| | T=3.5 energy | T=3.5 \|M\| |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | +0.0069 ± 0.0019 | **−0.0032 ± 0.0005** | +0.0147 ± 0.0080 | −0.0078 ± 0.0037 | +0.0009 ± 0.0103 | −0.0007 ± 0.0048 |
| 100 | −0.0017 ± 0.0018 | +0.0006 ± 0.0005 | +0.0034 ± 0.0062 | −0.0028 ± 0.0031 | −0.0011 ± 0.0095 | −0.0020 ± 0.0038 |
| 400 | −0.0017 ± 0.0013 | +0.0004 ± 0.0004 | −0.0004 ± 0.0069 | −0.0004 ± 0.0035 | −0.0017 ± 0.0101 | −0.0017 ± 0.0044 |
| 1600 | +0.0033 ± 0.0009 | −0.0008 ± 0.0004 | −0.0002 ± 0.0071 | −0.0019 ± 0.0032 | +0.0084 ± 0.0085 | −0.0023 ± 0.0044 |

Bold: survives Bonferroni (p = 0.00014).

Paired shifts against burn-in 0 that survive Bonferroni: burn 100 at T=1.5 (energy −0.0086 ± 0.0016, p = 0.0004; |M| +0.0039 ± 0.0005, p = 0.00002) and at T=2.269 (energy −0.0113 ± 0.0025, p = 0.0016; |M| +0.0050 ± 0.0010, p = 0.0006); burn 400 at T=1.5 (energy −0.0086 ± 0.0020, p = 0.0019; |M| +0.0036 ± 0.0006, p = 0.0002). No paired shift at T=3.5 is distinguishable from zero.

## Interpretation (bounded)

1. **Observation:** zero burn-in from random initial spins leaves a detectable bias at and below the benchmark temperature in the direction expected from incomplete equilibration (energy too high, |M| too low). 100 sweeps of burn-in removes it within the resolution of this experiment. At T=3.5, where mixing is fast, no effect is visible.
2. **Methodological finding:** binary coverage counts (e.g. 8/10 vs 10/10) did not reveal this; the paired continuous contrast did. Coverage tallies alone are a weak equilibration diagnostic at this sample size.
3. **Unresolved anomaly candidate:** burn-in 1600 at T=1.5 shows an energy bias of +0.0033 ± 0.0009 (p = 0.0048), which does **not** survive Bonferroni and has no obvious mechanism. With 24 tests, one such value is not surprising by chance. It must not be interpreted until a fresh-seed replication either reproduces or removes it.
4. Nothing here concerns critical behaviour in the thermodynamic limit, emergent geometry or fundamental physics.

## Next discriminating step

Preregister a fresh-seed replication (new disjoint base seed) restricted to burn-in 0, 100 and 1600 at T=1.5 and T=2.269, with ≥20 batches, testing (a) the zero-burn-in bias and (b) whether the burn-1600 energy offset persists. Report paired shifts as the primary outcome and coverage as secondary.
