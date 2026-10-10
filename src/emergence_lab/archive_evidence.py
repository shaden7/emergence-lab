"""Fail-closed verifier and provenance manifest for Phase-0 raw evidence.

No simulation here. The release workflow verifies preregistered raw-byte hashes,
config/report consistency and negative controls before publishing evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np

EXPECTED = {
    "coverage": {
        "raw": "97a81cb7898c1048716a3464793488d4502b00df24a8d4d786f7fdc48adbf5a5",
        "config": "a03e68c5c49e2cb93e4718fe33fd7d99d7820579347593860b661bd81594fc1b",
    },
    "finite_size": {
        "raw": "b18423a20e428583a493e45ff24146a5b0dd5592c6b8654772aecd8914cc2287",
        "config": "2176235a66c7c437d008307ebe8129519b138c7ec62520b0afbda6b073fae6a2",
    },
}
COVERAGE_RUN = 38042967864


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_gate(
    kind: str,
    raw_path: Path,
    report_path: Path,
    config_path: Path,
    *,
    expected: dict | None = None,
) -> dict:
    """Return a manifest entry or raise ValueError; expected override is for tests."""
    if kind not in EXPECTED:
        raise ValueError(f"Unknown gate: {kind}")
    pins = expected if expected is not None else EXPECTED[kind]
    raw = raw_path.read_bytes()
    report_bytes = report_path.read_bytes()
    cfg = json.loads(config_path.read_text())
    report = json.loads(report_bytes)
    raw_sha = digest(raw)
    cfg_sha = digest(json.dumps(cfg, sort_keys=True).encode())
    if raw_sha != pins["raw"] or report.get("raw_npz_sha256") != raw_sha:
        raise ValueError(f"{kind}: raw bytes differ from preregistered evidence")
    if cfg_sha != pins["config"] or report.get("config_sha256") != cfg_sha or report.get("config") != cfg:
        raise ValueError(f"{kind}: config or reported config differs from preregistration")
    if report.get("gate_pass") is not True:
        raise ValueError(f"{kind}: gate did not pass")
    if kind == "coverage":
        if set(report["sizes"]) != {str(s) for s in cfg["sizes"]}:
            raise ValueError("coverage: missing size")
        if not all(s["main"]["pass"] is True and s["power_control"]["pass"] is False
                   for s in report["sizes"].values()):
            raise ValueError("coverage: power control or primary gate invalid")
    else:
        if len(report["main"]["checks"]) != 65 or not all(
            x is True for x in report["main"]["checks"].values()
        ):
            raise ValueError("finite_size: incomplete or failed registered checks")
        if not all(report["controls"][label]["rejected"] is True
                   for label in ("off_critical", "j0_iid")):
            raise ValueError("finite_size: a negative control was not rejected")
    try:
        with np.load(raw_path, allow_pickle=False) as saved:
            keys = saved.files
            if not keys or len(set(keys)) != len(keys):
                raise ValueError(f"{kind}: raw archive missing or duplicate arrays")
            per_array = {key: digest(np.ascontiguousarray(saved[key]).tobytes()) for key in keys}
            if kind == "coverage":
                expected_keys = {f"{measurement}_L{size}"
                                 for size in cfg["sizes"]
                                 for measurement in ("energy_sum", "magnetization_sum")}
                if set(keys) != expected_keys or report.get("raw_digests") != per_array:
                    raise ValueError("coverage: raw arrays/digests do not match report")
                draws = (cfg["warmup_sweeps"] + cfg["sample_sweeps"]) // cfg["sample_every"]
                for key in keys:
                    if saved[key].shape != (cfg["batches"], cfg["chains_per_batch"], draws):
                        raise ValueError(f"coverage: wrong shape for {key}")
            else:
                expected_keys = {f"{part}_L{size}_{field}"
                                 for part in ("main", "off_critical", "j0_iid")
                                 for size in cfg["sizes"]
                                 for field in ("energy_sum", "magnetization_sum", "seeds", "starts")}
                if set(keys) != expected_keys:
                    raise ValueError("finite_size: missing or unexpected raw arrays")
                for size in cfg["sizes"]:
                    for part in ("main", "off_critical", "j0_iid"):
                        stem = f"{part}_L{size}_"
                        count = (2 * cfg["chains_per_start"] if part == "main" else
                                 2 * cfg["controls"]["off_critical"]["chains_per_start"] if part == "off_critical"
                                 else cfg["controls"]["j0_iid"]["chains"])
                        for field in ("energy_sum", "magnetization_sum", "seeds", "starts"):
                            arr = saved[stem + field]
                            if arr.shape[0] != count:
                                raise ValueError(f"finite_size: invalid chain count {stem + field}")
                        if saved[stem + "energy_sum"].shape != saved[stem + "magnetization_sum"].shape:
                            raise ValueError(f"finite_size: mismatched observable shapes {stem}")
                        if len(set(saved[stem + "seeds"].tolist())) != count:
                            raise ValueError(f"finite_size: colliding seeds in {stem}")
    except (OSError, KeyError) as exc:
        raise ValueError(f"{kind}: invalid NPZ contents") from exc
    return {
        "raw_npz": raw_path.name,
        "raw_npz_sha256": raw_sha,
        "raw_array_sha256": per_array,
        "report_json": report_path.name,
        "report_json_sha256": digest(report_bytes),
        "config_path": str(config_path),
        "config_sha256": cfg_sha,
        "environment": report.get("environment"),
        "gate_pass": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage-raw", type=Path, required=True)
    ap.add_argument("--coverage-report", type=Path, required=True)
    ap.add_argument("--finite-raw", type=Path, required=True)
    ap.add_argument("--finite-report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    entries = {
        "coverage": verify_gate("coverage", args.coverage_raw, args.coverage_report,
                                Path("configs/coverage_gate.json")),
        "finite_size": verify_gate("finite_size", args.finite_raw, args.finite_report,
                                  Path("configs/finite_size_gate.json")),
    }
    manifest = {
        "schema": 1,
        "scope": "Phase-0 Ising calibration, gates 4 and 5; not a physical discovery",
        "archive_workflow_commit": os.getenv("GITHUB_SHA"),
        "archive_workflow_run": os.getenv("GITHUB_RUN_ID"),
        "coverage_source_run": COVERAGE_RUN,
        "gates": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print("Verified pinned Phase-0 raw SHA-256, configs, outcome and controls.")


if __name__ == "__main__":
    main()
