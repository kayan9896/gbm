from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from probability import estimate_vol, hit_range

YAHOO = "https://query1.finance.yahoo.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
}

RANGE_MAP = {
    "1d": ("1d", "5m"),
    "5d": ("5d", "15m"),
    "1mo": ("1mo", "1d"),
    "3mo": ("3mo", "1d"),
    "6mo": ("6mo", "1d"),
    "ytd": ("ytd", "1d"),
    "1y": ("1y", "1d"),
    "5y": ("5y", "1wk"),
    "max": ("max", "1mo"),
}

INTRADAY = {"1d", "5d"}

# symbol -> (fetched_at_epoch, [daily closes, oldest first]); 10-minute TTL
_vol_cache: dict[str, tuple[float, list[float]]] = {}
_VOL_TTL = 600

app = FastAPI(title="Tickline")
http = httpx.AsyncClient(headers=HEADERS, timeout=20.0, follow_redirects=True)


def yahoo_symbol(raw: str) -> str:
    symbol = raw.strip().upper().replace(" ", "")
    if not symbol:
        raise HTTPException(status_code=400, detail="Ticker is required")
    return symbol.replace(".", "-")


async def daily_closes_1y(ticker: str) -> list[float]:
    """1 year of daily closes for volatility estimation (cached briefly)."""
    now = time.time()
    hit = _vol_cache.get(ticker)
    if hit and now - hit[0] < _VOL_TTL:
        return hit[1]
    try:
        response = await http.get(
            f"{YAHOO}/v8/finance/chart/{ticker}",
            params={"range": "1y", "interval": "1d", "events": "div,splits"},
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Price data is unavailable right now") from exc
    results = (payload.get("chart") or {}).get("result") or []
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    quote = ((results[0].get("indicators") or {}).get("quote") or [{}])[0]
    closes = [c for c in (quote.get("close") or []) if isinstance(c, (int, float)) and c > 0]
    if len(closes) < 60:
        raise HTTPException(status_code=502, detail="Not enough history to estimate volatility")
    _vol_cache[ticker] = (now, closes)
    return closes


class ProbRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    price: float = Field(..., gt=0)
    target: float = Field(..., gt=0)
    years: float = Field(0.5, gt=0, le=5)
    risk_free: float = Field(0.04, ge=0, le=1)
    drift: float | None = Field(None, ge=-1, le=5)


@app.post("/api/probability")
async def probability(req: ProbRequest):
    """P(price touches `target` at least once within `years`), as a range.

    GBM first-passage model (same math as tools/barrier_prob.py). Volatility
    is the 1y realized daily vol, bracketed 0.7x/1x/1.3x; drifts are 0%,
    the risk-free rate, and an optional custom drift.
    """
    if req.target == req.price:
        raise HTTPException(status_code=400, detail="Target equals the starting price")
    ticker = yahoo_symbol(req.symbol)
    closes = await daily_closes_1y(ticker)
    base_vol = estimate_vol(closes)
    grid = hit_range(req.price, req.target, req.years, base_vol, req.risk_free, req.drift)
    return {
        "symbol": ticker,
        "price": req.price,
        "target": req.target,
        "years": req.years,
        "direction": "up" if req.target > req.price else "down",
        **grid,
    }


@app.get("/api/search")
async def search(q: str = Query(..., min_length=1, max_length=40)):
    try:
        response = await http.get(
            f"{YAHOO}/v1/finance/search",
            params={"q": q.strip(), "quotesCount": 8, "newsCount": 0},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Search is unavailable right now") from exc

    quotes = response.json().get("quotes") or []
    results = []
    for quote in quotes:
        symbol = quote.get("symbol")
        if not symbol:
            continue
        results.append(
            {
                "symbol": symbol,
                "name": quote.get("shortname") or quote.get("longname") or symbol,
                "type": quote.get("quoteType") or "",
                "exchange": quote.get("exchDisp") or quote.get("exchange") or "",
            }
        )
    return {"results": results}


@app.get("/api/chart")
async def chart(
    symbol: str = Query(..., min_length=1, max_length=20),
    range: str = Query("6mo"),
):
    key = range.lower()
    if key not in RANGE_MAP:
        raise HTTPException(status_code=400, detail="Unknown range")

    yahoo_range, interval = RANGE_MAP[key]
    ticker = yahoo_symbol(symbol)

    try:
        response = await http.get(
            f"{YAHOO}/v8/finance/chart/{ticker}",
            params={
                "range": yahoo_range,
                "interval": interval,
                "includePrePost": "false",
                "events": "div,splits",
            },
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Price data is unavailable right now") from exc

    error = (payload.get("chart") or {}).get("error")
    results = (payload.get("chart") or {}).get("result") or []
    if error or not results:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    result = results[0]
    meta = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    closes = quote.get("close") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    volumes = quote.get("volume") or []

    points = []
    for index, ts in enumerate(timestamps):
        if index >= len(closes) or closes[index] is None:
            continue
        if key in INTRADAY:
            time_value = int(ts)
        else:
            time_value = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        points.append(
            {
                "time": time_value,
                "value": round(float(closes[index]), 4),
                "high": None if index >= len(highs) or highs[index] is None else round(float(highs[index]), 4),
                "low": None if index >= len(lows) or lows[index] is None else round(float(lows[index]), 4),
                "volume": None if index >= len(volumes) or volumes[index] is None else int(volumes[index]),
            }
        )

    if not points:
        raise HTTPException(status_code=404, detail=f"No plottable prices for {ticker}")

    last = points[-1]["value"]
    price = meta.get("regularMarketPrice") or last
    previous = meta.get("previousClose")
    if previous is None and len(points) > 1:
        previous = points[-2]["value"]
    change = None if previous in (None, 0) else float(price) - float(previous)
    change_pct = None if previous in (None, 0) else (change / float(previous)) * 100

    return {
        "symbol": meta.get("symbol") or ticker,
        "name": meta.get("longName") or meta.get("shortName") or ticker,
        "currency": meta.get("currency") or "USD",
        "exchange": meta.get("fullExchangeName") or meta.get("exchangeName") or "",
        "price": round(float(price), 4),
        "previousClose": previous,
        "change": None if change is None else round(change, 4),
        "changePercent": None if change_pct is None else round(change_pct, 4),
        "marketState": meta.get("marketState") or "",
        "points": [{"time": p["time"], "value": p["value"]} for p in points],
        "range": key,
        "interval": interval,
    }


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
