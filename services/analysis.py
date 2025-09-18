from typing import Optional

import pandas as pd

from .statements import StandardizedStatements, standardize_statements


def _to_series(df: pd.DataFrame, name: str) -> pd.Series:
    if df.empty:
        return pd.Series(dtype='float64')
    series = df[df['Item'] == name].iloc[0].drop('Item')
    return pd.to_numeric(series, errors='coerce')


def _resolve_std(
    std: Optional[StandardizedStatements], ticker: str, folder_path: str, data_dir: str
) -> StandardizedStatements:
    base = std or standardize_statements(ticker, folder_path, data_dir)
    return base.ensure_ok()


def compute_ratios(
    ticker: str = '', folder_path: str = '', data_dir: str = './data', std: Optional[StandardizedStatements] = None
):
    std = _resolve_std(std, ticker, folder_path, data_dir)
    is_df, bs_df, cf_df = std.income_statement, std.balance_sheet, std.cash_flow
    out = {}

    rev = _to_series(is_df, 'Total Revenue')
    gp = _to_series(is_df, 'Gross Profit')
    op = _to_series(is_df, 'Operating Income')
    ni = _to_series(is_df, 'Net Income')
    ebitda = _to_series(is_df, 'EBITDA')

    assets = _to_series(bs_df, 'Total Assets')
    equity = _to_series(bs_df, 'Total Equity')
    st_debt = _to_series(bs_df, 'Short Term Debt')
    lt_debt = _to_series(bs_df, 'Long Term Debt')

    cfo = _to_series(cf_df, 'CFO')
    capex = _to_series(cf_df, 'Capex')

    out['Gross Margin'] = (gp / rev).round(4).to_dict()
    out['Operating Margin'] = (op / rev).round(4).to_dict()
    out['Net Margin'] = (ni / rev).round(4).to_dict()
    out['EBITDA Margin'] = (ebitda / rev).round(4).to_dict()

    out['Debt to Equity'] = ((st_debt + lt_debt) / equity).round(4).to_dict()
    out['ROA'] = (ni / assets).round(4).to_dict()
    out['ROE'] = (ni / equity).round(4).to_dict()

    out['FCF'] = (cfo - capex).round(2).to_dict()

    return out


def common_size(
    ticker: str = '', folder_path: str = '', data_dir: str = './data', std: Optional[StandardizedStatements] = None
):
    std = _resolve_std(std, ticker, folder_path, data_dir)
    is_df, bs_df = std.income_statement.copy(), std.balance_sheet.copy()

    rev = pd.to_numeric(is_df[is_df['Item'] == 'Total Revenue'].iloc[0].drop('Item'), errors='coerce')
    cs_is = is_df.set_index('Item')
    for col in cs_is.columns:
        cs_is[col] = (pd.to_numeric(cs_is[col], errors='coerce') / rev[col]) * 100
    cs_is = cs_is.reset_index()

    assets = pd.to_numeric(bs_df[bs_df['Item'] == 'Total Assets'].iloc[0].drop('Item'), errors='coerce')
    cs_bs = bs_df.set_index('Item')
    for col in cs_bs.columns:
        cs_bs[col] = (pd.to_numeric(cs_bs[col], errors='coerce') / assets[col]) * 100
    cs_bs = cs_bs.reset_index()

    return {'income_statement': cs_is, 'balance_sheet': cs_bs}


def dupont_breakdown(
    ticker: str = '', folder_path: str = '', data_dir: str = './data', std: Optional[StandardizedStatements] = None
):
    std = _resolve_std(std, ticker, folder_path, data_dir)
    is_df, bs_df = std.income_statement, std.balance_sheet

    ni = pd.to_numeric(is_df[is_df['Item'] == 'Net Income'].iloc[0].drop('Item'), errors='coerce')
    rev = pd.to_numeric(is_df[is_df['Item'] == 'Total Revenue'].iloc[0].drop('Item'), errors='coerce')
    assets = pd.to_numeric(bs_df[bs_df['Item'] == 'Total Assets'].iloc[0].drop('Item'), errors='coerce')
    equity = pd.to_numeric(bs_df[bs_df['Item'] == 'Total Equity'].iloc[0].drop('Item'), errors='coerce')

    profit_margin = ni / rev
    asset_turnover = rev / assets
    equity_multiplier = assets / equity
    roe = profit_margin * asset_turnover * equity_multiplier

    return {
        'Profit Margin': profit_margin.round(4).to_dict(),
        'Asset Turnover': asset_turnover.round(4).to_dict(),
        'Equity Multiplier': equity_multiplier.round(4).to_dict(),
        'ROE (DuPont)': roe.round(4).to_dict(),
    }


def growth_table(
    ticker: str = '', folder_path: str = '', data_dir: str = './data', std: Optional[StandardizedStatements] = None
):
    std = _resolve_std(std, ticker, folder_path, data_dir)
    is_df, bs_df = std.income_statement, std.balance_sheet

    def yoy(series):
        s = pd.to_numeric(series, errors='coerce')
        return (s / s.shift(-1) - 1).round(4)

    rev = is_df[is_df['Item'] == 'Total Revenue'].iloc[0].drop('Item')
    ni = is_df[is_df['Item'] == 'Net Income'].iloc[0].drop('Item')
    assets = bs_df[bs_df['Item'] == 'Total Assets'].iloc[0].drop('Item')

    return {
        'Revenue YoY': yoy(rev).to_dict(),
        'Net Income YoY': yoy(ni).to_dict(),
        'Assets YoY': yoy(assets).to_dict(),
    }
