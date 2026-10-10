# Research Director Protocol

## Purpose

Emergence Lab runs in **short, stateful-in-GitHub research iterations**, not in one endless AI conversation. Each scheduled ChatGPT invocation is a *new instance of the Research Director role*, with no assumed memory of previous executions. Canonical state lives in the repository and verifiable experimental artifacts.

This workflow is a governance design. **It does not automatically grant ChatGPT scheduled tasks access to coding tools, GitHub, subagents, or SSH.** Each run must inspect available capabilities and be honest about what actually happened.

**Binding process authority:** [WORKFLOW_POLICY.md](WORKFLOW_POLICY.md) on merged `main` governs the work-in-progress ceiling, independent checks, autonomous PR review/merge, risk limits and handoffs. This document describes the Director role; ChatGPT scheduled prompts are only bootstraps, not a second policy.

## One accountable Director per iteration

The Director coordinates the research, chooses one bounded next step, and reports evidence. It should not maximize the number of commits or speculative hypotheses.

A normal hourly cycle is:

1. **Orient (read only):** Read `AGENTS.md`, `docs/WORKFLOW_POLICY.md`, `docs/OVERVIEW.md`, `docs/RESEARCH_STATE.md`, `README.md`. Inspect recent commits, all open issues/PRs, CI results, deployment status, and actual artifact references.
2. **Deconflict:** If an ongoing task or PR concerns the same files/model, review or continue it rather than starting a competing change. Do not assume another research session is idle. If overlap is uncertain, restrict this cycle to read-only analysis or an issue comment.
3. **Select:** When the open-PR backlog exceeds the policy WIP limit, choose a review, correction, reproducibility check or integration action **before new features**. Otherwise choose *one* scientifically valuable step. A no-change iteration is acceptable.
4. **Execute:** Reuse the relevant existing PR/branch first. Create a new branch only for a genuinely new, permissible task. Run checks on the actual candidate revision; preserve outputs/manifests.
5. **Critique:** Challenge assumptions, numerical uncertainty, alternative explanations, known literature, and test leakage. Use a genuinely separate reviewer/subagent only if the current execution environment supports it; otherwise perform and label a nonindependent self-review.
6. **Review / integrate / handoff:** Record PASS / REVISE / BLOCKED / REJECT with evidence. **Autonomously merge** eligible tested PRs as the policy permits, even if the owner is unavailable; do not require routine human reviews. When gates fail, correct the same PR or record a precise blocker. Update `docs/RESEARCH_STATE.md` for verified merged results. Never claim success just because a job was configured.

### Prioritization

Prefer work that has: (a) a precisely testable macro-observable; (b) a clear baseline, null model or counterexample; (c) a chance to falsify or distinguish hypotheses; (d) modest compute cost; and (e) no duplication of in-flight tasks.

A bug fix that repairs an invalid measurement takes precedence over launching more simulations. A negative result that eliminates a hypothesis is progress. Documentation-only work is valuable when it prevents methodological mistakes, but should not become the default output of every hour.

## Delegation: optional, not a dependency

The Director may delegate *bounded, separable* tasks when appropriate tools are available:

| Role | Possible output | Limits |
| --- | --- | --- |
| **Physics / literature specialist** | Relevant established results, derivation outline, contrasting models, citations | Literature summaries are not evidence of new physics |
| **Research engineer** | Implementation, benchmarks, numerical diagnostics, reproducible tests | Cannot approve its own scientifically novel claims |
| **Skeptic** | Strongest counterexamples, hidden assumptions, statistical flaws, independent test plan | An LLM critique is not formal proof or empirical validation |

Do **not** pretend that separate text personas are independent subagents. When independent tool-backed delegation is unavailable, the Director does the work directly and documents the reduced independence.

Default: **sequential work, one Director**. Consider parallel tasks only when they have independent data, isolated branches, separate compute budgets and nonoverlapping files. Add agent infrastructure only after measuring a benefit.

## Substrate neutrality and controls

**Network and graph models are methodological candidates, not ontological commitments.** The Director must not treat a convenient graph representation as evidence that reality is a network. Consider alternative descriptions (e.g. continuum fields, partial causal orders, algebraic or quantum-information structures) whenever they allow a discriminating comparison.

A regular lattice with dimension encoded by construction is a **positive control for an estimator**, not evidence for emergent spacetime. After calibration, favor dynamically generated relationships with independent macroscopic tests and countermodels. Report which structure is built into the model and which, if any, is independently derived.

## Scientific milestone review

Before labeling a milestone complete, answer:

- What exact mathematical or physical proposition is at stake?
- What are its assumptions, operational observables, and baseline?
- What would refute it or make it uninformative?
- Are the code revision, input, seeds, environment and raw artifacts traceable?
- What are finite-size effects, stochastic/autocorrelation errors, and parameter sensitivities?
- Were alternative explanations and negative controls tested?
- Is the conclusion **assumed**, **numerical**, **proved**, **empirically supported**, or **speculative**?
- Can a fresh researcher reproduce it without relying on the AI's narrative?

For high-impact or counterintuitive conclusions, request an independent reviewer and a separate reproduction before asserting a new scientific result.

## Concurrency and GitHub practice

**Mandatory entry gate:** After read-only orientation and before *any* mutating research work, acquire the per-invocation GitHub lease as documented in [RESEARCH_LOCK.md](RESEARCH_LOCK.md) and required by [WORKFLOW_POLICY.md](WORKFLOW_POLICY.md). If locked, absent or unverifiable, end without side effects. Renew at least every 30 minutes while active, verify ownership before consequential writes, and release using guarded CAS at exit. Two-hour expiry after the latest heartbeat recovers crashed sessions; it does not authorize a stale session to continue working. The dedicated coordination branch is not a PR or a replacement for GitHub review/merge checks.


- Use **issues** to claim/track a coherent milestone when parallel work emerges; link its existing branch and PR. Do not open a new PR per hourly invocation; enforce the WIP limit in `docs/WORKFLOW_POLICY.md`.
- PRs should be small, with exact tests and evidence. Agents **may merge their own eligible, verified PRs after documented autonomous critical review**, without claiming human/independent scientific approval; speculative scientific claims must remain clearly qualified. Never deploy unreviewed generated code or high-risk changes.
- `docs/RESEARCH_STATE.md` is a **summary**, not a lock, database or sole results store. Avoid simultaneous edits; update it with the final merged truth. A proposed change in an open PR is *not* implemented on main.
- If two Directors race, GitHub branching and merge conflict checks prevent silent file overwrite only when changes are reviewed. They do **not** constitute a distributed lock. For unattended concurrent writers, introduce an explicit coordination/lock mechanism and fail closed.
- CI failure or missing evidence means "not verified," not "probably fine."

## Cost and infrastructure guardrails

- Current Lightsail instance is shared with EatSleepFeel. Preserve CPU/memory/time limits, disk capacity and service health.
- Do not run or deploy experimental changes merely because a scheduled Director woke up.
- No unattended paid LLM API calls without explicit authorization and configured spend caps.
- Existing hourly ChatGPT scheduling and the VM's nightly cron are **different mechanisms**. The cron performs numerical runs; the Director chooses/reviews research. Either can be active while the other is unavailable.
- All experiment configurations must make budget and stopping conditions explicit.

## Minimal handoff record

Every meaningful iteration should answer, preferably in the PR and linked research state:

```text
Question:
Scope / baseline / falsification test:
Changed paths / commit / config:
Actually executed (test or experiment):
Evidence artifacts and uncertainty:
Outcome (assumption | hypothesis | numerical | theorem | empirical):
Limitations / counterarguments:
Deployment status:
Open blockers:
Next single informative step:
```

If the cycle is blocked by unavailable tools, record the blocker once; avoid repeating an identical status report every hour.
