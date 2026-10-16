"""Target-hit probability math for the Tickline probability popup.

Self-contained port of the first-passage model in ``tools/barrier_prob.py``
(same repo) — geometric Brownian motion, reflection principle, closed form.
Kept as a separate module so the FastAPI app stays deployable from this
directory without reaching into ``../tools``.

Question answered: P(price touches `target` at least once within T years),
as a RANGE over plausible volatility and drift scenarios.

Caveats (same as the reference implementation): assumes smooth diffusion;
jumps around events (earnings, launches) make true tail risk fatter than
shown. Cross-check with the option chain:
    P(never touch) <= 1 - |delta| at the target strike.
"""

from __future__ import annotations

import math
from statistics import NormalDist, stdev

N = NormalDist().cdf
TRADING_DAYS = 252


def estimate_vol(closes: list[float]) -> float:
    """Annualized volatility from daily log returns. Oldest first."""
    if len(closes) < 3:
        raise ValueError("need at least 3 closes to estimate volatility")
    rets = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
    return stdev(rets) * math.sqrt(TRADING_DAYS)


def p_hit(price: float, target: float, years: float, vol: float, drift: float) -> float:
    """P(price touches `target` at least once within `years`).

    GBM with annualized volatility `vol` and total expected return `drift`.
    Works for upper (target > price) and lower (target < price) barriers.
    """
    nu = drift - 0.5 * vol**2
    sT = vol * math.sqrt(years)
    if target > price:  # upper barrier
        b = math.log(target / price)
        return N((-b + nu * years) / sT) + math.exp(2 * nu * b / vol**2) * N((-b - nu * years) / sT)
    # lower barrier (symmetry: flip the drift sign)
    b = math.log(price / target)
    return N((-b - nu * years) / sT) + math.exp(-2 * nu * b / vol**2) * N((-b + nu * years) / sT)


def hit_range(
    price: float,
    target: float,
    years: float,
    base_vol: float,
    risk_free: float = 0.04,
    extra_drift: float | None = None,
) -> dict:
    """Scenario grid: vols 0.7x/1x/1.3x of base_vol, drifts 0% / risk-free / optional.

    Returns JSON-serializable dict with per-cell P(hit) and the overall range.
    """
    vols = [("low (x0.7)", 0.7 * base_vol), ("base", base_vol), ("high (x1.3)", 1.3 * base_vol)]
    drifts = [("zero drift", 0.0), (f"risk-free ({risk_free:.0%})", risk_free)]
    if extra_drift is not None:
        drifts.append((f"custom ({extra_drift:.1%})", extra_drift))

    cells: list[dict] = []
    lo, hi = 1.0, 0.0
    for drift_label, mu in drifts:
        for vol_label, sig in vols:
            p = min(max(p_hit(price, target, years, sig, mu), 0.0), 1.0)
            cells.append({"vol": vol_label, "drift": drift_label, "p": round(p, 4)})
            lo, hi = min(lo, p), max(hi, p)
    return {
        "cells": cells,
        "lo": round(lo, 4),
        "hi": round(hi, 4),
        "base_vol": round(base_vol, 4),
    }
