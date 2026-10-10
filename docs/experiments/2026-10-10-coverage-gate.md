# Result — many-batch coverage gate (report gate 4), 2026-10-10

Preregistration: [`docs/COVERAGE_GATE_PREREGISTRATION.md`](../COVERAGE_GATE_PREREGISTRATION.md), committed in `8440df236a37a0b03782559ff8f1d7004c8a8190` before the run. Config `configs/coverage_gate.json`, SHA-256 `a03e68c5c49e2cb93e4718fe33fd7d99d7820579347593860b661bd81594fc1b` (unchanged). Full report: [`2026-10-10-coverage-gate-report.json`](2026-10-10-coverage-gate-report.json). Director session `rd-claude-20261010T085643Z-4977d0`.

## Execution and provenance

- Simulated locally (session container, 2 workers, Python 3.13.16, NumPy 2.5.3) with the code of the preregistration commit `8440df2`; ≈ 690 s wall, 3,200 chains, 8.19 × 10⁹ attempted flips. Nothing ran on Lightsail.
- Raw `.npz` SHA-256 `97a81cb7898c1048716a3464793488d4502b00df24a8d4d786f7fdc48adbf5a5` (~10 MB; not committed — gate 6 archival is still open). Per-array digests are in the JSON report.
- **Deviation 1 (analysis only):** after writing the `.npz`, the run's JSON serialization failed (`numpy.bool_` in two check fields). The analysis was refactored into `analyze()` with a `--from-npz` path, the booleans cast, a serialization/reanalysis test added, and the report produced by reanalysing the saved `.npz`. Simulation code, config, seeds and criteria are untouched. Six chains (batches 0, 217, 399 at both sizes) were re-simulated and are bit-identical to the stored arrays.
- **Deviation 2 (secondary only):** the SciPy binomial test was replaced by a NumPy implementation (SciPy is not a project dependency; push-CI on `8440df2` failed in collection). Checked against `scipy.stats.binomtest` in tests.
- **Not done:** an execution on a GitHub runner. `workflow_dispatch` returns HTTP 403 for this integration; the run is reproducible by manual dispatch of the CI step on this branch or on `main`, which should regenerate the identical `.npz` digest.

## Numerical observations

Primary (energy per spin, 4-chain Student-t intervals, exact finite-torus reference):

| L | Exact E | Covered | Coverage | Wilson 95 % | C1 half-width < 0.05 | C2 lower ≥ 0.90 | Binomial p vs 0.95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | −1.453065323725986 | 379 / 400 | 0.9475 | [0.9211, 0.9654] | yes (0.022) | **yes** | 0.82 |
| 32 | −1.4336590464244536 | 381 / 400 | 0.9525 | [0.9270, 0.9694] | yes (0.021) | **yes** | 0.91 |

No undefined (zero-spread) intervals. **Preregistered verdict: GATE 4 PASS.**

Secondary (prespecified, not gating):

| L | Pooled E − exact (1,600 chains) | bias z | sd(batch means)/RMS SE, E | same, \|m\| | Per-chain Geyer-ESS intervals covering | Per-chain ESS median / min |
| --- | --- | --- | --- | --- | --- | --- |
| 16 | +0.000111 ± 0.000278 | +0.40 | 0.976 | 0.973 | 1521 / 1600 = 0.951 [0.939, 0.960] | 247 / 58 |
| 32 | −0.000375 ± 0.000269 | −1.39 | 0.961 | 0.965 | **1445 / 1600 = 0.903 [0.888, 0.917]** | 101 / 16 |

Power control (first 40 sweeps after a random start, no warmup; expected to fail):

| L | Covered | Wilson 95 % | Pooled bias | C2 | Pilot-based prediction |
| --- | --- | --- | --- | --- | --- |
| 16 | 314 / 400 | [0.742, 0.822] | +0.0905 (z 37.9) | fails | ≈ 0.76 |
| 32 | 48 / 400 | [0.092, 0.156] | +0.1268 (z 106) | fails | ≈ 0.10 |

The control fails at both sizes, so the coverage criterion is discriminating for start bias of this size.

## Interpretation (hypotheses and bounded conclusions)

- Supported at the registered scope: the batch-level 4-chain t intervals for the energy per spin at T = 2.269185, L = 16 and 32, with 1,000 warmup + 3,000 sampling sweeps, are **not materially undercovering** (coverage ≥ 0.92 at 95 % confidence for each size). No energy bias is detected at a resolution of ≈ 3 × 10⁻⁴ (well below the batch-interval half-width), consistent with the L32 gate and the Wolff cross-check.
- **New finding (secondary):** at L = 32 with 750 draws per chain, single-chain intervals built from Geyer ESS undercover (0.903, Wilson upper 0.917 < 0.95); at L = 16 they are calibrated. The L32 gate's per-chain criterion G6 passed with 10,000 draws per chain. *Hypothesis:* in short chains near Tc the Geyer estimate of τ is biased low for some chains (min ESS 16), so per-chain ESS-based standard errors are too small. Consequence for later designs: prefer between-chain intervals over single-chain ESS intervals for short critical runs; the hypothesis is untested.
- The batch-mean spread ratios slightly below 1 (0.96–0.98) mean the reported between-chain SEs are, if anything, slightly conservative; not significant on its own.

## Limitations

Energy only has an exact reference (|m| checked only by the spread ratio); one temperature; one sampler (cross-checked earlier against Wolff); random starts only; one execution environment; self-review by the producing session (a later-pass challenge is invited). Passing gate 4 does not make Phase 0 GO: finite-size gate 5 and archival gate 6 remain open.
