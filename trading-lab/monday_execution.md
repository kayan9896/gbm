# Monday Oct 12, 2026 — Rule A execution sheet (15/15, closes-based)

Prepared Sat Oct 10. Triggers evaluated on **closing prices only**; 9.x% does not trigger.
Earnings-day triggers deferred one close.

## Rung table (taxable 15/15)

Friday Oct 9 closes re-verified Sun Oct 11 against multiple market-data sources
(statmuse / marketminute / marketbeat for MSFT; statmuse / tapeboard / tickeron for META;
finbold / marketbeat / stockscan for PLTR; marketbeat for MCD). Distances below use
these closes. **No name crossed a rung on Friday — statuses below confirm the
no-action expectation.**

| Name | Anchor (basis) | −15% buy-back rung | +15% trim rung | Fri Oct 9 close | Dist to nearest rung |
|---|---|---|---|---|---|
| MSFT | $486.43 (derived: $535.07 was ~+10% vs cost) | **$413.46** | **$559.39** | **$535.07** | 4.5% below trim rung |
| META | $777.00 (last action: sale) | **$660.45** | **$893.55** | **$718.67** | 8.8% above buy-back rung |
| PLTR | $190.05 (derived: $209.05 was ~+10% vs cost) | **$161.54** | **$218.55** | **$209.05** | 4.5% below trim rung |
| MCD | $251.50 (avg of 267 + ~236 buys, **equal-size assumption — confirm**) | **$213.78** | **$289.23** | **$235.42**¹ | 10.1% above buy-back rung |

¹ One aggregator (stockscan) shows $235.23, likely a split/dividend-adjusted figure vs
MarketBeat's $235.42 actual close print. The 19¢ difference doesn't move the ladder
either way; watch the broker's own close on Monday.

**Monday expectation: no-action day.** All four names sit between their first rungs.
Nothing fires unless a close crosses a rung above — then walk all crossed rungs.

## What each trigger means mechanically

- **Trim rung hit:** sell 15% of current holdings; reference ratchets to that close.
- **Buy-back rung hit:** buy 15% (add 15% of current share count); reference ratchets to that close.
- **Floor:** never trim below 50% of starting share count.
- **Cap:** cumulative rebuys ≤ 100% of starting share count (max 2× position).
- **Rebuys need cash on hand** (stress test finding: severe bears produce zero trim proceeds, so rebuys must come from a standing reserve, not assumed proceeds).

## Corrections vs the Oct 10 draft (actionable)

1. **MCD rungs were the old 10% numbers.** The doc said trim $276.65 / add $226.35
   — those are ±10% of $251.50. Under the adopted 15/15 rule the correct first
   rungs are **trim $289.23 / add $213.78**. Fixed in trading_rules.md.
2. **MSFT/PLTR anchors are derived, not stated.** $486.43 and $190.05 come from
   "10% gain from buying price" at $535.07 / $209.05. If his actual cost bases
   differ, the rungs shift proportionally — worth confirming the true cost bases
   before Monday's close.
3. **MCD average cost assumes equal-size buys** ($251.50). Unequal lots change it.

## Earnings watch (Rule A deferral clause)

- **PLTR Q3 earnings: Mon Nov 2, 2026, after market close** (estimate, corroborated
  across calendars). Defer any trigger on that day's close by one session.
- **MCD Q3 earnings: Wed Nov 4, 2026 — company-confirmed** (McDonald's own IR
  Events page, checked Oct 10: "11/04/26 — McDonald's Q3 2026 Earnings Conference
  Call", 08:30 AM EST). The aggregator claims of Oct 21/22 were not supported by
  any official source — treat them as wrong. Defer any trigger on the Nov 4
  close by one session; review the three MCD thesis flips (§3 of policy) before
  the print.
- **MSFT + META Q3 earnings: Wed Oct 28, 2026, after close — the double day**
  (confirmed Oct 10). Per the deferral rule, any trigger on Oct 28's close is
  evaluated on Oct 29's close instead. Weekend note (Motley Fool, Oct 11):
  META has fallen ≥7.95% in the sessions following three of its last four
  earnings prints, on capex concerns. META's buy-back rung ($660.45) sits 8.8%
  below Friday's close ($718.67) — i.e., right at the historical post-earnings
  drop magnitude. If Oct 28 repeats the pattern, the deferral clause means the
  buy-back would be evaluated on Oct 29's close, not in the earnings-day
  dislocation itself.
