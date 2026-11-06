# D2-M0 reference implementation and supervised execution

The reviewed/frozen design is docs/CS0_D2_M0_PROTOCOL.md. This diagnostic uses
exact combinatorial weights and numerical inversion; it generates no random
samples and does not authorize a CS0 study or any physical claim.

`d2_m0_reference` implements the complete N=2,...,32 curve only when explicitly
called. Unit tests use N=2/N=3 controls and manufactured failure fixtures, not
the target curve. Independent calculations use mpmath 1.3.0, exact rational
conversion, 80-digit direct gamma functions and bisection. Install the optional
reference dependency with `pip install -e '.[reference]'` when needed; tests
include the same pinned dependency.

`d2_m0_runner` requires a clean exact checkout, verifies project source bytes,
loaded origins and protocol bytes, and invokes the computation exactly once in
an isolated Python worker. It preserves raw JSON, exact weights, full CSV,
checks, source/config/protocol pins, versions and artifact hashes. Outcomes are
REFERENCE_COMPLETE, NUMERICAL_CHECK_FAILED or INCOMPLETE. A numerical failure
cannot override a resource/provenance failure; every occupancy is retained.

The worker has kernel limits of 27 CPU seconds, 55 wall seconds, 384 MiB address
space and 700,000 captured bytes. The controller checks the protocol's total
30 CPU seconds / 60 wall seconds / 512 MiB / 1,000,000 retained-byte budget,
using all waited-child CPU and a conservative sum of parent/child peak RSS.
Derived artifacts are preplanned under the total byte reserve before writing.
One CPU/wall second is reserved for finalization; this is an allowance, not
measured or enforced final fsync cost. An external timing record should verify
the complete invocation when reporting an actual run. The manifest explicitly
states `strict_aggregate_containment=false`; these observations do not satisfy
the separate full-CS0 aggregate containment requirements.

Run from a trusted interpreter with a fresh source-cache prefix, substituting
absolute checkout/output paths and a pinned commit:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -I -B -X pycache_prefix=/tmp/m0-launcher-cache-UNIQUE -c \
 'import sys; sys.path.insert(0,"/absolute/checkout/src"); from emergence_lab.d2_m0_runner import main; sys.exit(main())' \
 --root /absolute/checkout --commit EXACT_40_CHARACTER_COMMIT \
 --output /tmp/d2-m0-UNIQUE
```

If the reviewed mpmath installation is in a private directory, the optional
`--dependency-path` explicitly adds that trusted directory in the worker. The
runtime and third-party dependencies remain trust assumptions, not a sandbox.
Keep failed/partial evidence. A failed control or resource stop is not an
invitation for an automatic retry or selected rerun.
