import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from services.statements import StandardizedStatements, StatementDataUnavailable, standardize_statements


@pytest.fixture
def app_with_tmp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv('DATA_DIR', str(tmp_path))
    application = create_app()
    application.config.update(TESTING=True)
    yield application


def test_standardize_returns_error_when_data_missing(tmp_path):
    std: StandardizedStatements = standardize_statements(ticker='MISSING', data_dir=str(tmp_path))
    assert not std.ok
    assert std.error
    with pytest.raises(StatementDataUnavailable):
        std.ensure_ok()


def test_statements_route_reports_missing_data(app_with_tmp_data_dir):
    client = app_with_tmp_data_dir.test_client()
    resp = client.get('/statements/?ticker=MISS')
    assert resp.status_code == 200
    assert b'Could not locate statements' in resp.data


def test_analysis_route_reports_missing_data(app_with_tmp_data_dir):
    client = app_with_tmp_data_dir.test_client()
    resp = client.get('/analysis/?ticker=MISS')
    assert resp.status_code == 200
    assert b'Could not locate statements' in resp.data
