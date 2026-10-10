#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p results
# Each run is archived under a timestamped directory, never overwriting older research results.
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "results/$stamp"
export GIT_SHA="$(git rev-parse HEAD)"
flock -n /tmp/emergence-lab.lock timeout --signal=TERM 7200 docker compose run --rm emergence-lab --config configs/nightly.json --output "/results/$stamp"
