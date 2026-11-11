# D2-E0 later-session freeze review — 2026-11-11

Baseline main: 7187492dd0bba7a7f52a71c213c18ea42ed83073; PR #77 is integrated.
Recovery audit: prior lease idle, no open PRs, only Issue #37 open. Latest
five inspected workflow runs completed-success, including main run
42987198413; no queued/in-progress run in that window. No claim of external
process liveness. This session obtained its own verified GitHub lease.

## Iteration 1: challenge the implementation

Baseline relevant tests: 106 passed on Python 3.12.14. Found a precondition
that was recorded but not enforced: CAP_SYS_RESOURCE could be true/unknown
while strict containment was claimed. Now refuse before any worker unless
it is verifiably false. Added both adverse cases. Also killed the controller
immediately after reference replace: a reference can exist, but its durable
manifest remains INCOMPLETE. This verifies the previously untested final-write
window without pretending every kill produces a finished record. 109 tests
passed after this change. No target numerical curve evaluated.

## Iteration 2: freeze and narrow target gate

Reviewed exact law, moments, MM inverse domain, endpoint convention, numerical
checks and partitioned budget. The separate direct-coordinate combinatorial
recheck passed all 5,914 permutations through N=9 and rational controls at
N=2..32 (0.070 CPU s here). This is computational checking, not formal proof.
The same host passes actual seccomp fork/thread denial, limit readback, worker
CPU/wall/memory stops, bytecode/provenance and failure tests. Effective
capabilities are zero; CAP_SYS_RESOURCE=false; Linux seccomp mode 2.

Freeze v1 retains r3 scientific thresholds and budgets. It explicitly resolves
the payload-size prerequisite: the **single** separately authorized attempt
measures the full compressed payload and returns INCOMPLETE if >800,000 B;
no preliminary target evaluation or retry is permitted. Fixed slots enforce
the bound regardless of compression. Earlier feasibility numbers are not a
size certificate. No numerical threshold was changed.

Target execution now additionally needs a committed JSON decision, explicit
matching id, exact source/protocol/config hashes, host boot identity, root and
output paths, interpreter and dependency versions, expiry and one-invocation
scope. The authorization file joins the before/after git blob checks. Target
runs forbid dependency overrides and check isolated/no-bytecode launch flags.
A pre-existing output directory cannot be reused. Once-only remains a
cooperative workflow guarantee, not protection against deleting the output or
forging the authorization. Without the separate decision, target remains
blocked. Tests use metadata fixtures and N<=10 only: 127 relevant tests passed
before the final documentation-only cleanup.

Review: scoped PASS for instrument engineering and protocol freeze, subject
to exact candidate validation in the PR. This is a later-session, AI-mediated
review of PR #77 plus nonindependent self-review of this session's additions;
no external peer review or new physics conclusion. Full-CS0 remains blocked.
No deployment, Lightsail/EatSleepFeel work or paid API.
