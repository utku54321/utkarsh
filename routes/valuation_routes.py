from flask import Blueprint, request, render_template, jsonify, current_app, send_file
from services.valuation import simple_dcf, comparables_table, export_valuation_xlsx

bp = Blueprint('valuation', __name__)


@bp.route('/', methods=['GET'])
def view():
    return render_template('valuation.html')


@bp.route('/dcf', methods=['POST'])
def dcf_calc():
    data = request.get_json() or {}
    required = ['ticker', 'wacc', 'terminal_growth', 'forecast_years']
    for r in required:
        if r not in data:
            return jsonify({'ok': False, 'error': f'missing {r}'}), 400
    res = simple_dcf(**data, data_dir=current_app.config['DATA_DIR'])
    return jsonify({'ok': True, 'dcf': res})


@bp.route('/comps', methods=['POST'])
def comps():
    data = request.get_json() or {}
    tickers = data.get('tickers', [])
    if not tickers:
        return jsonify({'ok': False, 'error': 'tickers required'}), 400
    tbl = comparables_table(tickers)
    return jsonify({'ok': True, 'table': tbl})


@bp.route('/export', methods=['POST'])
def export():
    data = request.get_json() or {}
    ticker = data.get('ticker', 'COMPANY')
    dcf = data.get('dcf') or {}
    comps = data.get('comps') or {}
    path = export_valuation_xlsx(ticker, dcf, comps, out_dir=current_app.config['DATA_DIR'])
    return send_file(path, as_attachment=True)
