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

## Status not yet verified here
- Lightsail deployment was started by the operator, but its final outcome has not been checked in this update.
- Nightly runs may therefore not be active yet.
- No robust error estimates or finite-size scaling analysis has been implemented.
- No Lean integration or autonomous LLM hypothesis generator exists.

## Scientific cautions
Monte Carlo samples are autocorrelated; the initial averages do not demonstrate a phase transition or novel physical findings. The infinite-lattice Ising benchmark critical temperature is 2/log(1+sqrt(2)) in units J=k_B=1.

## Next priority
1. Check GitHub Actions Lightsail deploy outcome and remote smoke-test manifest; avoid changes to unrelated services.
2. Implement error bars accounting for autocorrelation, finite-size scaling, and visual plots of magnetization/energy vs. temperature.
3. Build a benchmark evaluation report and independent-seed comparison.
4. Only then prototype emergent geometry/causal structure models and Lean statements.

## Handoff requirements
After each meaningful research iteration, record: question, exact commit and config, computational resource budget, observed results, uncertainty and negative controls, scientifically supported conclusion, limitations, and next experiment. Keep large raw result files in versioned artifact storage rather than bloating Git history.
