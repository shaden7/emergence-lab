"""The committed D3-E0/M0 v1 target authorization pins the current frozen files.

Expiry is deliberately not tested here (it would make CI time-dependent);
``check_authorization`` enforces it at run time.
"""
import hashlib
import json
import subprocess

from emergence_lab import d3_e0_campaign as c

AUTH = c.REPO / "docs/experiments/d3-e0-v1-target-auth-20261119/authorization.json"


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_authorization_pins_match_head():
    a = json.loads(AUTH.read_text())
    assert a["protocol"] == "D3-E0/M0 v1" and a["mode"] == "target"
    assert a["config_sha256"] == _sha(c.CONFIG)
    assert a["protocol_sha256"] == _sha(c.PROTOCOL)
    assert set(a["blobs"]) == set(c.PINNED_PATHS)
    for p in c.PINNED_PATHS:
        blob = subprocess.check_output(["git", "rev-parse", f"HEAD:{p}"], cwd=c.REPO, text=True).strip()
        assert a["blobs"][p] == blob, p
    pilot = c.REPO / a["pilot_record"]
    assert _sha(pilot) == a["pilot_record_sha256"]
    rec = json.loads(pilot.read_text())
    assert rec["status"] == "PILOT_COMPLETE" and rec["target_sizes"]["status"] == "OK"
    assert rec["seed_root"] != json.loads(c.CONFIG.read_text())["seed_roots"]["target"]
