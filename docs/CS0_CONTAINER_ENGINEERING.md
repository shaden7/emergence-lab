# CS0 outer container engineering envelope

Status: engineering fixture only, not CS0 full-run authorization or section 6
compliance. No full-study entropy or orders are used.

Build the separate `Dockerfile.cs0` image, resolve its immutable local image ID,
then run from a clean reviewed checkout on a verified non-Lightsail host:

```sh
docker build -f Dockerfile.cs0 -t cs0-engineering .
docker image inspect cs0-engineering --format '{{.Id}}'
CS0_HOST_CLASS=non-lightsail sh scripts/run-cs0-engineering-contained.sh \
  sha256:EXACT_64_LOWERCASE_HEX_IMAGE_ID /absolute/new/output
```

The script accepts exactly two arguments and supplies only the fixed 40-row
engineering launcher. Full-mode/entropy arguments are refused before Docker.
It requires a full immutable image ID, a clean checkout top level and new output
outside the repository. Mount paths containing commas are refused.

The whole in-container pipeline (launcher, Git/source checks, worker and stored-R
recheck) receives Docker CPU quota 1, 1 GiB cgroup memory with no additional swap,
no network, read-only root/source, PID limit 64, dropped capabilities and no new
privileges. Its PID1 is GNU timeout with a 30-second SIGKILL deadline; exiting
PID1 terminates the container namespace. This wall/quota combination is a bounded
engineering envelope, not measured aggregate CPU evidence for a full study.

A fsynced host `envelope.json` starts INCOMPLETE before Docker. Only a successful
container exit plus matching inner engineering manifest changes it to
ENGINEERING_COMPLETE. All records remain `study_authorized=false`. The bind
mount exposes only `output/payload` as `/results`; the host anchor and client log
remain outside the container's writable mount. Inner artifacts are retained under
`payload/run`. The finalizer resets its outcome to INCOMPLETE before checking
new evidence, so stale success cannot survive a failed command. The bind
output retains inner checkpoints/raw files on container failure; a killed host
wrapper leaves its durable INCOMPLETE anchor. If the client or wrapper is killed,
the container may remain active until its own 30-second deadline. Host/daemon or
filesystem failure cannot guarantee persistence or termination.

There is **no aggregate output cap** on the bind mount. The host client log has a
per-file shell limit; this is not a disk quota. No host transport CPU, aggregate
RSS measurement, Docker daemon overhead, image build cost or total output
accounting is claimed. The image/runtime and Docker daemon are trusted. These
gaps still block full-run authorization.

Local refusal/argument/checkpoint tests use a fake Docker executable and establish
only wrapper behavior. Actual cgroup enforcement, OOM, namespace cleanup and
timeout behavior require real Docker CI probes before being called verified.
CI builds the dedicated image, executes the actual fixed engineering wrapper,
then runs `scripts/test-cs0-container-limits.py` on disposable named containers
with the same memory/quota/PID/security flags. The probes read cgroup-v2 limits,
exercise a one-second PID1 timeout with a sleeping descendant, and request a
2 GiB bytearray inside the 1 GiB cgroup. OOM must be confirmed by Docker's
`State.OOMKilled`; an exit code alone is insufficient. Probe containers are
removed explicitly, and their report/checkpoints are collected even on failure.
These are generic engineering fixtures, not CS0 observations. A passing result
does not establish aggregate disk limits or total host-side compute accounting.
No deployment, paid service, Lightsail or EatSleepFeel change is included.
