async function fetchJSON(url = '', method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return res.json();
}

async function fetchYF() {
  const ticker = document.getElementById('yf_ticker').value.trim();
  const start = document.getElementById('yf_start').value || null;
  const end = document.getElementById('yf_end').value || null;
  const interval = document.getElementById('yf_interval').value;
  const out = document.getElementById('yf_result');
  out.textContent = 'Fetching...';
  const res = await fetchJSON('/data/fetch', 'POST', { ticker, start, end, interval });
  out.textContent = JSON.stringify(res, null, 2);
}

async function uploadXLSX() {
  const f = document.getElementById('upload_file').files[0];
  if (!f) return alert('Pick a file');
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch('/data/upload', { method: 'POST', body: fd });
  const json = await res.json();
  document.getElementById('upload_result').textContent = JSON.stringify(json, null, 2);
}

async function runDCF() {
  const ticker = document.getElementById('dcf_ticker').value.trim();
  const wacc = parseFloat(document.getElementById('dcf_wacc').value);
  const tg = parseFloat(document.getElementById('dcf_tg').value);
  const years = parseInt(document.getElementById('dcf_years').value, 10);
  const out = document.getElementById('dcf_out');
  out.textContent = 'Running...';
  const res = await fetchJSON('/valuation/dcf', 'POST', {
    ticker,
    wacc,
    terminal_growth: tg,
    forecast_years: years,
  });
  out.textContent = JSON.stringify(res, null, 2);
}

async function runComps() {
  const s = document.getElementById('comps_tickers').value.trim();
  const arr = s.split(',').map((x) => x.trim()).filter(Boolean);
  const out = document.getElementById('comps_out');
  out.textContent = 'Building...';
  const res = await fetchJSON('/valuation/comps', 'POST', { tickers: arr });
  out.textContent = JSON.stringify(res, null, 2);
}

async function exportValuation() {
  const dcfText = document.getElementById('dcf_out').textContent.trim();
  const compsText = document.getElementById('comps_out').textContent.trim();
  try {
    const dcf = dcfText ? JSON.parse(dcfText).dcf || {} : {};
    const comps = compsText ? JSON.parse(compsText).table || {} : {};
    const ticker = (document.getElementById('dcf_ticker').value || 'COMPANY').trim();
    const res = await fetch('/valuation/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, dcf, comps }),
    });
    if (!res.ok) throw new Error('export failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${ticker}_valuation.xlsx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (e) {
    document.getElementById('export_out').textContent = String(e);
  }
}

async function fetchLive() {
  const out = document.getElementById('live_out');
  out.textContent = 'Fetching...';
  const res = await fetch('/sports/live');
  const json = await res.json();
  out.textContent = JSON.stringify(json, null, 2);
}
