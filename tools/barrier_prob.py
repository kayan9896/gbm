#!/usr/bin/env python3
"""
Barrier survival probability calculator.

Question answered: P(stock X NEVER reaches price Y within T years),
estimated as a RANGE over plausible volatility and drift assumptions.

Theory: first-passage probability for geometric Brownian motion
(reflection principle). No ML, no training data beyond price history
for volatility estimation.

Usage:
    python3 barrier_prob.py --price 68.76 --target 80 --years 1 --prices prices.csv
    python3 barrier_prob.py --price 68.76 --target 80 --years 1 --vol 0.54

prices.csv: one closing price per line (or a single column CSV), oldest first.
If --vol is given it overrides the estimate from --prices.
"""
import argparse, csv, math, sys
from statistics import NormalDist, stdev

N = NormalDist().cdf
TRADING_DAYS = 252


def estimate_vol(prices):
    """Annualized volatility from daily log returns."""
    rets = [math.log(prices[i + 1] / prices[i]) for i in range(len(prices) - 1)]
    if len(rets) < 2:
        raise ValueError("need at least 3 prices to estimate volatility")
    return stdev(rets) * math.sqrt(TRADING_DAYS)


def p_hit(S, barrier, T, sig, mu):
    """
    P(price touches `barrier` at least once within T years),
    GBM with annualized vol `sig` and total expected return `mu`.
    Works for upper (barrier > S) and lower (barrier < S) barriers.
    """
    nu = mu - 0.5 * sig ** 2
    sT = sig * math.sqrt(T)
    if barrier > S:  # upper barrier
        b = math.log(barrier / S)
        return N((-b + nu * T) / sT) + math.exp(2 * nu * b / sig ** 2) * N((-b - nu * T) / sT)
    else:  # lower barrier (symmetry: flip the drift sign)
        b = math.log(S / barrier)
        return N((-b - nu * T) / sT) + math.exp(-2 * nu * b / sig ** 2) * N((-b + nu * T) / sT)


def main():
    ap = argparse.ArgumentParser(description="P(stock never reaches target Y within T years), as a range.")
    ap.add_argument("--price", type=float, required=True, help="current price S")
    ap.add_argument("--target", type=float, required=True, help="barrier price Y")
    ap.add_argument("--years", type=float, default=1.0, help="horizon in years (default 1)")
    ap.add_argument("--prices", help="CSV file of daily closes, oldest first (for vol estimation)")
    ap.add_argument("--vol", type=float, help="annualized vol, overrides --prices (e.g. 0.54)")
    ap.add_argument("--rf", type=float, default=0.04, help="risk-free rate (default 0.04)")
    ap.add_argument("--capm", type=float, default=None,
                    help="CAPM expected return, e.g. 0.20 (else derived from --beta)")
    ap.add_argument("--beta", type=float, default=None, help="stock beta for CAPM drift")
    args = ap.parse_args()

    S, Y, T = args.price, args.target, args.years

    # --- volatility scenarios ---
    vols = {}
    if args.vol is not None:
        vols["given"] = args.vol
    if args.prices:
        with open(args.prices) as f:
            rows = [r for r in csv.reader(f) if r]
        closes = [float(r[0]) for r in rows]
        vols[f"realized({len(closes)}d)"] = estimate_vol(closes)
    if not vols:
        sys.exit("provide --vol or --prices (need volatility from somewhere)")
    base_vol = next(iter(vols.values()))
    # bracket vol +/-30% to show sensitivity
    vols = {"low (x0.7)": 0.7 * base_vol, "base": base_vol, "high (x1.3)": 1.3 * base_vol}

    # --- drift scenarios: this is where the RANGE comes from ---
    drifts = {"zero drift (conservative)": 0.0, f"risk-free ({args.rf:.0%})": args.rf}
    if args.capm is not None:
        drifts[f"CAPM ({args.capm:.0%})"] = args.capm
    elif args.beta is not None:
        capm = args.rf + args.beta * 0.05  # 5% equity risk premium
        drifts[f"CAPM beta={args.beta} ({capm:.0%})"] = capm

    direction = "reach or exceed" if Y > S else "fall to or below"
    print(f"\nP({S} will NEVER {direction} {Y} within {T}yr)\n")
    print(f"{'drift scenario':<28}" + "".join(f"{k:>14}" for k in vols))
    print("-" * (28 + 14 * len(vols)))
    lo, hi = 1.0, 0.0
    for dname, mu in drifts.items():
        row = []
        for vname, sig in vols.items():
            p_never = 1 - p_hit(S, Y, T, sig, mu)
            p_never = min(max(p_never, 0.0), 1.0)
            lo, hi = min(lo, p_never), max(hi, p_never)
            row.append(f"{p_never:>13.1%}")
        print(f"{dname:<28}" + "".join(row))
    print(f"\nRange across scenarios: {lo:.0%} - {hi:.0%}")
    print("Note: assumes smooth diffusion; jumps around events (earnings, launches)")
    print("make true tail risk fatter than shown. Cross-check with the option chain:")
    opt = "call" if Y > S else "put"  # upper barrier -> call, lower barrier -> put
    print(f"  P(never touch) <= 1 - |delta({Y}-strike {opt}, ~{T}yr expiry)|.")


if __name__ == "__main__":
    main()
