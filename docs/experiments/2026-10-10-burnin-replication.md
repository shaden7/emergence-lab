# Fresh-seed burn-in replication — result (2026-10-10)

**Preregistration:** `docs/BURNIN_REPLICATION_PREREGISTRATION.md`, commit `ad3bc54b7aa910ec8ba7422f7c74034e90d89f98` (pushed 08:27:37 UTC), **before** any holdout draw. Director session `rd-claude-20261010T081233Z-2bca3d`.
**Status:** preregistered confirmatory test of seven hypotheses that were themselves found post hoc (PR #10 analysis). Numerical observations about the project's 4 × 4 Metropolis sampler; no physics claim.

## Execution

| | Local | GitHub runner |
| --- | --- | --- |
| Commit | `ad3bc54` (clean tree) | `ad3bc54`, [run 38037948647](https://github.com/shaden7/emergence-lab/actions/runs/38037948647) success |
| Environment | Python 3.13.16, NumPy 2.5.3, 1 core, 50 s | Python 3.12.15, NumPy 2.5.3 |
| Seven primary statistics and verdicts | — | **identical** to every printed digit (check annotations) |

480 chains, 1.05 × 10⁷ attempted flips, seeds 2029061001–2029061160. Full output: `2026-10-10-burnin-replication-result.json` (includes all raw batch records and field-group digests).

## Primary hypotheses (Bonferroni α = 0.00714, two-sided t, df = 19)

| ID | Quantity | Original (10 batches) | Replication (20 batches) | 95 % t-CI | p | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | bias \|M\|, T 1.5, burn 0 | −0.0032 ± 0.0005 | −0.00381 ± 0.00049 | [−0.00483, −0.00279] | 2.3e-7 | **replicated** |
| P2 | bias E, T 1.5, burn 0 | +0.0069 ± 0.0019 | +0.00826 ± 0.00134 | [+0.00545, +0.01107] | 6.6e-6 | **replicated** |
| P3 | shift E 0→100, T 1.5 | −0.0086 ± 0.0016 | −0.00840 ± 0.00089 | [−0.01026, −0.00654] | 1.3e-8 | **replicated** |
| P4 | shift \|M\| 0→100, T 1.5 | +0.0039 ± 0.0005 | +0.00381 ± 0.00036 | [+0.00305, +0.00456] | 2.1e-9 | **replicated** |
| P5 | shift E 0→100, T 2.269 | −0.0113 ± 0.0025 | −0.00619 ± 0.00296 | [−0.01238, −0.00000] | 0.050 | not replicated |
| P6 | shift \|M\| 0→100, T 2.269 | +0.0050 ± 0.0010 | +0.00368 ± 0.00135 | [+0.00086, +0.00651] | 0.013 | not replicated |
| P7 | bias E, T 1.5, burn 1600 | +0.0033 ± 0.0009 | +0.00017 ± 0.00144 | [−0.00284, +0.00319] | 0.91 | not replicated |

## Interpretation (bounded)

1. **Replicated numerical observation:** on the 4 × 4 torus at T = 1.5, zero burn-in from random spins biases E upward (≈ +0.008) and |M| downward (≈ −0.004); 100 sweeps of burn-in remove it — the exploratory burn-100 biases are −0.00014 ± 0.00113 (E) and −0.00000 ± 0.00041 (|M|). Two independent seed sets now agree.
2. **At T = 2.269 the effect is not established.** Both shifts point the same way as before and are nominally significant without correction (p = 0.050, 0.013), but they fail the preregistered threshold. Between-batch variance at Tc is far larger than estimated from the original run (P5 SE 0.0030 vs ≈ 0.0018 expected). Read as: *a bias of order 0.005 may exist at Tc but 20 batches of 4 chains cannot resolve it*; not as evidence of absence.
3. **The burn-1600 anomaly candidate is closed as most likely chance**, under the preregistered rule. The verdict is marginal: the interval's upper end (+0.00319) lies just below the original estimate (+0.0033). Contributing explanation: the original SE (0.0009 from 10 batches) underestimated variability — the replication SE is 0.0014 with twice as many batches.
4. **Prospective power was overestimated** for P5–P7 because it was scaled from noisy 10-batch standard errors. This is a lesson for future preregistrations: size from a pilot's variance with an allowance for its own uncertainty.
5. **Coverage (secondary, uncorrected):** zero burn-in at T = 1.5 gave 16/20 (E) and 16/20 (|M|) covering intervals; every arm with burn-in ≥ 100 gave 20/20 at T = 1.5. At Tc: 20/20, 19/20 (burn 0), 20/20, 17/20 (burn 100), 20/20, 20/20 (burn 1600). Unlike the original 10-batch run, coverage did flag the zero-burn-in problem at T = 1.5 here; at Tc the 17/20 is within binomial noise.

Nothing here bears on critical behaviour in the thermodynamic limit, emergent geometry or fundamental physics.

## Byte-level reproduction

The full-report digest differs between local and runner (`a788ba92…` vs `f79a9d3d…`) although all reported statistics agree to every printed digit — the same pattern as the earlier unexplained burn-in mismatch. Field-group digests were added after the run (reporting only; hypotheses and decision code unchanged) and the runner re-executed on `eaaed5a` ([run 38038206636](https://github.com/shaden7/emergence-lab/actions/runs/38038206636)):

| Field group | Local = runner? |
| --- | --- |
| batch means (all Monte-Carlo estimates) | **identical** (`bc028efd…`) |
| per-batch interval bounds | **identical** (`9f701c42…`) |
| coverage aggregates | **identical** (`87d5b6a6…`) |
| exact-enumeration references | differ (`d4d72ab2…` vs `17d65429…`) |
| paired contrasts (contain mean − reference) | differ, as a consequence |

**Numerical observation:** the simulation output is byte-identical across platforms; only the floating-point value of the exhaustive 4 × 4 Boltzmann sum differs, at the ULP level (earlier sessions recorded ≈ 2.4e-14 for these references). *Hypothesis (not verified):* the unexplained byte mismatch of the 2026-10-10 burn-in re-run has the same cause, since that JSON also embeds the references. Future byte-level reproduction checks should hash simulation output separately from analytic references.

## Phase-0 consequence

Report priority 1 (burn-in replication) is **done**: practical rule confirmed for T ≤ 1.5 on 4 × 4; at Tc open with a sharper statement of required batch count. Phase-0 decision remains **NO-GO**; open gates: many-batch coverage (gate 4), finite-size (gate 5), raw-artifact archival (gate 6).
