#!/usr/bin/env python3
"""
Stress-test the Tier 1 Trim Ladder through synthetic bear years.

Usage:
    python3 ladder_stress_test.py                  # runs the two built-in scenarios
    python3 ladder_stress_test.py prices.csv        # runs on real daily closes (oldest first)

Rule simulated (taxable 15/15 version): anchored at first close; on closes,
every +15% vs last action -> sell 15% of holdings; every -15% -> buy 15% more.
Holdings floor 50% of starting shares; cumulative rebuys capped at starting
shares (2x); rebuys are cash-only from a dedicated reserve (default 1x initial
position value).
"""
import csv, math, random, sys

def make_bear(anchors, target_end, vol=0.45, seed=7):
    """Calibrated synthetic bear: monthly anchors + daily noise, exact endpoint."""
    random.seed(seed); sig_d = vol / math.sqrt(252); per = 21
    cur, prices = math.log(anchors[0]), []
    for a, b in zip(anchors, anchors[1:]):
        step = (math.log(b) - math.log(a)) / per
        for _ in range(per):
            cur += step + random.gauss(0, sig_d)
            prices.append(math.exp(cur))
    adj = math.log(target_end / prices[-1]) / len(prices)
    return [p * math.exp(adj * (i + 1)) for i, p in enumerate(prices)]

def ladder(prices, band=0.15, frac=0.15, reserve_mult=1.0):
    shares, ref = 100.0, prices[0]
    cash = reserve = 100 * prices[0] * reserve_mult
    start, trims, rebuys, bought = 100.0, 0, 0, 0.0
    peak, max_dd = None, 0.0
    cap_hit = cash_out = False
    for p in prices[1:]:
        while p >= (1 + band) * ref:                      # trim rungs
            sell = frac * shares
            if shares - sell < 0.5 * start:
                sell = max(0.0, shares - 0.5 * start)     # floor
            if sell <= 0:
                break
            shares -= sell; cash += sell * p; ref *= (1 + band); trims += 1
        while p <= (1 - band) * ref:                      # rebuy rungs
            if bought >= start:
                cap_hit = True; break
            buy = min(frac * shares, start - bought)
            if buy * p > cash:
                cash_out = True; break
            shares += buy; cash -= buy * p; bought += buy
            ref *= (1 - band); rebuys += 1
        v = shares * p + cash
        peak = v if peak is None or v > peak else peak
        max_dd = max(max_dd, 1 - v / peak)
    return dict(trims=trims, rebuys=rebuys, shares=shares,
                reserve_used=1 - cash / reserve, cap_hit=cap_hit, cash_out=cash_out,
                strat=shares * prices[-1] + cash, bh=100 * prices[-1], dd=max_dd,
                bh_dd=1 - min(prices) / prices[0], end=prices[-1] / prices[0] - 1)

def report(name, prices):
    r = ladder(prices)
    print(f"--- {name}: {prices[0]:.0f} -> {prices[-1]:.0f} ({r['end']:.0%}), trough {min(prices):.0f} ---")
    print(f"ladder: {r['trims']} trims / {r['rebuys']} rebuys | shares {r['shares']:.0f}/200 "
          f"| 2x cap hit: {r['cap_hit']} | cash exhausted: {r['cash_out']} | reserve used {r['reserve_used']:.0%}")
    print(f"end value: ladder ${r['strat']:,.0f} vs buy-hold ${r['bh']:,.0f} ({r['strat']/r['bh']-1:+.0%})")
    print(f"max drawdown: ladder {r['dd']:.0%} vs buy-hold {r['bh_dd']:.0%}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            prices = [float(r[0]) for r in csv.reader(f) if r]
        report(f"real data: {sys.argv[1]}", prices)
    else:
        report("SEVERE bear, META-2022-style",
               make_bear([336,220,222,200,195,162,160,162,138,100,95,120], 120))
        report("MODERATE bear, MSFT-2022-style",
               make_bear([336,310,305,290,280,260,265,255,245,230,215,240], 240))
