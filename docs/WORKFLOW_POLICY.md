# Research Workflow Policy — GitHub is the Source of Truth

**Status:** binding process policy for interactive and scheduled Emergence Lab research agents.
**Scope:** project planning, coding, literature, research claims, pull-request integration, releases and scientific review.

## 1. Authority and state hierarchy

1. **Merged `main` is the only authoritative source of project-wide rules**: `AGENTS.md`, this file, `docs/RESEARCH_DIRECTOR.md`, `docs/OVERVIEW.md`. A rule existing only in a chat, automation prompt, draft PR or issue is **not yet binding**.
2. `docs/RESEARCH_STATE.md` on `main` summarizes the *verified, integrated* scientific/technical state and outstanding limitations. It is a curated summary, not an exclusive storage location or an up-to-the-minute work queue.
3. GitHub issues and PRs represent **proposed/in-progress** work, with scope, ownership, dependencies, evidence, and blockers. They are authoritative for their own workstream but not proof that code is integrated or a claim established.
4. Commits, fixed configs, experiment manifests, CI run IDs, versioned external raw artifacts, and formal proofs supply the **audit trail**. Scientific claims require traceable supporting evidence.
5. ChatGPT conversations and scheduled-task prompts are **execution entry points**, not a second competing source of policy or scientific truth. Keep them minimal: open the repo, read these files, apply their latest merged contents. Temporary task instructions may further narrow scope but must not silently override repo safety/evidence rules.
6. Record enduring process decisions in Git **before** changing automation behavior wherever feasible. When a bootstrap prompt and Git disagree, report the discrepancy and follow the safer/higher-evidence rule; reconcile explicitly.

## 2. One director, asynchronous sessions, no human review bottleneck

The project owner **does not act as the routine PR reviewer**. The research agents must autonomously inspect, test, challenge, fix and integrate eligible work to the extent GitHub capabilities and repository settings permit. Do not leave a PR indefinitely blocked with the sole explanation "the user must review".

Each scheduled invocation is a **fresh Research Director**. It must read current policy and inspect existing open issues/PRs, dependencies, latest commits, CI and experiment artifacts. It should select the **highest-value work that advances acceptance or integration**; opening a PR is neither a requirement nor success metric.

A separate subsequent session should challenge the producer's claims when feasible; call this a **later-pass review**, not independent external peer review. A distinct tool-backed Skeptic or independent numerical implementation improves scrutiny but remains an AI-mediated check. Never invent reviewer identities, independent validation or GitHub approval events. Review and merge are separate actions; an agent may merge if the objective merge gates below pass, even if GitHub cannot create a formal approval by the PR author's own account.

### Exclusive Research Director lease (mandatory)

To prevent overlapping interactive/hourly Research Directors, **all mutating Director work requires a verified exclusive GitHub lease** from the persistent `coordination/research-lock` branch. Its sole file is `lease.json`. Follow the complete **[acquire / CAS / heartbeat / release and two-hour expiry protocol](RESEARCH_LOCK.md)**. The rules live on `main`; the mutable lease lives only on the dedicated coordination branch. When an existing valid lease is occupied, the new invocation exits without writes. Missing GitHub capability, ownership uncertainty or lost/expired lease means fail closed. A stale Director must not write or release another session's lease. Read-only orientation before acquisition is allowed.

This serialized workflow coordinates **cooperating Directors**; it is not transactional fencing of every GitHub, SSH or compute operation. Continue to use PR/commit validation, expected-head guards and shared Lightsail safety limits. Review/merge policy is unchanged. The lease branch is **never** merged into `main` and is not counted as a research PR. Scheduled ChatGPT automations cannot currently be configured more frequently than once per hour; this rule does not claim otherwise.

## 3. Hard work-in-progress limits

- Default ceiling: **3 open feature/research PRs across the project**. If >3 are already open, the default task is **backlog reduction**; no additional feature PRs.
- One coherent milestone should normally have **one PR**, regardless of how many hourly sessions contribute. Reuse an existing issue, branch and PR whenever possible.
- An exception to the ceiling requires a concrete documented safety/critical-breakage reason; do not use exceptions to avoid finishing difficult research.
- Prefer the oldest **unblocked, independently checkable dependency** before doing downstream work. Do not manufacture chains of stacked PRs merely to create hourly progress.
- When stuck, first improve tests, debug CI, correct assumptions, review an existing PR or explicitly document a blocker. A no-change iteration is legitimate.

### Current backlog snapshot (2026-10-09; re-query GitHub at each run)

At policy creation there were **eight open PRs**:
- Ising dependency chain: **#1 → #3 → #7 → #9 → #10**. Work bottom-up; test, critically assess and merge/rebase/retarget as required by the actual PR base branches.
- Separate work: **#5** (representation-neutral strategy), **#8** (literature review, Issue #6), **#11** (preregistered causal-propagation pilot).
- Issue **#4** remains a later dimension-estimator calibration question.
This enumeration is a **historical handoff, not an everlasting priority list**. Status changes must be verified, not inferred.

## 4. Autonomous review and merge gates

The agent performing integration is accountable for evidence, not for producing an optimistic review narrative.

### All PRs

1. Confirm correct **head/base relationship**, no unexamined conflicting upstream changes and no accidental unrelated edits or secrets.
2. Fetch/read the actual diff or changed files. Review assumptions, failure modes, configuration, test design and PR/issue acceptance criteria.
3. Record an explicit review decision: **PASS**, **REVISE**, **BLOCKED**, or **REJECT / CLOSE**, with reasons and evidence in the PR discussion or review record.
4. Verify the final head SHA immediately before merging and use an expected-head-SHA guard when available.
5. After merge, verify the changed files/merge commit on `main`; then update the curated research state as needed. Never label an open PR as integrated.

### Code, numerical methods, analysis, and experiment configuration

- **Require applicable automated tests to pass on the exact candidate commit**, plus a relevant end-to-end/smoke check when possible. A missing/unknown CI status is not "green".
- Check independent analytic or computational benchmarks, negative/adversarial cases, seed determinism, uncertainty/autocorrelation where relevant, runtime/resource ceilings, data provenance and reproducibility.
- If CI is unavailable, agents may run the equivalent commands in their accessible environment and attach precise results, platform/version and limitations; document why the required check could not run. Do not claim CI passed. Code with unmet necessary validation remains blocked.
- Distinguish **merging an experimental tool** from **accepting its scientific conclusions**. A well-tested exploratory model may merge with claims clearly tagged *hypothesis/unvalidated*; a claim of measured or fundamental discovery requires substantially higher independently reproducible evidence.
- Check for destructive changes, credential exposure, paid API charges and regressions to the shared EatSleepFeel/Lightsail instance. **Do not auto-deploy or run high-risk infrastructure changes** merely because a PR merges.

### Documentation, process, and literature

- Verify factual accuracy and that links, cross-references, scientific classifications, and state descriptions are consistent.
- For research literature, audit references and distinguish review from proof/empirical result. Merge only with correctly bounded claims.
- **Low-risk process-only documentation** may be committed directly to `main` when urgently correcting coordination or avoiding PR proliferation, provided the agent reads current state, checks conflicts, validates references and records the change. Otherwise favor an existing compatible PR. This does not authorize direct-to-main simulation/analysis code.
- No human sign-off is required for ordinary doc/process changes.

### Risk escalation

- If testing, permissions, branch protection or credible independent scrutiny block a PR, leave a specific machine- or researcher-actionable blocker; try other safe tasks instead. Do not substitute a fabricated approval.
- New claims about fundamental physics must undergo stronger, separately reproducible validation. If an independent scientific reviewer cannot be obtained, merge only the clearly qualified work, **not** the unsupported claim of discovery.
- Stop and seek explicit user authorization only for *new spending, secrets/credentials handling beyond existing authorized workflows, production-impacting destructive operations, or disabling safety protections*. Do not seek the user to routinely review, decide PR order, approve routine tests or press the merge button.

## 5. Managing stacked PRs

Before integrating a stack, identify each PR's actual base/head and tests. Integrate the **root first** when ready. Rebase or retarget descendants as appropriate and run tests against their changed integration base; avoid accepting a descendant on an obsolete green check. Never blindly merge an entire chain. Merge in small verifiable increments, and update the linked PRs/issues as dependencies resolve.

An upstream failure is not a reason to create another downstream PR. It is a reason to fix or reject the failing upstream assumption.

## 6. Minimum hourly cycle / handoff

1. Read `AGENTS.md`, `docs/RESEARCH_DIRECTOR.md`, this policy, `docs/RESEARCH_STATE.md`, and the scientific overview/README.
2. Enumerate actual open PRs/issues; choose an unblock/review/integration step **before** new development while above WIP limit.
3. Inspect the chosen branch/diff, run checks or experiment within resource limits, attempt a counterexample, record an evidence-level review.
4. If the objective gates pass, **merge autonomously** using the available GitHub tool, respecting branch protection and no-auto-deploy safeguards; otherwise revise the existing PR or state exactly what fails.
5. Keep `docs/RESEARCH_STATE.md` representative of `main`, using traceable commit/config/artifact IDs. Link to the review/merge decisions.
6. Leave one short handoff describing **tested, reviewed, merged, merely proposed**, specific blockers and next discriminating action.

This policy is **operational guidance, not proof that the platform provides CI enforcement, dedicated reviewer agents, or guaranteed 60-minute runtime**. Verify what tools and permissions each invocation actually has. Automation frequency does not entail success.

## 7. Changing the policy

Change it by a traceable Git commit with rationale and tests/consistency checks. When policy conflicts with another repo document, resolve the inconsistency explicitly rather than keeping parallel instructions. After substantive workflow changes, reduce/refresh the scheduled automation prompt so future sessions bootstrap from Git and do not carry obsolete procedural copies.
