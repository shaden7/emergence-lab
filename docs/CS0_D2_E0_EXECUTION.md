# D2-E0 v1 once-only execution decision — 2026-11-11

**Consumed:** the single target invocation completed on 2026-11-11. See
[the archived outcome](experiments/2026-11-11-d2-e0-run.md). This decision
authorizes no additional invocation. Original JSON pins remain unchanged.

Authorized only after this separate operational record is committed to main.
The reviewed code/protocol gate is integrated by PR #78, merge 864a443b4bb9db839026ae9314b724a27fc76360
(exact reviewed head 4f2330cecb7ba432c17f322589a364838ab1a500).
Exact-head CI 43093197785 succeeded; 127 relevant local tests passed.
Host preflight N=2..10 in a clean clone was REFERENCE_COMPLETE with cap=false
and actual no-fork/limit tests passing. An earlier engineering preflight
refused bytecode caches; preserve that failure. Neither preflight is target data.

## Scope and decision

One deterministic N=2..32 invocation of frozen CS0_D2_E0_PROTOCOL.md v1,
using the exact source/protocol/config/interpreter/host/output/expiry pins in
[CS0_D2_E0_AUTHORIZATION.json](CS0_D2_E0_AUTHORIZATION.json).
Current source hashes match the reviewed head. Record the **actual execution
HEAD**, authorization SHA-256, config and protocol hash before launch.
No RNG, sampling, new infrastructure, Lightsail, deployment or paid API.
Keep REFERENCE_COMPLETE, NUMERICAL_CHECK_FAILED or INCOMPLETE and all artifacts;
do not rerun after a failure or remove/reuse the output directory.
The full compressed payload has not been measured; >800,000 B means INCOMPLETE.
Do not relax 30 CPU s / 60 wall s / 512 MiB / 2,000,000 simultaneous content B.
Trust boundary and tick granularity remain as in the frozen protocol.

## Pinned launch

Use a clean detached checkout of this integrated decision revision at the
JSON's root. Exact command (substitute only the actual 40-character HEAD):

```sh
/workspace/scratch/07eb96782918/research-venv/bin/python -I -B -X pycache_prefix=/nonexistent-d2-e0-pycache -c 'import sys; sys.path.insert(0,"/workspace/scratch/07eb96782918/d2-e0-execution/src"); from emergence_lab.d2_e0_runner import main; sys.exit(main())' \
 --root /workspace/scratch/07eb96782918/d2-e0-execution --commit ACTUAL_40_CHARACTER_HEAD \
 --output /workspace/scratch/07eb96782918/d2-e0-v1-run --sizes 2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32 \
 --authorization-id d2-e0-v1-20261111-once
```

External timing may be recorded outside the runner's fixed output slots;
the wrapper is explicitly outside the accountable process tree, and must not
be misreported as kernel-contained. After the attempt, archive original bytes,
verify all digests, and re-analyze saved output with independent code. The
post-run recheck is analysis of stored data, not another target invocation.

## Review and workflow

Scoped PASS for this one local bounded instrument diagnostic, not for scientific
acceptance. AI-mediated/nonindependent decision; no external peer review.
This separate low-risk operational documentation is committed directly under
WORKFLOW_POLICY.md section 4 to make the single-run decision concrete while
avoiding an additional process-only PR. It changes no source, numerical
threshold or resource limit and is separate from the implementation PR.
The owner's instruction to perform several iterations supplies the routine
work authorization; no new spending or production risk is introduced.
