# Emergence Lab

Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

Our long-term goal is to explore foundational physics, not merely conventional microscopic phenomena. Initial benchmarks such as the Ising model validate our research methods; **we do not claim to have discovered a fundamental theory of physics**.

For the project's broader scientific ambition, research questions and evidence standards, see the [scientific overview](docs/OVERVIEW.md). Agent working rules are in [AGENTS.md](AGENTS.md), with GitHub-authoritative [workflow and autonomous review policy](docs/WORKFLOW_POLICY.md) and the [Research Director protocol](docs/RESEARCH_DIRECTOR.md). The latest verified work is recorded in [Research State](docs/RESEARCH_STATE.md).

## First experiment: Ising model

A 2D ferromagnetic Ising lattice with periodic boundaries, Metropolis updates, fixed random seeds, energy density and absolute magnetization. The known infinite-lattice transition temperature is `2 / log(1+sqrt(2)) ≈ 2.269185` for `J=k_B=1`. Finite lattices require finite-size scaling and uncertainty analysis before quantitative conclusions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q
emergence-lab --config configs/smoke.json --output results
```

## Run with Docker

```bash
mkdir -p results
sudo chown 10001:10001 results
sudo docker compose build
sudo docker compose run --rm emergence-lab --config configs/smoke.json --output /results/smoke
```

The Compose service is capped at 0.5 vCPU and 1.5 GiB RAM. Lightsail CPU-burst credits still limit sustained performance. Running this alongside other apps can affect their responsiveness.

## Deploy to Lightsail

A **manual** GitHub Actions workflow deploys to Ubuntu on `18.158.243.28` using the existing repository secret `LIGHTSAIL_SSH_PRIVATE_KEY`.

See [deployment instructions](docs/deployment.md). Open **Actions → Deploy to Lightsail → Run workflow** after verifying SSH and the Docker prerequisites. A successful run builds the project, verifies a smoke experiment, and installs the 02:00 UTC cron job. It does not touch EatSleepFeel.

## Exclusive Research Director sessions

Research Director invocations (manual or scheduled) coordinate through the independent `coordination/research-lock` GitHub branch. The operational [exclusive lease protocol](docs/RESEARCH_LOCK.md), including guarded atomic acquisition, heartbeat, two-hour crash recovery and guarded release, is binding via [AGENTS.md](AGENTS.md) and [workflow policy](docs/WORKFLOW_POLICY.md) on `main`. This lease serializes cooperating sessions; it does not launch new ChatGPT sessions or change their minimum hourly scheduling interval. The Lightsail nightly cron is separate.

## Research safeguards

- The deterministic Monte Carlo implementation is a reference system, not evidence for new physics.
- Samples are autocorrelated and v0.1 does **not** calculate confidence intervals.
- Next: finite-size scaling, error bars, distinct baselines, and explicit falsification criteria.
- No AI API integration, automatic theory generation or Lean formalization is implemented yet.

See [research plan](docs/research-plan.md).
