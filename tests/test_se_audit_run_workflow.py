"""Structural guards for the once-only SE-audit run workflow (no YAML dependency).

These do not execute the workflow. They pin the fail-closed properties named in
docs/SE_AUDIT_RUN_AUTHORIZATION.md so a later edit cannot silently weaken them.
They never draw audit seeds (2036101901).
"""
from pathlib import Path
import os
import re
import subprocess

from emergence_lab import spectral_s1 as s1

WF = Path(".github/workflows/se-audit-run.yml")
TEXT = WF.read_text()
CI = Path(".github/workflows/ci.yml").read_text()
SCRIPT = Path("scripts/run-se-audit-contained.sh").resolve()


def step_index(name: str) -> int:
    i = TEXT.find(name)
    assert i >= 0, name
    return i


def test_activation_flag_is_true_but_dispatch_remains_once_only():
    assert s1.SE_AUDIT_RUN_AUTHORIZED is True
    assert 'gh release view "$TAG"' in TEXT and "TAG: se-audit-run-v1" in TEXT


def test_dispatch_only_from_main_with_confirmation():
    on_block = TEXT[TEXT.index("\non:"):TEXT.index("\npermissions:")]
    assert "workflow_dispatch:" in on_block
    assert "push:" not in on_block and "pull_request" not in on_block and "schedule" not in on_block
    assert "if: github.ref == 'refs/heads/main'" in TEXT
    assert 'test "$CONFIRM" = SE-AUDIT-ONCE-2036101901' in TEXT
    assert "cancel-in-progress: false" in TEXT


def test_hosted_runner_and_no_lightsail_access():
    assert "runs-on: ubuntu-latest" in TEXT
    assert 'test "$RUNNER_ENVIRONMENT" = github-hosted' in TEXT
    for text in (TEXT.lower(), SCRIPT.read_text().lower()):
        for forbidden in ("lightsail_ssh", "secrets.", "ssh ", "18.158.243.28", "self-hosted"):
            assert forbidden not in text, forbidden


def test_guard_order_lock_then_marker_then_run():
    lock = step_index("assert s.SE_AUDIT_RUN_AUTHORIZED is True")
    once = step_index('gh release view "$TAG"')
    tests = step_index("run: pytest -q")
    marker = step_index('gh release create "$TAG"')
    run = step_index("sh scripts/run-se-audit-contained.sh")
    assert lock < once < tests < marker < run


def test_timeouts_cover_native_wall_stop_and_cpu_budget():
    script = SCRIPT.read_text()
    walls = sorted(int(w) for w in re.findall(r"wall_limit=(\d+)s", script))
    assert walls == [118, 5998]  # engineering, full SE audit
    assert walls[-1] < 100 * 60  # wall stop never extends the 100 CPU-min hard stop
    job = int(re.search(r"timeout-minutes: (\d+)\n    env:", TEXT).group(1))
    step = int(re.search(r"Contained SE-audit run.*\n        timeout-minutes: (\d+)", TEXT).group(1))
    assert walls[-1] / 60 < step < job <= 360


def test_evidence_archived_even_on_abort_and_never_overwritten():
    for name in ("Package evidence", "upload-artifact", "Archive non-overwriting"):
        tail = TEXT[step_index(name):]
        assert "if: always()" in tail[:400], name
    assert "Digest conflict" in TEXT and "sha256sum --check" in TEXT
    assert "--clobber" not in TEXT and "gh release delete" not in TEXT


def test_admissibility_requires_clean_resource_evidence_and_audit_seeds():
    tail = TEXT[step_index("Admissibility check"):]
    assert "resource_evidence.json" in tail and "resource_stop.json" in tail
    assert "clean_exit" in tail and "watchdog_failure" in tail
    assert "m['mode'] == 'se_audit'" in tail and "2036101901" in tail
    assert "s2_run_authorized'] is False" in tail


def test_release_archive_is_owned_by_this_invocation(tmp_path):
    """Execute the archive guard prefix without GitHub: denied runs cannot backfill assets."""
    archive = TEXT[step_index("Archive non-overwriting release assets"):]
    script = archive.split("        run: |\n", 1)[1].split("          test -s se_audit_run_evidence.tar.gz", 1)[0]
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
               GIT_SHA="abc123", TAG="se-audit-run-v1", GITHUB_REPOSITORY="example/repo",
               GH_CALLS=str(calls),
               RELEASE_BODY="STARTED by https://github.com/example/repo/actions/runs/100 at commit abc123, image sha256:1.")
    env["PATH"] = str(tmp_path) + os.pathsep + env.get("PATH", "")
    denied = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert denied.returncode == 0, denied.stderr
    assert not calls.exists()

    consume = TEXT[step_index("Consume seeds"):step_index("Contained SE-audit run")]
    writer = [line.strip() for line in consume.splitlines()
              if "se_audit_marker_created_by_this_run" in line and ">" in line]
    assert len(writer) == 1, writer
    made = subprocess.run(["bash", "-e", "-c", writer[0]], env=env, capture_output=True, text=True)
    assert made.returncode == 0, made.stderr
    assert (tmp_path / "se_audit_marker_created_by_this_run").read_text() == env["RUN_URL"] + "\n"
    env["RELEASE_BODY"] = "STARTED by https://github.com/example/repo/actions/runs/OLD at commit abc123, image old."
    mismatched = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert mismatched.returncode != 0
    assert calls.exists()

    env["RELEASE_BODY"] = "STARTED by " + env["RUN_URL"] + " at commit abc123, image sha256:1."
    matching = subprocess.run(["bash", "-c", guard], env=env, capture_output=True, text=True)
    assert matching.returncode == 0, matching.stderr


def test_contained_full_run_receives_this_invocations_marker_proof():
    run_step = TEXT[step_index("Contained SE-audit run"):step_index("Package evidence")]
    assert 'SE_AUDIT_ONCE_MARKER="$RUNNER_TEMP/se_audit_marker_created_by_this_run"' in run_step
    consume = TEXT[step_index("Consume seeds"):step_index("Contained SE-audit run")]
    assert '> "$RUNNER_TEMP/se_audit_marker_created_by_this_run"' in consume


def test_ci_never_forges_marker_or_seed_gate():
    """Tripwire: with the flag True, a fake marker or env gate in CI would draw audit seeds."""
    assert "SE-audit full mode refuses without once-only marker proof" in CI
    assert "SE-audit engineering containment smoke" in CI
    assert "SE_AUDIT_ONCE_MARKER" not in CI and "SE_AUDIT_ALLOW_SEEDS" not in CI
    assert "se-audit-run.yml" not in CI


def _script_env(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "--allow-empty", "-m", "t"], check=True)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    docker = bindir / "docker"
    docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$DOCKER_CALLS"\n')
    docker.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("RUN_URL", "SE_AUDIT_ONCE_MARKER")}
    env.update(PATH=f"{bindir}{os.pathsep}{env.get('PATH', '')}", S1B_HOST_CLASS="non-lightsail",
               DOCKER_CALLS=str(tmp_path / "docker_calls"))
    return repo, env


def _contained(repo, env, out, *extra):
    return subprocess.run(["sh", str(SCRIPT), "sha256:0", str(out), *extra], cwd=repo, env=env,
                          capture_output=True, text=True)


def test_contained_full_mode_requires_marker_proof_before_docker(tmp_path):
    repo, env = _script_env(tmp_path)
    calls = tmp_path / "docker_calls"
    url = "https://github.com/o/r/actions/runs/7"
    proof = tmp_path / "proof"
    cases = [
        ({}, "no proof, no RUN_URL"),
        ({"RUN_URL": url}, "no proof"),
        ({"SE_AUDIT_ONCE_MARKER": str(proof)}, "proof but no RUN_URL"),
        ({"RUN_URL": url, "SE_AUDIT_ONCE_MARKER": str(tmp_path / "missing")}, "missing proof file"),
        ({"RUN_URL": url + "8", "SE_AUDIT_ONCE_MARKER": str(proof)}, "proof of another invocation"),
        ({"RUN_URL": url, "S1B_ONCE_MARKER": str(proof)}, "S1b marker variable is not accepted"),
    ]
    proof.write_text(url + "\n")
    for i, (extra, label) in enumerate(cases):
        out = tmp_path / f"out{i}"
        r = _contained(repo, dict(env, **extra), out)
        assert r.returncode == 2, label
        assert "once-only marker proof" in r.stderr, label
        assert not out.exists() and not calls.exists(), label
    empty = tmp_path / "empty"
    empty.write_text("")
    r = _contained(repo, dict(env, RUN_URL="", SE_AUDIT_ONCE_MARKER=str(empty)), tmp_path / "out_empty")
    assert r.returncode == 2 and not calls.exists()

    ok = _contained(repo, dict(env, RUN_URL=url, SE_AUDIT_ONCE_MARKER=str(proof)), tmp_path / "out_ok")
    assert ok.returncode == 0, ok.stderr
    args = calls.read_text()
    assert "--mode se_audit" in args and "SE_AUDIT_ALLOW_SEEDS=1" in args and "--network none" in args
    assert "spectral_se_audit" in args and "--cpus 1" in args and "--memory 2g" in args


def test_contained_engineering_needs_no_marker_and_never_opens_seed_gate(tmp_path):
    repo, env = _script_env(tmp_path)
    r = _contained(repo, env, tmp_path / "eng", "engineering")
    assert r.returncode == 0, r.stderr
    args = (tmp_path / "docker_calls").read_text()
    assert "--mode engineering --contained-engineering --no-controls" in args
    assert "SE_AUDIT_ALLOW_SEEDS=0" in args and "SE_AUDIT_ALLOW_SEEDS=1" not in args


def test_contained_script_refuses_without_host_attestation(tmp_path):
    repo, env = _script_env(tmp_path)
    env.pop("S1B_HOST_CLASS")
    r = _contained(repo, env, tmp_path / "eng", "engineering")
    assert r.returncode == 2 and "non-Lightsail" in r.stderr
    assert not (tmp_path / "docker_calls").exists() and not (tmp_path / "eng").exists()
