# Trading Rules — Steven (Oct 2026)

Two tiers, two rules. Tier is decided once, at position initiation, and never changed mid-trade.

## Tier definitions

- **Tier 1** = S&P 500 (VOO) member. Economic meaning: profitable, liquid, durable —
  time heals drawdowns. VOO membership is the executable proxy.
- **Tier 2** = everything else. Higher fat-tail risk; no price-based safety net.

## Rule A — Tier 1 Trim Ladder (take profit into strength, rebuy weakness)

Scope: Tier 1 positions only. All triggers on **closing prices**. 9.x% is not a trigger.
Earnings-day triggers may be deferred one close (don't fade fresh information).

**Taxable account version (15/15):**
- Anchor at cost basis; after each action the reference ratchets to that action's price.
- Close ≥ +15% vs reference → **sell 15%** of current holdings.
- Close ≥ −15% vs reference → **buy back 15%** (increase holdings by 15%).
- If multiple rungs are crossed at once, walk them all.
- **Floor:** holdings never fall below 50% of starting share count
  (trim only down to the floor). That half is sold on thesis break only, never on price.
- **Cap:** cumulative rebuys ≤ 100% of starting shares (max 2× starting position).

**Tax-free account version (10/10):** same mechanics with ±10% bands and 10% fractions
(tighter harvesting; no tax friction). First trim rungs are closer — use where the
account type allows it.

## Rule B — Tier 2 Swing Entries (harvest volatility, never average down)

Scope: non-VOO positions. **No rebuys on pullbacks** — unlike Tier 1, Tier 2 never
averages down (don't martingale into speculation).

**Entry — all three conditions required:**

1. **Fundamental filter.** Last 2 earnings reports both beat on EPS *and* revenue;
   no guidance cut in the last 2 quarters. (For unprofitable names: beats plus
   intact revenue growth.)
2. **Support filter.** Define the regime: if any 60-day window contained a ≥100% rise
   (a "leap breakthrough"), discard all data before that window; otherwise use a
   1-year lookback. Support S = a level with ≥90% of daily closes since regime start
   above S, **and** ≥2 touches (daily low within 3% above S) that closed back above.
   Entry trigger: daily low touches [S, 1.03×S] → buy at the close.
   If price *closes* >3% below S, that's a support break — no entry, wait for a reclaim.
3. **Probability filter.** With `~/workspace/tools/barrier_prob.py`:
   entry price → target = 1.10× entry, horizon = **6 months**.
   Require the **upper bound** of the P(reach +10%) scenario range to be **≥ 80%**.
   (This is a volatility gate: it admits lively names where the rung system can work
   and rejects calm ones. Calibrated Oct 2026: an RKLB-like 54%-vol name scores 84%
   at 6 months — but only 78% at 3 months, so don't shorten the horizon.)

**Exit:**
- **Trim 30%** of current holdings at each +10% compounded rung from entry
  (1.10×, 1.21×, 1.331× …), close-based. No floor required — Tier 2 is rented, not owned
  (a small 10% sentimental core is optional, never mandatory).
- **Thesis stop only — no price stops.** At entry, write down 3 named thesis killers
  for the position. Automatic exit review (default: sell) on: any EPS or revenue miss,
  any guide-down, or any killer triggering.

**Sizing (the real stop-loss for Tier 2):** each Tier 2 position ≤ 5% of portfolio;
total Tier 2 exposure ≤ 25%. (Fill in your own caps — but fill them in.)

## Shared principles

- Entries are systematic; exits are systematic. "Fear of the last round-trip" is not
  an exit rule — the ladder is.
- Tier 1 rebuys weakness because quality mean-reverts. Tier 2 never adds because
  speculation doesn't.
- Barrier probabilities answer "is this +EV?" (hold/don't hold). Position sizing and
  thesis stops answer "can I survive being wrong?" Both questions, every position.
- Re-check tier at initiation only. A Tier 2 name that later joins the S&P 500
  doesn't retroactively become Tier 1 for an open swing.

## Worked anchors (Oct 9, 2026 closes)

- MSFT $535.07 / META $718.67 / PLTR $209.05 — Rule A (taxable 15/15).
  META forward ladder anchored at last sale $777: trim on close > $893.55,
  buy-back on close < $660.45.
- MCD avg cost ~$251.50, px $236.90 — Rule A (15/15): trim rung $289.23, add rung $213.78.
  (Corrected Oct 10 — the draft listed the old 10%-band numbers $276.65/$226.35.)
- RKLB half held @ $62 cost, px ~$68.26 — Tier 2: no ladder; thesis stop only.
  Downside reference: P(touch $62 within 1yr) 73–93%; P(touch $50) 31–76%.
