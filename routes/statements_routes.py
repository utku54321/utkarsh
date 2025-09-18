from flask import Blueprint, request, current_app, render_template, send_file
from services.statements import standardize_statements, export_statements_xlsx

bp = Blueprint('statements', __name__)


@bp.route('/', methods=['GET'])
def view():
    ticker = (request.args.get('ticker') or '').upper().strip()
    path = request.args.get('path')

    if not ticker and not path:
        return render_template('statements.html', error='Provide ticker or path from fetch step.')

    std = standardize_statements(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    return render_template('statements.html', result=std, ticker=ticker, folder_path=path)


@bp.route('/export', methods=['GET'])
def export():
    ticker = (request.args.get('ticker') or '').upper().strip()
    path = request.args.get('path')
    std = standardize_statements(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    out_path = export_statements_xlsx(std, ticker=ticker or 'COMPANY', out_dir=current_app.config['DATA_DIR'])
    return send_file(out_path, as_attachment=True)
