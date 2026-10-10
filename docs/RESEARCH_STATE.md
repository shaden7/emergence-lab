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

## Representation-neutral strategy adopted (proposed 2026-10-09; integrated via PR #5 on 2026-10-10)
- `docs/REPRESENTATION_STRATEGY.md` distinguishes encodability, faithful/economical representation and physical explanation; requires an assumption audit, at least two substantively different model families where comparison is meaningful, null/failure cases and explicit discriminators before model choice.
- Methodology only: no simulation, proof, benchmark, ontology inference or discovery of new mathematics is claimed. Its gates keep cross-family computations **design-only until the Ising calibration gate is met**, which is consistent with the current Phase-0 NO-GO.
- Review correction at integration: the Physics Reports GPT introduction is attributed to M. Plávala (arXiv:2103.07469), not Janotta et al.

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

## Burn-in sensitivity follow-up (2026-10-09; PR #10)

**Question:** How sensitive are finite-4x4 Ising means and nominal between-chain CI coverage to initial equilibration (burn-in)?

**Design:** Frozen config `configs/exact4_burnin_sensitivity.json`: three temperatures, 10 independent batches of four chains per temperature, same seed within each matched comparison across burn-in arms 0, 100, 400, 1600; 800 sampling sweeps, every fifth sweep. 480 chains, 4 × 10 × 4 × 3 × 800 sampling sweeps plus differing burn-in; budget cap 500 chains; no Lightsail. Paired differences must not be analyzed as independent arms.

**Implementation:** `src/emergence_lab/burnin4.py`, tests and configuration on branch `research/exact4-burnin-sensitivity-20261009` (PR #10). The fixed-seed experiment was executed in CI (below) and re-executed in the 2026-10-10 review. Negative findings must not be discarded.

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

### Later-pass review and paired bias analysis (2026-10-10)

**Review (AI-mediated, non-independent of the project's agents):** seed schedule verified to depend only on (temperature, batch, chain), so arms are genuinely paired and share their random initial state; seeds 2027021001–2027021120 are disjoint from the M4 pilot (2027010101–2027010532) and the exact4 holdout. Added tests for paired-contrast consistency, shared seed schedule across arms (a deliberate seed-offset mutation fails this test), batch-count caveat and rejection of invalid variants/budgets; corrected a caveat that stated 12 instead of the configured 10 batches.

**Reproduction:** local re-execution (Python 3.13.16, NumPy 2.5.3) reproduces all 24 coverage counts above exactly. The CI artifact ZIP could not be downloaded from the review environment, so no byte-level comparison was made.

**Numerical observation (post hoc, exploratory):** treating the 10 disjoint-seed batches as replicates, zero burn-in leaves a bias at T=1.5 in the direction expected from incomplete equilibration (|M| −0.0032 ± 0.0005, p = 0.00014; energy +0.0069 ± 0.0019, p = 0.005). Paired shifts from burn-in 0 to 100 are clearly nonzero at T=1.5 and T=2.269 (e.g. |M| +0.0039 ± 0.0005 at T=1.5, p = 0.00002) and survive a Bonferroni correction over the 18 paired tests; at T=3.5 no shift is resolvable. Binary coverage counts did not reveal this, so coverage tallies alone are a weak equilibration diagnostic at this sample size. One **unresolved anomaly candidate**: burn-in 1600 at T=1.5 shows an energy bias +0.0033 ± 0.0009 (p = 0.005), not surviving correction over 24 bias tests and without a known mechanism; it is not interpreted. Full table and method: [experimental note](experiments/2026-10-10-burnin-paired-analysis.md).

**Next discriminating step (proposed, not executed):** preregister a fresh-seed replication with ≥20 batches at T=1.5 and T=2.269 for burn-in 0, 100 and 1600, with paired shifts as primary outcome, to confirm the zero-burn-in bias and test whether the burn-1600 offset persists.

**Earlier next-step note (2026-10-09, now addressed above):** Inspect the raw paired bias shifts (not merely binary coverage), compute uncertainty from independent paired batches, and contrast longer sampling regimes and an analytically initialized equilibrium baseline where feasible. The run was predeclared, with no selective favorable reruns. The CI experiment step has been restricted to manual dispatch for future reproducibility without repeated load on each PR push.

## Research Director Phase-0 audit and decision (2026-10-09; PR #12)

**Question and decision:** Are the Monte-Carlo, uncertainty, control and provenance tools reliable enough to begin Phase 1? **NO-GO** on the present evidence. See [full audit and criteria](ISING_CALIBRATION_REPORT.md). The phase remains open; this is a **completed critical assessment**, not a claim that all calibration gates passed.

**Deconfliction:** GitHub PRs #1 → #3 → #7 → #9 → #10 were open and stacked on inspection; none had a recorded approving review. Audit branch `research/phase0-director-audit-20261009` was created from PR #10 SHA `069997129e98ca634e515767355ef1dbaa8dd5ce`; all modifications isolated there. PR #5 representation strategy, #8 literature draft and #11 causal-pilot preregistration remain separate. **No merges, deployments, Lightsail runs, paid services or EatSleepFeel changes.**

**Executed source-data audit:** GitHub Actions ZIPs for [M4 37994539424/artifact 11646079121](https://github.com/shaden7/emergence-lab/actions/runs/37994539424) and [burn-in 37995173975/artifact 11647295336](https://github.com/shaden7/emergence-lab/actions/runs/37995173975) were downloaded and the JSON records read directly, not inferred from PR summaries. Locally recomputed 6 × 24 coverage-cell observations, 24 arm summaries (each 10 batches) and 18 paired burn-in contrasts, including t-95-% uncertainty from independent batches, using `scripts/phase0_artifact_audit.py`. M4 observed counts: 23/24,23/24 at T1.5; 23/24,24/24 at Tc; 22/24,22/24 at T3.5 (E, |M|). At T1.5/zero burn-in: E bias +0.00693 [0.00264,0.01122] and |M| bias −0.00324 [−0.00440,−0.00208]. The 100-vs-0-burn paired contrasts: E −0.008594 ±0.003583, |M| +0.003887 ±0.001109 (95-%-t-halfwidth); 18 contrasts are exploratory and uncorrected. This supports caution about start bias, not an equilibrium proof.

**New experiment implemented and actually run:** `src/emergence_lab/finite_size.py` (checkerboard Metropolis and exact J=0 iid-spin control), `configs/fss_pilot.json`, `tests/test_finite_size.py`; L 8/16/24/32 × T 2.1/2.269185/2.45 × six chains per model; 72 Ising + 72 J=0, 27,648,000 Ising proposed flips. Local Python 3.13.5/NumPy 2.3.5: 3 new pytest checks passed; pilot 5.31 sec wall, 5.25 sec CPU, about 96 MB max resident memory. [CI 37996248059](https://github.com/shaden7/emergence-lab/actions/runs/37996248059), source commit `5d54156e6407a4f61006c28f3cbdef543712cd19`: **success**, including pytest, exact4 reference holdout, bounded pilot and artifact upload; [raw artifact 11646539226](https://github.com/shaden7/emergence-lab/actions/runs/37996248059/artifacts/11646539226), Python 3.12.15/NumPy 2.5.3. **All 144 numerical chain records match the local run exactly**, including seeds and observables. Fixed base seed 2027030001; separate null-model namespace. The null's |m| scales near L^-1 and χ_abs near L^0; Ising gives exploratory effective L slopes for |m| −0.1224 (chain-bootstrap95 [−0.1731,−0.0771]) and χ_abs +1.7141 ([1.2553,2.0721]) at externally known Tc. These are **not** calibrated critical-exponent estimators: bootstrap omits finite-size/systematic bias and only 6 chains/L were used. ν unmeasured.

**Autocorrelation controls executed:** `scripts/autocorr_synthetic_audit.py`, eight independent length-12000 stationary AR(1) traces per φ=0/0.5/0.9/0.98/0.995, exact analytic τ=(1+φ)/(2(1−φ)), fixed seeds 102938–102945. [CI 37996395511](https://github.com/shaden7/emergence-lab/actions/runs/37996395511) **success**, with [raw artifact 11647447009](https://github.com/shaden7/emergence-lab/actions/runs/37996395511/artifacts/11647447009). For φ=.995 true τ=199.5, original heuristic median 171.44 (range ~114.91–318.50), Geyer-like positive pairs median 171.44, block-mean width 500 median 121.28; credible long-tail underestimation/uncertainty risk, not an established universal direction of bias. Constant/short controls were reported undefined. Method does not test equilibration.

**Scientific and engineering restrictions:** Student-t across independent chain means requires mixing and approximate normality; M4 Wilson coverage ranges too wide, 18 paired contrasts unadjusted, small finite lattices and nonlinear χ/Binder estimates carry systematic bias; no dependable ν extraction, no Binder crossings claimed. Original `cli.py` rounds temperatures for seed scheduling and chain-count-only cap does not bound computational work; new finite-size pilot explicitly caps proposals. The downloaded artifact ZIPs have finite GitHub retention, not guaranteed permanent provenance. Independent review and integration remain open.

**Next discriminating experiment (not started):** Reconstruct exact equilibrium-distributed initial spin states for L4; independently contrast stationary, random, ordered-hot/cold starts on fresh fixed seeds over registered time windows, compare bias to exact enumeration and autocorrelation/window diagnostics; then test mixing and finite-size corrections at L16–32. Do not tune on M4 seeds or start Phase 1 before a new evidence gate.

### Additional controlled equilibration experiment (same isolated PR #12, 2026-10-09)

**Question:** Do L4 ensemble observables relax from random/fully ordered starts toward the independently enumerated Boltzmann reference, and what does an **exact stationary-initialized** positive control look like? **Change:** `src/emergence_lab/equilibration4.py`, `tests/test_equilibration4.py`, `configs/equilibration4_pilot.json` and bounded CI command. Commit `bc5bf407764f022465ed1c14e4c2366198cb4e32`, 3 temperatures, 64 distinct seeds per each of 3 starts (random, ordered, exact Boltzmann), snapshots at sweep 0/5/20/100/400; 576 chains/2880 raw records, 3,686,400 attempted random-site Metropolis flips; seed basis 2027040101. Explicit proposal cap 5 million; no Lightsail work.

**Verified execution:** Locally Python 3.13.5/NumPy 2.3.5, 3 new tests passed, 14.68s wall / 14.60s CPU, ~99 MB RSS. [GitHub CI 37996892064](https://github.com/shaden7/emergence-lab/actions/runs/37996892064) success; [raw artifact 11647700495](https://github.com/shaden7/emergence-lab/actions/runs/37996892064/artifacts/11647700495), Python 3.12.15/NumPy 2.5.3. **All 2880 raw numeric records identical** across CI and local; separately enumerated reference floats differ ~2.4e-14, not bitwise identical summaries. At T=1.5 random-start mean E bias vs exact reference at sweeps 0/5/20/100: +1.9741 ±0.0980, +0.3374 ±0.1213, −0.0376 ±0.0240, −0.0103 ±0.0347 (descriptive 95% t halfwidth over independent 64 chains). At Tc random start +1.5187 ±.0905, +.1594 ±.1482, −.0437 ±.1270, +.0188 ±.1301; exact stationary-init Tc zero-sweep −.0555 ±.1186. Initial fully ordered spins have zero within-ensemble variance and degenerate t intervals at sweep zero—**not statistical precision**.

**Critical limitations:** Intervals at 90 overlapping time/start/temperature/observable cells are not multiple-comparison corrected; correlated snapshot times, one occasional stationary-reference miss at Tc sweep400, and small finite-L size prohibit proof of detailed balance, convergence bounds or correct L16–32 sampling. Exact Boltzmann initialization is a constructed L4 positive control, not emergent physics. See `docs/ISING_CALIBRATION_REPORT.md` section F. **NO-GO remains**; next is independent L16/32 mixing/ESS/block-length diagnostic and review before merging. Draft PR #12 targets #10; no concurrent writes/merges into base.

### Director deepening: actual L16–32 ESS failure, analytical interacting null, source fixes (2026-10-09)

**Question:** Does agreement of L16/32 final hot/cold observables conceal insufficient effective sample sizes? Does the analysis distinguish 2D scaling not only from J=0 but also from an **interacting** control without finite-temperature criticality? See full measurements and critical caveats in `docs/ISING_CALIBRATION_REPORT.md` Sections G–I.

**L16/32 experiment** `src/emergence_lab/mixing_pilot.py` + `configs/mixing_pilot.json` (revision `e8ae9eb18ced369489cbb629fcb090f8fac2295e`): L16/32, T2.1/Tc/2.45, 12 independent hot/random and 12 ordered starts per size/temperature, 1800 sweeps / measurement every 5, all 360 per-chain samples retained, **144 chains / 165,888,000 attempted flips / 103,680 raw energy and absolute-magnetization values**, 3000 independent-chain bootstrap replicates. Local ~20.79s/~107 MB. [GitHub CI 37997377758](https://github.com/shaden7/emergence-lab/actions/runs/37997377758) **success**, [raw artifact 11648100844](https://github.com/shaden7/emergence-lab/actions/runs/37997377758/artifacts/11648100844), Python3.12.15/NumPy2.5.3. **103680/103680 raw scalar samples exactly match** local NumPy2.3.5 execution; aggregate τ floating difference ≤1e−12.

**Quantified failure:** At **Tc/L32**, |m| median τ=3.781 sampled intervals (each 5 sweeps), median ESS=23.9 of 180 samples, min ESS=4.16; **12/24** independently seeded chains had ESS<25. For energy at Tc/L32, median τ=2.216, min ESS=11.78, **4/24** chains had ESS<25. The controlled rule in source required both bootstrap hot-vs-cold mean differences within ±0.08 (|m|) / ±0.12 (E) and ESS≥25 for every chain: although **12/12** mean-difference intervals met the first criterion, **5/12** size/temperature/observable groups failed ESS and the rule was **False**. Gate is exploratory/non-universal and was not independently preregistered before first local run. A single Tc/L32 chain had τ_last=21.61 by original heuristic vs τ_batch20=7.14, showing method/win-size sensitivity. `scripts/mixing_diagnostics.py` independently recomputed **classic unranked** split Rhat: **1.0402** for |m| and **1.0137** for E at Tc/L32, with synthetic adversarial scale/location controls. No proof of mixing/non-mixing. The initial six-chain FSS exponent slopes are **not quantitatively reliable**.

**Actual source hardening on isolated PR #12:** `src/emergence_lab/cli.py` now validates planned seeds and **100 million attempted-spin default budget** before creating output, while preserving legacy L4 seeds; detects rounded-temperature collisions (e.g. 2.269180 vs 2.269190) and size/T aliases. `src/emergence_lab/stats.py` returns **undefined SEM/CI** for exactly zero variance between independent chains rather than artificially perfect precision. `src/emergence_lab/coverage4.py` counts missing intervals as **non-coverage** and records `interval_defined=false`. Added mutation/regression tests, CI successful [37997530526](https://github.com/shaden7/emergence-lab/actions/runs/37997530526), [37997611607](https://github.com/shaden7/emergence-lab/actions/runs/37997611607). All changes are unmerged; historical M4 data unchanged.

**Second negative model:** `src/emergence_lab/ising_1d_control.py` and `configs/ising_1d_control.json`, revision `71f0f3c77e3006e54ee42a1f142335bb9d5c58a0`: interacting 1D periodic nearest-neighbor ferromagnet with **no T>0 critical point**. The exact finite-L energy follows `Z_L=(2cosh(1/T))^L+(2sinh(1/T))^L`; independently checked by direct L8 enumeration. **96 chains, L8/16/24/32, T1.5/Tc2D/3.5, 8 reps, 300 burn+700 sample sweeps, 1,920,000 flips**, local 4.58s/~96MB. [GitHub CI 37998097492](https://github.com/shaden7/emergence-lab/actions/runs/37998097492) **success**, [raw artifact 11648136813](https://github.com/shaden7/emergence-lab/actions/runs/37998097492/artifacts/11648136813): 96/96 raw chain records and all 12 summaries identical to local. At 2D-Tc, 1D Binder U4 L8→L32 falls **0.419→0.029** and χ_abs stays ~0.28–0.39, distinguishing from 2D near Tc (U4 ~0.61, χ_abs increasing with L). This is an expected *control* under known 1D theory, **not emergent geometry**.

**Preserved anomaly and adaptive investigation:** At T3.5 the first 1D run's four L-energy means were all below exact values, with |difference|/between-chain SEM **1.721/1.675/2.734/1.620**. Do not discard or over-interpret uncorrected multiple comparisons. After seeing the discrepancy, an explicitly **adaptive**, distinct-seed longer-chain run was specified (`configs/ising_1d_anomaly_followup.json`; T3.5, 4 L, 8 chains, 1000 burn+10000 sample, 7,040,000 flips; new seed base 2099990101; local 14.97s): signed standardized energy differences approximately **−0.431/−1.943/+0.427/−0.431**. Not a preregistered confirmation; retain both raw experiments. [CI run 37998319268](https://github.com/shaden7/emergence-lab/actions/runs/37998319268) **success** on exact code commit `4f5c434506b9517e8774d3cd35275aaa6df355da`, [raw artifact **11648032310**](https://github.com/shaden7/emergence-lab/actions/runs/37998319268/artifacts/11648032310). All 32 per-chain records and four summary cells match the local run exactly. This is an **adaptive exploratory** replication, not a prospectively independent validation.

**Provenance:** New finite-size/AR1/L4-equilibration/1D/mixing scripts now record Python/NumPy versions and `GIT_SHA` from bounded GitHub CI in result JSON; scripts retain full raw controls and exact seed configurations. Historical Actions artifacts still have finite retention; long-term storage is an open requirement.

**Decision remains NO-GO.** A true next calibration gate needs longer independently seeded L32 trajectories at Tc, robust autocorrelation/window estimates, a modern rank-normalized folded convergence diagnostic, separated warmup & sampling, narrower new-seed coverage uncertainty, quantitative finite-size corrections, reviewed stacked merge #1→#3→#7→#9→#10→#12. **Do not start Phase 1**, deploy to Lightsail, or claim fundamental-physics discoveries.

### CI-cost containment and final review handoff (2026-10-09)

Completed bounded pilots were run successfully and primary artifact IDs/code revisions are documented above. New longer runs must not be triggered by routine documentation pushes: commit `ac9ccc055473b073aeebc639e13c80a7d09f9ddb` changes the combined phase-0 pilot workflow to **manual `workflow_dispatch` only**, on the isolated audit branch or after reviewed merge on `main`. Standard `pytest`, smoke and exact4 control remain in push/PR CI; M4/Burn-in original manual runs retain their own specific branch gates. GitHub Actions runner `timeout-minutes: 5`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`; **no Lightsail/EatSleepFeel interaction**.

**Review tasks, not automatically merged:** human code/methodology review for PRs #1, #3, #7, #9, #10, then draft PR [#12](https://github.com/shaden7/emergence-lab/pull/12), preserving the actual stack; verify full tests on resolved combined main, archive raw JSON durably, repeat L32 critical-T long-chain/warmup separated validation on fresh seeds and the new-seed CI-coverage protocol before choosing GO. Source baseline remains representation-neutral (#5) and literature draft (#8) open. **Decision NO-GO.**

### Durable artifact integrity register and final status (2026-10-09)

[Checksum registry](experiments/phase0-artifact-checksums-20261009.json) records **nine** actually downloaded source JSONs: CI run, Actions artifact ID, pinned code SHA, ZIP member name, and SHA-256 of extracted JSON. The JSON registry is versioned in GitHub; it is **not a durable copy of the raw source data**. The latter must be archived separately before Actions expiration for full long-term provenance. No paid service or new resource was created.

**Last known consolidated decision:** **NO-GO**; Ising calibration **not** declared complete. The draft review branch [PR #12](https://github.com/shaden7/emergence-lab/pull/12) contains source, configs, tests, null controls, all measured uncertainties, quantitative L32 ESS failures, report and research-state updates. PRs #1/#3/#7/#9/#10/#12 require human review in dependency order; no automatic merges on CI alone. Next essential research gate is independent longer critical-L32 and interval-coverage confirmation with preregistered controls and trustworthy ESS.

### Later-pass review and integration status of PR #12 (2026-10-10)

**Status correction:** the 2026-10-09 text above records PRs #1 → #10 as open and asks for human review. Since then PRs #1, #3, #7, #9 and #10 were merged by Director sessions, and `docs/WORKFLOW_POLICY.md` assigns routine review and merge to agents; no human review is required. The historical text is kept unchanged as an audit trail.

**Review (AI-mediated, not independent external review):** core code changes checked — `cli.py` keeps the legacy seed formula but now rejects seed collisions and plans above 100 million spin proposals before writing output (`configs/nightly.json` at 6.1·10⁷ proposals stays within the limit, so the Lightsail cron configuration is unaffected); `stats.py` returns undefined intervals for zero between-chain variance; `coverage4.py` counts undefined intervals as non-covered. New CI steps run only on manual `workflow_dispatch`.

**Independent re-execution (Python 3.13.16, NumPy 2.5.3) on the branch merged with `main`:** all seven pilot commands completed in ≈100 s single-core. Headline values reproduce exactly: L32/Tc |m| median ESS 23.88 and minimum 4.16, prospective gate `False`; exploratory log–log slopes at Tc −0.1224 (|m|) and 1.7141 (χ_abs); 1D control Binder at the 2D Tc 0.419 / 0.177 / 0.110 / 0.029 for L = 8 / 16 / 24 / 32. The burn-in re-run output does not match the registered artifact SHA-256 byte-for-byte (cause not determinable without the artifact; all compared statistics agree to the reported precision).

**Evidence levels after integration:** exact Tc and exponents are *known theory*; slopes, ESS and Binder values are *numerical observations*; agreement of slopes with β/ν = 1/8 and γ/ν = 7/4 is *not* a validated exponent measurement; the NO-GO is a *methodological decision* about tool readiness, not a physics result. No theorem is claimed.

## Interrupted-session recovery protocol (2026-10-10)
- Added an explicit recovery audit to `docs/RESEARCH_LOCK.md` and the `docs/WORKFLOW_POLICY.md` Director cycle. After acquiring a new lease, a Director responding to an interrupted run checks relevant PR/branch heads, unfinished GitHub Actions jobs, logs, artifacts and partially integrated results **before** launching duplicate work.
- An `idle` lease is not proof a ChatGPT session or GitHub Actions experiment finished; an expired lease cannot stop external jobs. Missing run status/artifacts remain unknown, not successes. Findings go to existing PR/issue or research-state handoff, avoiding extra feature PRs.
- Integration: process-only documentation commits `e744d093d2dedcd816c0ab8129f1796e68dcfc04` and `69206ab0c42f11b9035a35189f49448bf29ad58e`. No scientific experiment, CI run, deployment or new liveness-monitor service was performed.
