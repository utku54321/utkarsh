# Finance Modelling Flask App

A modular Flask web app to fetch financial data from Yahoo Finance, build Income Statement / Balance Sheet / Cash Flow,
run Financial Statement Analysis (ratios, growth, DuPont, common-size), and perform Valuation (DCF + Comparable Multiples).
It also includes a **one-pager dashboard** and an optional **Live Football Analysis** module.

## Quick Start

1. **Clone / unzip** this folder.
2. **Python 3.10+** recommended. Create a virtual env and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set values (optional; only needed for the sports API or advanced config).
4. Run the app:
   ```bash
   export FLASK_APP=app.py
   flask run --debug
   # or
   python app.py
   ```
5. Open **http://127.0.0.1:5000**

## What makes this different
- **Step-by-step pipeline UI:** Ingestion → Statements → Analysis → Valuation → One-Pager → Export.
- **Download everything:** Raw data, standardized statements, ratio tables, and model outputs (CSV/XLSX).
- **Common-size + DuPont + Quality-of-Earnings** checks out-of-the-box.
- **Scenario Manager** for DCF (base/optimistic/pessimistic) and **Monte Carlo** (optional extension placeholder).
- **Upload fallback:** If Yahoo Finance fails, upload your own XLSX and continue the same pipeline.
- **API-first:** Clean JSON endpoints for using the engine from other apps.
- **Sports add-on:** Example blueprint showing how to add a live football page via an external API (plug your key).

## Structure
```
finance-flask-app/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ routes/
│  ├─ __init__.py
│  ├─ data_routes.py
│  ├─ statements_routes.py
│  ├─ analysis_routes.py
│  ├─ valuation_routes.py
│  └─ sports_routes.py
├─ services/
│  ├─ __init__.py
│  ├─ data_fetch.py
│  ├─ statements.py
│  ├─ analysis.py
│  ├─ valuation.py
│  └─ utils.py
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ statements.html
│  ├─ analysis.html
│  ├─ valuation.html
│  └─ sports.html
├─ static/
│  ├─ css/styles.css
│  └─ js/main.js
├─ data/        # saved outputs
└─ uploads/     # user uploads
```

## Notes
- Yahoo Finance sometimes changes field names. This app normalizes key items. You can extend `services/statements.py` mappings.
- For valuation, you can **type parameters** (WACC, terminal growth) or **auto-derive** partial inputs from market data if available.
- For live football, get an API key (e.g., API-Football on RapidAPI) and set `API_FOOTBALL_KEY` in `.env`.

## Extend / Differentiate
- Add **batch mode** to fetch/standardize many tickers and export a **comp-set** workbook.
- Add **factor screens** (e.g., Quality, Value, Momentum) using rolling metrics.
- Add **alerts** (e.g., valuation gap > 20%, margin compression, unusual accruals).
- Add **PDF report export** (WeasyPrint/ReportLab) to auto-generate a one-pager.
