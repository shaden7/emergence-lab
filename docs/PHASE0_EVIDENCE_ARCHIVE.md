# Phase-0 calibration raw-evidence archive (gate 6)

**Purpose:** preserve the raw Monte Carlo time series of report gates 4 and 5 beyond GitHub Actions' finite artifact retention. These data calibrate our experimental/statistical infrastructure; they are not evidence for a new theory of physics.

**Tag:** `phase0-evidence-2026-10-10-v1`. The workflow `.github/workflows/archive-phase0-evidence.yml` runs on merge to `main` when the workflow file or `src/emergence_lab/archive_evidence.py` changes, and otherwise only by deliberate manual dispatch. A configured workflow is **not** evidence that the release exists or that gate 6 has passed: verify the completed workflow run and downloadable release bytes.

## Inputs and immutable identity checks

| Gate | Original provenance | Registered raw SHA-256 | Config file SHA-256 (`sha256sum` of the file bytes) |
| --- | --- | --- | --- |
| 4, energy interval coverage | GitHub Actions run [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864), head `378d386591832075bc56336f2f4a9f41fde2accb`; raw data reproduced byte-for-byte against local run | `97a81cb7898c1048716a3464793488d4502b00df24a8d4d786f7fdc48adbf5a5` | `a03e68c5c49e2cb93e4718fe33fd7d99d7820579347593860b661bd81594fc1b` |
| 5, finite-size scaling | Preregistered commit `7005c0fdbbbcebf880150259fb976b426a877a14`, local 2-worker run, 713 s wall; raw bytes reproduced on a GitHub runner in archive run [38045856455](https://github.com/shaden7/emergence-lab/actions/runs/38045856455) (step 6 `sha256sum --check` passed) | `b18423a20e428583a493e45ff24146a5b0dd5592c6b8654772aecd8914cc2287` | `2176235a66c7c437d008307ebe8129519b138c7ec62520b0afbda6b073fae6a2` |

The workflow retrieves gate 4 from the named existing runner artifact and recomputes gate 5 with the unchanged config and fixed seeds. The code checks **raw NPZ SHA-256 independently of the JSON report**, plus config file/hash, raw array identities, coverage power-control failures, and finite-size non-critical controls. It re-analyses both NPZ files using the present code and checks outcomes against the original reports. JSON analyses may contain platform-dependent floating-point differences even when the raw simulation arrays are identical.

The release contains `coverage_gate.npz`, `finite_size_gate.npz`, their original JSON reports, two regenerated analysis JSON reports, and a provenance manifest with per-array raw-data SHA-256 values. Hashes of numerical arrays are distinguished from hashes of exact analytic references and reports. The workflow refuses changed byte hashes, missing data, or an unexpectedly passing negative control.

Release publication uses `GITHUB_TOKEN` and attempts only new asset uploads; existing assets must have matching remotely reported SHA-256 digests. No `--clobber` is used. It downloads the release assets after upload and runs the verifier again. **Release assets are more durable than expiring Actions artifacts but are not cryptographically immutable against repository administrators**; the tag, manifest, hashes and workflow audit trail establish detectable identity if independently retained. GitHub's retention and administrator deletion policies still apply.

**Config digest conventions.** The pins above are SHA-256 of the config file bytes. The gate reports record `config_sha256` as SHA-256 of canonical JSON (`json.dumps(cfg, sort_keys=True)`; gate 4 `97d3bb6f…`, gate 5 `689f2a9d…`). The verifier checks the file against the pin and, separately, the report's canonical digest and embedded config against the file. The first archive run (38045856455, merge `8d83d8e`) failed closed because the verifier compared the canonical digest with the file-byte pin; no release was published. Both raw NPZ digests reproduced in that run, and both re-analyses passed. The fix did not change any pin, config, seed or criterion.

## Execution and scope

- Uses GitHub-hosted `ubuntu-latest`, Python 3.12 and NumPy 2.5.3; 2 worker processes for gate 5, bounded by `max_proposals=6e9` (actual design 5.69e9) and a 30-minute step / 45-minute job. Actual runtime and success must be read from the resulting job, not inferred.
- GitHub Actions permissions: `actions:read` for existing artifacts and `contents:write` for the release. No new paid APIs, cloud instances or Lightsail workload.
- On any hash mismatch, abnormal power-control result, unavailable original artifact, missing release permission, or download mismatch, **gate 6 remains failed/unverified**. Do not silently regenerate a different dataset and call it the registered evidence.
- A full Phase-0 **GO/NO-GO decision is a separate review** after verified archival. Passing gates 4 and 5 does not erase the warning that gate-4 short-chain per-chain ESS intervals under-cover at L32 or that the gate-5 `1/nu` fit requires a tolerance allowance. These limitations must carry into Phase 1.

To verify a downloaded archive again from the repository root:

```bash
python -m emergence_lab.archive_evidence \
  --coverage-raw archive/coverage_gate.npz \
  --coverage-report archive/coverage_gate.json \
  --finite-raw archive/finite_size_gate.npz \
  --finite-report archive/finite_size_gate.json \
  --out archive/reverified_manifest.json
```

**Status of this note:** a protocol and acceptance plan; until a completed archive run and remote download verify successfully, no archival PASS is claimed.
