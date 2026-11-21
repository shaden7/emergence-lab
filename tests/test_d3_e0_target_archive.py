"""The archived D3-E0/M0 v1 target run is internally consistent with its pins."""
import csv
import hashlib
import json

from emergence_lab import d3_e0_campaign as c

D = c.REPO / "docs/experiments/d3-e0-v1-target-20261120"
AUTH = c.REPO / "docs/experiments/d3-e0-v1-target-auth-20261119/authorization.json"


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_target_archive_provenance_and_table():
    m = json.loads((D / "manifest.json").read_text())
    a = json.loads(AUTH.read_text())
    assert m["mode"] == "target" and m["status"] == "COMPLETE"
    assert m["authorization_id"] == a["authorization_id"]
    assert m["config_sha256"] == a["config_sha256"] and m["protocol_sha256"] == a["protocol_sha256"]
    assert m["git_dirty_pinned"] is False
    assert m["seed_roots"]["target"] == json.loads(c.CONFIG.read_text())["seed_roots"]["target"]
    assert m["raw_counts_sha256"] == _sha(D / "raw_counts.npz")
    assert all(g["passed"] for g in m["gates"].values())
    assert m["cpu_s"] < 600 and m["peak_rss_mib"] < 512
    rows = list(csv.DictReader((D / "cells.csv").open()))
    assert len(rows) == 17 and all(r["label"] in ("ABOVE", "BELOW") for r in rows)
    rev = sorted(int(r["N"]) for r in rows if r["arm"] == "B" and r["label"] == "ABOVE"
                 and any(q["arm"] == "A" and q["N"] == r["N"] and q["label"] == "BELOW" for q in rows))
    assert rev == m["sign_reversal_N"]
