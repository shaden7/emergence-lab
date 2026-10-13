# Exclusive Research Director lease (binding operating protocol)

This is the concrete coordination protocol for **interactive and scheduled** Emergence Lab Directors. Its authority comes from `AGENTS.md` and `docs/WORKFLOW_POLICY.md` on `main`; the mutable lock **does not** live on `main`.

## Canonical lock record

- Dedicated persistent branch: `coordination/research-lock`.
- Its tree contains **only** `lease.json` (schema 1) at the root. Do not copy repository files onto this branch: GitHub reads push-triggered workflows from the pushed commit, so any `.github/workflows` file on the lock branch makes every lease commit run CI (observed 2026-10-10: lease commits with a full repository tree triggered the test workflow; a lease-only tree did not).
- `status`: `idle` or `running`; `owner` and `leaseId` uniquely identify the invocation.
- `acquiredAt`, `heartbeatAt`, `expiresAt`: UTC ISO 8601 timestamps (`Z`).
- `task` gives an informative short work description; `previousOwner` is informational.
- This branch is never merged, rebased, reset, deleted, or used as a working/PR branch. GitHub is the shared serialization service; do not rely on a file in a feature branch.

## Required entry protocol — fail closed

1. Read all required project policy files on `main`. Read `refs/heads/coordination/research-lock` via the GitHub connector, obtaining HEAD commit SHA **H**. Read `lease.json` from **that same commit** (not default `main`), and its tree SHA. Avoid time-of-check/time-of-use errors by using the same snapshot.
2. If `status=running` and `expiresAt` is strictly in the future, **do not do any research-side mutation**. Report the current owner/expiry and end the invocation. Do not create a PR, comment, deploy, start remote work, merge, or change the lock. Read-only diagnosis is allowed, but do not pretend to be the sole active Director.
3. If `status=idle`, or a running lease is expired, prepare a new record with `status=running`, a fresh **unique per-invocation owner and unpredictable leaseId**, `acquiredAt=now UTC`, `heartbeatAt=now UTC`, and `expiresAt=now+2 hours`. On takeover of an expired lease, record `previousOwner`. Never reuse a previous lease ID.
4. Construct a Git tree based on H's **tree SHA**, replacing only `lease.json` (GitHub `create_tree`, mode `100644`, type `blob`); if H's tree contains anything besides `lease.json`, the candidate tree may instead contain only the new `lease.json` (one-time pruning to the canonical form above, recorded in the commit message); create a Git commit with **parent H** and that tree (`create_commit`).
5. Atomically move ONLY `coordination/research-lock` to the candidate commit using GitHub `update_ref` with `branch_name="coordination/research-lock"`, `sha=<candidate commit SHA>`, `expected_sha=H` and `force=true` (**force-with-lease**, never unguarded force). Only one contender using the same H may succeed. Never use `force=true` on `main`.
6. Read back the branch HEAD and its lease from the resulting HEAD commit. Work may begin only when the observed `leaseId` equals this invocation's lease ID, `status=running`, and the expiry is still in the future. If an API call errors (including ambiguous connector/GraphQL errors), do not infer success or retry blind: reread HEAD and verify the lease ID. On uncertainty, fail closed.
7. If acquisition fails because the ref changed, **do not immediately retry the takeover in a busy loop**. Read and respect the winner's current lease; the next scheduled run may try again.

## Connector failures: reconcile first, bounded retry only for transient errors

The lease is a **fail-closed safety gate**, not an invitation to evade connector permissions or safety checks. A write API error is not proof that nothing happened. Treat `create_tree`, `create_commit`, `update_ref`, heartbeat, and release separately, and classify the failure **before** considering recovery.

1. **Always reconcile with GitHub (read only).** Re-read the coordination ref and `lease.json` from that exact HEAD. If the HEAD is this invocation's intended commit and the observed `leaseId`/status/expiry match, acquisition succeeded despite an ambiguous tool response; continue without replaying the write. If another valid lease exists, **stop**. If GitHub cannot be read or results disagree, **stop**. Never use a locally cached lease as ownership evidence.
2. **Transient, explicitly retryable failure only.** If the connector reports a temporary network/timeout error, HTTP 5xx, or an HTTP 429 expressly permitting a later retry (without a separate authorization/safety denial), and the reconciled HEAD is still the expected **H** with a still-acquirable idle/expired lease, allow **at most one retry in this invocation**. Rebuild the candidate from the freshly re-read HEAD/tree and repeat the normal `create_tree` → `create_commit` → expected-SHA `update_ref` → read-back verification sequence. Apply the same rule during renew/release only while ownership remains verified. Do not repeat an uncertain `update_ref` blindly.
3. **Explicit denial: no retry or workaround.** A connector message saying `blocked by safety checks`, permission denied, 401/403, a policy refusal, or a rate-limit response not explicitly safe to retry is **not** a transient error for this purpose. Do **not** resubmit the denied call, alter payloads to get past the block, switch endpoints/identities, or attempt an alternative write mechanism to circumvent it. Reconcile the HEAD read-only; if ownership was not verified, end with a concise blocker report. A later independently started session can execute its own normal entry protocol, not inherit this invocation's lease.
4. **A changed or ambiguous HEAD ends the attempt.** Even if the new lease looks idle, do not race or loop for ownership within this invocation. Report the current observed status and let a later session reassess. An orphaned candidate blob/tree/commit created before a denied or failed ref update **does not constitute a lock**.
5. **Bounded reporting.** Record the failed stage, error class, observed ref and lease state, whether the one permitted transient retry was used, and the final `owned` / `not owned` verdict. Never claim a retry succeeded without the step-6 read-back check. Do not include secrets or credentials in the report. If a lease was actually acquired, release it using the standard guarded protocol on exit.

**Observed motivating incident (2026-10-13):** a `create_tree` call succeeded, the following `create_commit` was explicitly blocked by the connector's safety checks, and the coordination ref did not move. A separate later invocation successfully acquired and released a lease using the canonical CAS sequence. The earlier block's root cause is unknown; the later success does **not** justify bypassing an explicit denial.

## During work — renew and fence

- Check ownership and expiry **before each consequential GitHub write, PR merge, experimental remote command, deployment, or publication of results**, especially after lengthy computations. This is a **cooperative write guard**; other actors that ignore it are not protected.
- Renew the heartbeat by the same read-tree / create-commit / compare-and-swap sequence, with unchanged owner/leaseId, `heartbeatAt=now UTC`, `expiresAt=now+2 hours`. Re-read and confirm after the update. Do so at least every 30 minutes of active work; if a long operation prevents this, ensure it finishes before the lease expires or refrain from subsequent writes. Do not assume an automatic background heartbeat exists.
- If ownership changed, the lease expired, or the connector is unavailable, **stop all mutations immediately**. A stale session must not release/overwrite the successor's lease. Pending writes are not a justification to ignore lost ownership.
- The two-hour expiry is a *crash-recovery lease*, not an unconditional session runtime cap. Expiration cannot terminate an abandoned computation or revoke already issued credentials: strict fencing would require every write target to validate the lease token. Existing GitHub merge head-SHA checks, branch conflict protection and risk controls still apply.
- Clock accuracy matters: use UTC timestamps, conservative checks when time is uncertain, and do not take over early. If connector permissions prevent a CAS update, no exclusive write access is established.

## Normal exit / crash recovery

- On completion, failure or early exit, reread branch HEAD and lease. Only if owner **and** leaseId still match, commit an `idle` record setting `owner`, `leaseId`, `acquiredAt`, `heartbeatAt`, `expiresAt`, `task` to null (and `previousOwner` to the finished owner), then update the ref by expected-SHA CAS. Verify release. If someone else has the lease, leave it untouched.
- If a session crashes, no release is possible; a successor may acquire only after `expiresAt`. A successor must treat results of a crashed predecessor as unverified and inspect GitHub for partial writes/PRs/remote activity.
- The coordination branch is a live operational record, **not** a scientific artifact, progress report, or queue. Document integrated evidence on `main` and ongoing work in existing PRs/issues.

## Recovery audit after an interrupted or crashed session

An idle lease means **no cooperating Director currently owns the write lease**; it does not certify that the preceding Director completed its work or that a separately started CI job has stopped.

After acquiring and verifying a new lease, inspect possible abandoned work **before opening new feature work or merging affected PRs**:

1. Read the prior `previousOwner` / last lease commit, the latest `main` revision, open PRs/issues, recently updated research branches and commit history. Determine which workstream or commits may have been left incomplete. A user-reported interrupted session is a trigger even when its lease was released cleanly.
2. For every relevant PR or unmerged branch, identify its exact current head and base, and find recent workflow runs and check conclusions. Classify them as **completed-success**, **completed-failure/cancelled**, **queued/in-progress**, or **missing/unknown**. Check each run's head SHA; a successful older run does not validate newer commits.
3. Inspect available uploaded artifacts, manifests, configs, seed/provenance metadata and logs. Incomplete, missing, or stale artifacts must not be presented as complete results. Record the exact evidence link and whether the job could still be running.
4. Reconcile any partially written files, PR descriptions, research-state assertions, or unmerged commits. Mark the work **verified, needs repair, pending external run, or blocked**. Only resume or rerun using a clear budget and fresh lease ownership; do not cherry-pick only favorable results or silently reset runs.
5. For a job still queued/in progress, inspect status and resource implications first. Do **not** blindly rerun, cancel or deploy over it. An expired lease alone cannot prove that an external job stopped, and the new Director lease cannot forcibly terminate jobs.
6. Record actionable recovery findings in the **existing** PR/issue or research-state handoff as appropriate, with head SHA, CI run URL, artifact ID, missing validation and next action. Respect the three-PR WIP limit; do not open a new feature PR for recovery bookkeeping.

This is a **GitHub evidence audit, not process-liveness detection**. A ChatGPT session may have stopped without leaving an identifiable trace, and unavailable runner logs cannot be inferred. When ownership or an ongoing write remains ambiguous, fail closed for conflicting mutations and document the uncertainty.

## Scheduled task and limits

- Every scheduled ChatGPT invocation must perform acquisition itself **before doing side-effecting work**; prior invocations' ownership cannot be inherited across sessions. The task prompt should bootstrap the current Git policy rather than duplicate this protocol.
- ChatGPT scheduled automations currently support at most **hourly** recurrence, not 15-minute recurrence. Changing the coordination lease does not change this scheduler limitation. GitHub Actions or a self-hosted scheduler can run a 15-minute *check*, but cannot on its own spawn a ChatGPT scheduled invocation. Do not claim the Director is continuously running.
- The shared Lightsail nightly experiment cron is not automatically covered by this Director lease: it is a separate workload. Do not alter it or other services merely to implement serialization.

## Acceptance checks (2026-10-10)

- Initialize branch with `status=idle` and no owner.
- Attempt two updates based on the **same** branch HEAD using `expected_sha`; confirm that only one change becomes HEAD and the stale contender does not supersede it.
- Restore `idle` by another guarded update, then read the resulting record.
- Treat unexpected API errors conservatively; the effective exclusion property for scheduled sessions relies on each session following these instructions.
