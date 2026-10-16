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
