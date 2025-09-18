from flask import Blueprint, request, render_template, current_app
from services.analysis import compute_ratios, common_size, dupont_breakdown, growth_table
from services.statements import standardize_statements

bp = Blueprint('analysis', __name__)


@bp.route('/', methods=['GET'])
def view():
    ticker = (request.args.get('ticker') or '').upper().strip()
    path = request.args.get('path')
    if not ticker and not path:
        return render_template('analysis.html', error='Provide ticker or path from fetch step.')

    std = standardize_statements(ticker=ticker, folder_path=path, data_dir=current_app.config['DATA_DIR'])
    if std.error:
        return render_template('analysis.html', error=std.error, ticker=ticker, folder_path=path)

    ratios = compute_ratios(std=std)
    cs = common_size(std=std)
    dup = dupont_breakdown(std=std)
    gr = growth_table(std=std)

    return render_template(
        'analysis.html',
        ratios=ratios,
        common_size=cs,
        dupont=dup,
        growth=gr,
        ticker=ticker,
        folder_path=path,
    )
