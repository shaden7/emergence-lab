# CS0 worker and stored-count engineering pipeline

Status: engineering components, **not a full-study runner or authorization**.
No full CS0 entropy or study data were drawn for this implementation.

`cs0_worker` is a trusted no-fork/no-file row producer. It implements the frozen
proposed full design (728 rows) and a separate development fixture (40 rows,
N=8,12 and 3 replicates, fixed entropy 2036110697). Each generated order is
checked for strict partial-order validity; sprinkled points are checked against
the diamond bounds. It emits JSONL with runtime metadata and deterministic
spawn keys. The internal worker API/CLI can represent full mode, but must only
be called in that mode by a separately reviewed, authorized launcher.

`cs0_engineering` exposes **only the miniature engineering fixture**. It:

- refuses a dirty/wrong-revision checkout and checks every tracked source byte
  against the pinned Git objects, detecting changes hidden by index flags;
- refuses unexpected source/extension files and symlinks, and binds the loaded
  launcher, supervisor, rechecker and package origins to the requested checkout;
- launches isolated Python with a fresh private bytecode-cache prefix and
  verifies worker/package/reference module origins;
- supervises worker CPU (15 s), wall time (30 s), address space (512 MiB) and
  captured output (1 MB), using the direct-worker parent-death guard;
- fsyncs the per-realization CSV, re-reads it, independently checks stored counts,
  and preserves the raw JSONL and nested worker manifest;
- writes durable INCOMPLETE checkpoints and records hashes, source/config pins,
  observed CPU and payload sizes. COMPLETE means engineering completion only.

Only the known inert setuptools metadata filenames in
`src/emergence_lab.egg-info` are admitted for editable installs; Python, `.pth`,
extension modules and nested metadata files remain refused. Ordinary source
bytecode caches are bypassed by the worker's fresh prefix, not trusted as code.
CI executes this same engineering-only path and archives its raw JSONL, CSV,
report and manifests in the standard smoke-results artifact.

The launcher must itself be started from the source checkout using a trusted
interpreter and fresh source-cache prefix. For example, substitute absolute
paths and a new output/cache directory:

```sh
python -I -B -X pycache_prefix=/tmp/cs0-launcher-cache-UNIQUE -c \
  'import sys; sys.path.insert(0,"/absolute/checkout/src"); from emergence_lab.cs0_engineering import main; sys.exit(main())' \
  --root /absolute/checkout --commit EXACT_40_CHARACTER_COMMIT \
  --output /tmp/cs0-engineering-UNIQUE
```

`cs0_recheck` imports neither producer nor worker. It enforces the complete
frozen row identities, integer pair-count bounds, seed-key labels, r=R/C(N,2),
independent gamma references and dimension inversion. It calculates G1–G3
descriptively for engineering fixtures. Full-shaped synthetic tests verify the
24-cell t(29) Bonferroni cutoff and N=1024 discrimination without any RNG.
Zero-SE stochastic cells have undefined t and cannot pass their mean test.

To recheck a saved CSV without generating orders:

```sh
PYTHONPATH=src python -m emergence_lab.cs0_recheck \
  --input /tmp/cs0-engineering-UNIQUE/measurements.csv \
  --mode engineering --entropy 2036110697
```

Engineering reports always say ENGINEERING_ONLY. A successful full-shaped count
report can say only PASS_CONDITIONAL_G0: stored R cannot prove partial-order
validity, point support, RNG execution or exact-commit unit-test success. This
is a distinct implementation of the arithmetic, not independent physical data
or external scientific peer review. MM alone cannot certify manifold-likeness.

## Remaining full-run blockers

Worker per-process limits are **not aggregate containment**. The engineering
manifest explicitly records `aggregate_caps_enforced=false`; observed aggregate
CPU includes waited child processes, while payload bytes exclude the manifest
itself. No aggregate peak RSS or hard parent/rechecker/output limit is claimed.
These measurements cannot satisfy preregistration section 6.

The launcher trusts the interpreter and system dependencies. `-I` still loads
system site packages and their startup hooks. Source hashes/origins do not
attest already-loaded machine code or protect against a concurrent malicious
filesystem writer. Do not use this API as an arbitrary-code sandbox.

A full runner still requires hard aggregate CPU/RSS/output enforcement, durable
failure accounting, complete runtime/provenance review, later-pass exact-commit
review and a separate versioned authorization freezing the entropy. No full
launcher or authorization is supplied here. No Lightsail or deployment change.
