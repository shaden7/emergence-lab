#!/bin/sh
# GitHub Actions only, on its disposable hosted Docker runner, NOT Lightsail.
# Exercise kernel OOM and unconditional SIGKILL after an fsynced engineering
# attempt, then prove the result is incomplete and the output cannot be reused.
set -eu
test "$#" -eq 2 || { echo 'usage: test-s1b-aborts.sh sha256:IMAGE_ID ABS_OUTPUT_ROOT' >&2; exit 2; }
image=$1
root=$2
case "$image" in sha256:*) ;; *) exit 2;; esac
case "$root" in /*) ;; *) exit 2;; esac
test "${S1B_HOST_CLASS:-}" = non-lightsail || { echo 'CI-only non-Lightsail host required' >&2; exit 2; }
revision=$(git rev-parse HEAD)
for mode in sigkill oom; do
  base="$root/$mode"
  mkdir -p "$base"
  name="s1b-abort-$mode-${GITHUB_RUN_ID:-manual}-$$"
  if test "$mode" = oom; then
    memory=256m
  else
    memory=2g
  fi
  # No --rm: Docker's OOMKilled state must be captured before removal.
  set +e
  timeout 30s docker run --name "$name" --network none --cpus 1 \
    --memory "$memory" --memory-swap "$memory" \
    --read-only --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges \
    --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=64m \
    -e S1B_HOST_CLASS=non-lightsail -e GIT_SHA="$revision" -e PYTHONPATH=/app/src \
    -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -e NUMEXPR_NUM_THREADS=1 \
    --mount "type=bind,src=$base,dst=/results" \
    --mount "type=bind,src=$(pwd),dst=/app,readonly" \
    --entrypoint python "$image" /app/scripts/s1b_abort_probe.py "$mode" /results/run
  rc=$?
  set -e
  oom_state=$(docker inspect --format '{{.State.OOMKilled}}' "$name")
  docker rm "$name" >/dev/null
  echo "S1b $mode: docker_rc=$rc, oom_killed=$oom_state"
  # 137 is SIGKILL; Docker's OOMKilled distinguishes kernel memory killing
  # from our intentional non-OOM SIGKILL. timeout(1) instead reports 124.
  test "$rc" -eq 137 || { echo "Expected SIGKILL (137), received $rc" >&2; exit 1; }
  # Some Docker/runner combinations also report OOMKilled=true for an
  # explicit PID-1 SIGKILL. The flag is not a trustworthy negative control.
  # For the OOM path require it *positively* in addition to the actual
  # memory-exhaustion fault and exit 137. The SIGKILL path checks only 137.
  if test "$mode" = oom; then
    test "$oom_state" = true || { echo 'Expected kernel OOMKilled=true' >&2; exit 1; }
  fi
  python - "$base/run" "$mode" <<'PY'
import json
from pathlib import Path
import sys

path, mode = Path(sys.argv[1]), sys.argv[2]
events = [json.loads(line) for line in (path/'attempts.jsonl').read_text().splitlines()]
manifest = json.loads((path/'manifest.json').read_text())
assert len(events) == 1 and events[0]['status'] == 'STARTED', events
assert events[0]['seed'][0] == 2036101797
assert manifest['run_status'] == 'STARTED'
assert manifest['seed_tuples_attempted'] == [events[0]['seed']]
assert not (path/'resource_evidence.json').exists()
assert not (path/'report.json').exists()
assert not (path/'sources.jsonl').exists()
print(f'S1b {mode}: fsynced STARTED, no terminal run/evidence/source outputs; partial data only')
PY
  # The real CLI must fail closed on the consumed output directory. No seed
  # may be redrawn on automatic retries.
  set +e
  refusal=$(python -m emergence_lab.spectral_s1b --mode engineering --no-controls --output "$base/run" 2>&1)
  refusal_rc=$?
  set -e
  test "$refusal_rc" -ne 0 || { echo "S1b $mode: unsafe output reuse was allowed" >&2; exit 1; }
  echo "$refusal" | grep -q FileExistsError || {
    echo "S1b $mode: restart failed for an unrelated reason, not consumed-output refusal" >&2
    echo "$refusal" >&2
    exit 1
  }
done
echo "S1b SIGKILL and kernel-OOM containment PASS (engineering-only)"
