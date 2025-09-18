import math
import os
import pandas as pd
import yfinance as yf
from .statements import standardize_statements


def _latest_value(df: pd.DataFrame, item: str):
    row = df[df['Item'] == item]
    if row.empty:
        return 0.0
    series = pd.to_numeric(row.iloc[0].drop('Item'), errors='coerce').dropna()
    if series.empty:
        return 0.0
    return float(series.iloc[0])


def simple_dcf(ticker: str, wacc: float, terminal_growth: float, forecast_years: int = 5, data_dir: str = './data'):
    std = standardize_statements(ticker=ticker, data_dir=data_dir)
    is_df, cf_df, bs_df = std['income_statement'], std['cash_flow'], std['balance_sheet']

    cfo = _latest_value(cf_df, 'CFO')
    capex = _latest_value(cf_df, 'Capex')
    base_fcf = cfo - capex

    try:
        rev = pd.to_numeric(is_df[is_df['Item'] == 'Total Revenue'].iloc[0].drop('Item'), errors='coerce')
        ni = pd.to_numeric(is_df[is_df['Item'] == 'Net Income'].iloc[0].drop('Item'), errors='coerce')
        g1 = float(rev.iloc[0] / rev.iloc[1] - 1.0) if len(rev) > 1 else 0.05
        g2 = float(ni.iloc[0] / ni.iloc[1] - 1.0) if len(ni) > 1 else 0.05
        growth = (g1 + g2) / 2.0
    except Exception:
        growth = 0.05

    years = list(range(1, int(forecast_years) + 1))
    fcfs = [base_fcf * ((1 + growth) ** t) for t in years]
    discounts = [(1 + wacc) ** t for t in years]
    pv_fcfs = [fcf / disc for fcf, disc in zip(fcfs, discounts)]
    terminal_value = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth) if wacc > terminal_growth else float('nan')
    pv_terminal = terminal_value / ((1 + wacc) ** years[-1]) if isinstance(terminal_value, (int, float)) and not math.isnan(terminal_value) else 0.0
    enterprise_value = sum(pv_fcfs) + pv_terminal

    ticker_obj = yf.Ticker(ticker)
    fast_info = getattr(ticker_obj, 'fast_info', {}) or {}
    info = getattr(ticker_obj, 'info', {}) or {}
    shares = fast_info.get('shares') or info.get('sharesOutstanding')

    cash = _latest_value(bs_df, 'Cash & ST Investments')
    long_debt = _latest_value(bs_df, 'Long Term Debt')
    short_debt = _latest_value(bs_df, 'Short Term Debt')
    net_debt = long_debt + short_debt - cash

    equity_value = enterprise_value - net_debt
    price_target = (equity_value / shares) if shares else None

    return {
        'base_fcf': base_fcf,
        'assumed_growth': growth,
        'wacc': wacc,
        'terminal_growth': terminal_growth,
        'forecast_years': forecast_years,
        'fcfs': fcfs,
        'pv_fcfs': pv_fcfs,
        'terminal_value': terminal_value,
        'pv_terminal_value': pv_terminal,
        'enterprise_value': enterprise_value,
        'net_debt': net_debt,
        'equity_value': equity_value,
        'price_target': price_target,
    }


def comparables_table(tickers):
    rows = []
    for tk in tickers:
        t = yf.Ticker(tk)
        fast_info = getattr(t, 'fast_info', {}) or {}
        info = getattr(t, 'info', {}) or {}
        rows.append({
            'ticker': tk.upper(),
            'price': fast_info.get('last_price') or info.get('currentPrice'),
            'pe': info.get('trailingPE'),
            'forwardPE': info.get('forwardPE'),
            'evToEbitda': info.get('enterpriseToEbitda'),
            'marketCap': info.get('marketCap'),
            'beta': info.get('beta'),
        })
    return rows


def export_valuation_xlsx(ticker: str, dcf: dict, comps: dict, out_dir: str = './data'):
    path = os.path.join(out_dir, f'{ticker}_valuation.xlsx')
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        pd.DataFrame([dcf]).to_excel(writer, sheet_name='DCF', index=False)
        if comps:
            if isinstance(comps, dict) and 'table' in comps:
                pd.DataFrame(comps['table']).to_excel(writer, sheet_name='Comps', index=False)
            else:
                pd.DataFrame(comps).to_excel(writer, sheet_name='Comps', index=False)
    return path
