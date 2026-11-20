# D3-E0/M0 v1 target authorization — 2026-11-19 (PROPOSED; target NOT run)

- **What:** the separate committed authorization required by `docs/CS0_D3_E0_PROTOCOL.md` §7. It becomes usable only after a later-pass review in a separate session and a merge to `main`.
- **Pins:**
  - SHA-256 of the protocol (`92aef68b…`) and of the config (`d4ee31bf…`).
  - Git blob ids at HEAD of all six `PINNED_PATHS`.
  - The archived pilot record `docs/experiments/d3-e0-v1-pilot-20261118/pilot_record.json` (SHA-256 `db8d0cdd…1a8a`, `PILOT_COMPLETE`, budget `OK`, all n_c = 10^5). That record was merged in PR #83 as `cdf4c00` after later-pass review r1 PASS.
- **Authorizes:** exactly **one** target run with the frozen target seed root `2631650520979328321`. The run is subject to the 600 CPU s and 512 MiB caps. Expiry: `2026-12-10T00:00:00Z`.
- **Outcomes:** `COMPLETE`, `UNDECIDABLE_AT_BUDGET` and `INVALID` are all retained. Protocol v1 allows no rerun with new seeds or a larger budget.
- **Command, after merge:** `python -m emergence_lab.d3_e0_campaign target --authorization docs/experiments/d3-e0-v1-target-auth-20261119/authorization.json --output <fresh dir>`. Run it on a clean worktree at a `main` commit whose pinned blobs equal those listed here.
- **Not done:** no target run, no D=3 target-cell mean or SD.
