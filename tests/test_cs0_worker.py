"""Small engineering-only row/protocol checks; never draw full CS0 seeds."""
import json

import numpy as np
import pytest

from emergence_lab import cs0_worker as worker


def test_design_is_frozen_and_returns_defensive_copies():
    full = worker.design('full')
    assert full['sizes'] == [128, 256, 512, 1024]
    assert full['replicates'] == 30
    assert len(full['sizes']) * (6 * full['replicates'] + 2) == 728
    full['sizes'].clear()
    full['family_indices'].clear()
    assert worker.design('full')['sizes'] == [128, 256, 512, 1024]
    assert worker.design('full')['family_indices']['diamond'] == 0
    with pytest.raises(ValueError):
        worker.design('pilot')


@pytest.mark.parametrize('entropy', [-1, True, None, 3.0, '3', worker.ENGINEERING_ENTROPY + 1])
def test_engineering_entropy_cannot_vary(entropy):
    with pytest.raises(ValueError):
        list(worker.generate_rows(entropy, 'engineering'))


def test_engineering_rows_are_deterministic_complete_and_json_safe():
    first = list(worker.generate_rows(worker.ENGINEERING_ENTROPY, 'engineering'))
    assert first == list(worker.generate_rows(worker.ENGINEERING_ENTROPY, 'engineering'))
    assert len(first) == 40
    assert len({tuple(row['spawn_key']) for row in first}) == 40
    assert {row['N'] for row in first} == {8, 12}
    assert {row['family'] for row in first} == set(worker.FAMILY_INDICES)
    json.dumps(first, allow_nan=False)
    for row in first:
        assert set(row) == {'family', 'D_or_k', 'N', 'rep', 'spawn_key', 'R', 'r',
                            'd_mm', 'classification'}
        pairs = row['N'] * (row['N'] - 1) // 2
        assert 0 <= row['R'] <= pairs
        assert row['r'] == row['R'] / pairs
        assert row['spawn_key'] == [worker.FAMILY_INDICES[row['family']],
                                    row['D_or_k'], row['N'], row['rep']]
        if row['family'] == 'chain':
            assert (row['R'], row['r'], row['d_mm'], row['classification']) == (
                pairs, 1.0, 1.0, 'TOTAL_ORDER')
        elif row['family'] == 'antichain':
            assert (row['R'], row['r'], row['d_mm'], row['classification']) == (
                0, 0.0, None, 'OUT_OF_RANGE')


def test_outside_diamond_is_refused_before_measurement(monkeypatch):
    monkeypatch.setattr(worker.mm, 'sprinkle_diamond',
                        lambda n, d, rng: np.ones((n, d)))
    with pytest.raises(ValueError, match='outside'):
        next(worker.generate_rows(worker.ENGINEERING_ENTROPY, 'engineering'))


def test_invalid_exact_control_is_refused(monkeypatch):
    monkeypatch.setattr(worker.mm, 'chain', lambda n: np.eye(n, dtype=bool))
    with pytest.raises(ValueError, match='irreflexive'):
        list(worker.generate_rows(worker.ENGINEERING_ENTROPY, 'engineering'))


def test_every_order_is_checked(monkeypatch):
    original = worker.mm.check_partial_order
    checked = []
    def check(prec):
        checked.append(prec.shape)
        original(prec)
    monkeypatch.setattr(worker.mm, 'check_partial_order', check)
    rows = list(worker.generate_rows(worker.ENGINEERING_ENTROPY, 'engineering'))
    assert len(checked) == len(rows) == 40


def test_cli_metadata_then_rows(capsys):
    worker.main(['--mode', 'engineering', '--entropy', str(worker.ENGINEERING_ENTROPY)])
    records = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(records) == 41
    metadata = records[0]
    assert metadata['type'] == 'metadata'
    assert metadata['schema'] == 1
    assert metadata['mode'] == 'engineering'
    assert metadata['entropy'] == worker.ENGINEERING_ENTROPY
    assert metadata['design'] == worker.design('engineering')
    assert set(metadata['versions']) == {'python', 'numpy', 'scipy'}
    assert all(value for value in metadata['modules'].values())
    assert all(row['type'] == 'row' for row in records[1:])
