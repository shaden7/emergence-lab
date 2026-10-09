# Research State

Last handoff update: 2026-10-09.

## Mission
Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

The Ising benchmark is a calibration step. The long-term question encompasses foundational spacetime, matter, interactions, and the principles that might give rise to them; candidate models still require rigorous mathematical and empirical evaluation.

## Documentation iteration (2026-10-09)
- Added `docs/OVERVIEW.md` to separate foundational-physics vision, specific research questions, validation methodology and roadmap.
- Refined `AGENTS.md` to require top-down observables, controls, evidence levels, bounded experiments, and reproducible session handoffs.
- Documentation-only change; no new experiment, proof, or deployment verification resulted from this iteration.

## Research process iteration (proposed PR, 2026-10-09)
- Documented a sequential hourly **Research Director** model in `docs/RESEARCH_DIRECTOR.md`, with optional specialized review only when delegation is actually available.
- Added deconfliction guidance: inspect open issues/PRs, prefer continuing existing work, use isolated branches, do not treat repository files as concurrency locks.
- Added evidence and milestone-review checklists, including an independent skepticism gate for novel claims.
- This is **workflow documentation only on a review branch**. It does not update the scheduled ChatGPT automation, verify the Lightsail deployment, run experiments, implement subagents, or introduce new scientific findings.
- Proposed adoption: review and merge the PR, then ensure the hourly automation follows the linked protocol.

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
