# Research State

Last handoff update: 2026-10-09.

## Mission
Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

The Ising benchmark is a calibration step. The long-term question encompasses foundational spacetime, matter, interactions, and the principles that might give rise to them; candidate models still require rigorous mathematical and empirical evaluation.

## Documentation iteration (2026-10-09)
- Added `docs/OVERVIEW.md` to separate foundational-physics vision, specific research questions, validation methodology and roadmap.
- Refined `AGENTS.md` to require top-down observables, controls, evidence levels, bounded experiments, and reproducible session handoffs.
- Documentation-only change; no new experiment, proof, or deployment verification resulted from this iteration.

## Research process iteration (2026-10-09)
- Documented a sequential hourly **Research Director** model in `docs/RESEARCH_DIRECTOR.md`, with optional specialized review only when delegation is actually available.
- Added deconfliction guidance: inspect open issues/PRs, prefer continuing existing work, use isolated branches, do not treat repository files as concurrency locks.
- Added evidence and milestone-review checklists, including an independent skepticism gate for novel claims.
- This is **workflow documentation only**. It does not update the scheduled ChatGPT automation, verify the Lightsail deployment, run experiments, implement subagents, or introduce new scientific findings.
- The hourly automation should read the Director protocol after PR #2 is merged; actual tool/subagent capabilities in scheduled invocations are unverified.

## Director automation activation (2026-10-09)
- Merged Research Director governance protocol via PR #2 (merge commit `5ef471ef98c8e1da05703ef644af784165c35f79`).
- Updated the existing **enabled hourly ChatGPT task** to read `docs/RESEARCH_DIRECTOR.md`, inspect open work before editing, prioritize Ising calibration, and treat networks as optional mathematical models rather than physical ontology. The hourly cadence remains unchanged.
- Clarified Issue #4: lattice dimensions encoded at construction time are estimator controls, not emergent spacetime discoveries.
- The task has **not yet demonstrated a successful subsequent hourly research run**, nor are GitHub write/tool availability or the Lightsail deployment verified by this documentation update. No simulation, proof, or code test was executed in this iteration.

## Autonomous integration governance (2026-10-09)
- Adopted [docs/WORKFLOW_POLICY.md](WORKFLOW_POLICY.md) directly on `main` as the binding source-of-truth and PR integration policy; synchronized `AGENTS.md`, `docs/RESEARCH_DIRECTOR.md` and the README. This was a **process/documentation-only correction**, not a scientific result or a code deployment.
- The project owner is **not** a routine PR reviewer. Subsequent research sessions are responsible for review, verification, correction and eligible merges. Agent-led review must not be misrepresented as external peer review; scientific claims and deployments retain stronger evidence/risk gates.
- Default work-in-progress limit: **3 open research/feature PRs**. When the backlog exceeds this, prioritize reviewing and integrating existing work over opening further feature PRs.
- At policy adoption, eight PRs were recorded as open: Ising dependency stack #1 → #3 → #7 → #9 → #10, plus #5 (representation-neutral strategy), #8 (literature review), and #11 (causal pilot). This is a historical snapshot; agents must refresh actual GitHub status each run.
- No Ising PR or other research PR was reviewed/merged by this governance iteration. No experiments were executed. A scheduling prompt may bootstrap this policy, but GitHub remains the binding authority.

## Session coordination implementation (2026-10-10)
- Created persistent `coordination/research-lock` branch, containing `lease.json` initialized `idle`; the operational state is deliberately not committed to `main`.
- Adopted [RESEARCH_LOCK.md](RESEARCH_LOCK.md) as the binding Director lease protocol via `AGENTS.md` / [WORKFLOW_POLICY.md](WORKFLOW_POLICY.md) / [RESEARCH_DIRECTOR.md](RESEARCH_DIRECTOR.md). Research-side mutations require CAS acquisition, ownership verification, periodic heartbeat, owner-checked release and two-hour stale-lease recovery.
- **GitHub connector integration check:** two candidate lease commits derived from the same initial HEAD; the first expected-SHA ref update returned success. The stale contender returned a generic GraphQL error (not a typed concurrency error); rereading the ref confirmed the first candidate remained HEAD. A guarded update then restored `idle` (commit `2a67540b9dd47280b3925b2065c5c858f60c18fd`). This demonstrates observed contention handling, not a proof of universal exclusion under failures.
- **Operational limitation:** enforcement is cooperative; every Director must obey the protocol, and lost leases cannot cancel already-started external work. ChatGPT automation cannot be configured to run every 15 minutes (hourly minimum). This iteration neither changed a ChatGPT task's enabled state nor executed scientific simulations or CI.

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

## M4 proposed: exact4 interval-coverage pilot (2026-10-09; stacked PR)

**Question:** Across *independent* batches of six independent seeded 4x4 Ising chains, how frequently do nominal 95% between-chain Student-t intervals enclose the exact finite-system energy and absolute-magnetization expectations?

**Preregistered protocol:** `configs/exact4_coverage_pilot.json`: temperatures 1.5, 2.269185 and 3.5; 24 batches per temperature; 6 chains per batch; 400 burn sweeps + 800 sample sweeps at interval 5; base seed 2027010101 (disjoint from milestone-3 holdout). Total 432 chains; 8,294,400 single-spin update proposals; 69,120 sampled configurations; capped at 500 chains by implementation. No Lightsail/paid API resources; run the full pilot only on a reviewed, bounded worker with adequate CPU time.

**Observable, controls, falsification:** For each temperature and each observable record 24 coverage indicators and Wilson binomial 95% uncertainty bounds. Exact enumeration is the independent target. Primary exploratory concern: a nominal interval showing very low empirical coverage; do not call 24 batches a precise coverage calibration. At 24 batches, even full observed coverage only bounds the population coverage loosely. Fix seed plan before running; retain *negative* and failed batches. Unit tests cover deterministic seeded short run, Wilson endpoints and rejection of invalid/excessive configs.

**Status:** `src/emergence_lab/coverage4.py`, configuration, tests committed to `research/exact4-coverage-pilot-20261009` (stacked on PR #7). Full configured 432-chain pilot **not executed** in this handoff; no numerical coverage claims. Test/CI result must be separately verified; no deployment.

**Methodological reservations:** Independent random-number seeds make batch Monte Carlo runs pseudorandomly disjoint, not logically independent guarantees. The t intervals are vulnerable to equilibration bias and nonnormal chain means; intervals for energy and magnetization within a batch are correlated. Wilson intervals across batches assume independent Bernoulli coverage events; no multiple-testing correction. A single finite-size target cannot validate critical scaling. The 24-batch pilot is for detecting gross miscalibration, not proving 95% coverage.

**Next action:** Verify CI on new PR, execute reviewed budgeted 432-chain pilot with recorded Python/NumPy and revision, retain machine-readable results, then compare observed undercoverage with burn-in/sampling sensitivity on *fresh* seeds before statistical claims.

### M4 CI execution extension (2026-10-09)

A follow-up change to PR #9 added the **full preregistered 432-chain M4 experiment** as an automated CI step, restricted to the M4 branch and capped at 20 minutes of CI wall-clock time. The step writes `results/exact4_coverage.json`, preserved by the existing upload-artifact action even on test failure. No Lightsail resources are required. The branch-specific CI run [37994539424](https://github.com/shaden7/emergence-lab/actions/runs/37994539424) was **in progress** at handoff; do not infer scientific results or completed execution until logs and uploaded JSON are inspected. Commit at submission: `d4169cffdb87dfd93aebefb5da2e4f27a13b292d`.

**A priori decision:** This is a method-calibration *measurement*, not a confirmation test that must pass. Undercoverage is a negative finding to retain, not grounds to retry with fresh seeds until favorable. The six reported empirical rates share correlations and should not be treated as six independent discoveries. Compare realized intervals to Wilson uncertainty; any inference about actual calibration must assess burn-in sensitivity using nonoverlapping new seeds and may need larger batch counts.

### M4 first fixed-seed coverage observation — measured 2026-10-09

**Execution and traceability:** [CI run 37994539424](https://github.com/shaden7/emergence-lab/actions/runs/37994539424), branch commit `d4169cffdb87dfd93aebefb5da2e4f27a13b292d`, Python 3.12.15 / NumPy 2.5.3 / pytest 9.1.1. All 26 pytest tests, smoke, finite 4x4 holdout and **full M4 432-chain batch experiment** completed successfully. M4 step ran approximately 51 seconds. Raw JSON artifact: [smoke-results #11646079121](https://github.com/shaden7/emergence-lab/actions/runs/37994539424/artifacts/11646079121); includes `results/exact4_coverage.json`; ZIP SHA-256 `8fefb1ceea323e67305a39681c21248927aa9f9e03a2a0cc9b4d581a4f89d08d`.

**Observed nominal 95% coverage (24 batches per temperature and observable):**

| T | Energy covered | |M| covered |
| --- | --- | --- |
| 1.5 | 23/24 = 95.8% (Wilson 95% 79.8–99.3%) | 23/24 = 95.8% (79.8–99.3%) |
| 2.269185 | 23/24 = 95.8% (79.8–99.3%) | 24/24 = 100.0% (86.2–100%) |
| 3.5 | 22/24 = 91.7% (74.2–97.7%) | 22/24 = 91.7% (74.2–97.7%) |

**Interpretation — numerical observation, not proof:** No gross undercoverage appeared in these six *correlated* pilot tallies. They are consistent with nominal coverage but are too imprecise to establish it. Two observables within a batch are not independent. A single fixed-seed experiment cannot establish general reliability; no adjustment for inspecting six diagnostics was applied. Run configurations and seed selection were set before the observed results; no selective rerun should be used to alter this evidence.

**Engineering follow-up:** To avoid repeating the expensive 432-chain pilot on each ordinary push, its CI step is now restricted to explicit `workflow_dispatch` runs of the M4 branch; prior successful run and original artifact remain authoritative. A subsequent CI job may confirm tests but does not constitute a fresh fixed-seed coverage experiment.

**Next discriminating measurement:** Pre-register a **new**, disjoint-seed burn-in sensitivity experiment (e.g. 0/100/400/1600 sweeps, matched chain sampling; fixed compute cap), report both mean bias relative to exact reference and interval coverage, and study whether near-critical uncertainty estimates are robust. Do not interpret the current results as evidence for emergent spacetime.

## Burn-in sensitivity follow-up (2026-10-09, proposed)

**Question:** How sensitive are finite-4x4 Ising means and nominal between-chain CI coverage to initial equilibration (burn-in)?

**Design:** Frozen config `configs/exact4_burnin_sensitivity.json`: three temperatures, 10 independent batches of four chains per temperature, same seed within each matched comparison across burn-in arms 0, 100, 400, 1600; 800 sampling sweeps, every fifth sweep. 480 chains, 4 × 10 × 4 × 3 × 800 sampling sweeps plus differing burn-in; budget cap 500 chains; no Lightsail. Paired differences must not be analyzed as independent arms.

**Implementation:** `src/emergence_lab/burnin4.py`, deterministic smoke test, configuration committed to branch `research/exact4-burnin-sensitivity-20261009`. **Not yet scientifically validated**: no full experiment was run or CI verified at this handoff. Code/review checks remain mandatory. Negative findings must not be discarded.

**Limitations:** With only 10 batches per condition, binomial uncertainty of interval coverage is substantial. Initial states are random spins, and chain mean differences conflate burn-in bias, Monte Carlo noise and trajectory divergence. Distinct seeded pairs do not establish absence of bias. No causality, geometry, or fundamental-physics conclusion follows.

**Next:** Run CI pytest, review the branch and execute bounded experiment as a manually triggered GitHub Actions step, retaining JSON outputs and detailed diagnostics. Report observed biases and failure cases, compare exact reference and independence assumptions. Do not deploy to Lightsail.

### M4 burn-in sensitivity: first fixed-seed numerical observation (2026-10-09)

**Confirmed execution:** [Actions run 37995173975](https://github.com/shaden7/emergence-lab/actions/runs/37995173975), experiment revision `7518f095e4776b3c8a751c354ada320350d80648`. Pytest, smoke, exact4 control and full burn-in experiment all succeeded. Full raw JSON `results/exact4_burnin.json` uploaded in [artifact 11647295336](https://github.com/shaden7/emergence-lab/actions/runs/37995173975/artifacts/11647295336) (ZIP SHA-256 `41392c9ba682c8ce8b331f30b1242179a91756542b56d98090ef473d02b365dd`). The controlled burn-in step ran approximately 45 seconds on GitHub CI; not on Lightsail.

**Observed coverage counts out of 10 batches at each temperature (energy / |M|):**

| Burn sweeps | T=1.5 | T=2.269185 | T=3.5 |
| --- | --- | --- | --- |
| 0 | 9/10, 8/10 | 10/10, 10/10 | 8/10, 10/10 |
| 100 | 9/10, 10/10 | 10/10, 10/10 | 9/10, 10/10 |
| 400 | 10/10, 10/10 | 10/10, 10/10 | 8/10, 10/10 |
| 1600 | 10/10, 10/10 | 8/10, 8/10 | 10/10, 10/10 |

**Critical interpretation:** There is **no monotonic burn-in improvement in the observed coverage counts**. A drop from 10/10 to 8/10 at the benchmark temperature with longer burn-in is a reminder that stochastic batch coverage fluctuates; it is not evidence that longer burn-in is harmful. Ten batches have very broad binomial uncertainty; even 10/10 does not prove calibrated 95% coverage. Matched seed arms are correlated, and 24 coverage metrics were inspected; no independent multiplicity-corrected significance finding or equilibration proof is claimed. The JSON contains per-batch mean deviations and paired differences but these have **not yet been summarized or independently reviewed** in this handoff.

**Next discriminating question:** Inspect the raw paired bias shifts (not merely binary coverage), compute uncertainty from independent paired batches, and contrast longer sampling regimes and an analytically initialized equilibrium baseline where feasible. The run was predeclared, with no selective favorable reruns. The CI experiment step has been restricted to manual dispatch for future reproducibility without repeated load on each PR push.

## Interrupted-session recovery protocol (2026-10-10)
- Added an explicit recovery audit to `docs/RESEARCH_LOCK.md` and the `docs/WORKFLOW_POLICY.md` Director cycle. After acquiring a new lease, a Director responding to an interrupted run checks relevant PR/branch heads, unfinished GitHub Actions jobs, logs, artifacts and partially integrated results **before** launching duplicate work.
- An `idle` lease is not proof a ChatGPT session or GitHub Actions experiment finished; an expired lease cannot stop external jobs. Missing run status/artifacts remain unknown, not successes. Findings go to existing PR/issue or research-state handoff, avoiding extra feature PRs.
- Integration: process-only documentation commits `e744d093d2dedcd816c0ab8129f1796e68dcfc04` and `69206ab0c42f11b9035a35189f49448bf29ad58e`. No scientific experiment, CI run, deployment or new liveness-monitor service was performed.
