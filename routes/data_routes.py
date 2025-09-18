import os
import datetime as dt
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from services.data_fetch import fetch_yf_history, fetch_yf_statements
from services.utils import ensure_dir

bp = Blueprint('data', __name__)


@bp.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json() or {}
    ticker = (data.get('ticker') or '').strip()
    start = data.get('start')
    end = data.get('end')
    interval = data.get('interval', '1d')

    if not ticker:
        return jsonify({'ok': False, 'error': 'ticker required'}), 400

    data_dir = current_app.config['DATA_DIR']
    date_tag = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    save_dir = os.path.join(data_dir, secure_filename(ticker.upper()), date_tag)
    ensure_dir(save_dir)

    hist = fetch_yf_history(ticker, start=start, end=end, interval=interval)
    price_path = os.path.join(save_dir, 'price_history.csv')
    hist.to_csv(price_path)

    is_df, bs_df, cf_df = fetch_yf_statements(ticker)
    is_path = os.path.join(save_dir, 'income_statement.csv')
    bs_path = os.path.join(save_dir, 'balance_sheet.csv')
    cf_path = os.path.join(save_dir, 'cash_flow.csv')
    is_df.to_csv(is_path, index=False)
    bs_df.to_csv(bs_path, index=False)
    cf_df.to_csv(cf_path, index=False)

    return jsonify({
        'ok': True,
        'folder': save_dir,
        'files': {
            'price_history': price_path,
            'income_statement': is_path,
            'balance_sheet': bs_path,
            'cash_flow': cf_path,
        },
    })


@bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'no file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'ok': False, 'error': 'no selected file'}), 400

    filename = secure_filename(file.filename)
    save_dir = current_app.config['UPLOAD_DIR']
    ensure_dir(save_dir)
    path = os.path.join(save_dir, filename)
    file.save(path)
    return jsonify({'ok': True, 'path': path})


@bp.route('/download', methods=['GET'])
def download():
    path = request.args.get('path')
    if not path:
        return jsonify({'ok': False, 'error': 'file not found'}), 404

    data_dir = os.path.realpath(current_app.config['DATA_DIR'])
    upload_dir = os.path.realpath(current_app.config['UPLOAD_DIR'])
    allowed_roots = [data_dir, upload_dir]

    def _is_allowed(resolved_path: str) -> bool:
        for root in allowed_roots:
            try:
                common = os.path.commonpath([resolved_path, root])
            except ValueError:
                # Occurs on Windows when drives differ.
                continue
            if common == root:
                return True
        return False

    candidates = [path] if os.path.isabs(path) else [
        os.path.join(data_dir, path),
        os.path.join(upload_dir, path),
    ]

    for candidate in candidates:
        resolved = os.path.realpath(candidate)

        if not _is_allowed(resolved):
            return jsonify({'ok': False, 'error': 'access denied'}), 403

        if not os.path.exists(resolved):
            continue

        return send_file(resolved, as_attachment=True)

    return jsonify({'ok': False, 'error': 'file not found'}), 404
