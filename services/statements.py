import os
import glob
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

KEY_MAP = {
    'Total Revenue': ['Total Revenue', 'TotalRevenue', 'Revenue'],
    'Cost of Revenue': ['Cost of Revenue', 'CostOfRevenue'],
    'Gross Profit': ['Gross Profit', 'GrossProfit'],
    'Operating Expense': ['Total Operating Expenses', 'OperatingExpense', 'Operating Expenses'],
    'Operating Income': ['Operating Income', 'OperatingIncome'],
    'Net Income': ['Net Income', 'NetIncome', 'Net Income Common Stockholders', 'Net Income Applicable To Common Shares'],
    'EBITDA': ['EBITDA', 'Ebitda'],
    'Total Assets': ['Total Assets', 'TotalAssets'],
    'Total Liabilities': ['Total Liabilities', 'TotalLiabilitiesNetMinorityInterest', 'Total Liabilities Net Minority Interest', 'TotalLiabilities'],
    'Total Equity': ['Total Stockholder Equity', 'Total Equity Gross Minority Interest', 'Total Equity'],
    'Cash & ST Investments': ['Cash And Cash Equivalents', 'Cash And Cash Equivalents And Short Term Investments'],
    'Short Term Debt': ['Short Long Term Debt', 'Short Term Debt', 'Short Term Borrowings'],
    'Long Term Debt': ['Long Term Debt', 'LongTermDebt'],
    'CFO': ['Operating Cash Flow', 'Total Cash From Operating Activities'],
    'CFI': ['Investing Cash Flow', 'Total Cashflows From Investing Activities', 'Net Cash Used For Investing Activities'],
    'CFF': ['Financing Cash Flow', 'Total Cash From Financing Activities', 'Net Cash Provided By (Used In) Financing Activities'],
    'Capex': ['Capital Expenditure', 'Capital Expenditures'],
    'Depreciation': ['Depreciation', 'Reconciled Depreciation'],
}


class StatementDataUnavailable(Exception):
    """Raised when standardized statements cannot be produced."""


@dataclass
class StandardizedStatements:
    income_statement: Optional[pd.DataFrame] = None
    balance_sheet: Optional[pd.DataFrame] = None
    cash_flow: Optional[pd.DataFrame] = None
    periods: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @classmethod
    def from_error(cls, message: str) -> 'StandardizedStatements':
        return cls(error=message)

    def ensure_ok(self) -> 'StandardizedStatements':
        if self.error:
            raise StatementDataUnavailable(self.error)
        return self

    @property
    def ok(self) -> bool:
        return self.error is None


def find_file(folder_path: str, pattern: str):
    files = glob.glob(os.path.join(folder_path, pattern))
    return files[0] if files else None


def load_latest_csv(data_dir: str, ticker_upper: str):
    folder = os.path.join(data_dir, ticker_upper)
    if not os.path.isdir(folder):
        return None, None, None
    subfolders = sorted(
        [os.path.join(folder, d) for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))],
        reverse=True,
    )
    for sub in subfolders:
        is_p = find_file(sub, 'income_statement.csv')
        bs_p = find_file(sub, 'balance_sheet.csv')
        cf_p = find_file(sub, 'cash_flow.csv')
        if all([is_p, bs_p, cf_p]):
            return is_p, bs_p, cf_p
    return None, None, None


def _pick(df: pd.DataFrame, canonical: str):
    if df is None or df.empty:
        return None
    aliases = KEY_MAP.get(canonical, [canonical])
    for alias in aliases:
        exact = df[df['Account'].astype(str).str.strip().str.lower() == alias.lower()]
        if len(exact):
            return exact.iloc[0, 1:].to_dict()
    for alias in aliases:
        contains = df[df['Account'].astype(str).str.contains(alias, case=False, na=False)]
        if len(contains):
            return contains.iloc[0, 1:].to_dict()
    return None


def standardize_statements(ticker: str = '', folder_path: str = '', data_dir: str = './data') -> StandardizedStatements:
    if not folder_path and ticker:
        is_p, bs_p, cf_p = load_latest_csv(data_dir, ticker.upper())
    else:
        is_p = os.path.join(folder_path, 'income_statement.csv') if folder_path else None
        bs_p = os.path.join(folder_path, 'balance_sheet.csv') if folder_path else None
        cf_p = os.path.join(folder_path, 'cash_flow.csv') if folder_path else None

    if not all([is_p, bs_p, cf_p]):
        return StandardizedStatements.from_error(
            'Could not locate statements. Run /data/fetch first or provide a valid folder.'
        )

    is_df = pd.read_csv(is_p)
    bs_df = pd.read_csv(bs_p)
    cf_df = pd.read_csv(cf_p)

    periods = [c for c in is_df.columns if c != 'Account']

    def build_frame(items):
        df = pd.DataFrame({'Item': items})
        for per in periods:
            df[per] = None
        return df

    keep_is = ['Total Revenue', 'Cost of Revenue', 'Gross Profit', 'Operating Expense', 'Operating Income', 'EBITDA', 'Net Income']
    keep_bs = ['Total Assets', 'Total Liabilities', 'Total Equity', 'Cash & ST Investments', 'Short Term Debt', 'Long Term Debt']
    keep_cf = ['CFO', 'CFI', 'CFF', 'Capex', 'Depreciation']

    std_is = build_frame(keep_is)
    std_bs = build_frame(keep_bs)
    std_cf = build_frame(keep_cf)

    for item in keep_is:
        pick = _pick(is_df, item)
        if pick:
            for per, val in pick.items():
                if per in std_is.columns:
                    std_is.loc[std_is['Item'] == item, per] = val
    for item in keep_bs:
        pick = _pick(bs_df, item)
        if pick:
            for per, val in pick.items():
                if per in std_bs.columns:
                    std_bs.loc[std_bs['Item'] == item, per] = val
    for item in keep_cf:
        pick = _pick(cf_df, item)
        if pick:
            for per, val in pick.items():
                if per in std_cf.columns:
                    std_cf.loc[std_cf['Item'] == item, per] = val

    return StandardizedStatements(
        income_statement=std_is,
        balance_sheet=std_bs,
        cash_flow=std_cf,
        periods=periods,
    )


def export_statements_xlsx(std: StandardizedStatements, ticker: str, out_dir: str = './data'):
    std = std.ensure_ok()
    path = os.path.join(out_dir, f'{ticker}_statements.xlsx')
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        std.income_statement.to_excel(writer, sheet_name='IncomeStatement', index=False)
        std.balance_sheet.to_excel(writer, sheet_name='BalanceSheet', index=False)
        std.cash_flow.to_excel(writer, sheet_name='CashFlow', index=False)
    return path
