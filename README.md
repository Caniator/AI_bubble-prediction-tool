# AI Exit-Trigger Dashboard v3

V3 adds a backtest / stress-test layer to the live monitoring dashboard.

## New in v3
- Live / Backtest / Model rules tabs
- Stress templates for Dot-com 2000–02, GFC 2007–09, Covid 2020, and 2022 inflation bear
- Comparison of 100% stocks, 50/50, and regime-based strategy
- First WATCH / RISK REDUCTION / DEFENSIVE dates
- CAGR and max drawdown
- Same Telegram/email alerts and daily scheduler

## Critical limitation
The bundled crisis templates are illustrative tests of the rule engine, not investment-grade point-in-time backtests. AI-specific indicators did not exist in 2000/2008, and macro data are revised after publication.

A real historical test should use period-appropriate proxies and only data that were available at the time.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Daily job
```bash
python daily_update.py
```

## Demo allocation mapping
- JAUDA: 100% equities
- WATCH: 100% equities
- RISK REDUCTION: 50% equities / 50% bonds
- DEFENSIVE: 100% bonds

## Suggested v4
- genuine point-in-time historical dataset
- configurable re-entry ladder after -20/-30/-40% drawdowns
- automatic SEC/company IR parsing
- persistent cloud DB and deployment template
