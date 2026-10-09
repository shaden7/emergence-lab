# Lightsail deployment

This repository includes a manually triggered workflow: **Actions → Deploy to Lightsail → Run workflow**.

Requirements:
- Repository Actions secret `LIGHTSAIL_SSH_PRIVATE_KEY` containing a private key authorized for the default Ubuntu account on 18.158.243.28.
- The `lightsail` GitHub Actions environment must be configured or created; configure required reviewers if desired.
- The server must already have Docker Engine with Compose v2, git, cron and passwordless sudo for the Ubuntu administrator.
- TCP port 22 must be reachable from GitHub-hosted Actions runners (allowlisting a stable IP is not possible with standard runners).
- The deploy initializes only `/opt/emergence-lab`, a namespaced Docker Compose project, and `/etc/cron.d/emergence-lab`. It does not restart other application containers.
- Deployment is **not** automatically triggered by commits; the operator must trigger it manually.

A successful deployment builds the Docker image, executes one smoke test and installs a daily **02:00 UTC** cron entry. Scientific output is stored on the instance in `/opt/emergence-lab/results/`.

Security caveat: the workflow bootstraps SSH host trust using `ssh-keyscan`. For stronger host identity validation, replace this with a separately verified server SSH host key fingerprint, recorded in a dedicated GitHub secret. Do not put the SSH *private* key into git.

Cloud compute is billed according to Lightsail's plan, but ongoing workloads can consume CPU burst capacity and impact the other application. Watch memory, CPU credits, disk utilization and API latency. The server processes will not use LLM APIs unless separately configured.
