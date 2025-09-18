from flask import Blueprint, request, render_template, current_app
from services.analysis import compute_ratios, common_size, dupont_breakdown, growth_table

bp = Blueprint('analysis', __name__)


@bp.route('/', methods=['GET'])
def view():
    ticker = (request.args.get('ticker') or '').upper().strip()
    path = request.args.get('path')
    if not ticker and not path:
        return render_template('analysis.html', error='Provide ticker or path from fetch step.')

    ratios = compute_ratios(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    cs = common_size(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    dup = dupont_breakdown(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    gr = growth_table(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])

    return render_template(
        'analysis.html',
        ratios=ratios,
        common_size=cs,
        dupont=dup,
        growth=gr,
        ticker=ticker,
        folder_path=path,
    )
