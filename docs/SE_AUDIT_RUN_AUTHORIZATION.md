# SE audit v0.1 once-only run authorization (step 3 of prereg § 6)

**Status:** PROPOSED by Director `rd-claude-20261027T0803Z-5ae580f5` on 2026-10-27, in the PR that adds this file. Until a separately started session's later-pass review gives PASS and the PR merges, **nothing here is authorized**.
- Merging activates the in-code flag (`SE_AUDIT_RUN_AUTHORIZED = True`).
- The run still needs one explicit dispatch of `se-audit-run.yml` that passes the once-only guards.
- This document claims no SE-audit run. To check, look for the release tag `se-audit-run-v1` and its archived evidence.

**Inputs:**
- Design: [`docs/SPECTRAL_SE_AUDIT_PREREGISTRATION.md`](SPECTRAL_SE_AUDIT_PREREGISTRATION.md) v0.1 (PR #55, merge `343be70`).
- Locked implementation: PR #56, merge `bb23e81`; later-pass PASS [here](https://github.com/shaden7/emergence-lab/pull/56#issuecomment-6436824997).
- Decision record: [`docs/S1_METHOD_SCOPE_DECISION.md`](S1_METHOD_SCOPE_DECISION.md).
- S1b precedent: [`docs/S1B_RUN_AUTHORIZATION.md`](S1B_RUN_AUTHORIZATION.md).
- Issue #37.

## 1. Is one SE-audit execution justified?

**Proposed answer: yes, once, at the frozen design.**

- *Question at stake:* does the tree-level delta SE of the annealed CAY window slope at N = 2¹⁴ describe its actual between-batch sampling spread? Under the frozen F(15, 176) rule, R > 1.313 rejects that SE model.
  - The decision record makes this the gate between option B (a symmetric equivalence study using this SE model) and option C (a new estimator).
- *Discrimination:* power of the frozen rule (assumptions, prereg § 4) is 0.44 at ρ = 1.3, 0.81 at ρ = 1.6 and 0.97 at ρ = 2.0. The nominal size is ≈ 0.05.
  - The PR #56 later-pass check reproduced a size of 0.052 through the merged module statistic (1500 synthetic reps).
  - An undetected ρ ≈ 1.3 is an accepted blind spot.
- *Cost:* ≈ 53 CPU-min projected, with a hard stop at 100 CPU-min. One core and 2 GiB, on free GitHub-hosted runner minutes for this public repository. No new spending, no paid API, not Lightsail.
- *The value of each outcome is fixed in advance* (prereg § 2):
  - SE-REJECTED → option C.
  - SE-NOT-REJECTED → option B may be preregistered separately. Wording: "not rejected at 2¹⁴", never "validated".
  - BLOCKED → no classification and no rerun.
  - No outcome authorizes S2 or changes S1 NO-GO, S1b C-INCONCLUSIVE/U-EQUIVALENT or Phase-0 GO.
- *Known weaknesses, accepted rather than resolved:* the audit covers one size only; R is blind to defects shared by all trees; the F level is nominal; the threshold is the frozen literal 1.313 (the exact value is 1.31284), so R in (1.31284, 1.313] reads NOT-REJECTED.

## 2. Host decision

The host is the same as for S1b, and the reasoning is unchanged (S1B_RUN_AUTHORIZATION.md § 2):
- shared Lightsail is excluded;
- the Director cloud sandbox is rejected (no cgroup-v2 quota files and no Docker daemon, re-observed in this session: `ResourceGuard` preflight refuses);
- the run goes on a GitHub-hosted `ubuntu-latest` runner.

The S1b run on that runner class completed cleanly with the same containment ([s1b-run-v1](https://github.com/shaden7/emergence-lab/releases/tag/s1b-run-v1)).

**Residual host risks:**
- CPU speed varies between runners. A budget stop yields BLOCKED, which is a valid preregistered outcome and not a reason to rerun.
- Runner loss is handled as in § 4.

## 3. Execution path

[`.github/workflows/se-audit-run.yml`](../.github/workflows/se-audit-run.yml) runs on dispatch only, from `main` only, with confirmation text `SE-AUDIT-ONCE-2036101901`. Its guard order is pinned by `tests/test_se_audit_run_workflow.py`:

1. confirmation text, hosted runner, clean checkout;
2. `SE_AUDIT_RUN_AUTHORIZED is True` on the dispatched commit;
3. release tag `se-audit-run-v1` absent (once only);
4. full `pytest -q` on the exact commit, then the image build;
5. **create `se-audit-run-v1` as the seed-consumption marker** before any draw;
6. run `scripts/run-se-audit-contained.sh`. Its settings: network none, `--cpus 1`, 2 GiB, zero swap, read-only checkout, single-threaded BLAS, the cgroup CPU watchdog at 100 CPU-min, and a native wall stop at 5,998 s.

**Seed factors.** A full run needs all of the following:
- `SE_AUDIT_RUN_AUTHORIZED = True`;
- `SE_AUDIT_ALLOW_SEEDS=1`. Only the contained script sets this, and only in full mode; engineering mode passes `0`;
- passing the `ResourceGuard` cgroup/network/host-attestation preflight;
- the once-only marker proof. `SE_AUDIT_ONCE_MARKER` must name a non-empty file whose content equals `RUN_URL`. Only the *Consume seeds* step writes it, after creating the release.

This is a cooperative guard against accidents, not a security boundary: an operator could forge the proof file.

**Containment reuse.** `s1b_limits.ResourceGuard` is reused unchanged, including its `S1B_HOST_CLASS=non-lightsail` attestation variable and its S1b-worded messages. Renaming it would touch the archived S1b execution path for a cosmetic gain. The platform-provided `RUNNER_ENVIRONMENT=github-hosted` check is the stronger host signal. This settles PR #56 later-pass note 3.

**CI controls** (general CI, engineering seed base only):
- An *SE-audit engineering containment smoke* runs the real Docker containment with `--contained-engineering --no-controls`. It requires clean resource evidence, 12 trees attempted, all at engineering base 2036101997, and `s2_run_authorized = false`.
- *SE-audit full mode refuses without once-only marker proof* expects exit 2 before `mkdir` or Docker.
- With the flag True, **general CI must never set `SE_AUDIT_ONCE_MARKER` or `SE_AUDIT_ALLOW_SEEDS`**. A structural test enforces that tripwire before any Docker step.
- The S1b forced-abort and OOM probes already exercise the shared `ResourceGuard` and ledger pattern. No SE-specific abort probe is added.

**Trigger.** In the S1b case, Directors' dispatch attempts were refused by tool-permission guards, and the owner pressed *Run workflow* once.
- Unless a Director verifiably can dispatch, the trigger is the same here: after merge, the owner opens *Actions → "SE audit v0.1 locked run (once only, dispatch from main)" → Run workflow* on `main`, with confirmation `SE-AUDIT-ONCE-2036101901`, **once**.
- This is a mechanical trigger, not a review step.

## 4. Archive and abnormal-stop protocol

These rules are identical in substance to S1B_RUN_AUTHORIZATION.md § 4.
- The marker release is created before seeds are touched, and any later dispatch fails closed.
- Each of the following means **incomplete: seeds consumed, BLOCKED, no rerun**:
  - a STARTED attempt without a terminal entry;
  - a missing `report.json`;
  - a manifest stuck at `run_status = STARTED`, for example after an exception outside the caught tuple (PR #56 later-pass note 1);
  - a `resource_stop.json`.
- Packaging and the 90-day workflow artifact always run. Release-asset upload additionally requires proof that this invocation created the marker. It also requires a marker body that binds the current run URL and commit, and then a non-overwriting upload with download re-verification.
- **Admissible for result review only if** all of these hold:
  - exit code 0;
  - `clean_exit` true;
  - no watchdog failure and no `resource_stop.json`;
  - `mode = se_audit`;
  - `run_status` in {FINISHED, BLOCKED};
  - every attempted seed at base 2036101901;
  - `s2_run_authorized` false.
- Admissibility is an engineering gate. The verdict still needs step 4's independently rechecked result note: recompute R from the archived `numeric.csv` against the frozen rule.

## 5. What this change contains

- `SE_AUDIT_RUN_AUTHORIZED = True` in `spectral_s1.py`. The lock tests now cover both directions: the flag without the env gate, and the env gate without the flag. A new test shows that the activated full mode is refused outside containment before `mkdir`, P0 or RNG.
- `scripts/run-se-audit-contained.sh`, `.github/workflows/se-audit-run.yml`, and the two CI steps above.
- `--contained-engineering` for `spectral_se_audit` (engineering mode only).
- `tests/test_se_audit_run_workflow.py`, with structural guards and script-refusal tests run against a stub Docker.
- This record.

## 6. Evidence labels

Everything above is a **process decision plus design arithmetic** that was already reviewed in PRs #55 and #56. It adds no numerical observation, theorem or empirical claim. Statements about the sandbox's capabilities are direct observations of this session's environment only.
