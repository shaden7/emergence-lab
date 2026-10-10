"""Pilot B stage 2: fail-closed guards for the once-only blind evaluation (prereg v1.0-r1 section 6).

This module adds no analysis. It pins the facts fixed by the stage-1 merge and refuses to run
the blind phase unless all of them still hold on the executing commit:

* the stage-1 merge commit and its committer time, and therefore the blind round R
  (recomputed here from the pinned merge time, not merely copied);
* the Git blob SHAs of the frozen stage-1 code (generator/oracle/evaluator, analyst, beacon),
  the preregistration and the config, so that no rule can change between merge and unblinding;
* the development-set decision digest, which the workflow recomputes before touching the beacon;
* wall-clock time: nothing is fetched before R's timestamp (plus a small safety margin).

``execute`` then verifies the beacon record (round == R, SHA-256(signature) == randomness, BLS),
runs ``pilot_b.run("blind", ...)`` exactly as frozen, and writes an archive manifest. A failing
B-gate is a *result* to be published (section 8), so ``execute`` exits 0 when the evaluation
completed, whatever the gate outcome; it exits non-zero only on a guard or runtime failure.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from emergence_lab import pilot_b as pb
from emergence_lab import pilot_b_beacon as bc

STAGE1_MERGE_COMMIT = "7780fc16a650d6be4a5bb49b755ff078a1568942"
STAGE1_MERGE_TIME = "2026-10-10T21:09:59Z"  # committer time of the merge commit, UTC
BLIND_ROUND = 32983212
BLIND_ROUND_UNIX = 1791753000  # 2026-10-11T21:10:00Z
SAFETY_MARGIN_SECONDS = 60  # do not even ask a relay for R until it is safely published
DEV_DECISIONS_SHA256 = "6da5c8e328ffad3be6172bebf9c0a7a016db88a9abc943e958636724a5fd9f50"
RELEASE_TAG = "pilot-b-blind-v1"

# Git blob SHAs at the stage-1 merge commit; the blind run must execute exactly this code.
FROZEN_BLOBS = {
    "src/emergence_lab/pilot_b.py": "ddbd434dbf2b46d550859d2c8e55fb18909f1b94",
    "src/emergence_lab/pilot_b_analyst.py": "8ec4da28b9ab1d79a85c93ef9c183f954ec847fa",
    "src/emergence_lab/pilot_b_beacon.py": "2421bab1a22f7d0c5e17ce19b2e8e2d68da1e386",
    "configs/pilot_b.json": "cf08823f550b761300ce3ff539bb7ad2dc4d78ba",
    "docs/PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md": "dd5dbefe950add3341366224b76ba179326282c8",
}


class GuardError(RuntimeError):
    """A stage-2 precondition does not hold; the blind run must not proceed."""


def check_round_pin() -> dict:
    rec = bc.blind_round_for_merge(STAGE1_MERGE_TIME)
    if rec["round"] != BLIND_ROUND or rec["round_unix"] != BLIND_ROUND_UNIX:
        raise GuardError(f"pinned R disagrees with the round arithmetic: {rec}")
    return rec


def check_frozen_code(root: Path = Path(".")) -> dict:
    observed = {p: pb.git_blob_sha((root / p).read_bytes()) for p in FROZEN_BLOBS}
    changed = {p: s for p, s in observed.items() if s != FROZEN_BLOBS[p]}
    if changed:
        raise GuardError(f"frozen stage-1 files changed since {STAGE1_MERGE_COMMIT[:7]}: {sorted(changed)}")
    return observed


def check_time(now_unix: float | None = None) -> float:
    now = time.time() if now_unix is None else now_unix
    if now < BLIND_ROUND_UNIX + SAFETY_MARGIN_SECONDS:
        when = dt.datetime.fromtimestamp(BLIND_ROUND_UNIX, dt.timezone.utc).isoformat()
        raise GuardError(f"too early: round {BLIND_ROUND} is published at {when} "
                         f"(+{SAFETY_MARGIN_SECONDS} s margin); now is {now:.0f}")
    return now


def check_dev_result(dev_output: Path) -> str:
    m = json.loads((dev_output / "manifest.json").read_text())
    if m.get("phase") != "dev" or m.get("decisions_sha256") != DEV_DECISIONS_SHA256:
        raise GuardError(f"development decision digest {m.get('decisions_sha256')} != {DEV_DECISIONS_SHA256}")
    return m["decisions_sha256"]


def check_beacon(beacon: dict) -> dict:
    if int(beacon.get("round", -1)) != BLIND_ROUND:
        raise GuardError(f"beacon round {beacon.get('round')} != pinned R {BLIND_ROUND}")
    if beacon.get("chain_hash") != bc.QUICKNET["hash"]:
        raise GuardError("beacon record is not from the pinned quicknet chain")
    # Re-verify locally rather than trusting the stored flags.
    v = bc.verify_round({"round": beacon["round"], "signature": beacon["signature"],
                         "randomness": beacon["randomness"]})
    if not v["signature_verified"]:
        raise GuardError("beacon record failed SHA-256/BLS re-verification")
    return v


def preflight(root: Path = Path("."), now_unix: float | None = None) -> dict:
    """All guards that need neither the beacon nor the development run."""
    rec = check_round_pin()
    blobs = check_frozen_code(root)
    pb.validate_frozen_files(root)
    now = check_time(now_unix)
    return {"round": rec, "frozen_blobs": blobs, "checked_at_unix": now}


def execute(beacon_path: Path, dev_output: Path, output: Path, root: Path = Path(".")) -> dict:
    pre = preflight(root)
    dev_digest = check_dev_result(dev_output)
    beacon = json.loads(beacon_path.read_text())
    check_beacon(beacon)
    out = pb.run("blind", output, beacon, root)
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(output.iterdir()) if p.name in ("rows.csv", "result.json", "manifest.json")}
    gates = {k: bool(g["pass"]) for k, g in out["gates"].items()}
    archive = {
        "schema": 1, "release_tag": RELEASE_TAG, "phase": "blind",
        "executing_commit": os.environ.get("GIT_SHA"),
        "workflow_run": os.environ.get("RUN_URL"),
        "stage1_merge_commit": STAGE1_MERGE_COMMIT, "stage1_merge_time": STAGE1_MERGE_TIME,
        "round": pre["round"], "beacon": beacon,
        "key_hex": pb.blind_key(BLIND_ROUND, beacon["randomness"]).hex(),
        "frozen_blobs": pre["frozen_blobs"],
        "dev_decisions_sha256": dev_digest,
        "blind_decisions_sha256": out["manifest"]["decisions_sha256"],
        "gates": gates, "all_gates_pass": all(gates.values()),
        "files_sha256": files,
        "evidence_level": ("one-shot blinded calibration of a frozen noise-aware bounded-speed test "
                           "on stipulated linear ring dynamics; not a physics result"),
    }
    (output / "blind_archive_manifest.json").write_text(json.dumps(archive, indent=1, sort_keys=True) + "\n")
    return archive


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pilot B stage-2 blind-run guards")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight")
    ex = sub.add_parser("execute")
    ex.add_argument("--beacon", type=Path, required=True)
    ex.add_argument("--dev-output", type=Path, required=True)
    ex.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "preflight":
            print(json.dumps(preflight(), indent=1, sort_keys=True))
            return 0
        rec = execute(a.beacon, a.dev_output, a.output)
    except GuardError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({k: rec[k] for k in ("gates", "all_gates_pass", "blind_decisions_sha256", "files_sha256")},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
