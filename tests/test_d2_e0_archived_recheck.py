"""Audit stored D2-E0 evidence; never invoke the target worker or regenerate a curve."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

pytest.importorskip('mpmath')
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/experiments/d2-e0-v1-20261111'
spec = importlib.util.spec_from_file_location('e0_archive_recheck', ROOT/'docs/experiments/d2_e0_recheck.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_archived_result_independent_reanalysis():
    report = module.recheck(DATA)
    assert report['outcome'] == 'RECHECK_PASS'
    assert report['support_fractions'] == 3921
    assert report['enumerated_permutations'] == 5914
    assert all(row['endpoint_mean_dimension'] < 2 for row in report['rows'])


@pytest.mark.parametrize('tamper', ['stale_digest', 'forged_law_with_updated_digests'])
def test_archived_reanalysis_rejects_tampering(tmp_path, tamper):
    manifest = json.loads((DATA/'manifest.json').read_bytes())
    compressed = (DATA/'reference.json.gz').read_bytes()
    if tamper == 'stale_digest':
        manifest['reference_sha256'] = '0'*64
    else:
        payload = json.loads(gzip.decompress(compressed))
        payload['weights'][2]['counts'][0] += 1
        raw = json.dumps(payload).encode()
        compressed = gzip.compress(raw)
        manifest['reference_sha256'] = hashlib.sha256(compressed).hexdigest()
        manifest['raw_sha256'] = hashlib.sha256(raw).hexdigest()
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    (tmp_path/'reference.json.gz').write_bytes(compressed)
    with pytest.raises(AssertionError):
        module.recheck(tmp_path)
