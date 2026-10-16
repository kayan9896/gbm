# Investment Policy — DRAFT for Steven's review (v0.1, Oct 9 2026)

Legend: **[H]** = Steven's stated position. **[P]** = assistant-proposed, needs his confirmation. Correct anything wrong; this is meant to become the written version of your system.

---

## 1. Core philosophy [H]

- No price stop-losses. When a position drops and fundamentals look intact, hold or average down.
- Evidence FOR: 52-week-bottom dip buys in HOOD, PLTR, MSFT, META — all rebounded profitably (META/MSFT bought Oct 9, 2026, rebounding same day). SPCX stopped at 109, then ran to 162 — the whipsaw cost of stops.
- Evidence AGAINST: FIG, bought 100+ post-IPO, now ~20 (−80%; needs +400% to recover). Held without a policy constraint.

## 2. Tier framework [H in principle; refinements P]

The FIG lesson, generalized: the mistake was granting a Tier 1 policy to a Tier 2 name.

- **Tier 1 — Compounder.** Dominant, profitable, real cash flow, durable position; bought washed-out. Policy: hold / average down freely, **but with a pre-committed maximum position size** so "Tier 1" doesn't become a license for unlimited doubling.
- **Tier 1.5 — Real business, priced on growth [P].** Real revenue and contracts, but unprofitable, high beta (RKLB-like: beta 3.2), priced on future growth. Policy: hold and average down **only on price-noise dips**, never on thesis-news dips; pre-committed max size; a written list of thesis killers that trigger exit regardless of price.
- **Tier 2 — Speculative.** Unprofitable, narrative-driven, no durable cash flow. Policy: small size and/or stop (price or thesis) required. No averaging without a fresh thesis.

The tier line is **cash flow and durability — whether time heals drawdowns — not VOO membership** (index inclusion is a lagging indicator) [P]. This supersedes the earlier "not in VOO → sell at −20%" shorthand, which you questioned.

**Open:** which tier the remaining RKLB half belongs in (Tier 1.5 proposed, not confirmed). Thesis-stop groundwork (three real catalysts, dated) prepared separately — confirm when reviewed.

## 3. Dip taxonomy [P]

Before adding to a loser, classify the dip and write the flip conditions down:

- **Price-noise dip:** multiple compression, execution stumble, macro derating. Business intact. Example: MCD Oct 2026 — 19.2x earnings vs 10-yr avg 26x, Q2 rev $7.10B (+3.7% YoY), EPS $3.38 beat vs $3.32 est; the damage was weak U.S. traffic (0.8% SSS), a value-menu misstep the CEO publicly owned, and the $8.5B NEXT franchisee plan spooking the market.
- **Thesis-news dip:** the reason you own it broke. Flip conditions must be specific and checkable. MCD's written flips: (1) U.S. traffic still negative despite the value fixes, (2) the 50-year dividend-growth streak breaking, (3) NEXT spending ballooning beyond plan. None have happened — dividend was just raised 3.8% in September.

## 4. Quant tools

- `~/workspace/tools/barrier_prob.py` — closed-form first-passage probabilities. Report **ranges over vol/drift scenarios, never points** (drift dominates the answer). Upside case (RKLB, ~68.26 on Oct 9): 18–36% chance of **never** reaching 80 in 12 months. Downside case: P(touching 62) 73–93%, P(touching 55) 46–84%, P(touching 50) 31–76%. Caveats: smooth-diffusion math understates jump risk around launches/earnings, so treat the "never" side as slightly optimistic. Downside cross-check fixed to put deltas.
- `~/workspace/trading-lab/aaoi_range_backtest.py` — in-sample scaffold only. Real lesson: the loss tail you ignored was real (intraday low 76 in July, −24% under the assumed bottom; no-stop variant worst drawdown −24.2%). Formalized rule "enter close ≤104 / exit close ≥128" reproduced your actual trade at +28.8%.

Use the barrier model to price patience (is holding +EV?); use the tier guardrails for the thesis-break paths the model is blind to.

## 5. Position ledger (documented facts only; sizes TBD)

| Ticker | Status | Entry | Exit / Last | Tier | Next checkpoint |
|---|---|---|---|---|---|
| AAOI | **Closed** Oct 6 | 100 (Sep 24) | 130 (+28.8% verified) | range trade | — |
| RKLB | **Half open** | 62 (Sep 1) | sold half at 75 (Oct 6); ~68.26 (Oct 9) | open question [P: 1.5] | earnings ~Nov 9; thesis killers pending review |
| MCD | **Open** | 267, then ~236 (avg ~251.50) | — | [P: Tier 1, price-noise dip] | **Q3 earnings Oct 21–22** (see §6) |
| META | Open | bought dip Oct 9 | rebounding, profitable | [P: Tier 1] | — |
| MSFT | Open | bought dip Oct 9 | rebounding, profitable | [P: Tier 1] | — |
| HOOD | (earlier) | 52w-bottom dip | rebounded | — | details TBD |
| PLTR | (earlier) | 52w-bottom dip | rebounded | — | details TBD |
| FIG | **Held** | 100+ post-IPO | ~20 | [P: Tier 2 — misclassified at entry] | thesis-stop needed |
| SPCX | Stopped | — | stopped 109 → ran to 162 | — | lesson recorded |

## 6. Active checkpoints

1. **MCD Q3 earnings — Wed Nov 4, 2026, company-confirmed** (McDonald's own IR Events
   page, checked Oct 10: earnings call 08:30 AM EST Nov 4; no Q3 press release
   published yet as of Oct 10). The Oct 21/22 aggregator claims were not supported
   by any official source. Review the three flip conditions (§3) before the print.
   Consensus est: EPS ~$3.42, rev ~$7.3–7.4B. Supersedes the "Oct 21/22" wording above.
2. **RKLB** — no launch dated before Monday's open (weekend check); earnings ~Nov 9 is the next real test. Thesis killers pending your review.

## 7. Rules I'm proposing you adopt [P]

1. Every new position gets a tier **before** entry, written down.
2. Every averaged-down loser gets written flip conditions **before** the add.
3. Every position gets a pre-committed max size; Tier 1 status never overrides the cap.
4. Barrier probabilities are ranges; drift dominates; jump risk is understated — size accordingly.
