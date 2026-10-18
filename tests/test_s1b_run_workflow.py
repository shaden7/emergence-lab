"""Structural guards for the proposed once-only S1b run workflow (no YAML dependency).

These do not execute the workflow. They pin the fail-closed properties named in
docs/S1B_RUN_AUTHORIZATION.md so a later edit cannot silently weaken them.
"""
from pathlib import Path
import re
import os
import subprocess

from emergence_lab import spectral_s1 as s1

WF = Path(".github/workflows/s1b-run.yml")
TEXT = WF.read_text()


def step_index(name: str) -> int:
    i = TEXT.find(name)
    assert i >= 0, name
    return i


def test_lock_still_false_in_this_revision():
    assert s1.S1B_RUN_AUTHORIZED is False


def test_dispatch_only_from_main_with_confirmation():
    on_block = TEXT[TEXT.index("\non:"):TEXT.index("\npermissions:")]
    assert "workflow_dispatch:" in on_block
    assert "push:" not in on_block and "pull_request" not in on_block and "schedule" not in on_block
    assert "if: github.ref == 'refs/heads/main'" in TEXT
    assert 'test "$CONFIRM" = S1B-ONCE-2036101701' in TEXT
    assert "cancel-in-progress: false" in TEXT


def test_hosted_runner_and_no_lightsail_access():
    assert "runs-on: ubuntu-latest" in TEXT
    assert 'test "$RUNNER_ENVIRONMENT" = github-hosted' in TEXT
    lowered = TEXT.lower()
    for forbidden in ("lightsail_ssh", "secrets.", "ssh ", "18.158.243.28", "self-hosted"):
        assert forbidden not in lowered, forbidden


def test_guard_order_lock_then_marker_then_run():
    lock = step_index("assert s.S1B_RUN_AUTHORIZED is True")
    once = step_index('gh release view "$TAG"')
    marker = step_index('gh release create "$TAG"')
    run = step_index("sh scripts/run-s1b-contained.sh")
    assert lock < once < marker < run


def test_timeouts_cover_native_wall_stop():
    script = Path("scripts/run-s1b-contained.sh").read_text()
    walls = sorted(int(w) for w in re.findall(r"wall_limit=(\d+)s", script))
    assert walls == [118, 11998]  # engineering, full S1b
    wall_s = walls[-1]
    job = int(re.search(r"timeout-minutes: (\d+)\n    env:", TEXT).group(1))
    step = int(re.search(r"Contained S1b run.*\n        timeout-minutes: (\d+)", TEXT).group(1))
    assert wall_s / 60 < step < job <= 360


def test_evidence_archived_even_on_abort_and_never_overwritten():
    for name in ("Package evidence", "upload-artifact", "Archive non-overwriting"):
        tail = TEXT[step_index(name):]
        assert "if: always()" in tail[:400], name
    assert "Digest conflict" in TEXT and "sha256sum --check" in TEXT
    assert "--clobber" not in TEXT and "gh release delete" not in TEXT


def test_admissibility_requires_clean_resource_evidence():
    tail = TEXT[step_index("Admissibility check"):]
    assert "resource_evidence.json" in tail and "resource_stop.json" in tail
    assert "clean_exit" in tail and "watchdog_failure" in tail


def test_release_archive_is_owned_by_this_invocation(tmp_path):
    """Execute archive guard prefix without GitHub: denied runs cannot backfill assets."""
    archive = TEXT[step_index("Archive non-overwriting release assets"):]
    script = archive.split("        run: |\n", 1)[1].split("          test -s s1b_run_evidence.tar.gz", 1)[0]
    lines = [line[10:] for line in script.splitlines() if line.strip()]
    guard = "set -e\n" + "\n".join(lines) + "\n"
    gh = tmp_path / "gh"
    calls = tmp_path / "gh_calls"
    gh.write_text('#!/bin/sh\n'
                  'echo called >> "$GH_CALLS"\n'
                  'printf "%s\\n" "$RELEASE_BODY"\n')
    gh.chmod(0o755)
    env = dict(os.environ, RUNNER_TEMP=str(tmp_path),
               RUN_URL="https://github.com/example/repo/actions/runs/100",
               GIT_SHA="abc123", TAG="s1b-run-v1", GITHUB_REPOSITORY="example/repo",
               GH_CALLS=str(calls),
               RELEASE_BODY="STARTED by https://github.com/example/repo/actions/runs/100 at commit abc123, image sha256:1.")
    env["PATH"] = str(tmp_path) + os.pathsep + env.get("PATH", "")
    denied = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert denied.returncode == 0, denied.stderr
    assert not calls.exists()

    (tmp_path / "s1b_marker_created_by_this_run").write_text(env["RUN_URL"] + "\n")
    env["RELEASE_BODY"] = "STARTED by https://github.com/example/repo/actions/runs/OLD at commit abc123, image old."
    mismatched = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert mismatched.returncode != 0
    assert calls.exists()

    env["RELEASE_BODY"] = "STARTED by " + env["RUN_URL"] + " at commit abc123, image sha256:1."
    matching = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert matching.returncode == 0, matching.stderr
