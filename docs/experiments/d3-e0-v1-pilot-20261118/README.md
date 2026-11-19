# D3-E0/M0 v1 engineering pilot — 2026-11-18

- **What:** the single blinded engineering pilot that `docs/CS0_D3_E0_PROTOCOL.md` §4 authorizes. It ran once, on the merged freeze `5d6c2ff` (PR #82), with the protocol's pilot seed root `1200746945068229832`.
- **Command:** `python3 -m emergence_lab.d3_e0_campaign pilot --output docs/experiments/d3-e0-v1-pilot-20261118`. Run on a clean worktree for the pinned paths (`git_dirty_pinned: false`).
- **Host:** Linux x86_64 cloud sandbox with 2 CPUs. Python 3.13.18, numpy 2.5.3, scipy 1.18.1, mpmath 1.3.0. These timings are for this host type only.
- **Record:** `pilot_record.json`, SHA-256 `db8d0cdd3569b99ffc7ea742d8432f849d5d16923c6b9db62a17f786827d1a8a`.
- **Outcome (engineering status only):**
  - Status: `PILOT_COMPLETE`.
  - Resources: 4.96 CPU s (cap 60) and 263 MiB peak RSS (cap 512).
  - Target sizes: every n_c is at the 10^5 floor (largest pilot SD̂ 0.77). The projected target is 23.8 CPU s (cap 600), so the budget status is `OK`.
- **Blinded:** no cell mean is written. Under protocol §4, the pilot SD̂, P̂(R=0) and timings are engineering inputs to n_c. They are **not results** and must never be pooled with target data.
- **Not done:** no target authorization exists, and no target run has been executed. A target run needs a separate committed authorization (protocol §7) that pins this record's path and hash.
