# Research State

Last handoff update: 2026-10-09.

## Mission
Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

The Ising benchmark is a calibration step. The long-term question encompasses foundational spacetime, matter, interactions, and the principles that might give rise to them; candidate models still require rigorous mathematical and empirical evaluation.

## Documentation iteration (2026-10-09)
- Added `docs/OVERVIEW.md` to separate foundational-physics vision, specific research questions, validation methodology and roadmap.
- Refined `AGENTS.md` to require top-down observables, controls, evidence levels, bounded experiments, and reproducible session handoffs.
- Documentation-only change; no new experiment, proof, or deployment verification resulted from this iteration.

## Implemented (repository code)
- 2D ferromagnetic Ising model, periodic lattice, Metropolis updates.
- Deterministic seeded CPU experiments with JSON configs.
- CSV measurements and JSON manifest, basic pytest tests, Docker container capped at 0.5 vCPU and 1536 MB.
- Smoke and larger nightly experiment configs; GitHub CI.
- Manual GitHub Actions Lightsail deployment targeting /opt/emergence-lab; deploy workflow checks prerequisites, builds, runs smoke, then installs cron for 02:00 UTC.

## Verified operational status (2026-10-09)
- [Lightsail deployment run 37985438961](https://github.com/shaden7/emergence-lab/actions/runs/37985438961), on commit 1533d6f17bd1b23029f9ae86613db0fc2a240de3, completed **success** at 20:12 UTC. The remote build/smoke step succeeded; it checks smoke manifest and measurements files and only then installs the scheduled 02:00 UTC cron file.
- The server's actual output contents and subsequent cron execution remain **uninspected**. Deployment is still older than the proposed statistics patch. No automatic deployment was triggered.
- No full finite-size scaling, Lean integration or autonomous LLM hypothesis generator exists.

## Scientific cautions
Monte Carlo samples are autocorrelated; the initial averages do not demonstrate a phase transition or novel physical findings. The infinite-lattice Ising benchmark critical temperature is 2/log(1+sqrt(2)) in units J=k_B=1.

## Next priority
1. Review and merge milestone 2 statistical code only if PR CI passes; manually deploy after review, and verify actual remote manifest and cron records without affecting EatSleepFeel.
2. Pre-register a longer independent-seed holdout, verify equilibration sensitivity and autocorrelation-window stability.
3. Establish calibrated uncertainty, finite-size scaling and plotted model comparisons with a noninteracting-spin negative control.
4. Only then prototype emergent geometry/causal-structure models and Lean statements.

## Handoff requirements
After each meaningful research iteration, record: question, exact commit and config, computational resource budget, observed results, uncertainty and negative controls, scientifically supported conclusion, limitations, and next experiment. Keep large raw result files in versioned artifact storage rather than bloating Git history.

## Milestone 2: first uncertainty diagnostics (2026-10-09; proposed PR)

**Research question:** How does temporal autocorrelation reduce the information content of sampled finite Ising chains near the benchmark critical temperature?

**Implementation:** New per-chain integrated-autocorrelation heuristic and effective sample count, adjusted within-chain SEM, and independent-seed Student-t approximate 95% intervals across *chain means* (never naïvely pooled sweeps); outputs measurements.csv, summary.csv and a manifest containing statistical method and caveats. Trapped or short chains report missing diagnostics. Simulation and nightly compute configs are unchanged.

**Controls / falsification criterion:** Synthetic i.i.d. Gaussian versus AR(1) correlated series must show reduced effective count under correlation; constant series must not report false certainty; same simulation seed must return same results; CI/smoke outputs must exist. Statistical confidence is provisional without empirical coverage checks and equilibration tests.

**Evidence (executed locally, not on Lightsail):** 10 pytest tests passed; 12-chain configs/smoke.json run completed and wrote 6 aggregate rows. Config SHA-256 31d500fb653db1368d46364c561c825770faa289a6775529192e5b1cb7ae8b5b, base repository commit 9d541146556e32187812175ea99a41ddf5daaa51, proposed branch research/ising-statistics-m2-20261009, Python 3.13.5, NumPy 2.3.5; local GIT_SHA was unset and therefore null in local manifest. Details: [experimental note](experiments/2026-10-09-ising-uncertainty.md).

**Numerical observation:** At L=16, T=2.269185, each of two independently seeded chains produced 40 measured configurations. Heuristic effective counts for |M| were ~4.56 and ~3.86, implying strong serial dependence for this short run. Between-chain |M| mean ~0.68555 and a very wide unconstrained approximate 95% interval [-0.00436,1.37545]. This is **not** a phase-transition inference or a new physical result.

**Limits and cost:** Only two short-run replicates and 100 burn-in sweeps, no demonstrated equilibration/normality or interval coverage, and potentially underestimated long autocorrelation tails. Local budget 12 chains × 300 sweeps with L=8/16. Nightly budget unchanged: 128 chains with 1000 sweeps, Docker 0.5 CPU/1536 MB and 7200 s script timeout. No remote experiment was started during this iteration.

**Next discriminating experiment:** Pre-register independent holdout seeds, 4–8 chains, longer burn-in and sampling near critical T, compare correlation-window and burn-in sensitivity, then use finite-size scaling and a noninteracting-spin negative control. No fundamental-physics claim is supported by current numbers.

## Validation milestone 3 — finite 4x4 equilibrium reference (stacked PR, 2026-10-09)

**Scientific question:** Do the seeded Metropolis equilibrium estimates and the independent-chain uncertainty summaries reproduce an independently calculated finite-system Boltzmann distribution? This is a method-validation question only, not an argument for fundamental physics.

**Independent baseline:** Enumerate all 2^16 = 65,536 spin configurations of a periodic 4x4 Ising lattice. Count disagreeing horizontal/vertical bonds directly from bitstrings, without calling the Monte Carlo energy function, then normalize Boltzmann weights. Exact numerical reference (T, energy per spin, |M|): (1.5, -1.95064256146, 0.98617329782), (2.269185, -1.56562403375, 0.84386054623), (3.5, -0.77615005043, 0.48843718389). These are floating-point evaluations of a finite exhaustive sum, not a newly proved theorem.

**Holdout specification and budget:** configs/exact4_validation.json, with fixed base_seed **2026120101** (different from prior development/pilot seeds), L=4, three temperatures, twelve independent chains per temperature, 800 burn-in sweeps plus 1800 sampled sweeps with a measurement every five sweeps. Total 36 chains, 1,497,600 proposed spin flips, 12,960 recorded measurements. NumPy enumeration requires roughly a few megabytes. Runs in ordinary GitHub CI, without changes to nightly Lightsail jobs or EatSleepFeel.

**Pre-execution anomaly-screen criterion for this holdout:** Recompute the mean and between-chain SEM directly from measurements.csv, compare to summary.csv, and require |chain-mean minus exact reference| <= 3.5 times the between-chain SEM for each of 3 temperatures x 2 observables. Reject missing/duplicate chains or seeds, config/manifest mismatch, zero SEM, and inconsistent summary aggregation. This is an **exploratory** diagnostic (not a calibrated 99.95% test); additionally record whether each reference lies within its reported nominal 95% confidence interval without requiring all six nominal intervals to contain their targets.

**Negative controls and checks:** In tests, the enumeration must approach the binomial independent-spin infinite-temperature mean |M| and the ordered ground-state limit; spin-flip signed magnetization must vanish. Deliberately biased summaries must fail the 3.5-SEM screen; malformed run data must fail validation. Independent enumeration checks both MC energy and magnetization, unlike comparing two implementations of the same estimator.

**Verified CI holdout (2026-10-09 20:33 UTC):** [GitHub Actions run 37987761035](https://github.com/shaden7/emergence-lab/actions/runs/37987761035) completed **success** on code commit **2d605e73900492e09492626e21fc9040ad791ac0** (PR #3 branch stacked on PR #1). The job checked out this exact commit, completed **18 pytest tests**, ran all **36 seeded chains**, wrote three summary rows, passed the exact-reference validator for all six comparisons, and uploaded the `smoke-results` artifact (id 11643658088, including `results/exact4`). The six absolute discrepancies in between-chain SEM units, energy then |M|, were: T=1.5 (0.79282, 0.72759), T=2.269185 (0.35814, 0.30627), T=3.5 (0.31131, 0.19801). The maximum is **0.793 SEM**, below the pre-run anomaly cutoff of 3.5 SEM. Reference values and the new fixed holdout config were committed before the official run. Config SHA-256: **d61c9b45b3629937f30fc9288f75d565ef90d2990a117f826173eda893129c68** (recheck exact hash before editing). GitHub CI uses Python 3.12; package revisions are captured in its install log. This is a **numerical calibration observation**, not a theorem or proof of interval coverage.

**Exploratory local checks:** A local *manually transcribed* Metropolis implementation (not a checked-out repository) had previously been used for 12-chain pilot/development-seed runs with base seeds 2026101001 and 2026110101; discrepancies were below 2.5 between-chain SEM. These were *not* treated as the fixed holdout. The GitHub CI holdout uses base_seed 2026120101. No Lightsail deployment performed.

**Limitations:** Only L=4, three temperatures and a single independent holdout; 3.5-SEM decision is deliberately conservative and cannot prove correct interval coverage or equilibration. The exact 4x4 finite-system reference has no singular phase transition; testing critical universality or fundamental spacetime properties requires different experiments.

**Next action:** Check CI test outcome and the uploaded holdout artifact. If it passes, retain the raw CSV/manifest and compare nominal 95% coverage over multiple distinct seeds, convergence with burn-in, and lattice-size scaling before making statistical claims. Stacked changes require review, then merge PR #1 before PR #2; do not auto-deploy.

## Exact4 provenance hardening (2026-10-09; separate stacked proposal)

**Question:** Can an otherwise plausible holdout CSV pass finite-4x4 validation after its preregistered RNG seeds or simulator run parameters are substituted?

**Baseline and falsification:** The original validator checked global uniqueness of seeds, record counts, manifest/config SHA and summary agreement, but not the producer-defined mapping (size, temperature, repeat) to individual seeds or per-chain burn/sampling metadata. Require exact seed sets per temperature and configured sweep counts and measurement cardinality; deliberate substitution of one still-unique seed or one runtime field must cause a ValueError.

**Implementation (unmerged branch):** `research/exact4-provenance-review-20261009` extends `src/emergence_lab/exact4.py` with explicit seed-schedule and run-parameter checks, plus five mutation-based negative-control tests in `tests/test_exact4.py`. Proposed commits `5386e87b79af63452ccb187f39889afad8fd2b56`, `461ac3545117be03917e246782238bf6029fc451`. Stacked on PR #3, which remains open and targets PR #1.

**Evidence level (verified):** GitHub Actions [run 37994018946](https://github.com/shaden7/emergence-lab/actions/runs/37994018946) completed **success** for commit `f8c09bc8d88bb9b2d2914a4a3befabcbb73be6ee`: pytest, smoke, exact 4x4 holdout and artifact upload each succeeded. The validation here is software/measurement-consistency evidence, not a new Ising discovery. The earlier PR #3 run does not independently review this change. No new Ising numerical result or scientific theorem is claimed.

**Limits:** The CSV can still be fabricated with matching metadata; validation verifies structural provenance consistency, not cryptographic authenticity or independence of runs. Seed mapping mirrors `cli.py` and therefore shares its rounding/schedule assumptions. Chain autocorrelation/equilibration and interval coverage remain open. Zero extra VM/GPU/API budget; no Lightsail deployment.

**Next step:** Inspect detailed CI logs/artifacts and request code review before merging the stack in order PR #1 -> PR #3 -> PR #7. Then pre-register an independent multi-batch coverage experiment with known exact 4x4 targets, fixed seeds, planned interval coverage and uncertainty; distinguish long-chain Monte Carlo bias from between-batch randomness.
