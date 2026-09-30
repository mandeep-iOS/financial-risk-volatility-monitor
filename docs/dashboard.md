# Dashboard and Product Notes

The primary product is the universal SwiftUI iOS/macOS dashboard in `ios-macos/`, powered by the Python/FastAPI data science and modeling engine in `src/risk_monitor/`. It uses a dark navy fintech dashboard system with branded navigation, compact cards, blue/cyan accents, orange risk accents, native chart panels, explicit status pills, and dense above-the-fold hierarchy.

The Vite React frontend in `frontend/` is retained as an optional web reference/fallback. The Streamlit app in `dashboard/app.py` is retained as a legacy prototype and validation fallback.

Routes:

- `/overview`: selected-asset summary and scenario analysis.
- `/compare`: SPY versus QQQ comparison with date controls.
- `/forecast`: selected-symbol volatility forecast and freshness contract.
- `/evidence`: baseline versus GARCH evidence and technical diagnostics.

## Freshness Contract

Pages preserve `latest_available_price_date`, `latest_return_date`, `model_training_cutoff`, `forecast_generated_at_utc`, `forecast_start_date`, `forecast_end_date`, `forecast_status`, and `is_current` where applicable. Current artifacts end before today, so forecasts are labeled `historical/example`.

## Refresh Workflow

```bash
mkdir -p .cache/matplotlib
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/refresh_data.py
.venv/bin/python scripts/fit_garch.py
.venv/bin/python scripts/run_evaluation.py
.venv/bin/python scripts/score_forecasts.py
.venv/bin/python scripts/forecast_five_days.py
```

After refreshing, run Ruff, tests, and frontend/backend smoke checks.
