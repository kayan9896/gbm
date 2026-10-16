"""Formalizes Steven's stated AAOI range-trading rule and stress-tests it.

Rule as stated in chat (2026-10-09):
  - Regime: ignore data before March 2026 (structural break: price doubled
    from ~45 to ~100 and never fell back).
  - Entry: buy near 100 ("100 is usually the bottom since March 1").
  - Exit: sell near 130 ("almost 50% of the time after March 1 it was under 140").

Formalization (daily bars, fills assumed at close, no costs/slippage):
  - entry: buy at close when close <= 104 (within 4% of 100 support), flat only
  - exit (no-stop variant): sell at close when close >= 128 (~130 with fill haircut)
  - exit (stop variant): same target, plus stop-loss at 85 (~15% below entry)
    and a 30-trading-day time stop (prevents indefinite bag-holding)
  - buy-and-hold benchmark: buy at first entry-signal date, hold to last bar

This is IN-SAMPLE (levels chosen after eyeballing the same chart) and single-ticker.
It is a scaffold for out-of-sample extension, not a validation. Not financial advice.

Data: workspace/trading-lab/aaoi_daily.csv (daily OHLCV, Finnhub via web search,
2025-09-26 to 2026-10-07).
"""
import csv, datetime

rows = list(csv.DictReader(open("aaoi_daily.csv")))
for r in rows:
    r["date"] = datetime.date.fromisoformat(r["date"])
    for k in ("open", "high", "low", "close", "volume"):
        r[k] = float(r[k])

REGIME_START = datetime.date(2026, 3, 1)
ENTRY_MAX = 104.0      # "near 100"
EXIT_MIN = 128.0       # "near 130"
STOP = 85.0            # ~15% under entry, prices the loss tail
TIME_STOP = 30         # trading days

def run(use_stop: bool, use_time_stop: bool):
    trades, pos = [], None
    for i, r in enumerate(rows):
        if r["date"] < REGIME_START:
            continue
        if pos is None:
            if r["close"] <= ENTRY_MAX:
                pos = {"entry_date": r["date"], "entry": r["close"],
                       "entry_i": i, "worst": r["low"]}
        else:
            pos["worst"] = min(pos["worst"], r["low"])
            exit_px, why = None, None
            if r["low"] <= STOP and use_stop:          # stop triggered intraday
                exit_px, why = STOP, "stop"
            elif r["close"] >= EXIT_MIN:
                exit_px, why = r["close"], "target"
            elif use_time_stop and i - pos["entry_i"] >= TIME_STOP:
                exit_px, why = r["close"], "time-stop"
            if exit_px is not None:
                ret = exit_px / pos["entry"] - 1
                trades.append({**pos, "exit_date": r["date"], "exit": exit_px,
                               "ret": ret, "mae": pos["worst"] / pos["entry"] - 1,
                               "why": why})
                pos = None
    if pos is not None:  # still open at end of data -> mark to market
        ret = rows[-1]["close"] / pos["entry"] - 1
        trades.append({**pos, "exit_date": rows[-1]["date"], "exit": rows[-1]["close"],
                       "ret": ret, "mae": pos["worst"] / pos["entry"] - 1, "why": "open"})
    return trades

def report(name, trades):
    wins = [t for t in trades if t["ret"] > 0]
    losses = [t for t in trades if t["ret"] <= 0]
    wr = len(wins) / len(trades) if trades else 0
    aw = sum(t["ret"] for t in wins) / len(wins) if wins else 0
    al = sum(t["ret"] for t in losses) / len(losses) if losses else 0
    exp = wr * aw - (1 - wr) * abs(al)
    total = 1.0
    for t in trades:
        total *= 1 + t["ret"]
    worst_mae = min((t["mae"] for t in trades), default=0)
    print(f"--- {name}: {len(trades)} trades ---")
    print(f"win rate {wr:.0%} ({len(wins)}W/{len(losses)}L)  avg win {aw:+.1%}  "
          f"avg loss {al:+.1%}  expectancy/trade {exp:+.2%}")
    print(f"total compounded {total-1:+.1%}   worst intra-trade drawdown {worst_mae:+.1%}")
    for t in trades:
        print(f"  {t['entry_date']} {t['entry']:.1f} -> {t['exit_date']} {t['exit']:.1f} "
              f"{t['ret']:+.1%} ({t['why']}, MAE {t['mae']:+.1%})")
    print()
    return trades

print("=== AAOI range rule backtest (in-sample, single ticker) ===\n")
t_nostop = report("A: no stop (closest to what he did)", run(False, False))
t_stop = report("B: stop 85 + 30-day time stop", run(True, True))

# Verify his descriptive claims on post-regime closes
post = [r for r in rows if r["date"] >= REGIME_START]
under140 = sum(1 for r in post if r["close"] < 140) / len(post)
above100 = sum(1 for r in post if r["close"] >= 100) / len(post)
under100 = sum(1 for r in post if r["close"] < 100) / len(post)
worst_under = min(r["low"] for r in post)
print(f"claim check, {len(post)} post-Mar-1 bars:")
print(f"  closes under 140: {under140:.0%}  (he said 'almost 50%')")
print(f"  closes at/above 100: {above100:.0%}  (he said 'most of the time above 100')")
print(f"  closes under 100: {under100:.0%}; lowest intraday low since Mar 1: {worst_under:.2f}")

# Buy-and-hold benchmark from first entry signal
first = next(r for r in rows if r["date"] >= REGIME_START and r["close"] <= ENTRY_MAX)
bh = rows[-1]["close"] / first["close"] - 1
print(f"\nbuy-and-hold from first entry signal ({first['date']}, {first['close']:.1f}) "
      f"to {rows[-1]['date']} ({rows[-1]['close']:.1f}): {bh:+.1%}")

# His actual trade in the data
b = next(r for r in rows if r["date"] == datetime.date(2026, 9, 24))
s = next(r for r in rows if r["date"] == datetime.date(2026, 10, 6))
print(f"his actual trade: buy 9/24 @ {b['close']:.2f} -> sell 10/6 @ {s['close']:.2f} = "
      f"{s['close']/b['close']-1:+.1%}")
