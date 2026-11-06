"""Hand-built stored-count adversaries; no study seeds or generated orders."""
import copy
import json
import math

import pytest

from emergence_lab.cs0_recheck import (ENGINEERING_ENTROPY, _fraction,
                                      _mean_test, check_rows)


def rows_fixture():
    # Deliberately all antichain observations except the exact chains. This is
    # a valid stored-count artifact with gross stochastic failures, not data.
    rows = []
    for n in (8, 12):
        for family, parameter, index in (
            ('diamond', 2, 0), ('diamond', 3, 0), ('diamond', 4, 0),
            ('two_layer', 0, 1), ('k_order', 3, 2), ('k_order', 4, 2),
            ('chain', 0, 3), ('antichain', 0, 4)):
            for rep in range(1 if family in ('chain', 'antichain') else 3):
                chain = family == 'chain'
                rows.append(dict(family=family, D_or_k=parameter, N=n, rep=rep,
                                 spawn_key=[index, parameter, n, rep],
                                 R=math.comb(n, 2) if chain else 0,
                                 r=1.0 if chain else 0.0,
                                 d_mm=1.0 if chain else None,
                                 classification='TOTAL_ORDER' if chain else 'OUT_OF_RANGE'))
    return rows


def check(rows):
    return check_rows(rows, 'engineering', ENGINEERING_ENTROPY)


def test_handbuilt_engineering_report_cannot_claim_pass():
    report = check(rows_fixture())
    assert report['verdict'] == 'ENGINEERING_ONLY'
    assert report['rows'] == 40
    assert not report['study_authorized'] and not report['scientific_acceptance']
    assert report['gates'] == dict(G0_rows=True, G1=False, G2=False, G3=False)
    assert 'random k-order' in report['limitation']
    assert 'conditional' in report['t_reference_caveat']
    assert all(c['t_unbounded'] for c in report['cells'] if c['family'] == 'diamond')
    json.dumps(report, allow_nan=False)


def test_closed_form_reference_and_zero_variance_policy():
    for d, reference in ((2, .5), (3, 8 / 35), (4, .1)):
        assert _fraction(d) == pytest.approx(reference, rel=2e-14)
    zero = _mean_test([.25] * 30, .25, 3.38)
    assert zero['t'] is None and not zero['t_defined']
    assert not zero['t_unbounded'] and not zero['mean_test_pass']
    wrong = _mean_test([.2] * 30, .25, 3.38)
    assert wrong['t'] is None and wrong['t_unbounded']
    assert not wrong['mean_test_pass']
    balanced = _mean_test([.125, .25, .375], .25, 3.38)
    assert balanced['t'] == 0 and balanced['mean_test_pass']


@pytest.mark.parametrize('mutation', [
    lambda rows: rows.pop(),
    lambda rows: rows.append(copy.deepcopy(rows[0])),
    lambda rows: rows.__setitem__(1, copy.deepcopy(rows[0])),
    lambda rows: rows[0].update(family='unknown'),
    lambda rows: rows[0].update(N=9),
    lambda rows: rows[0].update(R=-1),
    lambda rows: rows[0].update(R=29),
    lambda rows: rows[0].update(R=True),
    lambda rows: rows[0].update(rep=False),
    lambda rows: rows[0].update(r=float('nan')),
    lambda rows: rows[0].update(r=float('inf')),
    lambda rows: rows[0].update(r=True),
    lambda rows: rows[0].update(r=1e-10),
    lambda rows: rows[0].update(r=-1e-16),
    lambda rows: rows[0].update(r=10 ** 1000),
    lambda rows: rows[0].update(d_mm=64.0),
    lambda rows: rows[0].update(classification='IN_RANGE'),
    lambda rows: rows[0].update(spawn_key=[True, 2, 8, 0]),
    lambda rows: rows[0].update(spawn_key=[0, 3, 8, 0]),
    lambda rows: rows[0].update(extra='not schema'),
])
def test_corrupt_artifact_refused(mutation):
    rows = rows_fixture()
    mutation(rows)
    with pytest.raises(ValueError):
        check(rows)


def test_exact_controls_refuse_plausible_but_wrong_counts():
    rows = rows_fixture()
    chain = next(r for r in rows if r['family'] == 'chain')
    chain.update(R=0, r=0.0, d_mm=None, classification='OUT_OF_RANGE')
    with pytest.raises(ValueError, match='chain'):
        check(rows)


def test_total_order_finite_dimension_recheck():
    rows = rows_fixture()
    rows[0].update(R=28, r=1, d_mm=1, classification='TOTAL_ORDER')
    assert check(rows)['verdict'] == 'ENGINEERING_ONLY'
    rows[0]['d_mm'] = float('nan')
    with pytest.raises(ValueError, match='finite'):
        check(rows)


@pytest.mark.parametrize('mode,entropy', [('other', 1), ('engineering', 1),
                                         ('engineering', True), ('full', -1)])
def test_invalid_setup_refused(mode, entropy):
    with pytest.raises(ValueError):
        check_rows(rows_fixture(), mode, entropy)


def test_independent_dimension_check_at_known_half_fraction():
    rows = rows_fixture()
    rows[0].update(R=14, r=.5, d_mm=2.0, classification='IN_RANGE')
    assert check(rows)['verdict'] == 'ENGINEERING_ONLY'
    rows[0]['d_mm'] = 2.001
    with pytest.raises(ValueError, match='independent inversion'):
        check(rows)


def test_full_shaped_synthetic_failure_has_correct_24_cell_cutoff(tmp_path, capsys):
    # No generator/RNG or authorized seed is invoked: this is an algebraically
    # manufactured full-shaped invalid instrument, not a CS0 study execution.
    rows = []
    for n in (128, 256, 512, 1024):
        for family, parameter, index in (
            ('diamond', 2, 0), ('diamond', 3, 0), ('diamond', 4, 0),
            ('two_layer', 0, 1), ('k_order', 3, 2), ('k_order', 4, 2),
            ('chain', 0, 3), ('antichain', 0, 4)):
            for rep in range(1 if family in ('chain', 'antichain') else 30):
                chain = family == 'chain'
                rows.append(dict(family=family, D_or_k=parameter, N=n, rep=rep,
                                 spawn_key=[index, parameter, n, rep],
                                 R=math.comb(n, 2) if chain else 0,
                                 r=1.0 if chain else 0.0,
                                 d_mm=1.0 if chain else None,
                                 classification='TOTAL_ORDER' if chain else 'OUT_OF_RANGE'))
    report = check_rows(rows, 'full', 0)
    assert report['rows'] == 728
    assert report['verdict'] == 'FAIL'
    assert report['df'] == 29 and report['bonferroni_cells'] == 24
    assert report['cutoff'] == pytest.approx(3.380557, abs=1e-6)
    assert len([c for c in report['cells'] if c['family'] == 'diamond']) == 12
    assert len([c for c in report['cells'] if c['family'] in ('two_layer', 'k_order')]) == 12
    assert all(c['N'] == 1024 for c in report['discrimination'])
    json.dumps(report, allow_nan=False)
    from emergence_lab.cs0_recheck import main
    path = tmp_path / 'synthetic.csv'
    write_fixture_csv(path, rows)
    assert main(['--input', str(path), '--mode', 'full', '--entropy', '0']) == 1
    assert json.loads(capsys.readouterr().out)['verdict'] == 'FAIL'


def write_fixture_csv(path, rows):
    import csv
    fields = ['family', 'D_or_k', 'N', 'rep', 'spawn_key', 'R', 'r', 'd_mm',
              'classification']
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, 'spawn_key': json.dumps(row['spawn_key']),
                             'd_mm': '' if row['d_mm'] is None else row['d_mm']})


def test_persisted_csv_round_trip_and_cli(tmp_path, capsys):
    from emergence_lab.cs0_recheck import main, read_rows_csv
    path = tmp_path / 'rows.csv'
    rows = rows_fixture()
    write_fixture_csv(path, rows)
    assert read_rows_csv(path) == rows
    assert main(['--input', str(path), '--mode', 'engineering',
                 '--entropy', str(ENGINEERING_ENTROPY)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report['verdict'] == 'ENGINEERING_ONLY'
    assert report['rows'] == 40 and report['study_authorized'] is False


@pytest.mark.parametrize('rewrite', [
    lambda text: text.replace('family,', 'unknown,', 1),
    lambda text: text.replace('D_or_k,', 'family,', 1),
    lambda text: text + '\n',
    lambda text: text.replace(',2,8,0,', ',2.0,8,0,', 1),
    lambda text: text.replace(',2,8,0,', ',true,8,0,', 1),
    lambda text: text.replace(',2,8,0,', ',2,08,0,', 1),
    lambda text: text.replace(',2,8,0,', ',2,8,+0,', 1),
    lambda text: text.replace('"[0, 2, 8, 0]"', '"[0, 2, 8, 0"', 1),
    lambda text: text.replace('OUT_OF_RANGE', 'OUT_OF_RANGE,extra', 1),
])
def test_csv_parser_rejects_structural_corruption(tmp_path, rewrite):
    from emergence_lab.cs0_recheck import read_rows_csv
    path = tmp_path / 'rows.csv'
    write_fixture_csv(path, rows_fixture())
    path.write_text(rewrite(path.read_text()))
    with pytest.raises(ValueError):
        read_rows_csv(path)


def test_csv_semantic_corruption_reaches_recheck_refusal(tmp_path, capsys):
    from emergence_lab.cs0_recheck import main, read_rows_csv
    path = tmp_path / 'rows.csv'
    rows = rows_fixture()
    rows[0]['r'] = float('nan')
    write_fixture_csv(path, rows)
    with pytest.raises(ValueError, match='finite'):
        check(read_rows_csv(path))
    assert main(['--input', str(path), '--mode', 'engineering',
                 '--entropy', str(ENGINEERING_ENTROPY)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report['verdict'] == 'INCOMPLETE'
    assert report['study_authorized'] is False


def test_csv_empty_and_truncated_quotes_refused(tmp_path):
    from emergence_lab.cs0_recheck import read_rows_csv
    path = tmp_path / 'rows.csv'
    path.write_text('')
    with pytest.raises(ValueError, match='headers'):
        read_rows_csv(path)
    write_fixture_csv(path, rows_fixture())
    path.write_text(path.read_text() + '"unfinished')
    with pytest.raises(ValueError, match='malformed CSV'):
        read_rows_csv(path)


def test_cli_missing_artifact_refuses_without_generation(tmp_path, capsys):
    from emergence_lab.cs0_recheck import main
    assert main(['--input', str(tmp_path / 'missing.csv'), '--mode', 'full',
                 '--entropy', '0']) == 2
    assert json.loads(capsys.readouterr().out)['verdict'] == 'INCOMPLETE'
