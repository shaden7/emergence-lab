"""Pilot B blind-key beacon: drand *quicknet* round arithmetic and verification.

Preregistration v1.0-r1 section 6.3: R is the first quicknet round whose timestamp is
>= 24 h after the stage-1 merge commit on main; the key is derived from R and the
round's 32-byte ``randomness``. This module:

* pins the quicknet chain parameters (``QUICKNET``) -- the pins are *claims to be checked*,
  and ``check_chain`` (run in GitHub Actions; the sandbox proxy blocks drand) compares
  them with the ``/info`` document served by several independent relays;
* implements round <-> time arithmetic (round 1 at genesis, one round per period);
* verifies a round record: ``randomness == SHA-256(signature)`` and the BLS signature
  (scheme bls-unchained-g1-rfc9380: signature in G1, public key in G2,
  message SHA-256(uint64_be(round)), DST below) using py_ecc.

Fail closed: any mismatch, missing library or network error raises.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import urllib.request

QUICKNET = {
    "hash": "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971",
    "public_key": ("83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c"
                   "8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb"
                   "5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a"),
    "period": 3,
    "genesis_time": 1692803367,
    "schemeID": "bls-unchained-g1-rfc9380",
}
DST_G1 = b"BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"
RELAYS = ("https://api.drand.sh", "https://api2.drand.sh", "https://api3.drand.sh",
          "https://drand.cloudflare.com")
BLIND_DELAY_SECONDS = 24 * 3600


# --------------------------------------------------------------------- arithmetic
def round_time(round_number: int, genesis: int = QUICKNET["genesis_time"],
               period: int = QUICKNET["period"]) -> int:
    if round_number < 1:
        raise ValueError("drand rounds start at 1")
    return genesis + (round_number - 1) * period


def first_round_at_or_after(unix_time: int, genesis: int = QUICKNET["genesis_time"],
                            period: int = QUICKNET["period"]) -> int:
    if unix_time <= genesis:
        return 1
    return -(-(unix_time - genesis) // period) + 1  # ceil division


def blind_round_for_merge(merge_iso: str) -> dict:
    """R for a stage-1 merge-commit timestamp (ISO 8601, UTC 'Z' or offset)."""
    t = dt.datetime.fromisoformat(merge_iso.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("merge timestamp must carry a timezone")
    target = int(math.ceil(t.timestamp())) + BLIND_DELAY_SECONDS
    r = first_round_at_or_after(target)
    return {"merge_time": merge_iso, "target_unix": target, "round": r,
            "round_unix": round_time(r),
            "round_utc": dt.datetime.fromtimestamp(round_time(r), dt.timezone.utc).isoformat()}


# ------------------------------------------------------------------- verification
def round_message(round_number: int) -> bytes:
    return hashlib.sha256(round_number.to_bytes(8, "big")).digest()


def verify_bls_g1(signature: bytes, public_key: bytes, message: bytes) -> bool:
    from py_ecc.bls.hash_to_curve import hash_to_G1
    from py_ecc.bls.point_compression import decompress_G1, decompress_G2
    from py_ecc.optimized_bls12_381 import G2, pairing, is_on_curve, b, b2, curve_order, multiply, is_inf

    if len(signature) != 48 or len(public_key) != 96:
        return False
    sig = decompress_G1(int.from_bytes(signature, "big"))
    pk = decompress_G2((int.from_bytes(public_key[:48], "big"), int.from_bytes(public_key[48:], "big")))
    if is_inf(sig) or is_inf(pk) or not is_on_curve(sig, b) or not is_on_curve(pk, b2):
        return False
    if not is_inf(multiply(sig, curve_order)) or not is_inf(multiply(pk, curve_order)):
        return False  # subgroup checks
    h = hash_to_G1(message, DST_G1, hashlib.sha256)
    return pairing(G2, sig) == pairing(pk, h)


def verify_round(record: dict, public_key_hex: str = QUICKNET["public_key"]) -> dict:
    r = int(record["round"])
    sig = bytes.fromhex(record["signature"])
    rand_ok = hashlib.sha256(sig).hexdigest() == record["randomness"].lower()
    bls_ok = verify_bls_g1(sig, bytes.fromhex(public_key_hex), round_message(r))
    return {"round": r, "randomness": record["randomness"].lower(), "signature": record["signature"],
            "randomness_is_sha256_signature": rand_ok, "signature_verified": bool(rand_ok and bls_ok)}


# ------------------------------------------------------------------------ network
def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "emergence-lab-pilot-b"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())


def check_chain(relays=RELAYS, min_agree: int = 2) -> dict:
    """Compare pinned quicknet parameters with relay /info documents; verify the latest round."""
    report = {"pinned": QUICKNET, "relays": {}}
    agree = 0
    for base in relays:
        try:
            info = _get(f"{base}/{QUICKNET['hash']}/info")
        except Exception as exc:  # recorded, not fatal unless too few relays agree
            report["relays"][base] = {"error": repr(exc)}
            continue
        fields = {k: info.get(k) for k in ("hash", "public_key", "period", "genesis_time", "schemeID")}
        ok = fields == QUICKNET
        report["relays"][base] = {"info": fields, "matches_pin": ok}
        agree += ok
    report["relays_matching"] = agree
    latest = _get(f"{RELAYS[0]}/{QUICKNET['hash']}/public/latest")
    v = verify_round(latest)
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    v["round_unix"] = round_time(v["round"])
    v["seconds_behind_now"] = now - v["round_unix"]
    report["latest"] = v
    # Round arithmetic sanity: the latest published round must be (about) the current round.
    report["arithmetic_ok"] = 0 <= v["seconds_behind_now"] < 60
    report["ok"] = bool(agree >= min_agree and v["signature_verified"] and report["arithmetic_ok"])
    return report


def fetch_verified_round(round_number: int, relays=RELAYS) -> dict:
    """Fetch round R from the first relay that answers and verify it (fails closed)."""
    errors = []
    for base in relays:
        try:
            rec = _get(f"{base}/{QUICKNET['hash']}/public/{round_number}")
        except Exception as exc:
            errors.append(f"{base}: {exc!r}")
            continue
        if int(rec["round"]) != round_number:
            raise RuntimeError("relay returned a different round")
        v = verify_round(rec)
        if not v["signature_verified"]:
            raise RuntimeError(f"round {round_number} failed verification from {base}")
        v["source_url"] = f"{base}/{QUICKNET['hash']}/public/{round_number}"
        v["chain_hash"] = QUICKNET["hash"]
        return v
    raise RuntimeError("no relay answered: " + "; ".join(errors))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pilot B drand quicknet beacon utilities")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-chain")
    rm = sub.add_parser("round-for-merge")
    rm.add_argument("merge_time")
    fr = sub.add_parser("fetch-round")
    fr.add_argument("round", type=int)
    a = ap.parse_args(argv)
    if a.cmd == "check-chain":
        rep = check_chain()
        print(json.dumps(rep, indent=1, sort_keys=True))
        return 0 if rep["ok"] else 1
    if a.cmd == "round-for-merge":
        print(json.dumps(blind_round_for_merge(a.merge_time), indent=1))
        return 0
    print(json.dumps(fetch_verified_round(a.round), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
