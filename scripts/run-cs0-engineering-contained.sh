#!/bin/sh
# Engineering fixture only; no full-study argument, entropy or authorization.
set -eu
test "$#" -eq 2 || { echo 'usage: run-cs0-engineering-contained.sh sha256:IMAGE_ID ABSOLUTE_NEW_OUTPUT_DIR' >&2; exit 2; }
image=$1
output=$2
case "$image" in sha256:*) ;; *) echo 'Use an immutable image ID' >&2; exit 2;; esac
digest=${image#sha256:}
test "${#digest}" -eq 64 || { echo 'Image ID must contain 64 lowercase hex digits' >&2; exit 2; }
case "$digest" in *[!0-9a-f]*) echo 'Image ID must contain 64 lowercase hex digits' >&2; exit 2;; esac
case "$output" in /*) ;; *) echo 'Output path must be absolute' >&2; exit 2;; esac
test "${CS0_HOST_CLASS:-}" = non-lightsail || { echo 'Verify the non-Lightsail host first' >&2; exit 2; }
root=$(git rev-parse --show-toplevel)
test "$(pwd -P)" = "$root" || { echo 'Run at the checkout top level' >&2; exit 2; }
case "$root$output" in *,*) echo 'Comma in mount path is unsupported' >&2; exit 2;; esac
test -z "$(git status --porcelain --untracked-files=all)" || { echo 'Use a clean reviewed checkout' >&2; exit 2; }
revision=$(git rev-parse HEAD)
# Host anchor precedes Docker; it survives container OOM, timeout or wrapper kill.
python - "$output" "$root" "$image" "$revision" <<'PY'
import json, os, pathlib, sys
output, root = map(pathlib.Path, sys.argv[1:3])
output, root = output.resolve(), root.resolve()
if output == root or root in output.parents:
    raise SystemExit('output must be outside checkout')
output.mkdir(exist_ok=False)
(output / 'payload').mkdir()
record = dict(schema=1, mode='engineering', outcome='INCOMPLETE',
              study_authorized=False, image=sys.argv[3], commit=sys.argv[4],
              container_memory_bytes=1073741824, container_cpu_quota=1,
              container_wall_seconds=30, aggregate_output_cap_enforced=False,
              host_transport_cpu_accounted=False)
with (output / 'envelope.json').open('w') as stream:
    json.dump(record, stream, sort_keys=True); stream.write('\n')
    stream.flush(); os.fsync(stream.fileno())
for directory in (output, output.parent):
    fd = os.open(directory, os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
PY
set +e
# The host log has a per-file cap, not an aggregate artifact cap. If the Docker
# client is killed, the container's PID1 timeout still bounds its lifetime.
(ulimit -f 2048
 docker run --rm --log-driver none --network none --cpus 1 \
  --memory 1g --memory-swap 1g --read-only --pids-limit 64 \
  --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -e HOME=/tmp -e GIT_OPTIONAL_LOCKS=0 \
  -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -e NUMEXPR_NUM_THREADS=1 \
  --mount "type=bind,src=$output/payload,dst=/results" \
  --mount "type=bind,src=$root,dst=/app,readonly" \
  --entrypoint timeout "$image" --signal=KILL 30s \
  python -I -B -X pycache_prefix=/tmp/cs0-launcher-cache -c \
  'import sys; sys.path.insert(0,"/app/src"); from emergence_lab.cs0_engineering import main; sys.exit(main())' \
  --root /app --commit "$revision" --output /results/run
) >"$output/container.log" 2>&1
status=$?
set -e
python - "$output" "$status" <<'PY'
import json, os, pathlib, sys
output = pathlib.Path(sys.argv[1]); path = output / 'envelope.json'
record = json.loads(path.read_text()); record['docker_exit_code'] = int(sys.argv[2])
record['outcome'] = 'INCOMPLETE'
try:
    if record['docker_exit_code'] != 0:
        raise ValueError('container command did not complete successfully')
    inner = json.loads((output / 'payload/run/manifest.json').read_text())
    if not (inner.get('outcome') == 'COMPLETE' and inner.get('mode') == 'engineering'
            and inner.get('study_authorized') is False and inner.get('rows') == 40
            and inner.get('report_verdict') == 'ENGINEERING_ONLY'
            and inner.get('commit') == record['commit']):
        raise ValueError('missing matching engineering completion evidence')
    record['outcome'] = 'ENGINEERING_COMPLETE'
except (OSError, ValueError) as error:
    record['error'] = str(error)
temporary = output / 'envelope.tmp'
with temporary.open('w') as stream:
    json.dump(record, stream, sort_keys=True); stream.write('\n')
    stream.flush(); os.fsync(stream.fileno())
os.replace(temporary, path)
fd = os.open(output, os.O_DIRECTORY)
try: os.fsync(fd)
finally: os.close(fd)
raise SystemExit(0 if record['outcome'] == 'ENGINEERING_COMPLETE' else 2)
PY
