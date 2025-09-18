import pandas as pd
import yfinance as yf


def fetch_yf_history(ticker: str, start=None, end=None, interval: str = '1d') -> pd.DataFrame:
    """Fetch OHLCV history from Yahoo Finance."""
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f'No price history for {ticker}')
    df.index.name = 'Date'
    return df


def fetch_yf_statements(ticker: str):
    """Fetch income statement, balance sheet, and cash flow (annual) from Yahoo Finance."""
    t = yf.Ticker(ticker)
    is_df = getattr(t, 'income_stmt', None)
    if is_df is None or is_df.empty:
        is_df = getattr(t, 'financials', None)
    bs_df = getattr(t, 'balance_sheet', None)
    cf_df = getattr(t, 'cashflow', None)

    def tidy(df):
        if df is None or df.empty:
            return pd.DataFrame()
        out = df.copy()
        out.index.name = 'Account'
        out.reset_index(inplace=True)
        return out

    return tidy(is_df), tidy(bs_df), tidy(cf_df)
