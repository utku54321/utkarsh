import os
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app


@pytest.fixture
def app_with_download_dirs(tmp_path, monkeypatch):
    data_dir = tmp_path / 'data'
    upload_dir = tmp_path / 'uploads'
    monkeypatch.setenv('DATA_DIR', str(data_dir))
    monkeypatch.setenv('UPLOAD_DIR', str(upload_dir))
    app = create_app()
    app.config.update(TESTING=True)
    yield app


def test_download_allows_file_within_data_dir(app_with_download_dirs):
    client = app_with_download_dirs.test_client()
    data_dir = Path(app_with_download_dirs.config['DATA_DIR'])
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / 'sample.txt'
    file_path.write_text('hello world')

    resp = client.get('/data/download', query_string={'path': str(file_path)})

    assert resp.status_code == 200
    assert resp.data == b'hello world'
    disposition = resp.headers.get('Content-Disposition')
    assert disposition and 'attachment' in disposition


def test_download_rejects_path_outside_allowed_roots(app_with_download_dirs, tmp_path):
    client = app_with_download_dirs.test_client()
    data_dir = Path(app_with_download_dirs.config['DATA_DIR'])
    data_dir.mkdir(parents=True, exist_ok=True)

    # Attempt directory traversal to escape data_dir.
    malicious_relative = os.path.join('..', 'secret.txt')
    resp = client.get('/data/download', query_string={'path': malicious_relative})

    assert resp.status_code == 403
    payload = resp.get_json()
    assert payload == {'ok': False, 'error': 'access denied'}
