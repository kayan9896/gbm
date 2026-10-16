# Tickline

Local stock chart desk. Type a ticker, get a Yahoo Finance price chart. No paid APIs or accounts.

## Run

```powershell
cd $HOME\stock-portal
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Quotes come from Yahoo Finance’s public chart endpoint through a tiny local proxy, so the browser never talks to Yahoo directly (that avoids CORS and keeps it free).

## Target probabilities

Click any point on the chart to open a popup for that date and price: enter a
target price (defaults to +10%), pick a horizon (3/6/12 months), optionally set
the risk-free rate and an extra drift scenario, then Calculate. The backend
(`POST /api/probability`, math in `probability.py`) returns P(reaching the
target) as a range over volatility (0.7×/1×/1.3× of the 1y realized daily vol)
and drift scenarios — a geometric-Brownian-motion first-passage model, the
same math as `tools/barrier_prob.py` in this repo. Smooth diffusion
understates event jumps; cross-check with the option chain.
