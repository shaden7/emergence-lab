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

Linux `PR_SET_PDEATHSIG(SIGKILL)` now terminates the **direct worker** if the
launching supervisor dies, including SIGKILL. A parent-PID check after arming
the signal closes the death-before-registration race. Registration failure
refuses worker execution. The caller must be single-threaded (`preexec_fn`);
the trusted worker must not clear the signal, fork or change credentials.
This is not containment of an arbitrary process tree. A killed supervisor
cannot finalize accounting: its durable record stays INCOMPLETE.

On output EOF the supervisor unregisters the pipe and waits with a bounded
timeout for exit or wall-limit expiry. An early output close therefore does
not cause a CPU busy loop or remove the wall limit.

## Limits that block full study authorization

- The worker must not fork. This API is for reviewed trusted code, not a sandbox
  for arbitrary commands. CPU and memory limits are per-process; they do not
  bound a malicious or forking process tree. File-size limits do not prevent
  zero-length files or directory changes.
- The generic supervisor's chosen byte limit applies to captured worker output.
  The separate engineering caller now reserves bounded metadata/CSV/report and
  atomic-copy slots (docs/CS0_ARTIFACT_BUDGET.md). This does not authorize the
  full runner or extend that fixed bound to arbitrary supervisor commands.
- The future runner must budget supervisor/preflight CPU under the aggregate
  600-second cap, leaving an explicit margin before launching the worker.
- A worker can be killed while the parent still writes a final checkpoint.
  A killed parent leaves its last durable INCOMPLETE record; a host/filesystem
  failure cannot guarantee successful persistence. No automatic retry exists.
- This component does not verify Python module resolution, freeze entropy,
  execute the study grid, recheck stored pair counts, or evaluate G0–G3. Those
  are required before any CS0 execution authorization.
- Git HEAD/status checks are not byte-exact executed-source verification:
  ignored Python files/bytecode and index flags can hide source changes.
  The future reviewed runner must verify module resolution and source bytes.

## Engineering checks

`PYTHONPATH=src pytest -q tests/test_cs0_supervisor.py` exercises a temporary clean
Git checkout, exact output digest, dirty/untracked/wrong-revision refusal,
output flood truncation, wall/CPU/memory stops, file-write rejection and invalid
setup. These are deterministic infrastructure fixtures, not calibration data.
Real SIGKILL/SIGTERM supervisor-death checks adopt and reap the worker in the
test harness, require SIGKILL termination, and check the durable INCOMPLETE
manifest. A mismatched-parent fixture covers the registration race. Early-EOF
fixtures check low supervisor CPU and continued wall-limit enforcement.

Next: wire a no-fork CS0 worker and independent pair-count recheck into a complete
runner, add aggregate accounting and module-resolution checks, then obtain a
later-pass exact-commit review before freezing any run entropy. Do not infer
that section 6 of the preregistration has been satisfied by this component.
