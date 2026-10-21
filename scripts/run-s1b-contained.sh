#!/bin/sh
# Reviewed/activated full runs require the once-only marker proof from s1b-run.yml.
# Without the proof, full mode exits before Docker; normal CI must never forge it.
# Build the existing Dockerfile first; pass an immutable local image ID (sha256:...).
set -eu
test "$#" -ge 2 && test "$#" -le 3 || { echo 'usage: run-s1b-contained.sh sha256:IMAGE_ID ABSOLUTE_NEW_OUTPUT_DIR [engineering]' >&2; exit 2; }
mode=s1b
if test "$#" -eq 3; then
  test "$3" = engineering || { echo 'Third argument must be engineering' >&2; exit 2; }
  mode=engineering
fi
case "$1" in sha256:*) ;; *) echo 'Use an immutable image ID' >&2; exit 2;; esac
case "$2" in /*) ;; *) echo 'Output path must be absolute' >&2; exit 2;; esac
test ! -e "$2" || { echo 'Refusing existing output directory' >&2; exit 2; }
# Docker creates no new infrastructure. The operator must verify this is NOT Lightsail.
test "${S1B_HOST_CLASS:-}" = non-lightsail || { echo 'Verify the non-Lightsail host first' >&2; exit 2; }
# Third factor (besides S1B_RUN_AUTHORIZED and S1B_ALLOW_SEEDS): a full run starts only inside the
# s1b-run.yml invocation that created the once-only release marker, whose proof file holds RUN_URL.
if test "$mode" = s1b; then
  test -n "${RUN_URL:-}" && test -s "${S1B_ONCE_MARKER:-/nonexistent}" \
    && test "$(cat "$S1B_ONCE_MARKER")" = "$RUN_URL" \
    || { echo 'Full S1b requires the once-only marker proof written by s1b-run.yml' >&2; exit 2; }
fi
test -z "$(git status --porcelain)" || { echo 'Use a clean reviewed checkout' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir "$2"
if test "$mode" = engineering; then
  set -- "$1" "$2" --mode engineering --contained-engineering --no-controls
  wall_limit=118s
else
  set -- "$1" "$2" --mode s1b
  wall_limit=11998s
fi
image=$1
output=$2
shift 2
docker run --rm --network none --cpus 1 --memory 2g --memory-swap 2g \
  --read-only --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -e S1B_ALLOW_SEEDS=1 -e S1B_HOST_CLASS=non-lightsail \
  -e GIT_SHA="$revision" -e PYTHONPATH=/app/src \
  -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -e NUMEXPR_NUM_THREADS=1 \
  --mount "type=bind,src=$output,dst=/results" \
  --mount "type=bind,src=$(pwd),dst=/app,readonly" \
  --entrypoint timeout "$image" --signal=KILL "$wall_limit" \
  python -m emergence_lab.spectral_s1b --output /results/run "$@"
