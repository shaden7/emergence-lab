"""Wrapper contract only: fake Docker does not test kernel containment."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/run-cs0-engineering-contained.sh'
IMAGE = 'sha256:' + 'a' * 64


@pytest.fixture
def setup(tmp_path):
    root, binary, output = tmp_path / 'repo', tmp_path / 'bin', tmp_path / 'output'
    root.mkdir(); binary.mkdir()
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'source.txt').write_text('fixture\n')
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=t@example.invalid',
                    'commit', '-qm', 'fixture'], cwd=root, check=True)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    fake = binary / 'docker'
    fake.write_text(f'#!{sys.executable}\n' + '''
import json,os,pathlib,sys
output=pathlib.Path(os.environ['TEST_OUTPUT'])
assert json.loads((output/'envelope.json').read_text())['outcome']=='INCOMPLETE'
pathlib.Path(os.environ['TEST_CAPTURE']).write_text(json.dumps(sys.argv[1:]))
if os.environ.get('TEST_LOG_FLOOD')=='1':
    for _ in range(48): os.write(1,b'x'*65536)
if os.environ.get('TEST_SUCCESS')=='1':
    (output/'payload/run').mkdir()
    (output/'payload/run/manifest.json').write_text(json.dumps(dict(outcome='COMPLETE',
        mode='engineering',study_authorized=False,rows=40,
        report_verdict='ENGINEERING_ONLY',commit=os.environ['TEST_REVISION'],
        inner_artifact_slots_verified=True,inner_artifact_bound_bytes=9000000,
        inner_artifact_slots={p:1000000 for p in ('manifest.json','manifest.tmp',
            'worker/manifest.json','worker/manifest.tmp','worker/worker.bin',
            'measurements.csv','measurements.tmp','report.json','report.tmp')})))
if os.environ.get('TEST_MISSING_BUDGET')=='1':
    path=output/'payload/run/manifest.json'
    record=json.loads(path.read_text()); record.pop('inner_artifact_slots_verified')
    path.write_text(json.dumps(record))
if os.environ.get('TEST_STALE_SUCCESS')=='1':
    path=output/'envelope.json'
    record=json.loads(path.read_text()); record['outcome']='ENGINEERING_COMPLETE'
    path.write_text(json.dumps(record))
if os.environ.get('TEST_RICH_ANCHOR')=='1':
    path=output/'envelope.json'
    record=json.loads(path.read_text()); record['noise']='\u2603'*3000
    path.write_text(json.dumps(record,ensure_ascii=False))
if os.environ.get('TEST_OVERSIZED_ANCHOR')=='1':
    (output/'envelope.json').write_text('x'*32768)
sys.exit(int(os.environ.get('TEST_STATUS','0')))
''')
    fake.chmod(0o755)
    env = {**os.environ, 'PATH': str(binary) + os.pathsep + os.environ['PATH'],
           'CS0_HOST_CLASS': 'non-lightsail', 'TEST_OUTPUT': str(output),
           'TEST_CAPTURE': str(tmp_path / 'capture.json'), 'TEST_REVISION': revision}
    return root, output, env


def invoke(setup, args=None, **environment):
    root, output, env = setup
    return subprocess.run(['sh', str(SCRIPT), *(args if args is not None else [IMAGE, str(output)])],
                          cwd=root, env={**env, **environment}, capture_output=True, text=True, timeout=10)


@pytest.mark.parametrize('image', ['tag:latest', 'sha256:a', 'sha256:' + 'g' * 64])
def test_invalid_image_refuses_before_docker(setup, image):
    result = invoke(setup, [image, str(setup[1])])
    assert result.returncode == 2
    assert not setup[1].exists()


def test_full_argument_and_wrong_host_refuse_before_docker(setup):
    assert invoke(setup, [IMAGE, str(setup[1]), 'full']).returncode == 2
    assert invoke(setup, CS0_HOST_CLASS='lightsail').returncode == 2
    assert not setup[1].exists()


def test_container_failure_retains_durable_incomplete(setup):
    assert invoke(setup, TEST_STATUS='137').returncode == 2
    record = json.loads((setup[1] / 'envelope.json').read_text())
    assert record['outcome'] == 'INCOMPLETE' and record['docker_exit_code'] == 137
    assert not record['aggregate_output_cap_enforced']


def test_matching_engineering_completion_and_container_flags(setup):
    assert invoke(setup, TEST_SUCCESS='1').returncode == 0
    record = json.loads((setup[1] / 'envelope.json').read_text())
    assert record['outcome'] == 'ENGINEERING_COMPLETE' and not record['study_authorized']
    assert record['fixed_pipeline_output_budget_enforced'] is True
    assert record['fixed_pipeline_output_bound_bytes'] == 11129920
    args = json.loads(Path(setup[2]['TEST_CAPTURE']).read_text())
    for flag, value in (('--memory', '1g'), ('--memory-swap', '1g'), ('--cpus', '1'),
                        ('--network', 'none'), ('--pids-limit', '64')):
        assert args[args.index(flag) + 1] == value
    assert '--read-only' in args and '--signal=KILL' in args and '30s' in args
    assert 'full' not in args and '--entropy' not in args
    mounts = [args[i + 1] for i, value in enumerate(args) if value == '--mount']
    assert f'type=bind,src={setup[1]}/payload,dst=/results' in mounts
    assert f'type=bind,src={setup[1]},dst=/results' not in mounts


def test_zero_exit_without_inner_completion_cannot_succeed(setup):
    assert invoke(setup).returncode == 2
    assert json.loads((setup[1] / 'envelope.json').read_text())['outcome'] == 'INCOMPLETE'


def test_stale_success_cannot_survive_finalizer_failure(setup):
    assert invoke(setup, TEST_STALE_SUCCESS='1', TEST_STATUS='137').returncode == 2
    assert json.loads((setup[1] / 'envelope.json').read_text())['outcome'] == 'INCOMPLETE'


def test_dirty_checkout_and_existing_output_are_not_overwritten(setup):
    (setup[0] / 'source.txt').write_text('dirty\n')
    assert invoke(setup).returncode == 2
    assert not setup[1].exists()
    subprocess.run(['git', 'checkout', '--', 'source.txt'], cwd=setup[0], check=True)
    setup[1].mkdir()
    marker = setup[1] / 'keep.txt'
    marker.write_text('keep')
    assert invoke(setup).returncode != 0
    assert marker.read_text() == 'keep'
    assert not (setup[1] / 'envelope.json').exists()


def test_log_flood_stops_and_preserves_bounded_incomplete(setup):
    assert invoke(setup, TEST_LOG_FLOOD='1').returncode == 2
    record = json.loads((setup[1] / 'envelope.json').read_text())
    assert record['outcome'] == 'INCOMPLETE'
    assert 0 < (setup[1] / 'container.log').stat().st_size <= 2097152
    assert (setup[1] / 'envelope.json').stat().st_size <= 16384
    assert not record['fixed_pipeline_output_budget_enforced']


@pytest.mark.parametrize('kind', ['TEST_RICH_ANCHOR', 'TEST_OVERSIZED_ANCHOR'])
def test_oversized_host_record_has_minimal_bounded_failure(setup, kind):
    assert invoke(setup, TEST_SUCCESS='1', **{kind: '1'}).returncode == 2
    path = setup[1] / 'envelope.json'
    record = json.loads(path.read_text())
    assert record['outcome'] == 'INCOMPLETE' and not record['study_authorized']
    assert not record['fixed_pipeline_output_budget_enforced']
    assert path.stat().st_size <= 16384
    assert len(record['error'].encode()) <= 4096
    assert not (setup[1] / 'envelope.tmp').exists()


def test_inner_completion_without_reviewed_slot_proof_is_incomplete(setup):
    assert invoke(setup, TEST_SUCCESS='1', TEST_MISSING_BUDGET='1').returncode == 2
    record = json.loads((setup[1] / 'envelope.json').read_text())
    assert record['outcome'] == 'INCOMPLETE'
    assert not record['fixed_pipeline_output_budget_enforced']
    assert 'artifact-bound evidence' in record['error']
