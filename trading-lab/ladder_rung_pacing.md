# Ladder rung pacing — P(first rung touched), from Friday Oct 9 closes

Prepared Sat Oct 10, 2026 (markets closed; closes are Fri Oct 9).
Companion to `monday_execution.md` — this answers "how soon does the machine start trading?"

## Inputs

| Name | Fri Oct 9 close | Anchor | Trim rung (+15%) | Buy-back rung (−15%) | Nearer rung | Distance to nearer rung |
|---|---|---|---|---|---|---|
| MSFT | $535.07 | $486.43 | $559.39 | $413.46 | trim | **+4.5%** |
| PLTR | $209.05 | $190.05 | $218.55 | $161.54 | trim | **+4.5%** |
| META | $718.67 | $777.00 | $893.55 | $660.45 | buy-back | **−8.1%** |
| MCD  | $235.23 | $251.50 | $289.23 | $213.78 | buy-back | **−9.1%** |

MSFT/PLTR sit ~10% above their anchors (Friday's moves: MSFT +2.38%, PLTR +5.17%);
META/MCD sit below theirs (META −7.5% under the 777 anchor, MCD −6.5% under 251.50).

60d realized vols (Finnhub daily closes, 2026): PLTR 71%, MSFT 38%, META 46%, MCD 22%.

## P(touch the rung at least once) — range over vol ±30% × drift {0%, 4%}

| Name | Rung | 1 month | 3 months | 6 months |
|---|---|---|---|---|
| **PLTR** | trim $218.55 (+4.5%) | **74–85%** | 84–90% | 88–92% |
| | buy-back $161.54 (−22.7%) | 8–38% | 32–65% | 50–78% |
| **MSFT** | trim $559.39 (+4.5%) | **55–75%** | 72–85% | 80–89% |
| | buy-back $413.46 (−22.7%) | 0–8% | 5–34% | 17–52% |
| **META** | buy-back $660.45 (−8.1%) | **36–65%** | 60–81% | 71–87% |
| | trim $893.55 (+24.3%) | 2–19% | 15–42% | 30–55% |
| **MCD** | buy-back $213.78 (−9.1%) | **3–25%** | 18–52% | 33–66% |
| | trim $289.23 (+23.0%) | 0–1% | 1–14% | 5–30% |

Reading: the ladder's first action is likely a **PLTR trim** (Friday's +5.17% put it
4.5% below the rung; a 59–85% chance of touching within a month even in the calmer
30d vol regime — PLTR's 30d vol is 42.5% vs 60d 71%; under the 30d regime the 1mo
trim-touch is 59–77%, 3mo 75–86%). MSFT's trim rung is the second-most-likely
first trigger. META leans toward a buy-back first; MCD will probably sit quiet —
its −9.1% rung has only 3–25% odds within a month at 22% vol.

## Earnings overlay (Rule A deferral clause)

- **MSFT: Wed Oct 28, 2026, after market close** — company-announced (Oct 7, 2026).
  Confirmed. Eve reminder proposed for Tue Oct 27.
- **META: Wed Oct 28, 2026, after market close** — TipRanks marks it "Confirmed"
  (checked Oct 10; independently corroborated by Oct 6 pre-earnings coverage).
  Same afternoon as MSFT: Oct 28 is a double-earnings day for the ladder, and the
  deferral clause covers both names' closes that day. Eve reminder proposed for
  Tue Oct 27 evening (matching the PLTR/MCD pattern).
- PLTR (Nov 2 AMC) and MCD (Nov 4, company-confirmed) already on the books.

Note: MSFT/META earnings both fall inside the 1-month window above. Earnings jumps
are exactly what smooth-diffusion math understates — the P(touch) ranges near
Oct 28 are the least reliable, and any rung crossed on those closes is deferred
one session per Rule A.

## Limits (do not drop when quoting)

1. First-passage "touch" ≠ close-crossing: the ladder triggers on closes only, so
   these slightly overstate trigger odds (intraday spike-and-reverse doesn't count).
2. Barriers ratchet after each action — these are single-rung numbers, not the full
   joint ladder path.
3. Ranges, not points: drift dominates the answer; zero-drift vs 4% is the whole spread.
4. Rungs here assume the anchors in monday_execution.md; if true cost bases differ,
   distances shift proportionally (esp. MSFT/PLTR derived anchors, MCD equal-lot assumption).
