const tickerInput = document.getElementById("ticker");
const form = document.getElementById("search-form");
const suggestions = document.getElementById("suggestions");
const statusEl = document.getElementById("status");
const symbolEl = document.getElementById("symbol");
const nameEl = document.getElementById("name");
const priceEl = document.getElementById("price");
const changeEl = document.getElementById("change");
const metaEl = document.getElementById("meta");
const chartHost = document.getElementById("chart");
const chartWrap = document.querySelector(".chart-wrap");

const money = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });
const state = { symbol: "AAPL", range: "6mo", chart: null, series: null, timer: null, points: [], pointByTime: new Map(), popup: null, popupPoint: null };

function formatPrice(value, currency) {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: currency || "USD",
      maximumFractionDigits: 2,
    }).format(value);
  } catch {
    return `${money.format(value)} ${currency || ""}`.trim();
  }
}

function createChart() {
  chartHost.replaceChildren();
  const chart = LightweightCharts.createChart(chartHost, {
    layout: {
      background: { color: "#14110e" },
      textColor: "#9a9184",
      fontFamily: "IBM Plex Mono, ui-monospace, monospace",
    },
    grid: {
      vertLines: { color: "rgba(243,238,228,0.06)" },
      horzLines: { color: "rgba(243,238,228,0.06)" },
    },
    rightPriceScale: { borderColor: "rgba(243,238,228,0.12)" },
    timeScale: { borderColor: "rgba(243,238,228,0.12)", timeVisible: true },
    crosshair: { vertLine: { color: "#e4b15a" }, horzLine: { color: "#e4b15a" } },
    width: chartHost.clientWidth,
    height: chartHost.clientHeight,
  });
  const series = chart.addAreaSeries({
    lineColor: "#e4b15a",
    topColor: "rgba(228,177,90,0.28)",
    bottomColor: "rgba(228,177,90,0.02)",
    lineWidth: 2,
  });
  window.addEventListener("resize", () => {
    chart.applyOptions({ width: chartHost.clientWidth, height: chartHost.clientHeight });
  });
  chart.subscribeClick(onChartClick);
  state.chart = chart;
  state.series = series;
}

async function loadChart(symbol, range) {
  const ticker = symbol.trim().toUpperCase();
  if (!ticker) return;
  statusEl.textContent = `Loading ${ticker}…`;
  try {
    const response = await fetch(`/api/chart?symbol=${encodeURIComponent(ticker)}&range=${encodeURIComponent(range)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Could not load chart");

    state.symbol = data.symbol;
    state.range = range;
    tickerInput.value = data.symbol;

    const up = (data.change || 0) >= 0;
    symbolEl.textContent = data.symbol;
    nameEl.textContent = data.name;
    priceEl.textContent = formatPrice(data.price, data.currency);
    changeEl.className = `change ${up ? "up" : "down"}`;
    changeEl.textContent =
      data.change == null
        ? ""
        : `${up ? "+" : ""}${money.format(data.change)} (${up ? "+" : ""}${money.format(data.changePercent)}%)`;
    metaEl.textContent = [data.exchange, data.marketState, range.toUpperCase()].filter(Boolean).join(" · ");

    const first = data.points[0]?.value;
    const last = data.points.at(-1)?.value;
    const rising = last >= first;
    state.series.applyOptions({
      lineColor: rising ? "#c8f07a" : "#ff7a62",
      topColor: rising ? "rgba(200,240,122,0.25)" : "rgba(255,122,98,0.25)",
      bottomColor: rising ? "rgba(200,240,122,0.02)" : "rgba(255,122,98,0.02)",
    });
    state.series.setData(data.points);
    state.points = data.points;
    state.pointByTime = new Map(data.points.map((p) => [p.time, p]));
    closePopup();
    state.chart.timeScale().fitContent();
    statusEl.textContent = `${data.points.length} prints · interval ${data.interval} · click a point for target odds`;
  } catch (error) {
    statusEl.textContent = error.message;
  }
}

async function searchTickers(query) {
  if (query.trim().length < 1) {
    suggestions.hidden = true;
    return;
  }
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  suggestions.replaceChildren();
  (data.results || []).slice(0, 7).forEach((item, index) => {
    const li = document.createElement("li");
    li.dataset.symbol = item.symbol;
    li.className = index === 0 ? "active" : "";
    li.innerHTML = `<span class="sym">${item.symbol}</span><span class="nm">${item.name}</span>`;
    li.addEventListener("mousedown", (event) => {
      event.preventDefault();
      pickSymbol(item.symbol);
    });
    suggestions.append(li);
  });
  suggestions.hidden = suggestions.childElementCount === 0;
}

function pickSymbol(symbol) {
  suggestions.hidden = true;
  tickerInput.value = symbol;
  loadChart(symbol, state.range);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const active = suggestions.querySelector(".active");
  pickSymbol(active?.dataset.symbol || tickerInput.value);
});

tickerInput.addEventListener("input", () => {
  clearTimeout(state.timer);
  state.timer = setTimeout(() => searchTickers(tickerInput.value), 180);
});

tickerInput.addEventListener("keydown", (event) => {
  const items = [...suggestions.querySelectorAll("li")];
  if (!items.length) return;
  const current = items.findIndex((item) => item.classList.contains("active"));
  if (event.key === "ArrowDown") {
    event.preventDefault();
    items.forEach((item) => item.classList.remove("active"));
    items[(current + 1) % items.length].classList.add("active");
  }
  if (event.key === "ArrowUp") {
    event.preventDefault();
    items.forEach((item) => item.classList.remove("active"));
    items[(current - 1 + items.length) % items.length].classList.add("active");
  }
  if (event.key === "Escape") suggestions.hidden = true;
});

document.getElementById("ranges").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-range]");
  if (!button) return;
  document.querySelectorAll("#ranges button").forEach((node) => node.classList.toggle("active", node === button));
  loadChart(state.symbol, button.dataset.range);
});

document.addEventListener("click", (event) => {
  if (!form.contains(event.target)) suggestions.hidden = true;
});

createChart();
loadChart(state.symbol, state.range);

/* ---- target-probability popup ----
 * Click a data point -> popup with a target-price input. Calculate posts to
 * /api/probability (GBM first-passage model, same math as
 * tools/barrier_prob.py) and renders P(reaching the target) as a range
 * over volatility/drift scenarios. */

function formatPointTime(t) {
  if (typeof t === "number") {
    return new Date(t * 1000).toLocaleString(undefined, {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  }
  return t;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function onChartClick(param) {
  if (!param || param.time == null || !param.point) {
    closePopup();
    return;
  }
  const point = state.pointByTime.get(param.time);
  if (!point) {
    closePopup();
    return;
  }
  openPopup(point, param.point);
}

function closePopup() {
  if (state.popup) {
    state.popup.remove();
    state.popup = null;
    state.popupPoint = null;
  }
}

function openPopup(point, at) {
  closePopup();
  state.popupPoint = point;
  const el = document.createElement("div");
  el.className = "prob-popup";
  const defaultTarget = (point.value * 1.1).toFixed(2);
  el.innerHTML = `
    <div class="pp-head">
      <span><b>${escapeHtml(state.symbol)}</b> · ${escapeHtml(formatPointTime(point.time))} · <b>${money.format(point.value)}</b></span>
      <button type="button" class="pp-x" aria-label="Close">×</button>
    </div>
    <div class="pp-body">
      <label>Target price
        <input id="pp-target" type="number" step="0.01" min="0.01" value="${defaultTarget}">
      </label>
      <label>Horizon
        <select id="pp-years">
          <option value="0.25">3 months</option>
          <option value="0.5" selected>6 months</option>
          <option value="1">1 year</option>
        </select>
      </label>
      <div class="pp-row">
        <label>Risk-free %
          <input id="pp-rf" type="number" step="0.1" value="4">
        </label>
        <label>Extra drift %
          <input id="pp-drift" type="number" step="0.1" placeholder="optional">
        </label>
      </div>
      <button type="button" class="pp-go" id="pp-calc">Calculate</button>
      <div class="pp-result" id="pp-result"></div>
      <p class="pp-caveat">GBM first-passage model (smooth diffusion). Jumps around events make true tail risk fatter than shown.</p>
    </div>`;
  chartWrap.appendChild(el);
  const pw = el.offsetWidth;
  const ph = el.offsetHeight;
  const cw = chartWrap.clientWidth;
  const ch = chartWrap.clientHeight;
  let x = at.x + 14;
  let y = at.y - ph - 10;
  if (x + pw > cw) x = at.x - pw - 14;
  if (y < 0) y = at.y + 18;
  if (y + ph > ch) y = Math.max(8, ch - ph - 8);
  el.style.left = `${Math.max(8, x)}px`;
  el.style.top = `${Math.max(8, y)}px`;
  el.querySelector(".pp-x").addEventListener("click", closePopup);
  el.querySelector("#pp-calc").addEventListener("click", calcProbability);
  el.querySelector("#pp-target").select();
  state.popup = el;
}

async function calcProbability() {
  const out = document.getElementById("pp-result");
  const point = state.popupPoint;
  if (!point) return;
  const target = parseFloat(document.getElementById("pp-target").value);
  const years = parseFloat(document.getElementById("pp-years").value);
  const rf = parseFloat(document.getElementById("pp-rf").value) / 100;
  const driftRaw = document.getElementById("pp-drift").value.trim();
  if (!Number.isFinite(target) || target <= 0) {
    out.innerHTML = `<p class="pp-err">Enter a positive target price.</p>`;
    return;
  }
  if (!Number.isFinite(rf) || rf < 0) {
    out.innerHTML = `<p class="pp-err">Enter a risk-free rate.</p>`;
    return;
  }
  const drift = driftRaw === "" ? null : parseFloat(driftRaw) / 100;
  if (drift !== null && !Number.isFinite(drift)) {
    out.innerHTML = `<p class="pp-err">Enter a valid drift.</p>`;
    return;
  }
  out.innerHTML = `<p class="pp-loading">Calculating…</p>`;
  try {
    const res = await fetch("/api/probability", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: state.symbol,
        price: point.value,
        target,
        years,
        risk_free: rf,
        drift,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Calculation failed");
    renderProbResult(out, data, target, years);
  } catch (error) {
    out.innerHTML = `<p class="pp-err">${escapeHtml(error.message)}</p>`;
  }
}

function renderProbResult(out, data, target, years) {
  const dir = data.direction === "up" ? "reach or exceed" : "fall to or below";
  const yrs = years === 0.25 ? "3 months" : years === 0.5 ? "6 months" : years === 1 ? "1 year" : `${years}y`;
  const gate =
    data.hi >= 0.8
      ? `<span class="badge yes">upper bound ≥ 80% ✓</span>`
      : `<span class="badge no">upper bound &lt; 80%</span>`;
  const vols = [...new Set(data.cells.map((c) => c.vol))];
  const drifts = [...new Set(data.cells.map((c) => c.drift))];
  let tbl = `<table class="pp-table"><tr><th>drift \\ vol</th>${vols.map((v) => `<th>${escapeHtml(v)}</th>`).join("")}</tr>`;
  for (const d of drifts) {
    tbl += `<tr><td>${escapeHtml(d)}</td>`;
    for (const v of vols) {
      const c = data.cells.find((c) => c.drift === d && c.vol === v);
      tbl += `<td>${(c.p * 100).toFixed(1)}%</td>`;
    }
    tbl += `</tr>`;
  }
  tbl += `</table>`;
  out.innerHTML = `
    <p class="pp-range">P(${dir} <b>${money.format(target)}</b> within ${yrs})<br>
      <b class="pp-big">${(data.lo * 100).toFixed(0)}% – ${(data.hi * 100).toFixed(0)}%</b> ${gate}</p>
    ${tbl}
    <p class="pp-muted">Range across vol (0.7×/1×/1.3× of ${(data.base_vol * 100).toFixed(1)}% realized 1y vol) and drift scenarios.</p>`;
}
