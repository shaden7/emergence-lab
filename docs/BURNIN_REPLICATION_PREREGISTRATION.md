# Preregistration — fresh-seed burn-in replication (Phase-0 gate, priority 1)

**Status:** preregistered 2026-10-10 by Director session `rd-claude-20261010T081233Z-2bca3d`, committed **before** the holdout run. `configs/exact4_burnin_replication.json`, the hypotheses in `src/emergence_lab/burnin_replication.py` (`PRIMARY`, `FAMILY_ALPHA`, `evaluate`) and the rules below must not be edited after this commit; any deviation is reported as a deviation.

## Question

The 2026-10-10 post hoc analysis of the burn-in experiment (PR #10, `docs/experiments/2026-10-10-burnin-paired-analysis.md`, 10 batches) found (a) a bias of zero burn-in at T = 1.5 in the direction of incomplete equilibration, (b) paired 0 → 100 sweep shifts at T = 1.5 and 2.269 surviving Bonferroni, and (c) an unexplained energy offset at burn-in 1600, T = 1.5 (+0.0033 ± 0.0009, p = 0.005, not surviving correction). Because (a)–(c) were found after looking at the data, they are hypotheses. **Do they replicate on fresh, disjoint seeds with twice the batches?** This is a methods-calibration question about the project's Metropolis sampler on a 4 × 4 torus; it concerns no physics claim.

## Design

| Item | Value |
| --- | --- |
| Model / sampler | periodic 4 × 4 Ising, J = k_B = 1; random-site Metropolis of `ising.run_chain` (unchanged), random initial spins |
| Temperatures | 1.5 and 2.269185 (T = 3.5 dropped: no effect was visible there) |
| Burn-in arms | 0, 100, 1600 sweeps; **paired**: every arm reuses the same seed, hence the same initial state, per (T, batch, chain) |
| Batches | 20 per temperature, 4 chains per batch; batch = independent replicate |
| Sampling | 800 sweeps after burn-in, measurement every 5th sweep |
| Seeds | `base + (t_index·20 + batch)·4 + chain`, base 2029061001 → 2029061001–2029061160; checked disjoint from all 1,780 seeds of earlier configs, the L32 gate and the Wolff cross-check |
| Budget | 480 chains, ≈ 1.05 × 10⁷ attempted flips; ≈ 1 min single core; local and GitHub runner only, **no Lightsail** |
| Reference | exact 4 × 4 enumeration (`exact4.exact_observables`) — known finite sum, not a result of this project |
| Runner | `python -m emergence_lab.burnin_replication --config configs/exact4_burnin_replication.json --output <json>` |

## Primary hypotheses (family of seven, Bonferroni α = 0.05/7 = 0.00714, two-sided Student t, df = 19)

Value per batch: *bias* = 4-chain mean − exact reference; *shift* = arm mean − burn-in-0 mean for the same batch.

| ID | Quantity | Original estimate | Replicated if |
| --- | --- | --- | --- |
| P1 | bias, T = 1.5, \|M\|, burn 0 | −0.0032 | p < α and negative |
| P2 | bias, T = 1.5, E, burn 0 | +0.0069 | p < α and positive |
| P3 | shift 0 → 100, T = 1.5, E | −0.0086 | p < α and negative |
| P4 | shift 0 → 100, T = 1.5, \|M\| | +0.0039 | p < α and positive |
| P5 | shift 0 → 100, T = 2.269185, E | −0.0113 | p < α and negative |
| P6 | shift 0 → 100, T = 2.269185, \|M\| | +0.0050 | p < α and positive |
| P7 | bias, T = 1.5, E, burn 1600 (anomaly candidate) | +0.0033 | see below |

**P7 has three outcomes:** *persists* if p < α and positive; *not replicated* if not significant **and** the 95 % t interval excludes the original +0.0033; *inconclusive* otherwise.

**Operating characteristics (approximate, computed before the run from the original standard errors scaled by √(10/20)):** expected |t| under the original effect sizes ≈ 9 (P1), ≈ 5 (P2), ≈ 7.6 (P3), ≈ 11 (P4), ≈ 6.4 (P5), ≈ 7 (P6), ≈ 5.2 (P7); the critical |t| at α = 0.00714, df = 19 is 3.01, so power for each is high if the original effect is real at that size. If P7's true value is 0, P(*not replicated*) ≈ 0.99. These rest on noisy original SEs and are indicative only.

## Secondary and exploratory (no inference claimed)

Interval coverage counts per arm/T/observable (Wilson ranges); all other bias and shift cells, uncorrected, labelled exploratory.

## Interpretation rules

- P1–P6 replicated → the zero-burn-in bias and the need for ≥ 100 sweeps burn-in from random starts at T ≤ 2.27 on 4 × 4 become **replicated numerical observations** (still small-lattice method facts, not physics).
- Any of P1–P6 not replicated → reported as such; the original post hoc finding is downgraded, not rescued by reruns.
- P7 *not replicated* → the anomaly candidate is closed as most likely chance; *persists* → open a specific investigation (RNG stream position, sampler), no interpretation before that; *inconclusive* → stays open.
- No rerun with new seeds or thresholds to change an outcome. All raw batch records are retained in the result JSON.
- This replication alone does not change the Phase-0 decision; remaining gates are coverage (report gate 4), finite-size (gate 5) and raw-artifact archival (gate 6).

## Known limitations (stated in advance)

- 4 × 4 only; burn-in requirements grow with L and near Tc.
- Arms share seeds, so arm-level coverage tallies are correlated; batches are independent only through distinct PCG64 seeds.
- Student-t on batch means assumes approximate normality of 4-chain means; 20 batches limit that check.
- The seven hypotheses were chosen from the previous run's results; this design tests them, it does not explore new ones.
