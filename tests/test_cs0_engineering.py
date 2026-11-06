"""Miniature engineering artifacts only; no gated CS0 data or full seed."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from emergence_lab.cs0_engineering import run_engineering, verify_sources


@pytest.fixture
def source_checkout(tmp_path):
    root = tmp_path / 'repo'
    source = Path(__file__).resolve().parents[1]
    package = root / 'src/emergence_lab'
    package.mkdir(parents=True)
    for name in ('__init__', 'causal_set_mm', 'cs0_worker', 'cs0_recheck',
                 'cs0_supervisor', 'cs0_engineering', 'cs0_artifacts'):
        relative = f'src/emergence_lab/{name}.py'
        (root / relative).write_bytes((source / relative).read_bytes())
    (root / '.gitignore').write_text('src/**/ignored*\nsrc/**/__pycache__/\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=t@example.invalid',
                    'commit', '-qm', 'fixture'], cwd=root, check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    return root, commit


def test_engineering_end_to_end(source_checkout, tmp_path):
    root, commit = source_checkout
    output = tmp_path / 'out'
    # Load the launcher itself from the pinned fixture checkout, not this test's
    # already-imported package. Isolate source-cache lookup for the parent too.
    bootstrap = ('import sys; sys.path.insert(0, ' + repr(str(root / 'src')) +
                 '); from emergence_lab.cs0_engineering import main; sys.exit(main())')
    process = subprocess.run([sys.executable, '-I', '-B', '-X',
        f'pycache_prefix={tmp_path / "launcher-cache"}', '-c', bootstrap,
        '--root', str(root), '--commit', commit, '--output', str(output)],
        text=True, capture_output=True, timeout=45,
        env={**__import__('os').environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
    assert process.returncode == 0, process.stderr + process.stdout
    record = json.loads(process.stdout)
    assert record['outcome'] == 'COMPLETE', record
    assert record['rows'] == 40
    assert record['study_authorized'] is False
    assert record['aggregate_caps_enforced'] is False
    assert record['inner_artifact_slots_verified'] is True
    assert record['inner_artifact_bound_bytes'] == 9_000_000
    assert record['report_verdict'] == 'ENGINEERING_ONLY'
    assert record == json.loads((output / 'manifest.json').read_text())
    report = json.loads((output / 'report.json').read_text())
    assert report['scientific_acceptance'] is False
    assert (output / 'measurements.csv').read_text().count('\n') == 41
    assert set(record['artifacts']) == {
        'worker/manifest.json', 'worker/worker.bin', 'measurements.csv', 'report.json'}
    assert record['payload_bytes'] == sum(x['bytes'] for x in record['artifacts'].values())
    assert record['observed_aggregate_cpu_seconds'] > 0
    assert list((output / 'empty-pycache').iterdir()) == []


@pytest.mark.parametrize('kind', ['assume-unchanged', 'skip-worktree', 'ignored-module', 'ignored-extension'])
def test_status_hidden_sources_refuse(source_checkout, tmp_path, kind):
    root, commit = source_checkout
    target = root / 'src/emergence_lab/cs0_worker.py'
    if kind in ('assume-unchanged', 'skip-worktree'):
        subprocess.run(['git', 'update-index', f'--{kind}', str(target.relative_to(root))],
                       cwd=root, check=True)
        target.write_text(target.read_text() + '\n# hidden modification\n')
    else:
        (target.parent / ('ignored.py' if kind == 'ignored-module' else 'ignored.so')).write_bytes(b'bad')
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=root)
    with pytest.raises(ValueError, match='source bytes differ|unexpected file'):
        verify_sources(root, commit)
    record = run_engineering(root, commit, tmp_path / 'out')
    assert record['outcome'] == 'INCOMPLETE'
    assert not (tmp_path / 'out/worker').exists()


def test_symlink_source_refused(source_checkout):
    root, commit = source_checkout
    target = root / 'src/emergence_lab/cs0_worker.py'
    target.unlink()
    target.symlink_to(root / 'src/emergence_lab/causal_set_mm.py')
    with pytest.raises(ValueError):
        verify_sources(root, commit)


def test_wrong_commit_durable_incomplete(source_checkout, tmp_path):
    root, _ = source_checkout
    record = run_engineering(root, '0' * 40, tmp_path / 'out')
    assert record['outcome'] == 'INCOMPLETE'
    assert 'source_sha256' not in record
    assert record == json.loads((tmp_path / 'out/manifest.json').read_text())


def test_output_inside_checkout_refuses(source_checkout):
    root, commit = source_checkout
    with pytest.raises(ValueError, match='outside'):
        run_engineering(root, commit, root / 'results')
    assert not (root / 'results').exists()


def test_installed_or_other_checkout_launcher_refuses(source_checkout, tmp_path):
    root, commit = source_checkout
    record = run_engineering(root, commit, tmp_path / 'out')
    assert record['outcome'] == 'INCOMPLETE'
    assert 'runtime origin differs' in record['error']
    assert not (tmp_path / 'out/worker').exists()


def test_only_inert_editable_install_metadata_is_allowed(source_checkout):
    root, commit = source_checkout
    metadata = root / 'src/emergence_lab.egg-info'
    metadata.mkdir()
    # Match the real repository's ignored editable-install metadata.
    with (root / '.git/info/exclude').open('a') as stream:
        stream.write('\n*.egg-info/\n')
    (metadata / 'PKG-INFO').write_text('Metadata-Version: 2.4\n')
    verify_sources(root, commit)
    (metadata / 'shadow.py').write_text('raise Exception()')
    with pytest.raises(ValueError, match='unexpected file'):
        verify_sources(root, commit)


def test_oversized_source_metadata_leaves_minimal_durable_incomplete(source_checkout, tmp_path,
                                                                   monkeypatch):
    from emergence_lab import cs0_engineering as engineering
    monkeypatch.setattr(engineering, 'verify_sources', lambda *args: {'source': 'x' * 2_000_000})
    monkeypatch.setattr(engineering, 'verify_runtime', lambda *args: None)
    root, commit = source_checkout
    record = run_engineering(root, commit, tmp_path / 'out')
    assert record['outcome'] == 'INCOMPLETE'
    assert record['stage'] == 'checkpoint-fallback'
    assert record == json.loads((tmp_path / 'out/manifest.json').read_text())
    assert not (tmp_path / 'out/worker').exists()
    assert (tmp_path / 'out/manifest.json').stat().st_size < 1024


@pytest.mark.parametrize('commit', [None, object(), 'x' * 2_000_000])
def test_invalid_commit_metadata_never_prevents_initial_checkpoint(source_checkout, tmp_path,
                                                                  commit):
    record = run_engineering(source_checkout[0], commit, tmp_path / 'out')
    assert record['outcome'] == 'INCOMPLETE'
    assert 'commit' not in record
    assert record == json.loads((tmp_path / 'out/manifest.json').read_text())
