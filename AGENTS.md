# Emergence Lab — Agent Instructions

## Mission
Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

Long-term ambition: contribute to understanding foundational physics, potentially a deeper account of why spacetime, matter and known physical laws exist. This is a research direction, **not** a claim that such a theory has been found. Benchmark micro-to-macro models are methodological validation, not a restriction of scope to condensed-matter physics.

Start from **specified macroscopic observables and falsifiable tests**, then investigate minimal sufficient or necessary assumptions. Do not claim fundamental physics discoveries from numerical patterns alone.

## Canonical project files
1. `README.md` — how to install, run, deploy.
2. `docs/RESEARCH_STATE.md` — current verified status, findings, next experiments.
3. `docs/research-plan.md` — scientific roadmap and criteria.
4. `docs/deployment.md` — Lightsail deployment boundaries.

Read these files and recent commits before planning changes. Code and test results supersede summaries when they disagree.

## Scientific workflow
- Specify a question, baseline, numerical observable, uncertainty estimate, falsification criterion, and compute budget before launching exploratory batches.
- Use deterministic random seeds and record config, commit SHA, dependencies, and environment with results.
- Separate **proved**, **numerically observed**, **hypothesized**, and **speculative** statements.
- Prevent confirmation bias: include negative controls, independent seeds and holdout tests. Account for autocorrelation and finite-size effects.
- Do not infer a physical breakthrough from a simulation without robust comparison to literature and experimental evidence.
- Prefer formal Lean proofs for precise mathematical claims, never as substitutes for empirical validation.
- Ensure new jobs are resource-bounded and do not interfere with EatSleepFeel.

## Engineering
- Use Python for simulation/analysis, pytest for tests, Lean 4 when justified.
- Small modular changes; run tests and smoke experiments.
- Commit progress and update `docs/RESEARCH_STATE.md` with actual results, limitations, and next steps.
- New conjectures/agent-proposed experiment configurations should go through PR review; no autonomous deployment of unreviewed code.
- No paid LLM API calls without explicit authorization and spending caps.
- Do not store credentials or private SSH keys in Git.

## Infrastructure
- GitHub: https://github.com/shaden7/emergence-lab
- Shared Ubuntu Lightsail instance: 18.158.243.28, 4 GB RAM, 2 vCPUs, 80 GB SSD.
- Deploy through the manual GitHub Actions workflow using GitHub secret LIGHTSAIL_SSH_PRIVATE_KEY.
- Runs under /opt/emergence-lab; maintain isolation from EatSleepFeel and resource limits.
- Research cron configured by successful deployment for 02:00 UTC. Do not assume it is actually installed until deployment succeeds.

## Session handoff
At the beginning, summarize the verified status and propose the smallest high-value next step. At the end, update RESEARCH_STATE.md with what changed, tests/evidence, blockers, and exact next action. Never report an unexecuted deployment or experiment as successful.
