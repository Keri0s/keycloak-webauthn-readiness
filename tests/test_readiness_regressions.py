"""Regression cases for review R02-R06; synthetic inputs, no lab access."""
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
import yaml

from apps.readiness.cli import main
from apps.readiness.evaluator import evaluate_scorecard, ScorecardValidationError
from apps.readiness.loader import load_criteria_from_yaml, CatalogValidationError
from apps.readiness.models import Criterion, ScorecardItem, ScorecardStatus
from apps.readiness.parser import parse_scorecard_csv

SAMPLE = Path(__file__).resolve().parents[1] / 'DU_LIEU_MAU/N15_San_sang_WebAuthn'


@pytest.fixture
def catalog():
    return load_criteria_from_yaml(SAMPLE / 'tieu_chi.yaml')


@pytest.fixture
def items():
    return parse_scorecard_csv(SAMPLE / 'phieu_cham_mau_day_du.csv')


def evaluate(items, catalog, **kwargs):
    return evaluate_scorecard(items, catalog, nguoi_cham='review-fixture', **kwargs)


def write_catalog(tmp_path, edit):
    data = yaml.safe_load((SAMPLE / 'tieu_chi.yaml').read_text(encoding='utf-8'))
    edit(data)
    path = tmp_path / 'catalog.yaml'
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding='utf-8')
    return path


def write_items(tmp_path, items):
    path = tmp_path / 'scorecard.csv'
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['ma', 'diem', 'nguon_bang_chung'])
        writer.writerows((item.ma, item.diem, item.nguon_bang_chung) for item in items)
    return path


def test_r02_loader_rejects_duplicate_code(tmp_path):
    path = write_catalog(tmp_path, lambda d: d['tieu_chi'].append(
        dict(d['tieu_chi'][0], ma=' CH-01 ', diem_toi_da=99)))
    with pytest.raises(CatalogValidationError, match='CH-01.*trùng'):
        load_criteria_from_yaml(path)


def test_r02_model_does_not_overwrite_existing_criterion(catalog):
    original = catalog.criteria['CH-01']
    with pytest.raises(ValueError, match='trùng'):
        catalog.add_criterion(Criterion('CH-01', 'cau_hinh', 'Duplicate', 99))
    assert catalog.criteria['CH-01'] is original
    assert catalog.total_max_score == 37


@pytest.mark.parametrize('blank', [None, '', '   '])
def test_r03_blank_csv_score_is_incomplete(tmp_path, items, catalog, blank):
    items[0].diem = blank
    items[0].nguon_bang_chung = ''
    parsed = parse_scorecard_csv(write_items(tmp_path, items))
    assert parsed[0].diem is None
    result = evaluate(parsed, catalog)
    assert result.trang_thai == ScorecardStatus.CHUA_HOAN_THANH
    assert result.missing_criteria == ['CH-01']
    assert result.tong_diem is None
    assert result.items['NK-03'].diem == 0


def test_r03_all_unscored_items_remain_incomplete(items, catalog):
    for item in items:
        item.diem = None
        item.nguon_bang_chung = ''
    result = evaluate(items, catalog)
    assert result.missing_criteria == sorted(catalog.criteria)
    assert result.tong_diem is None


@pytest.mark.parametrize('first,second', [(None, 1), (1, None), (None, None), (1, 1)])
def test_r03_duplicate_rows_not_hidden_by_blank_score(items, catalog, first, second):
    items[0].diem = first
    items.append(ScorecardItem('CH-01', second, 'fixture'))
    with pytest.raises(ScorecardValidationError, match='trùng'):
        evaluate(items, catalog)


def test_r03_unscored_unknown_code_still_rejected(items, catalog):
    items.append(ScorecardItem('UNKNOWN', None, ''))
    with pytest.raises(ScorecardValidationError, match='không tồn tại'):
        evaluate(items, catalog)


@pytest.mark.parametrize('value', ['abc', '1.5', 'nan', 'inf', 'true'])
def test_r03_invalid_csv_score_not_treated_as_missing(tmp_path, value):
    path = write_items(tmp_path, [ScorecardItem('CH-01', value, 'fixture')])
    with pytest.raises(ValueError, match='số nguyên'):
        parse_scorecard_csv(path)


@pytest.mark.parametrize('body', [
    'ma,nguon_bang_chung\nCH-01,fixture\n',
    'ma,diem,nguon_bang_chung\n,1,fixture\n',
    'ma,diem,nguon_bang_chung\nCH-01,1,fixture,extra\n',
])
def test_r03_malformed_csv_not_silently_ignored(tmp_path, body):
    path = tmp_path / 'invalid.csv'
    path.write_text(body, encoding='utf-8')
    with pytest.raises(ValueError):
        parse_scorecard_csv(path)


@pytest.mark.parametrize('field,value', [
    ('nhom', 'other'), ('nhom', None), ('nhom', 42),
    ('ma', None), ('ma', []), ('ma', ' '),
    ('mo_ta', ''), ('mo_ta', '  '), ('mo_ta', None), ('mo_ta', 42),
    ('diem_toi_da', True), ('diem_toi_da', False), ('diem_toi_da', 0),
    ('diem_toi_da', -1), ('diem_toi_da', 1.5), ('diem_toi_da', '3'),
    ('can_cu', []), ('cach_thu_bang_chung', None),
])
def test_r04_invalid_catalog_fields_have_domain_error(tmp_path, field, value):
    path = write_catalog(tmp_path, lambda d: d['tieu_chi'][0].update({field: value}))
    with pytest.raises(CatalogValidationError, match=field):
        load_criteria_from_yaml(path)


def test_r04_reject_fifth_group_even_when_required_groups_present(tmp_path):
    path = write_catalog(tmp_path, lambda d: d['tieu_chi'].append(
        dict(d['tieu_chi'][0], ma='OTHER-01', nhom='other')))
    with pytest.raises(CatalogValidationError, match='nhom'):
        load_criteria_from_yaml(path)


def test_r04_catalog_size_and_total_are_not_hardcoded(tmp_path):
    path = write_catalog(tmp_path, lambda d: d['tieu_chi'].append(
        dict(d['tieu_chi'][0], ma='CH-05', diem_toi_da=4)))
    result = load_criteria_from_yaml(path)
    assert len(result.criteria) == 17
    assert result.total_max_score == 41


def test_r04_malformed_yaml_has_readable_error(tmp_path):
    path = tmp_path / 'broken.yaml'
    path.write_text('tieu_chi: [\n', encoding='utf-8')
    with pytest.raises(CatalogValidationError, match='YAML.*dòng'):
        load_criteria_from_yaml(path)


@pytest.mark.parametrize('score', [float('nan'), float('inf'), float('-inf'), True, False, 1.5, 1.0, '1', [], {}])
def test_r05_public_evaluator_rejects_invalid_score_type(items, catalog, score):
    items[0].diem = score
    with pytest.raises(ScorecardValidationError, match='số nguyên'):
        evaluate(items, catalog)


@pytest.mark.parametrize('source', [None, 42, [], '', '   '])
def test_r05_scored_item_requires_text_evidence(items, catalog, source):
    items[0].nguon_bang_chung = source
    with pytest.raises(ScorecardValidationError, match='nguồn bằng chứng'):
        evaluate(items, catalog)


@pytest.mark.parametrize('name', [None, '', '   ', 42, []])
def test_r06_evaluator_required_for_complete_scorecard(items, catalog, name):
    with pytest.raises(ScorecardValidationError, match='Người chấm'):
        evaluate_scorecard(items, catalog, nguoi_cham=name)


@pytest.mark.parametrize('day', ['', '2026-02-30', '20261113', '13/11/2026', '2026-1-1', ' 2026-11-13 ', 42, True])
def test_r06_date_must_be_real_iso_calendar_date(items, catalog, day):
    with pytest.raises(ScorecardValidationError, match='Ngày chấm'):
        evaluate(items, catalog, ngay_cham=day)


def test_r06_default_date_uses_vietnam_timezone(items, catalog):
    vn = timezone(timedelta(hours=7))
    before = datetime.now(vn).date().isoformat()
    result = evaluate_scorecard(items, catalog, nguoi_cham='  synthetic-evaluator  ')
    after = datetime.now(vn).date().isoformat()
    assert result.ngay_cham in {before, after}
    assert result.nguoi_cham == 'synthetic-evaluator'
    assert result.tong_diem == 29


def test_r06_preserves_explicit_date_for_fixture(items, catalog):
    assert evaluate(items, catalog, ngay_cham='2024-02-29').ngay_cham == '2024-02-29'


def test_cli_requires_evaluator(monkeypatch, capsys):
    monkeypatch.setattr('sys.argv', ['readiness', '--scorecard', str(SAMPLE / 'phieu_cham_mau_day_du.csv')])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert '--evaluator' in capsys.readouterr().err


def test_cli_blank_score_and_metadata(tmp_path, items, monkeypatch, capsys):
    items[0].diem = None
    items[0].nguon_bang_chung = ''
    path = write_items(tmp_path, items)
    monkeypatch.setattr('sys.argv', ['readiness', '--catalog', str(SAMPLE / 'tieu_chi.yaml'),
                                   '--scorecard', str(path), '--evaluator', 'synthetic-evaluator'])
    main()
    output = capsys.readouterr().out
    assert 'CHƯA HOÀN THÀNH' in output
    assert 'Tiêu chí bị thiếu: CH-01' in output
    assert 'Ngày chấm' in output
    assert 'synthetic-evaluator' in output
    assert 'None/' not in output


def test_cli_bad_catalog_exits_cleanly(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'broken.yaml'
    path.write_text('tieu_chi: [', encoding='utf-8')
    monkeypatch.setattr('sys.argv', ['readiness', '--catalog', str(path), '--scorecard', 'unused.csv',
                                   '--evaluator', 'synthetic-evaluator'])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert 'LỖI DANH MỤC' in capsys.readouterr().out
