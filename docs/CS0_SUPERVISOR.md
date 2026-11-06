# CS0 supervised execution building block

Status: engineering component only, not a gated runner or run authorization.
No CS0 seed entropy is selected by this module and no study data were drawn.

`emergence_lab.cs0_supervisor.supervise` runs a trusted **single-process** worker
on Linux. It refuses dirty/untracked checkouts and requires an exact 40-character
HEAD pin. Output must be outside the checkout. An atomically replaced, fsynced
INCOMPLETE manifest precedes provenance validation and child startup. The parent
captures the worker's combined stdout/stderr through a pipe, truncates at the
configured byte limit, hashes retained bytes, and fsyncs the artifact.

Worker CPU is kernel-limited with RLIMIT_CPU; virtual memory is kernel-limited
with RLIMIT_AS, conservatively restricting RSS as well. File writes and core
dumps have zero size limits. Wall time is supervised, and the process group is
killed on exit. The final record includes child CPU, peak RSS and exit status.
COMPLETE describes engineering execution only; it is never a scientific PASS.

## Limits that block full study authorization

- The worker must not fork. This API is for reviewed trusted code, not a sandbox
  for arbitrary commands. CPU and memory limits are per-process; they do not
  bound a malicious or forking process tree. File-size limits do not prevent
  zero-length files or directory changes.
- The byte limit applies to captured worker output only. The future runner must
  reserve and account for manifest, configuration, CSV and report overhead under
  the preregistered 50 MB aggregate cap.
- The future runner must budget supervisor/preflight CPU under the aggregate
  600-second cap, leaving an explicit margin before launching the worker.
- A worker can be killed while the parent still writes a final checkpoint.
  A killed parent leaves its last durable INCOMPLETE record; a host/filesystem
  failure cannot guarantee successful persistence. No automatic retry exists.
- This component does not verify Python module resolution, freeze entropy,
  execute the study grid, recheck stored pair counts, or evaluate G0–G3. Those
  are required before any CS0 execution authorization.

## Engineering checks

`PYTHONPATH=src pytest -q tests/test_cs0_supervisor.py` exercises a temporary clean
Git checkout, exact output digest, dirty/untracked/wrong-revision refusal,
output flood truncation, wall/CPU/memory stops, file-write rejection and invalid
setup. These are deterministic infrastructure fixtures, not calibration data.

Next: wire a no-fork CS0 worker and independent pair-count recheck into a complete
runner, add aggregate accounting and module-resolution checks, then obtain a
later-pass exact-commit review before freezing any run entropy. Do not infer
that section 6 of the preregistration has been satisfied by this component.
