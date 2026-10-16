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

const money = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });
const state = { symbol: "AAPL", range: "6mo", chart: null, series: null, timer: null };

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
    state.chart.timeScale().fitContent();
    statusEl.textContent = `${data.points.length} prints · interval ${data.interval}`;
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
