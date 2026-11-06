# CS0 fixed-writer artifact budget

The engineering pipeline now caps serialization **before opening files**. Each
inner JSON/CSV/worker slot admits at most 1,000,000 bytes. Atomic replacements
reserve both the existing file and its `.tmp` sibling. Oversized or invalid
terminal metadata becomes a small durable INCOMPLETE manifest; it cannot carry
successful slot-proof evidence into the outer wrapper.

| Admitted file slots | Count | Maximum per slot | Combined bytes |
| --- | ---: | ---: | ---: |
| Inner manifest and temporary replacement | 2 | 1,000,000 | 2,000,000 |
| Worker manifest and temporary replacement | 2 | 1,000,000 | 2,000,000 |
| Captured worker output | 1 | 1,000,000 | 1,000,000 |
| CSV and temporary replacement | 2 | 1,000,000 | 2,000,000 |
| Report and temporary replacement | 2 | 1,000,000 | 2,000,000 |
| Host envelope and temporary replacement | 2 | 16,384 | 32,768 |
| Host client log (conservative shell-limit bound) | 1 | 2,097,152 | 2,097,152 |
| **Total** | **12** | | **11,129,920** |

The inner manifest reports its nine admitted slots and 9,000,000-byte bound.
The wrapper requires the matching proof before recording
`fixed_pipeline_output_budget_enforced=true`. Generic supervisor callers may
choose a different worker-output cap; the bound above applies only to the fixed
engineering caller, which selects 1,000,000 bytes. The generic default remains
separate and does not establish an aggregate artifact bound.

This is a structural bound on regular-file contents produced by the reviewed,
trusted fixed-writer pipeline, including interrupted atomic copies. It is not
an arbitrary filesystem quota or a guarantee against an unreviewed/malicious
worker creating additional files. Runtime scratch/cache, container image,
filesystem metadata, daemon storage and later archive copies are outside this
artifact-set statement. No full CS0 run is authorized by this component.

Child-process/parent loss retains the last durable checkpoint. Host power loss,
new-directory persistence and filesystem failures remain outside the durability
guarantee; the host envelope separately fsyncs its parent directory.

Tests cover oversized JSON/CSV, Unicode byte expansion, error truncation,
repeated replacement, rich-manifest fallback, invalid initial parameters,
missing slot proof and a real host log flood through the fake Docker transport.
The fake transport validates wrapper behavior; the normal CI additionally runs
the real engineering container pipeline.
