# S1b run authorization record (PROPOSED, not granted)

**Status:** proposed by Director `rd-claude-20261018T0704Z-356d121a6b25` on 2026-10-18.
**This record does not authorize a run.** `spectral_s1.S1B_RUN_AUTHORIZED` stays
`False`; no S1b graph, source or bootstrap seed has been drawn. The decision
becomes effective only after (1) a separate later-pass review merges this record
and its workflow, and (2) a further reviewed activation commit flips the lock.

Inputs: S1b v0.2 design ([`docs/SPECTRAL_S1B_PREREGISTRATION.md`](SPECTRAL_S1B_PREREGISTRATION.md),
PR #48, merge `4614500`), locked implementation (PR #49, merge `7487f0c`),
abort/OOM CI evidence ([run 39086327672](https://github.com/shaden7/emergence-lab/actions/runs/39086327672)),
Issue #37.

## 1. Is one S1b execution justified?

**Proposed answer: yes, once, at the fixed design.**

- *Question at stake:* is the CAY larger-minus-smaller spectral slope difference
  at W = 128–1024 seen in the S1 pilot (+0.071, SE 0.029; archived numeric
  observation, PR #47) a material size effect `D > +0.03`, or not? This decides
  whether the S1 estimator can be used for size-stable calibration on CAY at all
  (Issue #37 asks whether short-scale dimensional reduction is robust or an
  estimator artifact).
- *Discrimination:* under the design's plug-in assumptions, P(material positive)
  is ≈ 0.76 at D = 0.07, ≈ 0.08 at D = 0.035, ≈ 0.0003 at D = 0 (assumption-
  dependent design arithmetic, PR #48 review; not a coverage guarantee).
- *Cost:* ~130 CPU-min projected, 200 CPU-min hard stop, one core, 2 GiB, free
  public-repository GitHub-hosted runner minutes. No new spending.
- *Value of each outcome is fixed in advance* (preregistration outcome rules);
  nondetection does **not** demonstrate equivalence, UST is descriptive only,
  and no outcome authorizes S2.
- *Known weaknesses accepted, not resolved:* heavy tails and fixed-n Welch
  calibration, completion/reliability-screen selection, winner's curse from the
  pilot estimate, modest power near the margin, unmeasured CAY 2^14 cost. These
  limit the inferential strength of any verdict; they are reasons for cautious
  labels, not for indefinitely withholding a cheap, preregistered test.

## 2. Host decision

| Candidate | Verdict | Evidence |
| --- | --- | --- |
| Shared Lightsail | **Excluded** | AGENTS.md / preregistration; would compete with EatSleepFeel |
| Director cloud sandbox (used for the S1 pilot) | **Rejected for S1b** | Checked 2026-10-18 07:0xZ in this session: cgroup v1 hierarchy (no `/sys/fs/cgroup/cpu.max`, `memory.max`, `cgroup.controllers`), Docker CLI present but no daemon socket, 2 vCPU / 8 GiB, container reclaimed after inactivity. `s1b_limits.preflight` requires cgroup-v2 quota/memory/swap files, so the guard would refuse; a ~3.3 h run also outlives an hourly session. |
| GitHub-hosted `ubuntu-latest` runner | **Proposed host** | Disposable VM, never Lightsail by construction; `RUNNER_ENVIRONMENT=github-hosted` is checked by the workflow (a platform-provided value, stronger than the bare `S1B_HOST_CLASS` operator attestation, though still not hardware attestation). The same runner class passed the real contained engineering smoke, SIGKILL and cgroup-OOM probes on `51ec5a9` (CI 39086327672). 6 h job ceiling > 200 min wall stop. |

Residual host risks: runner CPU model varies between jobs, so CPU-min per tree
may differ from the sandbox-measured projection (a budget STOP then yields
BLOCKED, which is a valid, preregistered outcome, not a reason to rerun);
hosted-runner loss mid-run is possible (handled in § 4).

## 3. Execution path

[`.github/workflows/s1b-run.yml`](../.github/workflows/s1b-run.yml), dispatch only,
`main` only, confirmation text `S1B-ONCE-2036101701`. Guard order (pinned by
`tests/test_s1b_run_workflow.py`):

1. confirmation text, hosted runner, clean checkout;
2. `S1B_RUN_AUTHORIZED is True` on the dispatched commit (fails today);
3. release tag `s1b-run-v1` absent (once-only);
4. full `pytest -q` on the exact commit and image build;
5. **create `s1b-run-v1` as the seed-consumption marker** before any draw;
6. `scripts/run-s1b-contained.sh` (network none, `--cpus 1`, 2 GiB, zero swap,
   read-only checkout, single-threaded BLAS, cgroup CPU watchdog, native
   11,998 s wall stop).

Trigger: Directors have so far lacked `actions: write` (dispatch returned 403,
2026-10-17). Until a Director verifies it can dispatch, the owner may press
*Run workflow* once after activation; this is a mechanical trigger, not a review
step. If neither is available, the activation PR may instead add a one-time
`push: main` path trigger on its own activation file (the pattern used by
`archive-phase0-evidence.yml`); that choice must be reviewed in the activation PR.

**CI negative control (this PR):** `ci.yml` runs the full-mode contained entry on
the hosted runner and requires refusal with the seed-lock message, with no
`run/` directory or other output created. This tests the lock on the proposed
host along the exact script path; it does not test a full run.

## 4. Archive and abnormal-stop protocol

- The marker release is created before seeds are touched; any later dispatch
  fails closed. A STARTED-without-terminal attempt ledger, a missing result or a
  `resource_stop.json` means **incomplete, seeds consumed, no rerun**.
- Packaging, artifact upload (90 days) and non-overwriting release-asset upload
  with download re-verification run `if: always()`, so watchdog, OOM or timeout
  stops still archive whatever exists. Runner loss before packaging leaves only
  the marker: recorded as *incomplete, no evidence*, not retried.
- A result is admissible for analysis review only with exit code 0,
  `resource_evidence.json` `clean_exit=true`, no watchdog failure, no
  `resource_stop.json`, `mode=s1b` (final workflow step). Admissibility is an
  engineering gate; the verdict itself still requires a later-pass review of the
  archived CSV against the frozen rules, as for the S1 pilot (PR #47).

## 5. What activation must contain (separate reviewed PR)

- flip `S1B_RUN_AUTHORIZED = True` and update the tests that pin `False`
  (`tests/test_spectral_s1b.py`, `tests/test_s1b_run_workflow.py`, the abort
  probe precondition, the CI lock negative control) so that engineering seeds
  remain disjoint and the abort probes still never touch scientific seeds;
- keep `S1B_ALLOW_SEEDS=1` set only inside `run-s1b-contained.sh`;
- update `configs/spectral_s1b.json` `status` text;
- record the reviewer's PASS and this record's accepted host decision.

## 6. Evidence labels

Everything above is a **process decision and design arithmetic**. No new
numerical observation, theorem or empirical claim. Sandbox capability facts are
direct observations of this session's environment only.
